import nltk
from nltk.corpus import wordnet
import re
import constants


class PostProcessor:
    def __init__(self):
        pass

    def conjugate_verb(self, base_verb):
        if base_verb.endswith(('o', 's', 'x', 'z', 'ch', 'sh')):
            return base_verb + 'es'
        elif base_verb.endswith('y') and base_verb[-2] not in 'aeiou':
            return base_verb[:-1] + 'ies'
        elif base_verb.endswith('y'):
            return base_verb + 's'
        else:
            return base_verb + 's'

    def morphological_process(self, text):
        words = re.split(r'[ ]', text)

        for i, word in enumerate(words):
            tag = nltk.pos_tag([word])

            # Cardinality to noun agreement, might not be needed with roles
            if tag[0][1] in constants.noun_tags:
                if words[i - 1]:
                    if '+pl' in words[i - 1]:
                        new_word = wordnet.morphy(word)
                        if new_word:
                            print(new_word)
                        else:
                            new_word = word + 's'
                        words[i] = new_word

            # ToDo Revisit
            # elif tag[0][1] in verb_tags:
            #     # Verb to noun agreement
            #     if tag[0][1] in ['VB', 'VBZ', 'VBP']:
            #         # Present tense
            #         new_word = wordnet.morphy(word)
            #         if new_word:
            #             print(new_word)
            #             words[i] = conjugate_verb(new_word)
            #         else:
            #             print("error")
            #     elif tag[0][1] in ['VBN']:
            #         # Passive form
            #         new_word = wordnet.morphy(word)
            #         print(new_word)

        # print(words)

        return ' '.join(words)

    # Aggregator : Discuss the requirement

    # ToDo Semantic analyser
