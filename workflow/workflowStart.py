import os

import pandas as pd
from src import util

from workflow.equalityChecker import EqualityChecker
from workflow.contradictionChecker import ContradictionChecker
from workflow.containmentChecker import ContainmentChecker


def get_prompts(file_name):
    dirname = util.get_project_directory()
    file_path = os.path.join(dirname, f'src/resources/prompts/{file_name}')
    with open(file_path, 'r') as file:
        content = file.read()

    local_vars = {}

    exec(content, local_vars)
    return local_vars['prompts']


parent_folder = "../entire-system-test"


class WorkflowStart:
    def __init__(self, individual_maps, domain):
        self.individual_maps = individual_maps
        self.equality_checker = EqualityChecker()
        self.contradiction_checker = ContradictionChecker()
        self.containment_checker = ContainmentChecker()
        # self.difference_finder = DifferenceFinder()
        self.domain = domain
        self.checks = ['equality', 'contradiction', 'inclusion']
        self.check_prompts = {}
        self.checkers = {}
        self.check_results = {}

        for check in self.checks:
            prompts = ['actual_description', 'generated_description']
            prompts.extend(get_prompts(check))

            self.check_prompts[check] = prompts
            self.check_results[check] = pd.DataFrame(columns=prompts)
            self.checkers[check] = self.get_checker(check)

    def get_checker(self, check):
        if check == 'equality':
            return self.equality_checker
        elif check == 'contradiction':
            return self.contradiction_checker
        else:
            return self.containment_checker

    def run(self):
        # Take actual and generated sentence Run all the checkers one by one. if result of any checker is true then
        # accordingly add it in warnings or errors array, Run next checker only if result of previous checker is false

        errors = []
        elements = ['attributes', 'associations', 'aggregations', 'compositions', 'inheritance']

        if not os.path.exists(rf"{parent_folder}"):
            os.makedirs(f"{parent_folder}")

        if not os.path.exists(rf"{parent_folder}//{self.domain}"):
            os.makedirs(f"{parent_folder}//{self.domain}")

        for index in range(len(self.individual_maps)):
            pred_map = self.individual_maps[index]
            for i, row in pred_map.iterrows():
                actual_description = row['actual_description']
                generated_description = row['generated_description']

                for check in self.checks:
                    checker = self.checkers[check]
                    check_res = self.check_results[check]

                    results, res = checker.run(actual_description, generated_description)
                    pred_map.at[i, check] = res
                    result = [actual_description, generated_description]
                    result.extend(results)
                    check_res.loc[len(check_res)] = result

                    if isinstance(res, bool):
                        if res:
                            if check == 'contradiction':
                                errors.append({
                                    'actual_description': actual_description,
                                    'generated_description': generated_description
                                })
                            break

            pred_map.to_csv(f"{parent_folder}/{self.domain}/{elements[index]}_pred_map.csv", index=False)

        for check in self.checks:
            check_res = self.check_results[check]
            check_res.to_excel(f"{parent_folder}/{self.domain}/{check}_check.xlsx", index=False)

        return errors
