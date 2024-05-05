from openai import OpenAI


def combine_prompt(prompt, statement1, statement2):
    # Combine the prompt and statements
    return f"{prompt}\nStatement 1: {statement1}\nStatement 2: {statement2}"


def call_api(sentence1, sentence2, prompt):
    prompt = combine_prompt(prompt, sentence1, sentence2)
    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system",
             "content": "You are a helpful, respectful and honest assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    # print(completion.choices[0].message)
    return completion.choices[0].message.content
    # return "Yes"
