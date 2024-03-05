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
    if attribute[-1] == 's':
        return ''
    elif attribute[0].lower() in ['a', 'e', 'i', 'o', 'u']:
        return 'an'
    else:
        return 'a'


def get_pos_tag(words):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(words)
    pos_tags = []

    for token in doc:
        pair = (token.text, token.tag_)
        pos_tags.append(pair)

    return pos_tags


# Function to split compound words written in camel case
def split_camel_case(word):
    # Use regular expression to split camelCase
    parts = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', word)
    return parts