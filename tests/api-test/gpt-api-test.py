from openai import OpenAI

import pandas as pd
import csv


few_shots = """
Q: Are the following two statements semantically equal? 
Statement1 : Each factory is located in a city.
Statement2 : A factory has a city.
A: Yes

Q: Are the following two statements semantically equal?
Statement1 : Each computer is connected to a screen.
Statement2 : A computer has a keyboard.
A: No

Q: Are the following two statements semantically equal?
Statement1 : A lamp is placed on a table.
Statement2 : A lamp has a bulb
A: No

Q: Are the following two statements semantically equal?
Statement1 : A city has a unique name.
Statement2 : A city has a name.
A: Yes

Q: Are the following two statements semantically equal?
Statement1 : Customers can open accounts with the bank.
Statement2 : A customer has accounts.
A: Yes

Q: Are the following two statements semantically equal?
"""

few_shots_with_explanation = ("Q: Are the following two statements semantically equal? Statement1=Each factory is "
                              "located in a city. Statement2=A factory has a city. A: Yes, As both statements convey "
                              "that the factory is related to the city. Q: Are the following two statements "
                              "semantically equal? Statement1=Each computer is connected to a screen. Statement2=A "
                              "computer has a keyboard. A: No, First statement tells that the computer is connected "
                              "to the screen whereas the second statement tells the computer has a keyboard. They are "
                              "talking about different components i.e. screen and keyboard connected to computer Q: "
                              "Are the following two statements semantically equal? Statement1=A lamp is placed on a "
                              "table. Statement2=A lamp has a bulb A: No, First statement tells the location of the "
                              "lamp, that it is placed on a table whereas the second statement tells about the lamp "
                              "having a bulb. Q: Are the following two statements semantically equal? Statement1=A "
                              "city has a unique name. Statement2=A city has a name. A: Yes, Both statements convey "
                              "that the city has a name. Q: Are the following two statements semantically equal? "
                              "Statement1=Customers can open accounts with the bank. Statement2=A customer has "
                              "accounts. A: Yes, Both statements convey that customers can have accounts with the "
                              "bank.")


def combine_prompt(prompt, statement1, statement2):
    # Combine the prompt and statements
    combined_prompt = f"{prompt}Statement1 :  {statement1}\nStatement2 :  {statement2}"
    return combined_prompt + "\nA:"


def call_api(prompt):
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
    # return 'abc'


file_path = "/examples.csv"

# Read the CSV file
df = pd.read_csv(file_path)

prompt = "Are the following two statements semantically equal?"

answer = []
# Iterate over each row in the DataFrame
for index, row in df.iterrows():
    statement1 = row["Statement 1 : Actual description"]
    statement2 = row["Statement2 : Generated description"]

    # combined_text = combine_prompt(few_shots, statement1, statement2)
    # response = call_api(combined_text)
    #
    # new_row = [statement1, statement2, response]
    #
    # answer.append(new_row)


    for i in range(2, len(df.columns)):
        prompt = df.columns[i]
        combined_text = combine_prompt(prompt, statement1, statement2)
        # print(combined_text)
        response = call_api(combined_text)
        df[prompt][index] = response

answer_path = "D:\\Thesis\\modelling-assistant\\few-shot-answers-gpt4.csv"
column_names = ['Statement1', 'Statement2', prompt]

with open(answer_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(column_names)
    writer.writerows(answer)

# answer.to_csv("D:\\Thesis\\modelling-assistant\\few-shot-answers.csv")
