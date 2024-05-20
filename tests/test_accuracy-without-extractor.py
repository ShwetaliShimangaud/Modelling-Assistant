import pandas as pd
from workflow.workflowStart import WorkflowStart


def determine_answer(row):
    if row['equal']:
        return 'equality'
    elif row['contradiction']:
        return 'contradiction'
    elif row['inclusion']:
        return 'inclusion'
    else:
        return 'exact difference'


# results = pd.read_csv("llama7b-results/results_after_modifications.csv")


results = pd.DataFrame(columns=["domain name",
                                "equality check accuracy attributes",
                                "unclear instances of attributes for equality",
                                "contradiction check accuracy attributes",
                                "unclear instances of attributes for contradiction",
                                "inclusion check accuracy attributes",
                                "unclear instances of attributes for inclusion",

                                "equality check accuracy relationships",
                                "unclear instances of relationships for equality",
                                "contradiction check accuracy relationships",
                                "unclear instances of relationships for contradiction",
                                "inclusion check accuracy relationships",
                                "unclear instances of relationships for inclusion",

                                "final accuracy attributes",
                                "final accuracy relationships",

                                ])


def test_accuracy():
    domains = ['bank', 'factory', 'smart-city', 'sustainable-transportation']
    model = "gpt4"
    parent_folder = "./without-sentence-generator-results/gpt4"

    for domain_name in domains:
        attributes_true_result = pd.read_csv(f"{domain_name}//Attributes map.csv")
        relationship_true_result = pd.read_csv(f"{domain_name}//Relationships map.csv")

        attributes_true_result['Final answer'] = attributes_true_result.apply(determine_answer, axis=1)
        relationship_true_result['Final answer'] = relationship_true_result.apply(determine_answer, axis=1)

        predicted_attributes_map = pd.read_csv(
            f"{parent_folder}/{domain_name}-logs-{model}//predicted_attributes_map.csv")
        predicted_relationships_map = pd.read_csv(
            f"{parent_folder}/{domain_name}-logs-{model}//predicted_relationships_map_after_modifications.csv")

        print("GPT results -----")
        # We already have actual and generated description mapped in csv files, so we will only run prompts
        # workflow = WorkflowStart(predicted_attributes_map, predicted_relationships_map)
        # workflow.run()

        predicted_attributes_map['Final answer'] = predicted_attributes_map.apply(determine_answer, axis=1)
        predicted_relationships_map['Final answer'] = predicted_relationships_map.apply(determine_answer, axis=1)

        checks = ['equal', 'contradiction', 'inclusion']

        res_instance = [domain_name]

        for check in checks:
            count = 0
            for true_label, pred_label in zip(attributes_true_result[check],
                                              predicted_attributes_map[check]):
                if true_label == pred_label or (true_label and pred_label == 'True') or (
                        true_label == False and pred_label == 'False'):
                    count = count + 1

            check_accuracy_attributes = count / len(attributes_true_result[check])
            unclear_attributes = sum(label == 'not clear' for label in predicted_attributes_map[check])

            res_instance.append(check_accuracy_attributes)
            res_instance.append(unclear_attributes)

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

        final_accuracy_attributes = sum(true_label == pred_label for true_label, pred_label in
                                        zip(attributes_true_result['Final answer'],
                                            predicted_attributes_map['Final answer'])) / len(
            attributes_true_result['Final answer'])
        final_accuracy_relationships = sum(true_label == pred_label for true_label, pred_label in
                                           zip(relationship_true_result['Final answer'],
                                               predicted_relationships_map['Final answer'])) / len(
            relationship_true_result['Final answer'])

        print("Final accuracy for attributes", final_accuracy_attributes)
        print("Final accuracy for relationships", final_accuracy_relationships)

        res_instance.append(final_accuracy_attributes)
        res_instance.append(final_accuracy_relationships)

        results.loc[len(results)] = res_instance

    results.to_csv(f"{parent_folder}/new_results.csv", index=False)
