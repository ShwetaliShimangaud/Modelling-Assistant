import constants
import re
import spacy


def get_cardinality(cardinality):
    if ".." not in cardinality:
        return constants.singular_cardinality_to_article_map[cardinality]
    else:
        return constants.multiple_cardinality_to_article_map[cardinality]


def is_singular(cardinality):
    return ".." not in cardinality


def contains_verb(tag):
    return any(substring in tag for substring in constants.verb_tags)


def get_appropriate_article(attribute):
    nlp = spacy.load("en_core_web_trf")
    doc = nlp(attribute)
    if 'Plur' in doc[0].morph.get("Number"):
        return ""
    elif attribute[0].lower() in ['a', 'e', 'i', 'o', 'u']:
        return 'an'
    else:
        return 'a'


def get_pos_tag(words):
    nlp = spacy.load("en_core_web_trf")
    doc = nlp(words)
    pos_tags = []

    for token in doc:
        pair = (token.text, token.tag_)
        pos_tags.append(pair)

    return pos_tags


# Function to split compound words written in camel case
def split_camel_case(word):
    # Use regular expression to split camelCase
    parts = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)(?![a-z0-9])(?![A-Z0-9])', word)
    return parts


def format_concept(concept):
    digit_pattern = re.compile(r'\d')
    article = get_appropriate_article(concept)

    if bool(digit_pattern.search(concept)):
        return article + " " + concept

    if bool(re.match(r'^[A-Z]+$', concept)):
        return article + " " + concept

    splitted_concept = split_camel_case(concept)
    return article + " " + " ".join([item.lower() for item in splitted_concept])


def format_role_name(role):
    splitted_concept = split_camel_case(role)
    return " ".join([item.lower() for item in splitted_concept])


def format_class_name(class_name):
    splitted_concept = split_camel_case(class_name)
    return " ".join([item.lower() for item in splitted_concept])
