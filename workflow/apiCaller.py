from openai import OpenAI
# import ollama
#
# from ollama import Client
#
# client = Client()
# ollama.pull("llama3:70b")


def combine_prompt(prompt, statement1, statement2):
    # Combine the prompt and statements
    return f"{prompt}\nStatement 1: {statement1}\nStatement 2: {statement2}"


def call_api(sentence1, sentence2, prompt):
    combined_prompt = combine_prompt(prompt, sentence1, sentence2)

    # response = client.chat(model='llama3:70b',
    #                        messages=[
    #                            {"role": "system",
    #                             "content": "You are a helpful, respectful and honest assistant."},
    #                            {"role": "user", "content": prompt}
    #                        ]
    #                        )
    #
    # return response['message']['content']
    #
    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system",
             "content": "You are a helpful, respectful and honest assistant."},
            {"role": "user", "content": combined_prompt}
        ]
    )

    # print(completion.choices[0].message)
    return completion.choices[0].message.content
    # return "srdtfgyhu"
