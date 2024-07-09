import replicate
import pandas as pd

import ollama

from ollama import Client

client = Client()
ollama.pull("llama3:70b")


def combine_prompt(prompt, statement1, statement2):
    # Combine the prompt and statements
    return f"{prompt}\nStatement 1: {statement1}\nStatement 2: {statement2}"


def call_api(prompt, statement1, statement2):
    combined_prompt = combine_prompt(prompt, statement1, statement2)

    response = client.chat(model='llama3:70b',
                           messages=[
                               {"role": "system",
                                "content": "You are a helpful, respectful and honest assistant."},
                               {"role": "user", "content": combined_prompt}
                           ]
                           )

    return response['message']['content']


library = pd.read_excel("D:\\Thesis\\modelling-assistant\\tests\\workflow-results\\library\\not_working.xlsx")

actual_sentences = list(library['actual_description'])
generated_sentences = list(library['generated_description'])

inclusion_prompts = list(library.columns)[2:]
columns = ['actual sentence', 'generated sentence', inclusion_prompts]

results = pd.DataFrame(columns=columns)

# Iterate over each row in the DataFrame
for statement1, statement2 in zip(actual_sentences, generated_sentences):
    # statement1 = row["Statement 1 : Actual description"]
    # statement2 = row["Statement2 : Generated description"]

    responses = [statement1, statement2]
    for prompt in inclusion_prompts:
        # prompt = df.columns[i]
        response = call_api(prompt, statement1, statement2)
        responses.append(response)

    results.loc[len(results)] = responses

results.to_csv("results.csv")
# df.to_csv("D:\\Thesis\\modelling-assistant\\Factory_equality_check.csv")
