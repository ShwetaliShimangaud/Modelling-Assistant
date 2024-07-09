import os

import pandas as pd
from workflow.workflowStart import WorkflowStart


def determine_answer(row):
    if row['equality'] == True:
        return 'equality'
    elif row['contradiction'] == True:
        return 'contradiction'
    elif row['inclusion'] == True:
        return 'inclusion'
    else:
        return 'exact difference'


results = pd.DataFrame(columns=["domain name",
                                "equality check accuracy",
                                "unclear instances for equality",

                                "contradiction check accuracy",
                                "unclear instances for contradiction",

                                "inclusion check accuracy",
                                "unclear instances for inclusion",

                                "final accuracy relationships",
                                ])


def test_accuracy():
    domains = ['library']
    model = "gpt4"
    checks = ['equality', 'contradiction', 'inclusion']
    parent_folder = "..//aggregation_results"

    for domain_name in domains:
        aggregations_true_result = pd.read_csv(f"..//ground-truth//{domain_name}//Aggregations map.csv")

        aggregations_true_result['Final answer'] = aggregations_true_result.apply(determine_answer, axis=1)

        predicted_aggregations_map = pd.read_csv(f"..//ground-truth//{domain_name}//Aggregations map.csv")

        predicted_maps = [predicted_aggregations_map]
        actual_individual_maps = [aggregations_true_result]

        print("GPT results -----")
        # We already have actual and generated description mapped in csv files, so we will only run prompts
        workflow = WorkflowStart(predicted_maps, domain_name)
        workflow.run()

        for pred_map in predicted_maps:
            pred_map['Final answer'] = pred_map.apply(determine_answer, axis=1)
            pred_map.to_csv(f"{parent_folder}//{domain_name}//predicted aggregations map.csv")

        res_instance = [domain_name]

        for check in checks:
            for actual_res, pred_res in zip(actual_individual_maps, predicted_maps):
                count = 0
                if len(pred_res) != 0:
                    for true_label, pred_label in zip(actual_res[check],
                                                      pred_res[check]):
                        if true_label == pred_label or (true_label and pred_label == 'True') or (
                                true_label == False and pred_label == 'False'):
                            count = count + 1

                    check_accuracy = count / len(actual_res[check])
                    unclear_count = sum(label == 'not clear' for label in pred_res[check])

                    res_instance.append(check_accuracy)
                    res_instance.append(unclear_count)
                else:
                    res_instance.append(1)
                    res_instance.append(1)

        for actual_res, pred_res in zip(actual_individual_maps, predicted_maps):
            if len(pred_res) != 0:
                final_accuracy = sum(true_label == pred_label for true_label, pred_label in
                                     zip(actual_res['Final answer'],
                                         pred_res['Final answer'])) / len(
                    actual_res['Final answer'])

                res_instance.append(final_accuracy)

            else:
                res_instance.append(1)

        results.loc[len(results)] = res_instance

    results.to_csv(f"{parent_folder}//results.csv", index=False)

