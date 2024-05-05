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


class WorkflowStart:
    def __init__(self, attributes_map, relationships_map):
        self.attributes_map = attributes_map
        self.relationships_map = relationships_map
        self.equality_checker = EqualityChecker()
        self.contradiction_checker = ContradictionChecker()
        self.containment_checker = ContainmentChecker()
        # self.difference_finder = DifferenceFinder()

    def run(self):
        # Take actual and generated sentence Run all the checkers one by one. if result of any checker is true then
        # accordingly add it in warnings or errors array, Run next checker only if result of previous checker is false
        warnings = []
        errors = []

        equality_prompts = ['actual_description', 'generated_description']
        contradiction_prompts = ['actual_description', 'generated_description']
        inclusion_prompts = ['actual_description', 'generated_description']

        equality_prompts.extend(get_prompts('equality'))
        contradiction_prompts.extend(get_prompts('contradiction'))
        inclusion_prompts.extend(get_prompts("containment"))

        equality_check = pd.DataFrame(columns=equality_prompts)
        contradiction_check = pd.DataFrame(columns=contradiction_prompts)
        inclusion_check = pd.DataFrame(columns=inclusion_prompts)

        for i, row in self.attributes_map.iterrows():
            actual_description = row['actual_description']
            generated_description = row['generated_description']
            results, res = self.equality_checker.run(actual_description, generated_description)
            self.attributes_map.at[i, 'equal'] = res
            result = [actual_description, generated_description]
            result.extend(results)
            equality_check.loc[len(equality_check)] = result

        for i, row in self.relationships_map.iterrows():
            actual_description = row['actual_description']
            generated_description = row['generated_description']
            results, res = self.equality_checker.run(actual_description, generated_description)
            self.relationships_map.at[i, 'equal'] = res
            result = [actual_description, generated_description]
            result.extend(results)
            equality_check.loc[len(equality_check)] = result

        for i, row in self.attributes_map.iterrows():
            actual_description = row['actual_description']
            generated_description = row['generated_description']
            results, res = self.contradiction_checker.run(actual_description, generated_description)
            self.attributes_map.at[i, 'contradiction'] = res
            result = [actual_description, generated_description]
            result.extend(results)
            contradiction_check.loc[len(contradiction_check)] = result

        for i, row in self.relationships_map.iterrows():
            actual_description = row['actual_description']
            generated_description = row['generated_description']
            results, res = self.contradiction_checker.run(actual_description, generated_description)
            self.relationships_map.at[i, 'contradiction'] = res
            result = [actual_description, generated_description]
            result.extend(results)
            contradiction_check.loc[len(contradiction_check)] = result

        for i, row in self.attributes_map.iterrows():
            actual_description = row['actual_description']
            generated_description = row['generated_description']
            results, res = self.containment_checker.run(actual_description, generated_description)
            self.attributes_map.at[i, 'inclusion'] = res
            result = [actual_description, generated_description]
            result.extend(results)
            inclusion_check.loc[len(inclusion_check)] = result

        for i, row in self.relationships_map.iterrows():
            actual_description = row['actual_description']
            generated_description = row['generated_description']
            results, res = self.containment_checker.run(actual_description, generated_description)
            self.relationships_map.at[i, 'inclusion'] = res
            result = [actual_description, generated_description]
            result.extend(results)
            inclusion_check.loc[len(inclusion_check)] = result

        if not os.path.exists("logs"):
            os.makedirs("logs")

        equality_check.to_csv("logs//equality_check.csv")
        contradiction_check.to_csv("logs//contradiction_check.csv")
        inclusion_check.to_csv("logs//inclusion_check.csv")

        self.attributes_map.to_csv("logs//predicted_attributes_map.csv")
        self.relationships_map.to_csv("logs//predicted_relationship_map.csv")

        # for i in enumerate(self.actual_description):
        #     # TODO Check whether this can be list or dict
        #     sentence1 = self.actual_description[i]
        #     sentence2 = self.generated_description[i]
        #
        #     if self.equality_checker.run(sentence1, sentence2):
        #         print("Semantically equal")
        #
        #     elif self.contradiction_checker.run(sentence1, sentence2):
        #         print("Contradictory")
        #         # TODO Add exact class/attribute/relationship error
        #         errors.append("Error")
        #
        #     elif self.containment_checker.run(sentence1, sentence2):
        #         print("Containment")
        #         errors.append("Actual description is more generic than modelled system")
        #         warnings.append("warning")
        #
        #     else:
        #         difference = self.difference_finder.run(sentence1, sentence2)
        #         errors.append(difference)
        #
        # return warnings, errors
