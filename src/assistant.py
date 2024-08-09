import pandas as pd

from src.descriptionReader import DescriptionReader
from extractor.RelationshipExtractor import RelationshipsExtractor
from extractor.conceptsExtractor import ConceptsExtractor
from sentence_generator.descriptionGenerator import DescriptionGenerator
from workflow.workflowStart import WorkflowStart
import spacy


def create_attributes_map(attributes_description, concepts, actual_description):
    data = pd.DataFrame(columns=['class_name', 'attributes', 'generated_description', 'actual_description'])
    all_sentence_ids = set()
    for sdx in range(len(actual_description)):
        all_sentence_ids.add("S" + str(sdx))

    for index, row in attributes_description.iterrows():
        class_name = row['class'].lower()
        attribute_name = row['attribute'].lower()
        generated_sentence = row['sentence']
        actual_sentence_ids = set()

        attribute_presence_set = set()
        class_name_presence_set = set()

        for i, token in concepts.iterrows():
            token_str = token['token'].lower_
            lemma_str = token['lemmatized_text'].lower()

            if token_str in attribute_name or lemma_str in attribute_name.lower():
                attribute_presence_set.add(token['s_id'])

            elif token_str in class_name.lower() or lemma_str in class_name.lower():
                class_name_presence_set.add(token['s_id'])

        answer_set = attribute_presence_set & class_name_presence_set
        if len(answer_set) == 0:
            if len(attribute_presence_set) != 0:
                answer_set = attribute_presence_set
            elif len(class_name_presence_set) != 0:
                answer_set = class_name_presence_set
            else:
                answer_set = all_sentence_ids

        actual_sentence_ids.update(answer_set)
        actual_sentences = [actual_description[int(idx.replace("S", ""))] for idx in actual_sentence_ids]
        for sentence in actual_sentences:
            data.loc[len(data)] = [class_name, attribute_name, generated_sentence, sentence]

        if len(actual_sentences) == 0:
            data.loc[len(data)] = [class_name, attribute_name, generated_sentence, ""]

    # print("Time for create attribute map ", (end-start)/60)
    return data


def flatten_list(nested_list):
    flat_list = []
    for element in nested_list:
        if isinstance(element, list):
            flat_list.extend(flatten_list(element))
        else:
            flat_list.append(element)
    return flat_list


def create_relationships_map(attributes_description, relationship_description, relationships, actual_description,
                             concepts, language_model):
    data = pd.DataFrame(columns=['source', 'target', 'role', 'generated_description', 'actual_description'])
    sentences = actual_description.split(".")
    for index, row in relationship_description.iterrows():
        source = row['source'].lower()
        target = row['target'].lower()
        role = row['role']
        actual_sentence_ids = set()
        for i, relationship in relationships.iterrows():
            # TODO add check for role
            rel_source = relationship['source'].lower()
            rel_target = relationship['target'].lower()

            if ((rel_source in source and rel_target in target)
                    or (rel_target in source and rel_source in target)):
                # sdx = relationship['sdx'].replace("S", '')
                actual_sentence_ids.add(relationship['sdx'])

        if len(actual_sentence_ids) == 0:
            res = language_model(source)
            for token in res:
                if token.head == token:
                    source_head = token.text.lower()
                    break

            res = language_model(target)
            for token in res:
                if token.head == token:
                    target_head = token.text.lower()
                    break

            source_presence_set = set()
            target_presence_set = set()
            for i, token in concepts.iterrows():
                token_str = token['token'].lower_
                lemma_str = token['lemmatized_text'].lower()

                if (token_str == source or lemma_str == source or
                        token_str == source_head or lemma_str == source_head):
                    source_presence_set.add(token['s_id'])

                elif (token_str in target or lemma_str in target
                      or token_str in target_head or lemma_str in target_head):
                    target_presence_set.add(token['s_id'])

            answer_set = source_presence_set & target_presence_set
            if len(answer_set) == 0:
                answer_set = source_presence_set | target_presence_set
            actual_sentence_ids.update(answer_set)

        # if len(actual_sentence_ids) == 0:
        #     words_to_match = [source, target, role]
        #     # words_to_match.extend(attributes_description.loc[attributes_description['class'] == source, 'attribute'])
        #     # words_to_match.extend(attributes_description.loc[attributes_description['class'] == target, 'attribute'])
        #     matching_sentences_index = re.get_matching_sentences(actual_description, flatten_list(words_to_match))
        #     actual_sentence_ids.update(matching_sentences_index)

        actual_sentences = [sentences[int(idx.replace("S", ""))] for idx in actual_sentence_ids]
        for sentence in actual_sentences:
            data.loc[len(data)] = [source, target, role, row['sentence'], sentence]

        if len(actual_sentences) == 0:
            data.loc[len(data)] = [source, target, role, row['sentence'], ""]

    return data


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
        self.language_model = spacy.load("en_core_web_lg")

        # TODO Redundant part
        self.domain_name = domain_name

        # Tokenizer treats 'id' as I'd and that's why it gets split as 'I' and 'd'.
        # but here I want it to be a single word, hence removing that rule.
        self.language_model.tokenizer.rules = {key: value for key, value in self.language_model.tokenizer.rules.items()
                                               if key != "id"}

    def get_errors(self):
        return self.errors

    def get_warnings(self):
        return self.warnings

    def run(self):
        actual_description = self.description_reader.get_actual_description()
        # preprocessed_description = coref.get_preprocessed_text(actual_description)
        # preprocessed_description = [sent.strip() for sent in preprocessed_description.split(".")]

        sentences = [sent.strip() for sent in actual_description.split(".")]
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

        self.attributes_map = create_attributes_map(self.description_generator.get_attributes(),
                                                    self.concepts_extractor.df_concepts, sentences)

        self.associations_map = create_relationships_map(self.description_generator.get_attributes(),
                                                         self.description_generator.get_associations(),
                                                         self.relationships_extractor.df_class_associations,
                                                         actual_description, self.concepts_extractor.df_concepts,
                                                         self.language_model)

        self.aggregations_map = create_relationships_map(self.description_generator.get_attributes(),
                                                         self.description_generator.get_aggregations(),
                                                         self.relationships_extractor.df_class_associations,
                                                         actual_description, self.concepts_extractor.df_concepts,
                                                         self.language_model)

        self.compositions_map = create_relationships_map(self.description_generator.get_attributes(),
                                                         self.description_generator.get_compositions(),
                                                         self.relationships_extractor.df_class_associations,
                                                         actual_description, self.concepts_extractor.df_concepts,
                                                         self.language_model)

        self.inheritance_map = create_relationships_map(self.description_generator.get_attributes(),
                                                        self.description_generator.get_inheritance(),
                                                        self.relationships_extractor.df_class_associations,
                                                        actual_description, self.concepts_extractor.df_concepts,
                                                        self.language_model)

        workflow = WorkflowStart(
            [self.attributes_map, self.associations_map, self.aggregations_map, self.compositions_map,
             self.inheritance_map], self.domain_name)
        errors = workflow.run()

        print(errors)
        print("Done")
