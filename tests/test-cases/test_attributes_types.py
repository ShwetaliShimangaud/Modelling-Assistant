import re

import pandas as pd

from domain_converter.xmlReader import parse_domain_model
from extractor.concept_prediction_updated import ConceptsPrediction

# from sentence_generator import util

domain_models_path = '../domain-models/cdm-models'

# nlp = spacy.load("en_core_web_trf")


def get_main_noun_in_attribute(attribute):
    parts = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)(?![a-z0-9])(?![A-Z0-9])', attribute)
    #
    return " ".join([item.lower() for item in parts])

    # if len(parts) == 1:
    #     return attribute
    # else:
    #     attributes = " ".join([item.lower() for item in parts])
    #     result = nlp(attributes)
    #     for doc in result:
    #         if doc.dep_ == 'ROOT':
    #             return doc.text
    #
    #     return parts[-1]


def test_attributes_types():
    domains = ['bank', 'car-maintenance', 'factory', 'flight-reservation', 'hotel-reservation',
               'library', 'production-cell-enum', 'production-cell-inheritance',
               'smart-city', 'sustainable-transportation']

    result = pd.DataFrame(columns=['class', 'attribute', 'type', 'prediction', 'probabilities'])
    predictor = ConceptsPrediction()

    for domain in domains:
        class_attributes = parse_domain_model(f"{domain_models_path}/{domain}.cdm", self.domain_name)[0]

        for class_name, attributes in class_attributes.items():
            for attribute in attributes:
                parts = attribute.split(":")
                attribute_main = get_main_noun_in_attribute(parts[0])
                prediction = predictor.predict_category_with_probability(attribute_main, get_main_noun_in_attribute(class_name))

                result.loc[len(result)] = [class_name, attribute_main, parts[1], max(prediction, key=prediction.get),
                                           prediction]

    correct_count = 0
    for i, row in result.iterrows():
        if row['type'].lower() in row['prediction']:
            correct_count += 1
        elif row['type'] == 'Int' and row['prediction'] == 'float':
            correct_count += 1
        elif (row['type'] == 'Double' and
              (row['prediction'] == 'integer' or row['prediction'] == 'float')):
            correct_count += 1

    accuracy = correct_count / len(result)

    print(accuracy)
    result.to_csv(f"{domain_models_path}/results_with_context_bert_synthetic_data.csv", index=False)


test_attributes_types()
