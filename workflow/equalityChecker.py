import apiCaller

file_path = "D:\\Thesis\\modelling-assistant\\src\\resources\\prompts\\equality"


class EqualityChecker:
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
