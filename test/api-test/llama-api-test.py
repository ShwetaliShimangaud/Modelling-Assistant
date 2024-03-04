# import replicate
#
# # The meta/llama-2-70b-chat model can stream output as it's running.
# for event in replicate.stream(
#         "meta/llama-2-70b-chat",
#         input={
#             "debug": False,
#             "top_k": 50,
#             "top_p": 1,
#             "prompt": "Can you write a poem about open source machine learning? Let's make it in the style of E. E. "
#                       "Cummings.",
#             "temperature": 0.5,
#             "system_prompt": "You are a helpful, respectful and honest assistant.",
#             "max_new_tokens": 500,
#             "min_new_tokens": -1
#         },
# ):
#     print(str(event), end="")

import replicate
import pandas as pd


def combine_prompt(prompt, statement1, statement2):
    # Combine the prompt and statements
    return f"{prompt}\nStatement 1: {statement1}\nStatement 2: {statement2}"


def call_api(prompt):
    response = ""
    output = replicate.run(
        "meta/llama-2-7b-chat",

        input={
            "debug": False,
            "top_k": 50,
            "top_p": 1,
            "prompt": prompt,
            "temperature": 0.5,
            "system_prompt": "You are a helpful, respectful and honest assistant. Always answer as helpfully as "
                             "possible, while being safe. Your answers should not include any harmful, unethical, "
                             "racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses "
                             "are socially unbiased and positive in nature.\n\nIf a question does not make any sense, "
                             "or is not factually coherent, explain why instead of answering something not correct. "
                             "If you don't know the answer to a question, please don't share false information.",
            "max_new_tokens": 500,
            "min_new_tokens": -1
        }
    )

    # The meta/llama-2-70b-chat model can stream output as it's running.
    # The predict method returns an iterator, and you can iterate over that output.
    for item in output:
        # https://replicate.com/meta/llama-2-70b-chat/api#output-schema
        response = response + item

    return response
    # ['https://replicate.com/api/models/stability-ai/stable-diffusion/files/50fcac81-865d-499e-81ac-49de0cb79264/out-0.png']


file_path = "/\\Factory_equality check.csv"

# Read the CSV file
df = pd.read_csv(file_path)

# Iterate over each row in the DataFrame
for index, row in df.iterrows():
    statement1 = row["Statement 1 : Actual description"]
    statement2 = row["Statement2 : Generated description"]

    for i in range(3, len(df.columns)):
        prompt = df.columns[i]
        combined_text = combine_prompt(prompt, statement1, statement2)
        print(combined_text)
        response = call_api(combined_text)
        df[prompt][index] = response

df.to_csv("D:\\Thesis\\modelling-assistant\\Factory_equality_check.csv")
