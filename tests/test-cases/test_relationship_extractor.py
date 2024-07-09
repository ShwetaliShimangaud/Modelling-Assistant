import ast

import pandas as pd
import spacy

from extractor.RelationshipExtractor import RelationshipsExtractor
from extractor.conceptsExtractor import ConceptsExtractor
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


def test_relationship_extractor():
    domains = ['bank', 'car-maintenance', 'factory', 'production-cell-inheritance',
               'smart-city', 'sustainable-transportation']

    domains = ['sustainable-transportation']

    parent_folder = "../extractor-results/relationships"

    # Tokenizer treats 'id' as I'd and that's why it gets split as 'I' and 'd'.
    # but here I want it to be a single word, hence removing that rule.
    language_model.tokenizer.rules = {key: value for key, value in language_model.tokenizer.rules.items() if
                                      key != "id"}

    for domain in domains:
        description_reader = DescriptionReader(domain)
        concepts_extractor = ConceptsExtractor()
        relationships_extractor = RelationshipsExtractor()
        actual_description = description_reader.get_actual_description()
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

        for index, row in true_result.iterrows():
            source = row['source']
            target = row['target']
            source_head = get_noun(row['source'])
            target_head = get_noun(row['target'])
            role = row['role']
            extracted_sentence_ids = set()

            for i, relationship in relationships_extractor.df_class_associations.iterrows():
                # TODO add check for role
                if (relationship['source'].lower() == source.lower() and relationship[
                    'target'].lower() == target.lower()) or (
                        relationship['source'].lower() == target.lower() and relationship[
                        'target'].lower() == source.lower()):
                    # sdx = relationship['sdx'].replace("S", '')
                    extracted_sentence_ids.add(relationship['sdx'])

                elif (relationship['source'].lower() == source_head.lower() and relationship[
                    'target'].lower() == target_head.lower()) or (
                        relationship['source'].lower() == target_head.lower() and relationship[
                        'target'].lower() == source_head.lower()):
                    # sdx = relationship['sdx'].replace("S", '')
                    extracted_sentence_ids.add(relationship['sdx'])

            if True:  # len(extracted_sentence_ids) == 0:
                source_presence_set = set()
                target_presence_set = set()
                for i, token in concepts_extractor.df_concepts.iterrows():
                    if (token['token'].lower_ == source.lower() or
                            token['lemmatized_text'].lower() == source.lower() or
                            token['token'].lower_ == source_head.lower() or
                            token['lemmatized_text'].lower() == source_head.lower()):
                        source_presence_set.add(token['s_id'])

                    if (token['token'].lower_ == target.lower() or
                          token['lemmatized_text'].lower() == target.lower() or
                          token['token'].lower_ == target_head.lower() or
                          token['lemmatized_text'].lower() == target_head.lower()):
                        target_presence_set.add(token['s_id'])

                answer_set = source_presence_set & target_presence_set
                extracted_sentence_ids.update(answer_set)

            top1_accuracy = top_n_accuracy(row['actual sentences'], list(extracted_sentence_ids), 1)
            top3_accuracy = top_n_accuracy(row['actual sentences'], list(extracted_sentence_ids), 3)
            data.loc[len(data)] = [row['source'], row['target'], role, row['actual sentences'],
                                   list(extracted_sentence_ids),
                                   top1_accuracy, top3_accuracy]

        data.to_excel(f"{parent_folder}/{domain}-result.xlsx", index=False)
