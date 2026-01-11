# nltk.download('averaged_perceptron_tagger_eng')

import os
import sys

from common.util import timer
from evaluation.ResultAggregator import calculate_metrics
from preprocessor.attribute_matcher import AttributeMatcher
from preprocessor.relationship_matcher import RelationshipMatcher

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from preprocessor import coreferenceResolution as coref
from src.descriptionReader import DescriptionReader
from extractor.RelationshipExtractor import RelationshipsExtractor
from extractor.conceptsExtractor import ConceptsExtractor
from sentence_generator.descriptionGenerator import DescriptionGenerator
from workflow.workflowStart import WorkflowStart
import spacy


class Assistant:
    def __init__(self, domain_name, results_dir):
        self.enum_map = None
        self.compositions_map = None
        self.aggregations_map = None
        self.associations_map = None
        self.attributes_map = None
        self.inheritance_map = None
        self.errors = []
        self.warnings = []
        self.language_model = spacy.load("en_core_web_trf")
        self.results_dir = results_dir
        self.description_reader = DescriptionReader(domain_name)

        # TODO Redundant part
        self.domain_name = domain_name

        self.log_file_path = f"{results_dir}//predictions//{self.domain_name}//domain_logs2.txt"
        if not os.path.exists(rf"{results_dir}//predictions//{self.domain_name}"):
            os.makedirs(f"{results_dir}//predictions//{self.domain_name}")

        if not os.path.exists(self.log_file_path):
            with open(self.log_file_path, "w") as f:
                f.write("Execution Time Log\n")

        self.description_generator = DescriptionGenerator(domain_name, self.language_model)

        self.concepts_extractor = ConceptsExtractor()
        self.relationships_extractor = RelationshipsExtractor()

        # Tokenizer treats 'id' as I'd and that's why it gets split as 'I' and 'd'.
        # but here I want it to be a single word, hence removing that rule.
        self.language_model.tokenizer.rules = {key: value for key, value in self.language_model.tokenizer.rules.items()
                                               if key != "id"}

        self.attribute_matcher = AttributeMatcher()
        self.relationships_matcher = RelationshipMatcher()

    def get_errors(self):
        return self.errors

    def get_warnings(self):
        return self.warnings

    def run(self):
        actual_description = self.description_reader.get_actual_description()
        with timer("Concept and Relationship extraction", self.log_file_path):
            sentences = [sent.strip() for sent in actual_description.split(".")]
            actual_description = actual_description.replace("e.g.", "")
            actual_description = actual_description.replace("i.e.", "")
            actual_description = actual_description.replace("etc.", "")

            original_description, sentences = coref.get_preprocessed_text(actual_description)

            noun_chunks = []

            for sdx, sent in enumerate(original_description):
                sent_doc = self.language_model(sent)
                for chunk in sent_doc.noun_chunks:
                    noun_chunks.append((sdx, chunk))

            for sdx, sent in enumerate(sentences):
                sdx = "S" + str(sdx)
                preprocessed_sent = sent.replace(".", "")
                sent_doc = self.language_model(preprocessed_sent)
                self.concepts_extractor.extract_candidate_concepts(
                    sent_doc, sdx
                )
                self.relationships_extractor.extract_candidate_relationships(
                    self.concepts_extractor.df_chunks,
                    self.concepts_extractor.df_concepts,
                    self.language_model,
                    sent_doc,
                    sdx,
                )

        # TODO: write results of concept and relationship extractor
        self.concepts_extractor.df_concepts.to_excel(
            f"{self.results_dir}/predictions/{self.domain_name}/extracted_concepts.xlsx", index=False)
        self.relationships_extractor.df_class_associations.to_excel(
            f"{self.results_dir}/predictions/{self.domain_name}/extracted_relationships.xlsx", index=False)

        with timer("Semantic matching", self.log_file_path):
            self.attributes_map, attributes_dict = self.attribute_matcher.create_attributes_map(
                self.description_generator.get_attributes(),
                self.concepts_extractor.df_concepts,
                original_description)

            self.associations_map, associations_dict = self.relationships_matcher.create_relationships_map(
                self.description_generator.get_attributes(),
                self.description_generator.get_associations(),
                self.relationships_extractor.df_class_associations,
                original_description, self.concepts_extractor.df_concepts,
                self.language_model, noun_chunks)

            self.aggregations_map, aggregations_dict = self.relationships_matcher.create_relationships_map(
                self.description_generator.get_attributes(),
                self.description_generator.get_aggregations(),
                self.relationships_extractor.df_class_associations,
                original_description, self.concepts_extractor.df_concepts,
                self.language_model, noun_chunks)

            self.compositions_map, compositions_dict = self.relationships_matcher.create_relationships_map(
                self.description_generator.get_attributes(),
                self.description_generator.get_compositions(),
                self.relationships_extractor.df_class_associations,
                original_description, self.concepts_extractor.df_concepts,
                self.language_model, noun_chunks)

            self.inheritance_map, inheritance_dict = self.relationships_matcher.create_relationships_map(
                self.description_generator.get_attributes(),
                self.description_generator.get_inheritance(),
                self.relationships_extractor.df_class_associations,
                original_description, self.concepts_extractor.df_concepts,
                self.language_model, noun_chunks)

            self.enum_map, enum_dict = self.attribute_matcher.create_enum_map(
                self.description_generator.get_enums(),
                self.concepts_extractor.df_concepts,
                self.relationships_extractor.df_class_associations,
                original_description)

        self.attributes_map.to_excel(
            f"{self.results_dir}/predictions/{self.domain_name}/attributes_semantic_matching_results.xlsx", index=False)
        self.associations_map.to_excel(
            f"{self.results_dir}/predictions/{self.domain_name}/associations_semantic_matching_results.xlsx",
            index=False)
        self.aggregations_map.to_excel(
            f"{self.results_dir}/predictions/{self.domain_name}/aggregations_semantic_matching_results.xlsx",
            index=False)
        self.compositions_map.to_excel(
            f"{self.results_dir}/predictions/{self.domain_name}/compositions_semantic_matching_results.xlsx",
            index=False)
        self.inheritance_map.to_excel(
            f"{self.results_dir}/predictions/{self.domain_name}/inheritance_semantic_matching_results.xlsx",
            index=False)
        self.enum_map.to_excel(
            f"{self.results_dir}/predictions/{self.domain_name}/enums_semantic_matching_results.xlsx", index=False)

        with timer("LLM ", self.log_file_path):
            workflow = WorkflowStart(
                [self.attributes_map, self.associations_map, self.aggregations_map, self.compositions_map,
                 self.inheritance_map, self.enum_map], self.domain_name, self.results_dir, self.runInParallel)
            errors = workflow.run()

        with timer("Result calculation", self.log_file_path):
            calculate_metrics(self.domain_name, self.results_dir)

        # print(errors)
        print("Done")


domains = ["R1-restaurant"]

for domain in domains:
    assistant = Assistant(domain, "../final_evaluation")
    assistant.run()
