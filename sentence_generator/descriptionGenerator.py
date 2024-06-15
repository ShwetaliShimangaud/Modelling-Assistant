import pandas as pd

from sentence_generator.sentenceFromAttributes import SentenceFromAttributes
from sentence_generator.sentenceFromAssociations import SentenceFromAssociations
from sentence_generator.sentenceFromCompositions import SentenceFromCompositions
from sentence_generator.postProcessor import PostProcessor

# model_path = "D:\\Thesis\\modelling-assistant\\tests\\domain-models\\bank"
# model_path = "D:\\Thesis\\modelling-assistant\\tests\\domain-models\\factory"
# model_path = "D:\\Thesis\\modelling-assistant\\tests\\domain-models\\sustainable-transportation"


model_path = "D:\\Thesis\\modelling-assistant\\tests\\\domain-models\\"


# model_path = "D:\\Thesis\\modelling-assistant\\tests\\domain-models\\production-cell"


class DescriptionGenerator:
    def __init__(self, domain_name):
        self.domain_name = domain_name
        attributes, associations, compositions = self.read_model()
        self.generator_from_attributes = SentenceFromAttributes(attributes)
        self.generator_from_associations = SentenceFromAssociations(associations)
        self.generator_from_compositions = SentenceFromCompositions(compositions)
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
        with open(model_path + self.domain_name, 'r') as file:
            content = file.read()

        local_vars = {}

        exec(content, local_vars)

        return local_vars.get('class_attributes', {}), local_vars.get('associations', []), local_vars.get(
            'compositions', [])

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
        for sentence in self.generator_from_compositions.get_sentences():
            sentence = self.post_processor.morphological_process(sentence)
            sentence = sentence.replace("+sg", '')
            sentence = sentence.replace("+pl", '')
            processed_sentences.append(sentence)

        sentences = processed_sentences

        final_sentence = ''.join([s + '. ' for s in sentences])
        self.description = final_sentence
        print(final_sentence)


dec = DescriptionGenerator('production-cell-inheritance')
print(dec.get_attributes())
print(dec.get_relationships())
