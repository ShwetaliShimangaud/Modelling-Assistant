import os
import pandas as pd

# TODO Change parent dir
parent_folder = "../system-test"
results_folder = "../evaluation"


def change_col(val):
    if val == 'TRUE' or val == 'True':
        return True
    elif val == 'FALSE' or val == 'False':
        return False
    return val


def find_common_answer(lst):
    ans = False
    for ele in lst:
        if isinstance(ele, bool):
            ans = ans | ele

    return ans


# Grouping by class_name and attribute_name
def process_group(group):
    result = {
        'class_name': group['class_name'].iloc[0],
        'attribute_name': group['attributes'].iloc[0],
        'generated_sentence': group['generated_description'].iloc[0],
        'actual_sentence': group['actual_description'].iloc[0],
        'equality': find_common_answer(list(group['equality'])),
        'contradiction': find_common_answer(list(group['contradiction'])),
        'inclusion': find_common_answer(list(group['inclusion']))}

    # Choosing the actual sentence
    # valid_sentences = group[is_valid((group['equality']) , (group['contradiction']) , (group['inclusion']))]
    # result['actual_sentence'] = valid_sentences['actual_description'].iloc[0] if not valid_sentences.empty else 'no match'

    # Determining the answer column value
    if result['contradiction'] == True:
        result['answer'] = 'wrong'
    elif result['equality'] == True or result['inclusion'] == True:
        result['answer'] = 'correct'
    elif result['actual_sentence'] == '':
        result['answer'] = 'no match'
    else:
        result['answer'] = 'inconclusive'

    return pd.Series(result)


def group_results(df, col1, col2):
    new_df = df.groupby([col1, col2]).apply(process_group).reset_index(drop=True)
    return new_df


def aggregate_attribute_results():
    domains = ['bank', 'car-maintenance', 'factory', 'flight-reservation', 'hotel-reservation', 'library',
               'production-cell-inheritance', 'smart-city', 'sustainable-transportation']

    try:
        for folder_name in os.listdir(parent_folder):
            folder_path = os.path.join(parent_folder, folder_name)
            if os.path.isdir(folder_path):
                df = pd.read_csv(f"{parent_folder}/{folder_name}/attributes_pred_map.csv")
                if not df.empty:
                    df['equality'] = df['equality'].apply(change_col)
                    df['contradiction'] = df['contradiction'].apply(change_col)
                    df['inclusion'] = df['inclusion'].apply(change_col)
                    processed_df = group_results(df, 'class_name', 'attributes')

                    if not os.path.exists(rf"{results_folder}/predictions/{folder_name}"):
                        os.makedirs(f"{results_folder}/predictions/{folder_name}")

                    processed_df.to_csv(f"{results_folder}/predictions/{folder_name}/attributes_results.csv",
                                        index=False)
    except Exception as e:
        raise Exception(e)


# aggregate_attribute_results()
