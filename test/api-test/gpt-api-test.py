from openai import OpenAI

import pandas as pd


def combine_prompt(prompt, statement1, statement2):
    # Combine the prompt and statements
    return f"{prompt}\nStatement 1: {statement1}\nStatement 2: {statement2}"


def call_api(prompt):
    client = OpenAI()

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are a helpful, respectful and honest assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    # print(completion.choices[0].message)
    return completion.choices[0].message.content



file_path = "D:\\Thesis\\modelling-assistant\\Transportation.csv"

# Read the CSV file
df = pd.read_csv(file_path)

# Iterate over each row in the DataFrame
for index, row in df.iterrows():
    statement1 = row["Statement 1 : Actual description"]
    statement2 = row["Statement2 : Generated description"]

    for i in range(2, len(df.columns)):
        prompt = df.columns[i]
        combined_text = combine_prompt(prompt, statement1, statement2)
        # print(combined_text)
        response = call_api(combined_text)
        df[prompt][index] = response

df.to_csv("D:\\Thesis\\modelling-assistant\\Transportation_Contradiction_answers.csv")
