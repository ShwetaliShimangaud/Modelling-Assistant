from abc import ABC, abstractmethod

from sentence_generator import util
from workflow import apiCaller
from sentence_generator.util import is_singular


def format_value(multiplicity):
    if is_singular(multiplicity):
        return 'instance'
    else:
        return 'instances'


def transform_multiplicity(multiplicity):
    if len(multiplicity) == 0:
        return ''
    if multiplicity == '1':
        return 'exactly one'
    elif multiplicity == '0..*':
        return 'zero or more'
    elif multiplicity == '1..*':
        return 'one or more'
    elif multiplicity == '*':
        return 'many'
    else:
        raise ValueError("invalid multiplicity")


def format_string(template: str, source: str, target: str,
                  statement1, statement2, multiplicity="") -> str:
    formatted_template = (template.replace("{source}", source)
                          .replace("{target}", target))

    formatted_template = formatted_template.replace("{multiplicity}", transform_multiplicity(multiplicity))
    formatted_template = formatted_template.replace("{instance}", format_value(multiplicity))
    formatted_template = formatted_template.replace("{statement1}", statement1).replace("{statement2}", statement2)
    formatted_template = formatted_template.replace("{target_plural}", util.get_plural('target'))
    return formatted_template


class AbstractChecker(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def get_prompts(self, model_element):
        pass

    def run(self, actual_sentence, generated_sentence, source, target, model_element, multiplicity):
        yes_count = 0
        no_count = 0
        unclear_count = 0

        results = []

        prompts = self.get_prompts(model_element)

        for prompt in prompts:
            combined_prompt = format_string(prompt, source, target, generated_sentence, actual_sentence, multiplicity)
            res = apiCaller.call_api(combined_prompt)
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
