import ast

import pandas as pd
import spacy

from preprocessor.coreferenceResolution import get_preprocessed_text
from extractor.RelationshipExtractor import RelationshipsExtractor
from extractor.conceptsExtractor import ConceptsExtractor
from preprocessor import util
from src.descriptionReader import DescriptionReader


def top_n_accuracy(true_labels, pred_labels, n=1):
    if any(label in pred_labels[:n] for label in true_labels):
        return 1
    return 0


language_model = spacy.load("en_core_web_trf")


def get_noun(phrase):
    res = language_model(phrase)
    for token in res:
        if token.head == token:
            return token.text


def find_indices(sentences, df, source, target):
    # Filter the DataFrame based on source and target
    filtered_df = df[(df['source'] == source) & (df['target'] == target)]

    # Extract the 'generated_description' values
    descriptions = filtered_df['generated_description'].tolist()

    # Find indices of descriptions in the sentences list
    indices = {desc: sentences.index(desc) for desc in descriptions if desc in sentences}

    return indices


def test_relationship_extractor():
    domains = ['bank', 'car-maintenance', 'factory', 'production-cell-inheritance',
               'smart-city', 'sustainable-transportation', 'insurance']

    parent_folder = "../extractor-results/relationships_results_with_noun_chunks"

    # Tokenizer treats 'id' as I'd and that's why it gets split as 'I' and 'd'.
    # but here I want it to be a single word, hence removing that rule.
    language_model.tokenizer.rules = {key: value for key, value in language_model.tokenizer.rules.items() if
                                      key != "id"}

    for domain in domains:
        description_reader = DescriptionReader(domain)
        concepts_extractor = ConceptsExtractor()
        relationships_extractor = RelationshipsExtractor()
        actual_description = description_reader.get_actual_description()

        actual_description = get_preprocessed_text(actual_description)

        sentences = [sent.strip() for sent in actual_description.split(".")]

        for sdx, sent in enumerate(sentences):
            sdx = "S" + str(sdx)
            preprocessed_sent = sent.replace(".", "")
            concepts_extractor.extract_candidate_concepts(
                language_model(preprocessed_sent), sdx
            )

            relationships_extractor.extract_candidate_relationships(
                concepts_extractor.df_chunks,
                concepts_extractor.df_concepts,
                language_model,
                language_model(preprocessed_sent),
                sdx,
            )

        data = pd.DataFrame(columns=['source', 'target', 'role', 'actual sentences',
                                     'extracted sentences', 'top1 accuracy', 'top3 accuracy'])

        true_result = pd.read_excel(f"../extractor-ground-truth/relationships/{domain}.xlsx")
        true_result['actual sentences'] = true_result['actual sentences'].apply(ast.literal_eval)

        # for index, row in true_result.iterrows():
        #     role = row['role']
        #     source = row['source']
        #     target = row['target']
        #
        #     extracted_sentence_ids = find_indices(sentences, results, source, target)
        #     extracted_sentence_ids = ["S" + str(i) for i in extracted_sentence_ids]
        #
        #     top1_accuracy = top_n_accuracy(row['actual sentences'], list(extracted_sentence_ids), 1)
        #     top3_accuracy = top_n_accuracy(row['actual sentences'], list(extracted_sentence_ids), 3)
        #     data.loc[len(data)] = [source, target, role, row['actual sentences'],
        #                            list(extracted_sentence_ids),
        #                            top1_accuracy, top3_accuracy]

        for index, row in true_result.iterrows():
            source = row['source'].lower()
            target = row['target'].lower()

            extracted_sentence_ids = util.find_matching_description(source, target,
                                                                    row['source_role'], row['target_role'],
                                                                    relationships_extractor.df_class_associations,
                                                                    concepts_extractor.df_concepts,
                                                                    sentences,
                                                                    language_model)

            top1_accuracy = top_n_accuracy(row['actual sentences'], list(extracted_sentence_ids), 1)
            top3_accuracy = top_n_accuracy(row['actual sentences'], list(extracted_sentence_ids), 3)
            data.loc[len(data)] = [row['source'], row['target'], row['target_role'], row['actual sentences'],
                                   list(extracted_sentence_ids),
                                   top1_accuracy, top3_accuracy]

        data.to_excel(f"{parent_folder}/{domain}-resultt.xlsx", index=False)


test_relationship_extractor()
