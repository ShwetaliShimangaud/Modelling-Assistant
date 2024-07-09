import ast

import pandas as pd
import spacy

from extractor.conceptsExtractor import ConceptsExtractor
from src.descriptionReader import DescriptionReader


def top_n_accuracy(true_labels, pred_labels, n=1):
    if any(label in pred_labels[:n] for label in true_labels):
        return 1
    return 0


def test_concept_extractor():
    domains = ['bank', 'car-maintenance', 'factory', 'production-cell-inheritance',
               'smart-city', 'sustainable-transportation']

    parent_folder = "../extractor-results/concepts"

    language_model = spacy.load("en_core_web_trf")
    # Tokenizer treats 'id' as I'd and that's why it gets split as 'I' and 'd'.
    # but here I want it to be a single word, hence removing that rule.
    language_model.tokenizer.rules = {key: value for key, value in language_model.tokenizer.rules.items() if key != "id"}

    for domain in domains:
        description_reader = DescriptionReader(domain)
        concepts_extractor = ConceptsExtractor()
        actual_description = description_reader.get_actual_description()
        sentences = [sent.strip() for sent in actual_description.split(".")]
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

            extracted_sentence_ids = set()

            attribute_presence_set = set()
            class_name_presence_set = set()
            for i, token in concepts_extractor.df_concepts.iterrows():
                if token['token'].lower_ in attribute_name.lower() or token[
                    'lemmatized_text'].lower() in attribute_name.lower():
                    attribute_presence_set.add(token['s_id'])

                elif token['token'].lower_ in class_name.lower() or token[
                    'lemmatized_text'].lower() in class_name.lower():
                    class_name_presence_set.add(token['s_id'])

            answer_set = attribute_presence_set & class_name_presence_set
            if len(answer_set) == 0:
                answer_set = attribute_presence_set

            extracted_sentence_ids.update(answer_set)

            top1_accuracy = top_n_accuracy(row['actual sentences'], list(extracted_sentence_ids), 1)
            top3_accuracy = top_n_accuracy(row['actual sentences'], list(extracted_sentence_ids), 3)
            data.loc[len(data)] = [class_name, attribute_name, row['actual sentences'], list(extracted_sentence_ids),
                                   top1_accuracy, top3_accuracy]

        data.to_excel(f"{parent_folder}/{domain}-result.xlsx", index=False)
