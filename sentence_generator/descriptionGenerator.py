import pandas as pd

from sentence_generator.sentenceFromAttributes import SentenceFromAttributes
from sentence_generator.sentenceFromAssociations import SentenceFromAssociations
from sentence_generator.sentenceFromCompositions import SentenceFromCompositions
from sentence_generator.sentenceFromAggregations import SentenceFromAggregation
from sentence_generator.sentenceFromInheritance import SentenceFromInheritance
from sentence_generator.postProcessor import PostProcessor
from domain_converter.xmlReader import parse_domain_model

model_path = "D:\\Thesis\\modelling-assistant\\tests\\\domain-models\\cdm-models\\"


class DescriptionGenerator:
    def __init__(self, domain_name):
        self.domain_name = domain_name
        attributes, associations, compositions, aggregations, inheritance, enums = self.read_model()
        self.generator_from_attributes = SentenceFromAttributes(attributes)
        self.generator_from_associations = SentenceFromAssociations(associations)
        self.generator_from_compositions = SentenceFromCompositions(compositions)
        self.generator_from_aggregations = SentenceFromAggregation(aggregations)
        self.generator_from_inheritance = SentenceFromInheritance(inheritance)
        self.post_processor = PostProcessor()

        # TODO : Keep only one format either description string or 'attributes' and 'relationships' dataframes
        self.description = ''
        self.attributes_description = pd.DataFrame(columns=['class', 'attribute', 'sentence'])
        self.relationships = pd.DataFrame(columns=['source', 'target', 'role', 'sentence'])
        self.generate_description()

    def get_description(self):
        return self.description

    def get_attributes(self):
        return self.attributes_description

    def get_relationships(self):
        return self.relationships

    def read_model(self):

        # Code to read domain diagram in .cdm format
        class_attributes, associations, compositions, aggregations, inheritance, enums = parse_domain_model(model_path + self.domain_name + ".cdm")

        return class_attributes, associations, compositions, aggregations, inheritance, enums
        # TODO below code was used to read domain diagram from txt file
        # with open(model_path + self.domain_name, 'r') as file:
        #     content = file.read()
        #
        # local_vars = {}
        #
        # exec(content, local_vars)
        #
        # return (local_vars.get('class_attributes', {}), local_vars.get('associations', []),
        #         local_vars.get('compositions', []), local_vars.get('aggregations', []),
        #         local_vars.get('inheritance', []))

    def generate_description(self):
        processed_sentences = []

        # From Attributes
        for index, row in self.generator_from_attributes.get_attributes().iterrows():
            # sentence = self.post_processor.morphological_process(sentence)
            sentence = row['sentence'].replace("+sg", '')
            sentence = sentence.replace("+pl", '')
            self.attributes_description.loc[len(self.attributes_description)] = [row['class'], row['attribute'],
                                                                                 sentence]
            processed_sentences.append(sentence)

        # From Associations
        for index, row in self.generator_from_associations.get_relationships().iterrows():
            # Since we are handling singular/plural thing while generating the sentences, this is not required here.
            # sentence = self.post_processor.morphological_process(row['sentence'])
            sentence = row['sentence'].replace("+sg", '')
            sentence = sentence.replace("+pl", '')
            self.relationships.loc[len(self.relationships)] = [row['source'], row['target'], row['role'],
                                                               sentence]
            processed_sentences.append(sentence)

        # From Compositions
        for index, row in self.generator_from_compositions.get_sentences().iterrows():
            sentence = self.post_processor.morphological_process(row['sentence'])
            sentence = sentence.replace("+sg", '')
            sentence = sentence.replace("+pl", '')
            processed_sentences.append(sentence)

        # From Aggregations
        for index, row in self.generator_from_aggregations.get_sentences().iterrows():
            sentence = self.post_processor.morphological_process(row['sentence'])
            sentence = sentence.replace("+sg", '')
            sentence = sentence.replace("+pl", '')
            processed_sentences.append(sentence)

        for index, row in self.generator_from_inheritance.get_sentences().iterrows():
            sentence = self.post_processor.morphological_process(row['sentence'])
            sentence = sentence.replace("+sg", '')
            sentence = sentence.replace("+pl", '')
            processed_sentences.append(sentence)

        sentences = processed_sentences

        final_sentence = ''.join([s + '. ' for s in sentences])
        self.description = final_sentence
        print(final_sentence)

# dec = DescriptionGenerator('Insurance')
# print(dec.get_attributes())
# print(dec.get_relationships())
