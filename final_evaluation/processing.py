import os
import pandas as pd

# Base directory containing all the subdirectories
BASE_DIR = "../final_evaluation_misalignment/predictions"
# BASE_DIR = "predictions"
# List to collect results
collected_rows = []


def format_domain_name(parts):
    answer = ""
    for i in range(1, len(parts)):
        answer += parts[i].title() + " "
    return answer


# Iterate over each directory
for dir_name in os.listdir(BASE_DIR):
    dir_path = os.path.join(BASE_DIR, dir_name)
    if os.path.isdir(dir_path):
        results_file = os.path.join(dir_path, f"results_{dir_name}.csv")

        if os.path.exists(results_file):
            df = pd.read_csv(results_file)

            # Filter row where model_element == 'attributes'
            attributes_row = df[df['model_element'] == 'association']
            index = 1
            if attributes_row['alignments'][index] == 0:
                attributes_row['overall_precision'][index] = ''
                attributes_row['overall_recall'][index] = ''
                attributes_row['precision_alignment'][index] = ''
                attributes_row['precision_misalignment'][index] = ''
                attributes_row['recall_alignment'][index] = ''
                attributes_row['recall_misalignment'][index] = ''

            if not attributes_row.empty:
                # selected_data = attributes_row[[
                #     'alignments',
                #     'alignments_predicted_correct',
                #     'alignments_identified_and_correct',
                #     'overall_precision',
                #     'overall_recall'
                # ]].copy()
                selected_data = attributes_row.copy()

                # Add model (directory name) column
                selected_data['model'] = dir_name.split("-")[0]
                selected_data['domain'] = format_domain_name(dir_name.split("-"))

                collected_rows.append(selected_data)

# Combine all collected rows into a final DataFrame
final_df = pd.concat(collected_rows, ignore_index=True)

# Save to a new CSV
final_df.to_csv('aggregated_results_associations_misalignments.csv', index=False)

print(final_df)
