import ast

import pandas as pd
import spacy
from functools import reduce


from coreferenceResolution import get_preprocessed_text
from extractor.conceptsExtractor import ConceptsExtractor
from src.descriptionReader import DescriptionReader


def top_n_accuracy(true_labels, pred_labels, n=1):
    if any(label in pred_labels[:n] for label in true_labels):
        return 1
    return 0


def test_concept_extractor():
    domains = ['bank', 'car-maintenance', 'factory', 'production-cell-inheritance',
               'smart-city', 'sustainable-transportation', 'flight-reservation', 'library',
               'insurance']

    domains = ['hotel-reservation']

    parent_folder = "../extractor-results/concepts/after_separation/"

    language_model = spacy.load("en_core_web_trf")
    # Tokenizer treats 'id' as I'd and that's why it gets split as 'I' and 'd'.
    # but here I want it to be a single word, hence removing that rule.
    language_model.tokenizer.rules = {key: value for key, value in language_model.tokenizer.rules.items() if
                                      key != "id"}

    for domain in domains:
        description_reader = DescriptionReader(domain)
        concepts_extractor = ConceptsExtractor()
        actual_description = description_reader.get_actual_description()

        actual_description = get_preprocessed_text(actual_description)

        all_sentence_ids = set()

        sentences = [sent.strip() for sent in actual_description.split(".")]
        temp = pd.DataFrame(columns=["id", "sent"])
        for sdx in range(len(sentences)):
            all_sentence_ids.add("S" + str(sdx))
            temp.loc[len(temp)] = ["S" + str(sdx), sentences[sdx]]

        for sdx, sent in enumerate(sentences):
            sdx = "S" + str(sdx)
            preprocessed_sent = sent.replace(".", "")
            concepts_extractor.extract_candidate_concepts(
                language_model(preprocessed_sent), sdx
            )

        data = pd.DataFrame(columns=['class ', 'attributes', 'actual sentences',
                                     'extracted sentences', 'top1 accuracy', 'top3 accuracy'])

        true_result = pd.read_excel(f"../extractor-ground-truth/concepts/{domain}.xlsx")
        true_result['actual sentences'] = true_result['actual sentences'].apply(ast.literal_eval)
        for index, row in true_result.iterrows():
            class_name = row['class']
            attribute_name = row['attribute']

            attribute_name_separated = attribute_name.split(" ")

            extracted_sentence_ids = set()
            attribute_presence_set = set()
            class_name_presence_set = set()

            attribute_presence_map = {}
            for i, token in concepts_extractor.df_concepts.iterrows():
                token_str = token['token'].lower_
                lemma_str = token['lemmatized_text'].lower()

                if token_str in attribute_name or lemma_str in attribute_name.lower():
                    attribute_presence_set.add(token['s_id'])

                # for att in attribute_name_separated:
                #     if token_str in att or lemma_str in att.lower():
                #         if att not in attribute_presence_map:
                #             attribute_presence_map[att] = []
                #         attribute_presence_map[att].append(token['s_id'])

                if token_str in class_name.lower() or lemma_str in class_name.lower():
                    class_name_presence_set.add(token['s_id'])

            lists = attribute_presence_map.values()

            # if not lists or all(len(lst) == 0 for lst in lists):
            #     attribute_presence_set = set([])
            # else:
            #     attribute_presence_set = set(list(reduce(set.intersection, map(set, lists))))
            #     if not attribute_presence_set:
            #         attribute_presence_set = set(list(set().union(*lists)))

            answer_set = attribute_presence_set & class_name_presence_set
            if len(answer_set) == 0:
                if len(attribute_presence_set) != 0:
                    answer_set = attribute_presence_set
                elif len(class_name_presence_set) != 0:
                    answer_set = class_name_presence_set
                else:
                    answer_set = all_sentence_ids

            extracted_sentence_ids.update(answer_set)

            top1_accuracy = top_n_accuracy(row['actual sentences'], list(extracted_sentence_ids), 1)
            top3_accuracy = top_n_accuracy(row['actual sentences'], list(extracted_sentence_ids), 3)
            data.loc[len(data)] = [class_name, attribute_name, row['actual sentences'], list(extracted_sentence_ids),
                                   top1_accuracy, top3_accuracy]

        data.to_excel(f"{parent_folder}/{domain}-result.xlsx", index=False)
