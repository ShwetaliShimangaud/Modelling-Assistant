from abc import ABC

import workflow.apiCaller as apiCaller
import os
from src import util
from workflow.abstractChecker import AbstractChecker

dirname = util.get_project_directory()
file_path = os.path.join(dirname, 'src/resources/prompts/contradiction')


class ContradictionChecker(AbstractChecker):
    def __init__(self):
        with open(file_path, 'r') as file:
            content = file.read()

        local_vars = {}

        exec(content, local_vars)
        self.attribute_prompts = local_vars['attribute_prompts']
        self.association_prompts = local_vars['association_prompts']
        self.inheritance_prompt = local_vars['inheritance_prompt']
        self.enum_prompt = local_vars['enum_prompt']

    def get_prompts(self, model_element):
        if model_element == 'associations' or model_element == 'aggregations':
            return self.association_prompts
        elif model_element == 'inheritance':
            return self.inheritance_prompt
        elif model_element == 'enums':
            return self.enum_prompt
        else:
            return self.attribute_prompts

