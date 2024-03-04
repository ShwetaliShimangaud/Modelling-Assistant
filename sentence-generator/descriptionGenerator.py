from sentenceFromAttributes import SentenceFromAttributes
from sentenceFromAssociations import SentenceFromAssociations
from sentenceFromCompositions import SentenceFromCompositions
from postProcessor import PostProcessor


class DescriptionGenerator:
    def __init__(self, model_path):
        self.model_path = model_path
        attributes, associations, compositions = self.read_model()
        self.generator_from_attributes = SentenceFromAttributes(attributes)
        self.generator_from_associations = SentenceFromAssociations(associations)
        self.generator_from_compositions = SentenceFromCompositions(compositions)
        self.post_processor = PostProcessor()
        self.description = ''

    def get_description(self):
        return self.description

    def read_model(self):
        with open(self.model_path, 'r') as file:
            content = file.read()

        local_vars = {}

        exec(content, local_vars)

        return local_vars.get('class_attributes', {}), local_vars.get('associations', []), local_vars.get(
            'compositions', [])

    def generate_description(self):
        processed_sentences = []

        # From Attributes
        for sentence in self.generator_from_attributes.get_sentences():
            sentence = self.post_processor.morphological_process(sentence)
            sentence = sentence.replace("+sg", '')
            sentence = sentence.replace("+pl", '')
            processed_sentences.append(sentence)

        # From Associations
        for sentence in self.generator_from_associations.get_sentences():
            sentence = self.post_processor.morphological_process(sentence)
            sentence = sentence.replace("+sg", '')
            sentence = sentence.replace("+pl", '')
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


# dec = DescriptionGenerator("D:\\Thesis\\modelling-assistant\\test\\domain-models\\bank.txt")
dec = DescriptionGenerator("/test/domain-models/factory")
dec.generate_description()
print(dec.get_description())
