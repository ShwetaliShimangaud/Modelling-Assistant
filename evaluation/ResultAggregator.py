import os

import pandas as pd

from evaluation.AttributeResultAggregator import aggregate_attribute_results
from evaluation.RelationshipResultAggregator import aggregate_relationship_results

ground_truth_dir = '../evaluation/ground-truth/'
predictions_dir = '../evaluation/predictions/'


def find_stats(actual, predicted):
    correct_correct = 0
    correct_incorrect = 0
    correct_noMatch = 0
    correct_inconclusive = 0

    incorrect_correct = 0
    incorrect_incorrect = 0
    incorrect_noMatch = 0
    incorrect_inconclusive = 0

    extra_correct = 0
    extra_incorrect = 0
    extra_noMatch = 0
    extra_inconclusive = 0

    for a, p in zip(actual, predicted):
        if a == 'correct':
            if p == 'incorrect':
                correct_incorrect += 1
            elif p == 'no_match':
                correct_noMatch += 1
            elif p == 'inconclusive':
                correct_inconclusive += 1
            elif p == 'correct':
                correct_correct += 1
        elif a == 'incorrect':
            if p == 'incorrect':
                incorrect_incorrect += 1
            elif p == 'no_match':
                incorrect_noMatch += 1
            elif p == 'inconclusive':
                incorrect_inconclusive += 1
            elif p == 'correct':
                incorrect_correct += 1
        elif a == 'extra':
            if p == 'incorrect':
                extra_incorrect += 1
            elif p == 'no_match':
                extra_noMatch += 1
            elif p == 'inconclusive':
                extra_inconclusive += 1
            elif p == 'correct':
                extra_correct += 1

    return {
        'correct_and_correct': correct_correct,
        'correct_and_incorrect': correct_incorrect,
        'correct_and_noMatch': correct_noMatch,
        'correct_and_inconclusive': correct_inconclusive,
        'incorrect_and_correct': incorrect_correct,
        'incorrect_and_incorrect': incorrect_incorrect,
        'incorrect_and_noMatch': incorrect_noMatch,
        'incorrect_and_inconclusive': incorrect_inconclusive,
        'extra_and_correct': extra_correct,
        'extra_and_incorrect': extra_incorrect,
        'extra_and_noMatch': extra_noMatch,
        'extra_and_inconclusive': extra_inconclusive
    }


def find_metrics_values(row):
    total_elements = 0
    for ele in row.values():
        if isinstance(ele, int):
            total_elements += ele

    no_prediction = row['correct_and_noMatch'] + row['correct_and_inconclusive'] + \
                    row['incorrect_and_noMatch'] + row['incorrect_and_inconclusive'] + \
                    row['extra_and_noMatch'] + row['extra_and_inconclusive']

    have_prediction = total_elements - no_prediction

    if have_prediction == 0:
        predicted_right = 0
        predicted_wrong = 0
    else:
        predicted_right = (row['correct_and_correct'] + row['incorrect_and_incorrect']) / have_prediction
        predicted_wrong = (row['correct_and_incorrect'] + row['incorrect_and_correct']) / have_prediction

    correct = (row['correct_and_correct'] + row['correct_and_incorrect'] +
               row['correct_and_noMatch'] + row['correct_and_inconclusive'])

    if correct == 0:
        correct_not_classified = 0
    else:
        correct_not_classified = (row['correct_and_noMatch'] + row['correct_and_inconclusive']) / correct

    incorrect = (row['incorrect_and_correct'] + row['incorrect_and_incorrect'] +
                 row['incorrect_and_noMatch'] + row['incorrect_and_inconclusive'])

    if incorrect == 0:
        incorrect_not_classified = 0
    else:
        incorrect_not_classified = (row['incorrect_and_noMatch'] + row['incorrect_and_inconclusive']) / incorrect

    return {
        'domain': row['domain'],
        'have_prediction': have_prediction / total_elements,
        'no_prediction': no_prediction / total_elements,
        'predicted_right': predicted_right,
        'predicted_wrong': predicted_wrong,
        'correct_not_classified': correct_not_classified,
        'incorrect_not_classified': incorrect_not_classified
    }


def calculate_metrics():
    # aggregate_attribute_results()
    # aggregate_relationship_results()

    detailed_results = pd.DataFrame(
        columns=['domain', 'correct_and_correct', 'correct_and_incorrect', 'correct_and_noMatch',
                 'correct_and_inconclusive', 'incorrect_and_correct',
                 'incorrect_and_incorrect', 'incorrect_and_noMatch',
                 'incorrect_and_inconclusive', 'extra_and_correct',
                 'extra_and_incorrect', 'extra_and_noMatch', 'extra_and_inconclusive'])

    results = pd.DataFrame(columns=['domain', 'have_prediction', 'predicted_right', 'predicted_wrong',
                                    'no_prediction', 'correct_not_classified',
                                    'incorrect_not_classified'])

    for folder_name in os.listdir(ground_truth_dir):
        folder_path = os.path.join(ground_truth_dir, folder_name)
        if os.path.isdir(folder_path):
            ground_truth_attributes = pd.read_csv(f"{folder_path}/attributes_results.csv")
            ground_truth_relationships = pd.read_csv(f"{folder_path}/relationship_results.csv")

            prediction_attributes = pd.read_csv(f"{predictions_dir}/{folder_name}/attributes_results.csv")
            prediction_relationships = pd.read_csv(f"{predictions_dir}/{folder_name}/relationship_results.csv")

            res = find_stats(list(ground_truth_attributes['answer']) + list(ground_truth_relationships['answer']),
                             list(prediction_attributes['answer']) + list(prediction_relationships['answer']))
            res['domain'] = folder_name
            detailed_results = pd.concat([detailed_results, pd.DataFrame([res])])

            final_res = find_metrics_values(res)
            results = pd.concat([results, pd.DataFrame([final_res])])

    detailed_results.to_csv("../evaluation/detailed_results.csv", index=False)
    results.to_csv("../evaluation/results.csv", index=False)


# calculate_metrics()
