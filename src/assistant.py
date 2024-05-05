import pandas as pd

from src.descriptionReader import DescriptionReader
from extractor.RelationshipExtractor import RelationshipsExtractor
from extractor.conceptsExtractor import ConceptsExtractor
from sentence_generator.descriptionGenerator import DescriptionGenerator
from workflow.workflowStart import WorkflowStart
import spacy


def create_attributes_map(attributes_description, concepts, actual_description):
    data = pd.DataFrame(columns=['class_name', 'attributes', 'generated_description', 'actual_description'])
    for index, row in attributes_description.iterrows():
        class_name = row['class']
        attribute_name = row['attribute']
        generated_sentence = row['sentence']
        actual_sentence_ids = set()

        attribute_presence_set = set()
        class_name_presence_set = set()
        for i, token in concepts.iterrows():
            if token['token'].lower_ in attribute_name.lower() or token[
                'lemmatized_text'].lower() in attribute_name.lower():
                attribute_presence_set.add(token['s_id'])

            elif token['token'].lower_ in class_name.lower() or token[
                'lemmatized_text'].lower() in class_name.lower():
                class_name_presence_set.add(token['s_id'])

        answer_set = attribute_presence_set & class_name_presence_set
        if len(answer_set) == 0:
            answer_set = attribute_presence_set

        actual_sentence_ids.update(answer_set)
        # for attribute in attribute_name: attribute_presence_set = set() class_name_presence_set = set() for i,
        # token in concepts.iterrows(): if token['token'].lower_ in attribute.lower() or token[
        # 'lemmatized_text'].lower() in attribute.lower(): attribute_presence_set.add(token['s_id'])
        #
        #         elif token['token'].lower_ in class_name.lower() or token[
        #             'lemmatized_text'].lower() in class_name.lower():
        #             class_name_presence_set.add(token['s_id'])
        #
        #     answer_set = attribute_presence_set & class_name_presence_set
        #     if len(answer_set) == 0:
        #         answer_set = attribute_presence_set
        #
        #     actual_sentence_ids.update(answer_set)


        actual_sentences = [actual_description[int(idx.replace("S", ""))] for idx in actual_sentence_ids]
        for sentence in actual_sentences:
            data.loc[len(data)] = [class_name, attribute_name, generated_sentence, sentence]

        if len(actual_sentences) == 0:
            data.loc[len(data)] = [class_name, attribute_name, generated_sentence, ""]

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
                             concepts):
    data = pd.DataFrame(columns=['source', 'target', 'role', 'generated_description', 'actual_description'])
    sentences = actual_description.split(".")
    for index, row in relationship_description.iterrows():
        source = row['source']
        target = row['target']
        role = row['role']
        actual_sentence_ids = set()
        for i, relationship in relationships.iterrows():
            # TODO add check for role
            if (relationship['source'].lower() in source.lower() and relationship[
                'target'].lower() in target.lower()) or (
                    relationship['source'].lower() in target.lower() and relationship[
                'target'].lower() in source.lower()):
                # sdx = relationship['sdx'].replace("S", '')
                actual_sentence_ids.add(relationship['sdx'])

        if len(actual_sentence_ids) == 0:
            res = assistant.language_model(source)
            for token in res:
                if token.head == token:
                    source_head = token.text
                    break

            res = assistant.language_model(target)
            for token in res:
                if token.head == token:
                    target_head = token.text
                    break

            source_presence_set = set()
            target_presence_set = set()
            for i, token in concepts.iterrows():
                if token['token'].lower_ == source.lower() or token[
                    'lemmatized_text'].lower() == source.lower() or token['token'].lower_ == source_head.lower() or token[
                        'lemmatized_text'].lower() == source_head.lower():
                    source_presence_set.add(token['s_id'])

                elif token['token'].lower_ in target.lower() or token[
                    'lemmatized_text'].lower() in target.lower() or token['token'].lower_ in target_head.lower() or token[
                    'lemmatized_text'].lower() in target_head.lower():
                    target_presence_set.add(token['s_id'])

            answer_set = source_presence_set & target_presence_set
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
        self.errors = []
        self.warnings = []
        self.description_reader = DescriptionReader(domain_name)
        self.description_generator = DescriptionGenerator(domain_name)
        self.concepts_extractor = ConceptsExtractor()
        self.relationships_extractor = RelationshipsExtractor()
        self.language_model = spacy.load("en_core_web_lg")

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

        domain_state = self.description_generator.get_description()

        self.attributes_map = create_attributes_map(self.description_generator.get_attributes(),
                                                    self.concepts_extractor.df_concepts, sentences)
        self.relationships_map = create_relationships_map(self.description_generator.get_attributes(),
                                                          self.description_generator.get_relationships(),
                                                          self.relationships_extractor.df_class_associations,
                                                          actual_description, self.concepts_extractor.df_concepts)


        # print(self.attributes_map)
        #
        print(self.relationships_map)
        workflow = WorkflowStart(self.attributes_map, self.relationships_map)
        workflow.run()

        print("Done")


# domain_name = "sustainable-transportation"
# assistant = Assistant(domain_name)
# assistant.run()
