from typing import List

from pandas import DataFrame

import sentence_generator.util as util
import pandas as pd
from sentence_generator.abstractSentenceGenerator import AbstractSentenceGenerator


class SentenceFromCompositions(AbstractSentenceGenerator):
    def __init__(self, compositions):
        self.compositions = compositions
        self.composition_phrase = 'is made up of'

        # TODO : Keep only one format either sentences list or 'relationships'  dataframe
        self.sentences = []
        self.compositions_result = pd.DataFrame(columns=['parent_class', 'child_class', 'role', 'sentence'])

        self.generate_sentences()

    def get_sentences(self) -> DataFrame:
        return self.compositions_result

    def generate_sentences(self):
        # TODO handle the case where role name is provided and it is not same as class name
        for composition in self.compositions:
            parent_class_name = util.format_class_name(composition['parent_class'])
            child_class_name = util.format_class_name(composition['child_class'])
            role = util.format_role_name(composition['role'])

            part_of_sentence = ''
            part_of_sentence += "Each " + parent_class_name + " "
            part_of_sentence += self.composition_phrase + " "
            part_of_sentence += util.get_cardinality(composition['cardinality']) + " "
            part_of_sentence += child_class_name
            self.sentences.append(part_of_sentence)
            self.compositions_result.loc[len(self.compositions_result)] = [parent_class_name, child_class_name, role,
                                                                           part_of_sentence]


compositions = [
    {
        'parent_class': 'Car',
        'child_class': 'Service',
        'cardinality': '*',
        'role': 'services'
    }
]

sfc = SentenceFromCompositions(compositions)
sfc.get_sentences()
