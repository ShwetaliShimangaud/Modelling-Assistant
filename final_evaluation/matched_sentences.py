import os
import pandas as pd


def get_csv_lengths(directory):
    # Define expected CSV filenames
    csv_files = [
        "associations_pred_map.csv",
        "aggregations_pred_map.csv",
        "attributes_pred_map.csv",
        "inheritance_pred_map.csv",
        "enums_pred_map.csv",
        "compositions_pred_map.csv"
    ]

    data = []

    # Iterate through subdirectories
    for subdir in os.listdir(directory):
        subdir_path = os.path.join(directory, subdir)
        if os.path.isdir(subdir_path):
            row = {"Domain": subdir}  # Store domain name

            # Read each CSV file and get its length
            for csv_file in csv_files:
                file_path = os.path.join(subdir_path, csv_file)
                if os.path.exists(file_path):
                    df = pd.read_csv(file_path)
                    row[csv_file] = len(df)
                else:
                    row[csv_file] = 0  # If file doesn't exist, set length to 0

            data.append(row)

    # Convert to DataFrame
    df_summary = pd.DataFrame(data)

    # Save to Excel
    excel_path = os.path.join(directory, "matched_sentences.xlsx")
    df_summary.to_excel(excel_path, index=False)
    print(f"Excel file saved at: {excel_path}")


# Example usage
directory = "predictions/"  # Change this to your directory path
get_csv_lengths(directory)
