import os
import pandas as pd
import re

# Define the base directory
base_dir =  "predictions/"  # Adjust if needed

# Define regex patterns to extract execution times
patterns = {
    "Sentence Generation": r"Sentence Generation took ([\d.]+) seconds",
    "Concept and Relationship Extraction": r"Concept and Relationship extraction took ([\d.]+) seconds",
    "Semantic Matching": r"Semantic matching took ([\d.]+) seconds",
    "LLM": r"LLM  took ([\d.]+) seconds",
    "Result Calculation": r"Result calculation took ([\d.]+) seconds",
}

# Store extracted data
data = []

# Traverse only subdirectories of 'predictions'
if os.path.exists(base_dir):
    for subdir in os.listdir(base_dir):
        subdir_path = os.path.join(base_dir, subdir)
        log_file_path = os.path.join(subdir_path, "domain_logs.txt")

        if os.path.isdir(subdir_path) and os.path.exists(log_file_path):
            # Read log file
            with open(log_file_path, "r") as f:
                content = f.read()

            # Extract execution times
            row = {"Domain": subdir}
            for key, pattern in patterns.items():
                match = re.search(pattern, content)
                row[key] = float(match.group(1)) if match else None  # Convert to float if found

            data.append(row)

# Convert to DataFrame
df = pd.DataFrame(data)

# Save to Excel
output_file = os.path.join(base_dir, "execution_times.xlsx")
df.to_excel(output_file, index=False)

print(f"Excel file saved: {output_file}")
