from typing import List

import nltk

from abstractSentenceGenerator import AbstractSentenceGenerator
import util


# Associations
# Template : o1 cardinality -> o1 name -> association name -> o2 cardinality -> o2 name
# Template: o1 cardinality -> o1 name/role -> "can have"/"can be associated to" -> o2 cardinality -> o2 name/roles
# association_phrase = "can be associated to"
# association_phrase = "is associated to
class SentenceFromAssociations(AbstractSentenceGenerator):
    def __init__(self, associations):
        self.associations = associations
        # self.association_phrase = "is connected to"
        self.sentences = []
        self.generate_sentences()

    def get_sentences(self) -> List[str]:
        return self.sentences

    # def get_association_phrase(self,cardinality):
    #     if cardinality == '0..*':
    #         return 'may be connected to'
    #     else:
    #         return self.association_phrase

    def get_role_and_cardinality(self, role, cardinality, associated_class):
        words = util.split_camel_case(role)
        pos_tag = util.get_pos_tag(" ".join(words))
        if util.contains_verb([pair[1] for pair in pos_tag]):
            return " ".join(words) + " " + util.get_cardinality(cardinality) + " " + associated_class
        elif associated_class.lower() in role.lower():
            return "has " + util.get_cardinality(cardinality) + " " + role
        else:
            # TODO check if you can use who,which etc instead of which always
            phrase = "has " + util.get_cardinality(cardinality) + " " + role + " which "
            if util.is_singular(cardinality):
                phrase += "is "
            else:
                phrase += "are "
            phrase += associated_class
            return phrase

    def generate_sentences(self):
        # With role name
        for association in self.associations:
            part_of_sentence = ''
            part_of_sentence += "Each " + association['class1'] + " " + self.get_role_and_cardinality(
                association['role_class2'],
                association[
                    'cardinality_class2'], association['class2']) + " "

            part_of_sentence += "while " + "each " + association['class2'] + " " + self.get_role_and_cardinality(
                association['role_class1'], association['cardinality_class1'], association['class1'])

            self.sentences.append(part_of_sentence)

        print(self.sentences)

    # without role name
    # for association in associations:
    #     part_of_sentence = ''
    #     part_of_sentence += "Each " + association['class1'] + " " + get_association_phrase(
    #         association['cardinality_class2']) + " "
    #     part_of_sentence += get_cardinality(association['cardinality_class2']) + " "
    #     part_of_sentence += association['class2'] + " "
    #     part_of_sentence += "while " + "Each " + association['class2'] + " " + 'belongs to' + " "
    #     part_of_sentence += get_cardinality(association['cardinality_class1']) + " "
    #     part_of_sentence += association['class1']
    #     sentences.append(part_of_sentence)

    # def get_role_name(role_information):
    #     words = split_camel_case(role_information)
    #     pos_tag = nltk.pos_tag(words)
    #     if contains_verb([pair[1] for pair in pos_tag]):
    #         return " ".join(words)
    #     else:
    #         return "has "


associations = [
    {
        'class1': 'Machine',
        'class2': 'Piece',
        'cardinality_class1': '1',
        'cardinality_class2': '*',
        'name': '',
        'role_class1': 'isProducedBy',
        'role_class2': 'produces'
    },
    {
        'class1': 'Machine',
        'class2': 'Worker',
        'cardinality_class1': '*',
        'cardinality_class2': '1..*',
        'name': '',
        'role_class1': 'operates',
        'role_class2': 'isOperatedBy'
    },
    {
        'class1': 'Factory',
        'class2': 'Worker',
        'cardinality_class1': '1',
        'cardinality_class2': '1..*',
        'name': '',
        'role_class1': 'workplace',
        'role_class2': 'workers'
    }
]

sp = SentenceFromAssociations(associations)
