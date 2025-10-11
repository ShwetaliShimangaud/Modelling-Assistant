import os

import pandas as pd

from evaluation.AttributeResultAggregator import aggregate_attribute_results

# Base directory containing all the subdirectories
BASE_DIR = "predictions"

# List to collect results
collected_rows = []


def format_domain_name(parts):
    answer = ""
    for i in range(1, len(parts)):
        answer += parts[i].title() + " "
    return answer

final_df =  []

# Iterate over each directory
for dir_name in os.listdir(BASE_DIR):
    dir_path = os.path.join(BASE_DIR, dir_name)
    if os.path.isdir(dir_path):
        attributes, enums = aggregate_attribute_results(dir_path)
        attributes = attributes[attributes['answer'] == 'inconclusive']
        final_df.append(attributes)

# Combine all collected rows into a final DataFrame
final_df = pd.concat(final_df, ignore_index=True)

# Save to a new CSV
final_df.to_csv('inconclusive attributes.csv', index=False)

print(final_df)


