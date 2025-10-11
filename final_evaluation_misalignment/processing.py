import os
import pandas as pd

# Path where your directories are located
BASE_DIR = "ground-truth"

# List to collect results
results = []

# Iterate over each directory
for dir_name in os.listdir(BASE_DIR):
    dir_path = os.path.join(BASE_DIR, dir_name)
    if os.path.isdir(dir_path):
        # Paths to the specific CSV files
        attributes_path = os.path.join(dir_path, 'attributes_results.csv')
        associations_path = os.path.join(dir_path, 'associations_results.csv')
        aggregations_path = os.path.join(dir_path, 'aggregations_results.csv')
        compositions_path = os.path.join(dir_path, 'compositions_results.csv')
        inheritance_path = os.path.join(dir_path, 'inheritance_results.csv')
        enums_path = os.path.join(dir_path, 'enums_results.csv')

        # Check if files exist
        if os.path.exists(attributes_path) and os.path.exists(associations_path):
            # Read the files
            attributes_df = pd.read_csv(attributes_path)
            associations_df = pd.read_csv(associations_path)
            aggregations_df = pd.read_csv(aggregations_path)
            compositions_df = pd.read_csv(compositions_path)
            inheritance_df = pd.read_csv(inheritance_path)
            enums_df = pd.read_csv(enums_path)

            # Count for attributes
            attributes_count = attributes_df.shape[0]

            # Count for attributes
            enums_count = enums_df.shape[0]

            # Counts for associations
            aligned_associations = associations_df[associations_df['answer'] == 'correct'].shape[0]
            misaligned_associations = associations_df[associations_df['answer'] == 'wrong'].shape[0]

            # Counts for associations
            aligned_associations += aggregations_df[aggregations_df['answer'] == 'correct'].shape[0]
            misaligned_associations += aggregations_df[aggregations_df['answer'] == 'wrong'].shape[0]

            # Counts for associations
            aligned_compositions = compositions_df[compositions_df['answer'] == 'correct'].shape[0]
            misaligned_compositions = compositions_df[compositions_df['answer'] == 'wrong'].shape[0]

            # Counts for associations
            aligned_inheritance = inheritance_df[inheritance_df['answer'] == 'correct'].shape[0]
            misaligned_inheritance = inheritance_df[inheritance_df['answer'] == 'wrong'].shape[0]

            # Append results
            results.append({
                'directory': dir_name.split("-")[0],
                'attributes': attributes_count,
                'aligned_associations': aligned_associations,
                'misaligned_associations': misaligned_associations,
                'aligned_compositions': aligned_compositions,
                'misaligned_compositions': misaligned_compositions,
                'enums_count': enums_count,
                'aligned_inheritance': aligned_inheritance,
                'misaligned_inheritance': misaligned_inheritance
            })

# Create final dataframe
final_df = pd.DataFrame(results)

# Save if needed
final_df.to_csv('final_summary.csv', index=False)

print(final_df)
