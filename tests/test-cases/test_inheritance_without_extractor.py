import os

import pandas as pd
from workflow.workflowStart import WorkflowStart


def determine_answer(row):
    if row['equal'] == True:
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
    domains = ['car-maintenance', 'production-cell-inheritance']
    model = "gpt4"
    parent_folder = f"../25th may inheritance results/{model}"

    for domain_name in domains:
        relationship_true_result = pd.read_csv(f"..//ground-truth//{domain_name}//inheritance map.csv")

        relationship_true_result['Final answer'] = relationship_true_result.apply(determine_answer, axis=1)

        predicted_relationships_map = pd.read_csv(f"..//ground-truth//{domain_name}//inheritance map.csv")

        print("GPT results -----")
        # We already have actual and generated description mapped in csv files, so we will only run prompts
        workflow = WorkflowStart(predicted_relationships_map, predicted_relationships_map, domain_name)
        workflow.run()

        # predicted_attributes_map['Final answer'] = predicted_attributes_map.apply(determine_answer, axis=1)
        predicted_relationships_map['Final answer'] = predicted_relationships_map.apply(determine_answer, axis=1)

        checks = ['equal', 'contradiction', 'inclusion']

        res_instance = [domain_name]

        for check in checks:
            count = 0
            # for true_label, pred_label in zip(attributes_true_result[check],
            #                                   predicted_attributes_map[check]):
            #     if true_label == pred_label or (true_label and pred_label == 'True') or (
            #             true_label == False and pred_label == 'False'):
            #         count = count + 1
            #
            # check_accuracy_attributes = count / len(attributes_true_result[check])
            # unclear_attributes = sum(label == 'not clear' for label in predicted_attributes_map[check])

            # res_instance.append(check_accuracy_attributes)
            # res_instance.append(unclear_attributes)

            count = 0
            for true_label, pred_label in zip(relationship_true_result[check],
                                              predicted_relationships_map[check]):
                if true_label == pred_label or (true_label and pred_label == 'True') or (
                        true_label == False and pred_label == 'False'):
                    count = count + 1

            check_accuracy_relationships = count / len(relationship_true_result[check])
            unclear_relationships = sum(label == 'not clear' for label in predicted_relationships_map[check])

            res_instance.append(check_accuracy_relationships)
            res_instance.append(unclear_relationships)

        # final_accuracy_attributes = sum(true_label == pred_label for true_label, pred_label in
        #                                 zip(attributes_true_result['Final answer'],
        #                                     predicted_attributes_map['Final answer'])) / len(
        #     attributes_true_result['Final answer'])
        final_accuracy_relationships = sum(true_label == pred_label for true_label, pred_label in
                                           zip(relationship_true_result['Final answer'],
                                               predicted_relationships_map['Final answer'])) / len(
            relationship_true_result['Final answer'])

        # print("Final accuracy for attributes", final_accuracy_attributes)
        print("Final accuracy for relationships", final_accuracy_relationships)

        # res_instance.append(final_accuracy_attributes)
        res_instance.append(final_accuracy_relationships)

        results.loc[len(results)] = res_instance

        if not os.path.exists(rf"{parent_folder}//{domain_name}"):
            os.makedirs(rf"{parent_folder}//{domain_name}")

        predicted_relationships_map.to_csv(f"{parent_folder}//{domain_name}//predicted inheritance map with changed "
                                           f"prompts.csv")

    results.to_csv(f"{parent_folder}//results with changed prompts.csv", index=False)

