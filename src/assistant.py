# nltk.download('averaged_perceptron_tagger_eng')

import os
import sys

from preprocessor.attribute_matcher import AttributeMatcher
from preprocessor.relationship_matcher import RelationshipMatcher

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import coreferenceResolution as coref
from src.descriptionReader import DescriptionReader
from extractor.RelationshipExtractor import RelationshipsExtractor
from extractor.conceptsExtractor import ConceptsExtractor
from sentence_generator.descriptionGenerator import DescriptionGenerator
from workflow.workflowStart import WorkflowStart
import spacy


class Assistant:
    def __init__(self, domain_name):
        self.compositions_map = None
        self.aggregations_map = None
        self.associations_map = None
        self.attributes_map = None
        self.inheritance_map = None
        self.errors = []
        self.warnings = []
        self.description_reader = DescriptionReader(domain_name)
        self.description_generator = DescriptionGenerator(domain_name)
        self.concepts_extractor = ConceptsExtractor()
        self.relationships_extractor = RelationshipsExtractor()
        self.language_model = spacy.load("en_core_web_trf")

        # TODO Redundant part
        self.domain_name = domain_name

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
        sentences = [sent.strip() for sent in actual_description.split(".")]

        actual_description = actual_description.replace("e.g.", "")
        actual_description = actual_description.replace("i.e.", "")
        actual_description = actual_description.replace("etc.", "")

        preprocessed_description = coref.get_preprocessed_text(actual_description)
        sentences = [sent.strip() for sent in preprocessed_description.split(".")]

        for sdx, sent in enumerate(sentences):
            sdx = "S" + str(sdx)
            preprocessed_sent = sent.replace(".", "")
            self.concepts_extractor.extract_candidate_concepts(
                self.language_model(preprocessed_sent), sdx
            )
            self.relationships_extractor.extract_candidate_relationships(
                self.concepts_extractor.df_chunks,
                self.concepts_extractor.df_concepts,
                self.language_model,
                self.language_model(preprocessed_sent),
                sdx,
            )

        # Get difference between previous version and current version to check the changes.
        # Generate sentences only for changed elements.

        # self.description_generator.generate_description(changes)

        self.attributes_map = self.attribute_matcher.create_attributes_map(self.description_generator.get_attributes(),
                                                                           self.concepts_extractor.df_concepts,
                                                                           sentences)

        self.associations_map = self.relationships_matcher.create_relationships_map(
            self.description_generator.get_attributes(),
            self.description_generator.get_associations(),
            self.relationships_extractor.df_class_associations,
            actual_description, self.concepts_extractor.df_concepts,
            self.language_model)

        self.aggregations_map = self.relationships_matcher.create_relationships_map(
            self.description_generator.get_attributes(),
            self.description_generator.get_aggregations(),
            self.relationships_extractor.df_class_associations,
            actual_description, self.concepts_extractor.df_concepts,
            self.language_model)

        self.compositions_map = self.relationships_matcher.create_relationships_map(
            self.description_generator.get_attributes(),
            self.description_generator.get_compositions(),
            self.relationships_extractor.df_class_associations,
            actual_description, self.concepts_extractor.df_concepts,
            self.language_model)

        self.inheritance_map = self.relationships_matcher.create_relationships_map(
            self.description_generator.get_attributes(),
            self.description_generator.get_inheritance(),
            self.relationships_extractor.df_class_associations,
            actual_description, self.concepts_extractor.df_concepts,
            self.language_model)

        workflow = WorkflowStart(
            [self.attributes_map, self.associations_map, self.aggregations_map, self.compositions_map,
             self.inheritance_map], self.domain_name)
        errors = workflow.run()

        # calculate_metrics()

        print(errors)
        print("Done")


assistant = Assistant("factory")
assistant.run()
