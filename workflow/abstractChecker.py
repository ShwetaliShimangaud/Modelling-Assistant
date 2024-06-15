from abc import ABC, abstractmethod

from workflow import apiCaller


class AbstractChecker(ABC):

    @abstractmethod
    def __init__(self):
        pass

    def run(self, actual_sentence, generated_sentence):
        yes_count = 0
        no_count = 0
        unclear_count = 0

        results = []

        for prompt in self.prompts:
            res = apiCaller.call_api(actual_sentence, generated_sentence, prompt)
            results.append(res)

            print("Prompt:", prompt)
            print("Actual sentence:", actual_sentence)
            print("Generated sentence:", generated_sentence)
            print("Result:", res)
            print()

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

        return results, final_answer

