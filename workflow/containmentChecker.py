import apiCaller
import os
from src import util

dirname = util.get_project_directory()
file_path = os.path.join(dirname, 'src/resources/prompts/containment')


class ContainmentChecker:
    def __init__(self):
        with open(file_path, 'r') as file:
            content = file.read()

        local_vars = {}

        exec(content, local_vars)
        self.prompts = local_vars['prompts']

    def run(self, actual_sentence, generated_sentence):
        results = []
        for prompt in self.prompts:
            result = apiCaller.call_api(actual_sentence, generated_sentence, prompt)
            results.append(result)
