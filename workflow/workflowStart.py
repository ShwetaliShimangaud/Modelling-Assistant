import os

import pandas as pd
from src import util

from workflow.equalityChecker import EqualityChecker
from workflow.contradictionChecker import ContradictionChecker
from workflow.containmentChecker import ContainmentChecker


# from workflow.differenceFinder import DifferenceFinder

def get_prompts(file_name):
    dirname = util.get_project_directory()
    file_path = os.path.join(dirname, f'src/resources/prompts/{file_name}')
    with open(file_path, 'r') as file:
        content = file.read()

    local_vars = {}

    exec(content, local_vars)
    return local_vars['prompts']


parent_folder = "..//aggregation_results"


class WorkflowStart:
    def __init__(self, individual_maps, domain):
        self.individual_maps = individual_maps
        self.equality_checker = EqualityChecker()
        self.contradiction_checker = ContradictionChecker()
        self.containment_checker = ContainmentChecker()
        # self.difference_finder = DifferenceFinder()
        self.domain = domain

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

        checks = ['equality', 'contradiction', 'inclusion']

        for check in checks:
            prompts = ['actual_description', 'generated_description']
            prompts.extend(get_prompts(check))
            check_results = pd.DataFrame(columns=prompts)
            checker = self.get_checker(check)

            for pred_map in self.individual_maps:
                for i, row in pred_map.iterrows():
                    actual_description = row['actual_description']
                    generated_description = row['generated_description']
                    results, res = checker.run(actual_description, generated_description)
                    pred_map.at[i, check] = res
                    result = [actual_description, generated_description]
                    result.extend(results)
                    check_results.loc[len(check_results)] = result

            if not os.path.exists(rf"{parent_folder}"):
                os.makedirs(f"{parent_folder}")

            if not os.path.exists(rf"{parent_folder}//{self.domain}"):
                os.makedirs(f"{parent_folder}//{self.domain}")

            check_results.to_excel(f"{parent_folder}/{self.domain}/{check}_check.xlsx", index=False)

