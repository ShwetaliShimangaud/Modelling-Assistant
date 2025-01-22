from functools import reduce

import pandas as pd
import spacy

import coreferenceResolution as coref
from domain_converter.xmlReader import parse_domain_model
from extractor.RelationshipExtractor import RelationshipsExtractor
from extractor.conceptsExtractor import ConceptsExtractor
from sentence_generator.SentenceFromEnums import SentenceFromEnums
from src.descriptionReader import DescriptionReader
from workflow.workflowStart import WorkflowStart

model_path = "D:\\Thesis\\modelling-assistant\\tests\\\domain-models\\cdm-models\\"


def read_model(domain_name):
    # Code to read domain diagram in .cdm format
    class_attributes, associations, compositions, aggregations, inheritance, enums = parse_domain_model(
        model_path + domain_name + ".cdm")

    # with open(model_path + domain_name, 'r') as file:
    # content = file.read()
    #
    # local_vars = {}
    #
    # exec(content, local_vars)
    #
    # return (local_vars.get('class_attributes', {}), local_vars.get('associations', []),
    #         local_vars.get('compositions', []), local_vars.get('aggregations', []),
    #         local_vars.get('inheritance', []))

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

    preprocessed_description = coref.get_preprocessed_text(actual_description)
    sentences = [sent.strip() for sent in preprocessed_description.split(".")]

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

    return concepts_extractor.df_concepts, relationships_extractor.df_class_associations, description


def create_enum_map(enum_df, concepts, relationships, actual_description):
    data = pd.DataFrame(columns=['enum', 'enum_member', 'generated_description', 'actual_description'])
    all_sentence_ids = set()

    actual_description = actual_description.replace("e.g.", "")
    actual_description = actual_description.replace(" i.e.", "")
    actual_description = actual_description.replace("etc.", "")
    actual_description = actual_description.split(".")
    for sdx in range(len(actual_description)):
        all_sentence_ids.add("S" + str(sdx))

    for index, row in enum_df.iterrows():
        enum = row['enum'].lower()
        enum_member = row['enum_member'].lower()
        generated_sentence = row['sentence']
        actual_sentence_ids = set()

        enum_member_separated = enum_member.split(" ")
        enum_separated = enum.split(" ")

        enum_presence_map = {}
        enum_member_presence_map = {}

        for i, token in concepts.iterrows():
            token_str = token['token'].lower_
            lemma_str = token['lemmatized_text'].lower()

            # if token_str in attribute_name or lemma_str in attribute_name.lower():
            #     attribute_presence_set.add(token['s_id'])

            for att in enum_member_separated:

                if token_str in att.lower() or lemma_str in att.lower():
                    if att not in enum_member_presence_map:
                        enum_member_presence_map[att] = []
                    enum_member_presence_map[att].append(token['s_id'])

            for att in enum_separated:
                if token_str in att.lower() or lemma_str in att.lower():
                    if att not in enum_presence_map:
                        enum_presence_map[att] = []
                    enum_presence_map[att].append(token['s_id'])

        lists = enum_member_presence_map.values()
        if not lists or all(len(lst) == 0 for lst in lists):
            enum_member_presence_set = set([])
        else:
            enum_member_presence_set = set(list(reduce(set.intersection, map(set, lists))))
            if not enum_member_presence_set:
                enum_member_presence_set = set(list(set().union(*lists)))

        lists = enum_presence_map.values()
        if not lists or all(len(lst) == 0 for lst in lists):
            enum_presence_set = set([])
        else:
            enum_presence_set = set(list(reduce(set.intersection, map(set, lists))))
            if not enum_presence_set:
                enum_presence_set = set(list(set().union(*lists)))

        answer_set = enum_member_presence_set & enum_presence_set
        if len(answer_set) == 0:
            if len(enum_member_presence_set) != 0:
                answer_set = enum_member_presence_set
            elif len(enum_presence_set) != 0:
                answer_set = enum_presence_set
            else:
                answer_set = all_sentence_ids

        actual_sentence_ids.update(answer_set)
        actual_sentences = [actual_description[int(idx.replace("S", ""))] for idx in actual_sentence_ids]
        for sentence in actual_sentences:
            data.loc[len(data)] = [enum, enum_member, generated_sentence, sentence]

        if len(actual_sentences) == 0:
            data.loc[len(data)] = [enum, enum_member, generated_sentence, ""]

    # print("Time for create attribute map ", (end-start)/60)
    return data


def test_enum():
    domains = ['production-cell-enum', 'flight-reservation', 'hotel-reservation']

    # domains = ['car-maintenance']
    for domain in domains:
        concepts, relationships, description = extract_concepts_and_relationships(domain)
        enums = read_model(domain)
        sfe = SentenceFromEnums(enums)
        enum_df = sfe.get_enums()

        enum_map = create_enum_map(enum_df, concepts, relationships, description)

        workflow = WorkflowStart(
            [enum_map], domain)
        errors = workflow.run()
        print(errors)


test_enum()
