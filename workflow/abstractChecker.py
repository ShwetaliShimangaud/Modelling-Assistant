import asyncio
import random
import time
from abc import ABC, abstractmethod

import pandas as pd
from openai import RateLimitError

from sentence_generator import util
from workflow import apiCaller
from sentence_generator.util import is_singular
from concurrent.futures import ThreadPoolExecutor, as_completed

from workflow.apiCaller import call_llm_async


def format_value(multiplicity):
    if pd.isna(multiplicity):
        return ''
    multiplicity = str(multiplicity)
    if is_singular(multiplicity):
        return 'instance'
    else:
        return 'instances'


def transform_multiplicity(multiplicity):
    if pd.isna(multiplicity):
        return ''
    multiplicity = str(multiplicity)
    if len(multiplicity) == 0:
        return ''
    if multiplicity == '1':
        return 'exactly one'
    elif multiplicity == '0..*':
        return 'zero or more'
    elif multiplicity == '1..*':
        return 'one or more'
    elif multiplicity == '2..*':
        return 'two or more'
    elif multiplicity == '*':
        return 'many'
    elif multiplicity == '3..3':
        return 'exactly three'
    elif multiplicity == '100':
        return 'exactly hundred'
    elif multiplicity == '6':
        return 'exactly six'
    elif multiplicity == '4':
        return 'exactly four'
    elif multiplicity == '2':
        return 'exactly two'
    elif multiplicity == '0..20':
        return 'zero to twenty'
    elif multiplicity == '0..1':
        return 'zero or one'
    elif multiplicity == '5..10':
        return 'five to ten'
    elif multiplicity == '100..200':
        return 'hundred to two hundred'
    elif multiplicity == '1000..2000':
        return 'one thousand to two thousand'
    elif multiplicity == '0..10':
        return 'one thousand to two thousand'
    elif multiplicity == '1..3':
        return 'one to three'
    else:
        return multiplicity


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

    @abstractmethod
    def process_response(self, response, model_element):
        pass

    def get_threshold_to_achieve_plurality(self, num):
        if num == 1:
            return 1
        elif num == 5:
            return 3
        elif num == 7:
            return 4
        else:
            raise ValueError("Invalid value provided for number of prompts")

    def synchronous_run(self, actual_sentence, generated_sentence, source, target, model_element, multiplicity):
        yes_count = 0
        no_count = 0
        unclear_count = 0

        results = []

        prompts = self.get_prompts(model_element)

        threshold_for_result = self.get_threshold_to_achieve_plurality(len(prompts))

        for prompt in prompts:
            combined_prompt = format_string(
                prompt, source, target, generated_sentence, actual_sentence, multiplicity
            )
            response = apiCaller.call_api(combined_prompt)
            results.append(response)

            res = self.process_response(response, model_element)
            if res.startswith("Yes") or res.startswith("yes"):
                yes_count = yes_count + 1
            elif res.startswith("No") or res.startswith("no"):
                no_count = no_count + 1
            else:
                unclear_count = unclear_count + 1

            if yes_count > threshold_for_result:
                return results, True

            elif no_count > threshold_for_result:
                return results, False

            elif unclear_count > threshold_for_result:
                return results, 'not clear'

        return results, 'not clear'

    async def call_llm_with_retry(self, prompt, max_retries=5):
        for attempt in range(max_retries):
            try:
                return await call_llm_async(prompt)

            except RateLimitError:
                backoff = (2 ** attempt) + random.uniform(0, 1)
                await asyncio.sleep(backoff)

        raise RuntimeError("Max retries exceeded")

    async def run_single_prompt_async(
            self,
            prompt,
            actual_sentence,
            generated_sentence,
            source,
            target,
            multiplicity,
            model_element
    ):
        formatted_prompt = format_string(
            prompt,
            source,
            target,
            generated_sentence,
            actual_sentence,
            multiplicity
        )

        response = await self.call_llm_with_retry(
            formatted_prompt
        )

        processed = self.process_response(response, model_element)
        return response, processed

    async def async_run_checker(
            self,
            actual_sentence,
            generated_sentence,
            source,
            target,
            model_element,
            multiplicity
    ):
        prompts = self.get_prompts(model_element)

        tasks = [
            self.run_single_prompt_async(
                prompt,
                actual_sentence,
                generated_sentence,
                source,
                target,
                multiplicity,
                model_element
            )
            for prompt in prompts
        ]

        results = await asyncio.gather(*tasks)

        responses = [r for r, _ in results]
        processed = [p for _, p in results]

        yes_count = sum(p.lower().startswith("yes") for p in processed)
        no_count = sum(p.lower().startswith("no") for p in processed)

        threshold = self.get_threshold_to_achieve_plurality(len(prompts))

        if yes_count > threshold:
            final = True
        elif no_count > threshold:
            final = False
        else:
            final = "not clear"

        return responses, final

    def run(self, actual_sentence, generated_sentence, source, target, model_element, multiplicity):
        yes_count = 0
        no_count = 0
        unclear_count = 0

        results = []

        prompts = self.get_prompts(model_element)

        def worker(prompt):
            combined_prompt = format_string(
                prompt, source, target, generated_sentence, actual_sentence, multiplicity
            )
            response = apiCaller.call_api(combined_prompt)
            return combined_prompt, response

        # ⚠️ Keep this conservative to avoid rate limits
        max_workers = len(prompts)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(worker, prompt) for prompt in prompts]

            for future in as_completed(futures):
                prompt, res = future.result()
                results.append(res)

                # print("Prompt:", prompt)
                # # print("Actual sentence:", actual_sentence)
                # # print("Generated sentence:", generated_sentence)
                # print("Result:", res)
                # # print()

                res = self.process_response(res, model_element)
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
