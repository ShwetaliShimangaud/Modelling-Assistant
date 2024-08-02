import os

import pandas as pd

from workflow import apiCaller


def determine_answer(row):
    if row['equality'] is True:
        return 'equality'
    elif row['contradiction'] is True:
        return 'contradiction'
    elif row['inclusion'] is True:
        return 'inclusion'
    else:
        return 'exact difference'


# results = pd.DataFrame(columns=["domain name",
#                                 "equality check accuracy",
#                                 "unclear instances for equality",
#
#                                 "contradiction check accuracy",
#                                 "unclear instances for contradiction",
#
#                                 "inclusion check accuracy",
#                                 "unclear instances for inclusion",
#
#                                 "final accuracy relationships",
#                                 ])

parent_folder = "../attribute_type_results"

prompts = [
    "Is Statement 2 possible given the context provided in Statement 1?",
    "Can Statement 2 be true based on the information in Statement 1?",
    "Is Statement 2 feasible given the details provided in Statement 1?",
    "Given Statement 1, could Statement 2 be valid?"
]

columns = ['actual_description', 'generated_description']
columns.extend(prompts)
check_results = pd.DataFrame(columns=columns)


def test_accuracy():
    domains = ['bank', 'car-maintenance', 'factory', 'insurance', 'library', 'smart-city',
               'sustainable-transportation']

    domains = ['smart-city']

    for domain in domains:
        ground_truth = pd.read_csv(f"../ground-truth_with_attribute_types/{domain}/Attributes map.csv")

        pred_map = ground_truth.copy()

        for i, row in pred_map.iterrows():
            actual_description = row['actual_description']
            generated_description = row['generated_description']
            yes_count = 0
            no_count = 0
            unclear_count = 0
            results = []

            for prompt in prompts:
                res = apiCaller.call_api(actual_description, generated_description, prompt)
                results.append(res)

                if res.startswith("Yes") or res.startswith("yes"):
                    yes_count = yes_count + 1
                elif res.startswith("No") or res.startswith("no"):
                    no_count = no_count + 1
                else:
                    unclear_count = unclear_count + 1

            if yes_count > no_count and yes_count > unclear_count:
                final_answer = True

            elif no_count > yes_count and no_count > unclear_count:
                final_answer = False

            else:
                final_answer = 'not clear'

            pred_map.at[i, 'check'] = final_answer
            result = [actual_description, generated_description]
            result.extend(results)
            check_results.loc[len(check_results)] = result

        if not os.path.exists(rf"{parent_folder}"):
            os.makedirs(f"{parent_folder}")

        if not os.path.exists(rf"{parent_folder}//{domain}"):
            os.makedirs(f"{parent_folder}//{domain}")

        pred_map.to_csv(f"{parent_folder}//{domain}//predicted attributes map.csv")
        check_results.to_csv(f"{parent_folder}//{domain}//check_results.csv")
