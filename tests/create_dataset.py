import os
import pandas as pd


def determine_value(text):
    if isinstance(text, str):
        if text.lower().startswith('yes'):
            return 'yes'
        elif text.lower().startswith('no'):
            return 'no'
    return ''


def collect_data_from_csvs(root_folder, names):
    # Create an empty DataFrame to store the results

    combined_data = []

    # Traverse the directory
    for subdir, _, files in os.walk(root_folder):
        for file in files:
            if 'equality_check.csv' in file:
                file_path = os.path.join(subdir, file)
                # Read the CSV file
                df = pd.read_csv(file_path)

                # Find the index of the 'generated_description' column
                if 'generated_description' in df.columns:
                    col_index = df.columns.get_loc('generated_description')

                    # Select all columns after 'generated_description'
                    selected_columns = df.iloc[:, col_index + 1:]

                    # Flatten the selected columns into a single list and extend the combined_data list
                    combined_data.extend(selected_columns.values.flatten())

    result_df = pd.DataFrame(combined_data, columns=['text'])

    # Apply the function to create the new column
    result_df['actual_answer'] = result_df['text'].apply(determine_value)
    return result_df


# Define the root folder and the list of file names
root_folder = '..//tests'
names = ['equality_check.csv']  # Example list of file names

# Call the function and get the result DataFrame
result_df = collect_data_from_csvs(root_folder, names)

# Display the result DataFrame
print(result_df)

result_df.to_csv("dataset.csv")
