from typing import List

import nltk
from abstractSentenceGenerator import AbstractSentenceGenerator
import util
import spacy


# Associations
# Template : o1 cardinality -> o1 name -> association name -> o2 cardinality -> o2 name
# Template: o1 cardinality -> o1 name/role -> "can have"/"can be associated to" -> o2 cardinality -> o2 name/roles
# association_phrase = "can be associated to"
# association_phrase = "is associated to

# Rules for "need of auxillary verb":
# 1. Auxillary verb + main verb :  isOperatedBy : no changes needed
# 2. Verb as adjective.modifier : bikesParked
# 3. Main verb with morph analysis Present/past/future tense : parkedIn : Decide on is/are/was/were
# TODO : Check if multiple tense conditions needs to be checked or will 'has' work in every case
# 4. Main verb infinitive form : drop : Go with 'has'


def get_main_and_auxillary_verb(result):
    main_verb = None
    auxillary_verb = None
    for token in result:
        if token.pos_ == 'VERB' and util.contains_verb(token.tag_):
            main_verb = token
        elif token.pos_ == 'AUX':
            auxillary_verb = token

    return main_verb, auxillary_verb


def ends_with_preposition(result):
    last_token = result[len(result) - 1]
    return last_token.pos_ == "ADP"


class SentenceFromAssociations(AbstractSentenceGenerator):
    def __init__(self, associations):
        self.associations = associations
        # self.association_phrase = "is connected to"
        self.nlp = spacy.load("en_core_web_trf")
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
        verb_forms_with_auxillary_verb = ['Inf', 'Part']
        words = util.split_camel_case(role)
        pos_tag = nltk.pos_tag(words)
        result = self.nlp(" ".join(words))

        auxillary_verb_needed = True
        main_verb, auxillary_verb = get_main_and_auxillary_verb(result)

        # TODO First condition is redundant when second condition is there, can be removed at the end
        if main_verb is not None and auxillary_verb is not None:
            auxillary_verb_needed = False
        elif auxillary_verb is not None:
            auxillary_verb_needed = False
        elif main_verb is not None:
            if main_verb.has_morph():
                verb_form = main_verb.morph.get('VerbForm', [])
                if any(elem in verb_forms_with_auxillary_verb for elem in verb_form):
                    auxillary_verb_needed = True
                else:
                    auxillary_verb_needed = False
            else:
                auxillary_verb_needed = True
        else:
            auxillary_verb_needed = True

        # Case 1: Main verb + auxiliary verb
        if not auxillary_verb_needed:
            return util.format_role_name(role) + " " + util.get_cardinality(cardinality) + " " + util.format_class_name(
                associated_class)

        # Case 2: auxillary verb needed, but role contains class name
        elif associated_class.lower() in role.lower():
            return "has " + util.get_cardinality(cardinality) + " " + util.format_role_name(role)

        # Case 3: auxillary verb needed along with role and class name, but role name ends with preposition
        elif ends_with_preposition(result):
            return "is " + util.format_role_name(role) + " " + util.get_cardinality(
                cardinality) + " " + util.format_class_name(associated_class)
        else:
            # TODO check if you can use who,which etc instead of which always
            phrase = "has " + util.get_cardinality(cardinality) + " " + util.format_role_name(role) + " which "
            if util.is_singular(cardinality):
                phrase += "is "
            else:
                phrase += "are "
            phrase += util.format_class_name(associated_class)
            return phrase

    def generate_sentences(self):
        # With role name
        for association in self.associations:
            part_of_sentence = ''
            part_of_sentence += "Each " + util.format_class_name(
                association['class1']) + " " + self.get_role_and_cardinality(
                association['role_class2'],
                association[
                    'cardinality_class2'], association['class2']) + " "

            part_of_sentence += "while " + "each " + util.format_class_name(
                association['class2']) + " " + self.get_role_and_cardinality(
                association['role_class1'], association['cardinality_class1'], association['class1'])

            self.sentences.append(part_of_sentence)

        print(self.sentences)


associations = [
    {
        'class1': 'BookCopy',
        'class2': 'Loan',
        'cardinality_class1': '1',
        'cardinality_class2': '0..1',
        'name': '',
        'role_class1': 'borrowedBook',
        'role_class2': 'loan'
    },
    {
        'class1': 'Loan',
        'class2': 'Member',
        'cardinality_class1': '0..*',
        'cardinality_class2': '1',
        'name': '',
        'role_class1': 'loans',
        'role_class2': 'currentHolder'
    },
    {
        'class1': 'Member',
        'class2': 'Book',
        'cardinality_class1': '0..*',
        'cardinality_class2': '0..*',
        'name': '',
        'role_class1': 'requesters',
        'role_class2': 'booksOnHold'
    },
    {
        'class1': 'MemberCategory',
        'class2': 'LoanPeriod',
        'cardinality_class1': '1',
        'cardinality_class2': '0..*',
        'name': '',
        'role_class1': 'memberCategory',
        'role_class2': 'loanPeriods'
    },
    {
        'class1': 'LoanPeriod',
        'class2': 'BookCategory',
        'cardinality_class1': '0..*',
        'cardinality_class2': '1',
        'name': '',
        'role_class1': 'loanPeriods',
        'role_class2': 'bookCategory'
    }
]

factory_associations = [
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
        'role_class2': 'employees'
    }
]

transportation_associations = [
    {
        'class1': 'BikeStation',
        'class2': 'Bike',
        'cardinality_class1': '0..1',
        'cardinality_class2': '0..*',
        'name': '',
        'role_class1': 'parkedIn',
        'role_class2': 'bikesParked'
    },
    {
        'class1': 'SustainableCity',
        'class2': 'BikeStation',
        'cardinality_class1': '1',
        'cardinality_class2': '1..*',
        'name': '',
        'role_class1': 'in',
        'role_class2': 'has'
    },
    {
        'class1': 'BikeStation',
        'class2': 'Rental',
        'cardinality_class1': '1',
        'cardinality_class2': '*',
        'name': '',
        'role_class1': 'dropOffStation',
        'role_class2': 'rentals'
    },
    {
        'class1': 'BikeStation',
        'class2': 'Rental',
        'cardinality_class1': '1',
        'cardinality_class2': '*',
        'name': '',
        'role_class1': 'pickupStation',
        'role_class2': 'rentals'
    },
    {
        'class1': 'Bike',
        'class2': 'Rental',
        'cardinality_class1': '1',
        'cardinality_class2': '0..*',
        'name': '',
        'role_class1': 'rents',
        'role_class2': 'rentals'
    },
    {
        'class1': 'User',
        'class2': 'Rental',
        'cardinality_class1': '1',
        'cardinality_class2': '0..*',
        'name': '',
        'role_class1': 'user',
        'role_class2': 'rentals'
    }
]

sfa = SentenceFromAssociations(transportation_associations)
print(sfa.get_sentences())
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
