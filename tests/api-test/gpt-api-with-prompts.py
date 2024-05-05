import csv

import pandas as pd
from openai import OpenAI

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
    combined_prompt = f"{prompt}\nStatement 1 :  {statement1}\nStatement 2 :  {statement2}"
    return combined_prompt


def combine_prompt_few_shot(statement1, statement2):
    combined_prompt = f"{few_shots}\nStatement1 :  {statement1}\nStatement2 :  {statement2}\nA:"
    return combined_prompt


def call_api_with_system_prompt(prompt, system_prompt):
    client = OpenAI()
    system_prompt = "You are a helpful assistant. You are working on the following context : " + system_prompt

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )

    return completion.choices[0].message.content
    # return 'abc'


def call_api(prompt):
    client = OpenAI()
    system_prompt = "You are a helpful assistant."

    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system",
             "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )

    return completion.choices[0].message.content
    # return 'abc'


file_path = "D:\\Thesis\\modelling-assistant\\examples.csv"
equality_check_prompts = [
    "are the following two statements semantically equal?",
    "Do the following two statements convey the exact same information?",
    "Are these two statements conveying the same meaning?",
    "Are these statements synonymous?",
    "Do statement 1 and statement 2 have identical implications?",
    "Are these two statements congruent in the information shared?",
    "Is the information within these two statements analogous?"
]

containment_check_prompts = [
    "Is there any information in Statement 1 that is not present in Statement 2? Check every detail.",
    "Does Statement 1 contain any details not found in Statement 2?	",
    "Does Statement 1 offer additional information not provided in Statement 2?",
    "Are there any distinct facts present in Statement 1 but missing in Statement 2?",
    "Are there any details exclusive to Statement 1 not mentioned in Statement 2?",
    "Does Statement 1 present any content not covered in Statement 2?",
    "Are there any pieces of information in Statement 1 not shared in Statement 2?",
    "Is there any data unique to Statement 1 that is absent in Statement 2?",
]

inclusion_check_prompts = [
    "Does every bit of information from Statement 2 appear in Statement 1?",
    "Do all the details in Statement 2 exist in Statement 1?",
    "Is Statement 1 inclusive of all the details given in Statement 2?",
    "Does Statement 1 include all the details mentioned in Statement 2?",
    "Does Statement 1 encompass all the information provided in Statement 2?",
    "Is all the data in Statement 2 covered in Statement 1?",
    "Can every detail from Statement 2 be found in Statement 1?",
    "Is Statement 1 comprehensive of all aspects mentioned in Statement 2?",
    "Does Statement 1 contain all the particulars brought up in Statement 2?"
]

# Read the CSV file
df = pd.read_csv(file_path, encoding='unicode_escape')

prompt = "Determine whether all facts from Statement 2 are included in Statement 1, either implicitly or explicitly."

answer = []
# Iterate over each row in the DataFrame
for index, row in df.iterrows():
    statement1 = row["Statement 1 : Actual description"]
    statement2 = row["Statement2 : Generated description"]
    system_prompt = row["system_description"]

    # combined_text = combine_prompt_few_shot(statement1, statement2)
    # response = call_api(combined_text)
    #
    # new_row = [statement1, statement2, response]
    #
    # answer.append(new_row)

    # combined_text = combine_prompt(prompt, statement1, statement2)
    # response = call_api_with_system_prompt(combined_text, system_prompt)
    # new_row = [statement1, statement2, response]
    # answer.append(new_row)

    for prompt in inclusion_check_prompts:
        combined_text = combine_prompt(prompt, statement1, statement2)
        response = call_api_with_system_prompt(combined_text, system_prompt)
        df.at[index, prompt] = response

    print("Done")
    print(statement1)
    print()

# answer_path = "D:\\Thesis\\modelling-assistant\\inclusion-check-all-examples-with-system-prompt-3.5.csv"
# column_names = ['Statement1', 'Statement2', prompt]
#
# with open(answer_path, 'w', newline='') as csvfile:
#     writer = csv.writer(csvfile)
#     writer.writerow(column_names)
#     writer.writerows(answer)

df.to_csv("D:\\Thesis\\modelling-assistant\\inclusion-check-all-examples-with-system-prompt-3.5.csv")
