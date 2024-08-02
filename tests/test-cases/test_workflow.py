
import pandas as pd

from workflow.workflowStart import WorkflowStart


def determine_answer(row):
    if row['equality'] == True or row['equality'] == 'True':
        return 'equality'
    elif row['contradiction'] == True or row['contradiction'] == 'True':
        return 'contradiction'
    elif row['inclusion'] == True or row['inclusion'] == 'True':
        return 'inclusion'
    else:
        return 'exact difference'


results = pd.DataFrame(columns=["domain name",
                                "equality check accuracy attributes",
                                "unclear instances for equality attributes",

                                "equality check accuracy associations",
                                "unclear instances for equality associations",

                                "equality check accuracy inheritance",
                                "unclear instances for equality inheritance",

                                "equality check accuracy compositions",
                                "unclear instances for equality compositions",

                                "contradiction check accuracy attributes",
                                "unclear instances for contradiction attributes",

                                "contradiction check accuracy associations",
                                "unclear instances for contradiction associations",

                                "contradiction check accuracy inheritance",
                                "unclear instances for contradiction inheritance",

                                "contradiction check accuracy compositions",
                                "unclear instances for contradiction compositions",

                                "inclusion check accuracy attributes",
                                "unclear instances for inclusion attributes",

                                "inclusion check accuracy associations",
                                "unclear instances for inclusion associations",

                                "inclusion check accuracy inheritance",
                                "unclear instances for inclusion inheritance",

                                "inclusion check accuracy compositions",
                                "unclear instances for inclusion compositions",

                                "final accuracy attributes",
                                "final accuracy associations",
                                "final accuracy inheritance",
                                "final accuracy compositions",
                                ])


def test_workflow():
    domains = ['bank', 'car-maintenance', 'factory', 'production-cell-inheritance',
               'smart-city', 'sustainable-transportation']

    domains = ['Insurance']

    parent_folder = "../workflow-results"
    checks = ['equality', 'contradiction', 'inclusion']

    parts_of_domain = ['Attributes', 'Associations', 'Inheritance', 'Compositions']

    for domain_name in domains:
        predicted_individual_maps = []
        actual_individual_maps = []
        for part in parts_of_domain:
            true_result = pd.DataFrame()
            predicted_map = pd.DataFrame()
            try:
                true_result = pd.read_csv(f"../ground-truth/{domain_name}/{part} map.csv")
                true_result['Final answer'] = true_result.apply(determine_answer, axis=1)
                actual_individual_maps.append(true_result)

                predicted_map = pd.read_excel(f"{parent_folder}//{domain_name}//predicted {part} map.xlsx")
                predicted_map['Final answer'] = predicted_map.apply(determine_answer, axis=1)
                predicted_individual_maps.append(predicted_map)
            except:
                print("Domain ", domain_name)
                print("Part of domain ", part)
                actual_individual_maps.append(true_result)
                predicted_individual_maps.append(predicted_map)

        print("GPT results -----")
        # We already have actual and generated description mapped in csv files, so we will only run prompts
        # workflow = WorkflowStart(predicted_individual_maps, domain_name)
        # workflow.run()

        # for i, pred_map in enumerate(predicted_individual_maps):
        #     if len(pred_map) != 0:
        #         pred_map['Final answer'] = pred_map.apply(determine_answer, axis=1)
        #
        #     pred_map.to_excel(f"{parent_folder}//{domain_name}//predicted {parts_of_domain[i]} map.xlsx", index=False)
        #
        res_instance = [domain_name]

        for check in checks:
            for actual_res, pred_res in zip(actual_individual_maps, predicted_individual_maps):
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

        for actual_res, pred_res in zip(actual_individual_maps, predicted_individual_maps):
            if len(pred_res) != 0:
                final_accuracy = sum(true_label == pred_label for true_label, pred_label in
                                     zip(actual_res['Final answer'],
                                         pred_res['Final answer'])) / len(
                    actual_res['Final answer'])

                res_instance.append(final_accuracy)

            else:
                res_instance.append(1)

        results.loc[len(results)] = res_instance

    results.to_excel(f"{parent_folder}/insurance_results.xlsx", index=False)
