import os
from functools import reduce

import pandas as pd
import spacy

from preprocessor import coreferenceResolution as coref, util
from domain_converter.xmlReader import parse_domain_model
from extractor.RelationshipExtractor import RelationshipsExtractor
from extractor.conceptsExtractor import ConceptsExtractor
from preprocessor.attribute_matcher import AttributeMatcher
from sentence_generator.SentenceFromEnums import SentenceFromEnums
from src.descriptionReader import DescriptionReader
from workflow.workflowStart import WorkflowStart

model_path = "D:\\Thesis\\modelling-assistant\\tests\\\domain-models\\processed_models\\"


def read_model(domain_name):
    file_path = model_path + domain_name
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            content = file.read()

        local_vars = {}

        exec(content, local_vars)

        return local_vars.get('enums', [])
    else:
        print(f"File {file_path} does not exist. Read cdm model")

        # Code to read domain diagram in .cdm format
        class_attributes, associations, compositions, aggregations, inheritance, enums = parse_domain_model(
            model_path + "cdm-models\\" + domain_name + ".cdm", self.domain_name)

        return enums


def extract_concepts_and_relationships(domain):
    description_reader = DescriptionReader(domain)
    concepts_extractor = ConceptsExtractor()
    relationships_extractor = RelationshipsExtractor()
    language_model = spacy.load("en_core_web_trf")

    description = description_reader.get_actual_description()
    actual_description = description.replace("e.g.", "")
    actual_description = actual_description.replace(" i.e.", "")
    actual_description = actual_description.replace("etc.", "")

    original_sentences, sentences = coref.get_preprocessed_text(actual_description)

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

    return concepts_extractor.df_concepts, relationships_extractor.df_class_associations, original_sentences


def test_enum():
    domains = ['bank-management', 'food-delivery-system', 'online-library-system', 'company']
    attribute_matcher = AttributeMatcher()
    language_model = spacy.load("en_core_web_trf")

    for domain in domains:
        concepts, relationships, description = extract_concepts_and_relationships(domain)
        enums = read_model(domain)
        sfe = SentenceFromEnums(enums, language_model)
        enum_df = sfe.get_enums()

        enum_map = attribute_matcher.create_enum_map(enum_df, concepts, relationships, description)

        workflow = WorkflowStart(
            [enum_map], domain)
        errors = workflow.run()
        print(errors)


test_enum()
