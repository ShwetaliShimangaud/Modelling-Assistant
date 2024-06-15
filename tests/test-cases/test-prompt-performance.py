import pandas as pd

# domains = ['bank', 'factory', 'smart-city', 'sustainable-transportation']
domains = ['car-maintenance', 'production-cell-inheritance']
checks = ['equality', 'contradiction', 'inclusion']


def pre_fill_values(df):
    result = pd.DataFrame(columns=['prompt', 'correct', 'incorrect', 'not clear'])
    for prompt in df.columns[2:]:
        result.loc[len(result)] = [prompt, 0, 0, 0]

    return result


def get_column(check):
    if check == 'equality':
        return 'equal'

    return check


parent_folder = "../25th-may-inheritance-results/gpt4"

for check in checks:
    # Just to get the prompts for each check
    df_check = pd.read_csv(f"{parent_folder}//{domains[0]}//{check}_check.csv")
    df_results = pre_fill_values(df_check)

    for domain in domains:
        predicted_attribute_map = pd.read_csv(f"{parent_folder}//{domain}//predicted inheritance map.csv")
        df_check = pd.read_csv(f"{parent_folder}//{domain}//{check}_check.csv")

        for index, result in enumerate(predicted_attribute_map[get_column(check)]):
            for i, prompt in enumerate(df_check.columns[2:]):
                res = df_check.iloc[index, i + 2]
                if res.startswith("Yes") or res.startswith("yes"):
                    answer = True
                elif res.startswith("No") or res.startswith("no"):
                    answer = False
                else:
                    answer = "not clear"

                if isinstance(answer, bool) and isinstance(result, bool):  # Check if answer is a boolean
                    if result == answer:
                        df_results.at[i, 'correct'] = 1 + df_results.iloc[i]['correct']
                    else:
                        df_results.at[i, 'incorrect'] = 1 + df_results.iloc[i]['incorrect']
                else:
                    df_results.at[i, 'not clear'] = 1 + df_results.iloc[i]['not clear']

    df_results.to_csv(f"{parent_folder}//{check}-results.csv")

print("Done")
