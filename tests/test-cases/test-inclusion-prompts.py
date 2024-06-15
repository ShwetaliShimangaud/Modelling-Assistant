import pandas as pd

from workflow import apiCaller

domains = ['bank', 'factory', 'smart-city', 'sustainable-transportation']

parent_folder = "./29th may inclusion prompt results"

prompts = [
    "Can Statement 2 be inferred from Statement 1?",
    "Can Statement 2 be implied from Statement 1?",
    "Can Statement 2 be determined from Statement 1?",
    "Can Statement 2 be derived from Statement 1?",
    "Can Statement 2 logically follow from Statement 1?",
    "Can Statement 2 be concluded based on Statement 1?",
    "Does Statement 1 support Statement 2?"
]

relationship_map = pd.DataFrame(
    columns=['generated_description', 'actual_description', 'actual_answer',
             'predicted_answer'])

generated_descriptions = [
    "an account has a balance"
]

actual_descriptions = [
    "At any time, the owner of a bank account can check its current balance"

]

columns = ['generated_description', 'actual_description']
columns.extend(prompts)
domain_result = pd.DataFrame(columns=columns)

for actual_description, generated_description in zip(actual_descriptions, generated_descriptions):

    yes_count = 0
    no_count = 0
    unclear_count = 0
    result = [generated_description, actual_description]

    for prompt in prompts:
        res = apiCaller.call_api(actual_description, generated_description, prompt)
        result.append(res)

        if res.startswith("Yes") or res.startswith("yes"):
            yes_count = yes_count + 1
        elif res.startswith("No") or res.startswith("no"):
            no_count = no_count + 1
        else:
            unclear_count = unclear_count + 1

    domain_result.loc[len(domain_result)] = result
    if yes_count > no_count and yes_count > unclear_count:
        relationship_map.loc[len(relationship_map)] = [generated_description, actual_description, True, True]
    elif no_count > yes_count and no_count > unclear_count:
        relationship_map.loc[len(relationship_map)] = [generated_description, actual_description, False, False]
    else:
        relationship_map.loc[len(relationship_map)] = [generated_description, actual_description, "not clear", "not "
                                                                                                               "clear"]
relationship_map.to_csv(f"../{parent_folder}/inclusion-prompts-new-results-relationships.csv", index=False)
domain_result.to_csv(f"../{parent_folder}/inclusion-prompts-updated.csv", index=False)

# columns = ['generated_description', 'actual_description']
# columns.extend(prompts)
#
# for domain_name in domains:
#     relationship_true_result = pd.read_csv(f"../ground-truth/{domain_name}/Relationships map.csv")
#
#     domain_result = pd.DataFrame(columns=columns)
#
#     for i, row in relationship_true_result.iterrows():
#         actual_description = row['actual_description']
#         generated_description = row['generated_description']
#
#         yes_count = 0
#         no_count = 0
#         unclear_count = 0
#         result = [actual_description, generated_description]
#
#         for prompt in prompts:
#             res = apiCaller.call_api(actual_description, generated_description, prompt)
#             result.append(res)
#
#             if res.startswith("Yes") or res.startswith("yes"):
#                 yes_count = yes_count + 1
#             elif res.startswith("No") or res.startswith("no"):
#                 no_count = no_count + 1
#             else:
#                 unclear_count = unclear_count + 1
#
#         domain_result.loc[len(domain_result)] = result
#         if yes_count > no_count and yes_count > unclear_count:
#             relationship_map.loc[len(relationship_map)] = [row['source'], row['target'],
#                                                            row['role'], generated_description,
#                                                            actual_description, row['inclusion'], True]
#         elif no_count > yes_count and no_count > unclear_count:
#             relationship_map.loc[len(relationship_map)] = [row['source'], row['target'],
#                                                            row['role'], generated_description,
#                                                            actual_description, row['inclusion'], False]
#         else:
#             relationship_map.loc[len(relationship_map)] = [row['source'], row['target'],
#                                                            row['role'], generated_description,
#                                                            actual_description, row['inclusion'], "not clear"]
#
#     domain_result.to_csv(f"..//{parent_folder}//{domain_name}_inclusion_check.csv")
#
# count = 0
# for true_label, pred_label in zip(relationship_map['actual_answer'], relationship_map['predicted_answer']):
#     if true_label == pred_label or (true_label and pred_label == 'True') or (
#             true_label == False and pred_label == 'False'):
#         count = count + 1
#
# check_accuracy_relationships = count / len(relationship_map['actual_answer'])
# unclear_relationships = sum(label == 'not clear' for label in relationship_map['predicted_answer'])
#
# print(check_accuracy_relationships)
# print(unclear_relationships)
#
# relationship_map.to_csv(f"../{parent_folder}/inclusion-prompts-results-relationships.csv")
