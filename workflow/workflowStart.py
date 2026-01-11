import os

import pandas as pd
from src import util

from workflow.equalityChecker import EqualityChecker
from workflow.contradictionChecker import ContradictionChecker
from workflow.containmentChecker import ContainmentChecker
import time

from workflow.workflowUtil import synchronous_execution_all_matching_sentences, synchronous_execution_until_matched


def get_prompts(file_name, model_element):
    dirname = util.get_project_directory()
    file_path = os.path.join(dirname, f'src/resources/prompts/{file_name}')
    with open(file_path, 'r') as file:
        content = file.read()

    local_vars = {}

    exec(content, local_vars)

    if file_name == 'contradiction':
        attribute_prompts = local_vars['attribute_prompts']
        association_prompts = local_vars['association_prompts']
        inheritance_prompt = local_vars['inheritance_prompt']
        enum_prompt = local_vars['enum_prompt']
        composition_prompts = local_vars['composition_prompt']

        if model_element == 'associations' or model_element == 'aggregations':
            return association_prompts
        elif model_element == 'inheritance':
            return inheritance_prompt
        elif model_element == 'enums':
            return enum_prompt
        elif model_element == 'compositions':
            return composition_prompts
        else:
            return attribute_prompts

    return local_vars['prompts']


class WorkflowStart:
    def __init__(self, individual_maps, domain, results_dir, run_in_parallel):
        self.individual_maps = individual_maps
        self.results_dir = f"{results_dir}/predictions"
        self.equality_checker = EqualityChecker()
        self.contradiction_checker = ContradictionChecker()
        self.containment_checker = ContainmentChecker()
        # self.difference_finder = DifferenceFinder()
        self.domain = domain
        self.checks = ['equality', 'contradiction', 'inclusion']
        self.checkers = {}
        self.check_results = {}

        self.run_in_parallel = run_in_parallel

        self.elements = ['attributes', 'associations', 'aggregations', 'compositions', 'inheritance', 'enums']

        for check in self.checks:
            for element in self.elements:
                prompts = ['actual_description', 'generated_description']
                prompts.extend(get_prompts(check, element))
                self.check_results[(check, element)] = pd.DataFrame(columns=prompts)
            self.checkers[check] = self.get_checker(check)

        # for check in self.checks:
        #     for element in self.elements:
        #         check_res = pd.read_excel(f"{self.results_dir}/{self.domain}/{element}_{check}_check.xlsx")
        #         self.check_results[(check, element)] = check_res
        #     self.checkers[check] = self.get_checker(check)

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

        if not os.path.exists(rf"{self.results_dir}"):
            os.makedirs(f"{self.results_dir}")

        if not os.path.exists(rf"{self.results_dir}//{self.domain}"):
            os.makedirs(f"{self.results_dir}//{self.domain}")

        # synchronous execution, run for all matching sentences
        # pred_map, errors = synchronous_execution_all_matching_sentences(self.individual_maps, self.checkers,
        #                                                                 self.check_results)

        # synchronous execution, run until result is achieved
        llm_results = synchronous_execution_until_matched(self.individual_maps, self.checkers, self.check_results)

        # pred_map.to_csv(f"{self.results_dir}/{self.domain}/{self.elements[index]}_pred_map2.csv", index=False)
        for check in self.checks:
            for element in self.elements:
                check_res = self.check_results[(check, element)]
                check_res.to_excel(f"{self.results_dir}/{self.domain}/{element}_{check}_check2.xlsx", index=False)

        return errors

# domain_name, results_dir = "R9-be-well-app", "../final_evaluation"
# attributes_map = pd.read_csv(f"{results_dir}/predictions/{domain_name}/attributes_pred_map.csv")
# associations_map = pd.read_csv(f"{results_dir}/predictions/{domain_name}/associations_pred_map.csv")
# aggregations_map = pd.read_csv(f"{results_dir}/predictions/{domain_name}/aggregations_pred_map.csv")
# compositions_map = pd.read_csv(f"{results_dir}/predictions/{domain_name}/compositions_pred_map.csv")
# inheritance_map = pd.read_csv(f"{results_dir}/predictions/{domain_name}/inheritance_pred_map.csv")
# enum_map = pd.read_csv(f"{results_dir}/predictions/{domain_name}/enums_pred_map.csv")
#
#
# try:
#     start_time = time.perf_counter()
#     workflow = WorkflowStart(
#         [attributes_map, associations_map, aggregations_map, compositions_map,
#          inheritance_map, enum_map], domain_name, results_dir)
#     errors = workflow.run()
#     end_time = time.perf_counter()
#     elapsed_time = end_time - start_time
#     print(f"LLM took {elapsed_time:.6f} seconds")
#     log_entry = f"LLM took {elapsed_time:.6f} seconds\n"
# except Exception:
#     print("got exception")
