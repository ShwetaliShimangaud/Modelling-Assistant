from typing import List
import sentence_generator.util as util

from sentence_generator.abstractSentenceGenerator import AbstractSentenceGenerator


class SentenceFromCompositions(AbstractSentenceGenerator):
    def __init__(self, compositions):
        self.compositions = compositions
        self.composition_phrase = 'is made up of'
        self.sentences = []
        self.generate_sentences()

    def get_sentences(self) -> List[str]:
        return self.sentences

    def generate_sentences(self):
        for composition in self.compositions:
            part_of_sentence = ''
            part_of_sentence += "Each " + composition['parent_class'] + " "
            part_of_sentence += self.composition_phrase + " "
            part_of_sentence += util.get_cardinality(composition['cardinality']) + " "
            part_of_sentence += composition['child_class']
            self.sentences.append(part_of_sentence)


