import time

import pandas as pd

checks = ['equality', 'contradiction', 'inclusion']
elements = ['attributes', 'associations', 'aggregations', 'compositions', 'inheritance', 'enums']


def add_dummy_values(check_index, pred_row):
    for index in range(check_index + 1, len(checks)):
        pred_row.append(False)


# queries LLM synchronously for each matching sentence for a model element until result is achieved
# While prompting LLM, if majority is achieved, stops querying
# @param individual_maps: contains maps for each type of model elements i.e. attributes, relationships and enums
# Each map contains information like model element, generated sentence and all matching sentences
# @param checkers: EqualityChecker, ContradictionChecker and ContainmentChecker instances
# @param check_results: dataframe to store results of each query made to LLM, based on element type and check

def synchronous_execution_until_matched(individual_maps, checkers, check_results):
    llm_results = []
    for index in range(len(individual_maps)):
        pred_map = individual_maps[index]
        results_map = pd.DataFrame(columns=pred_map.columns)
        for i, row in pred_map.iterrows():
            actual_sentences = row['actual_description']  # list of all matching sentences
            generated_description = row['generated_description']
            source = row.get('source', row['class_name'])
            target = row.get('target', row['attributes'])
            multiplicity = row.get('multiplicity', '')
            role = row.get('role', '')

            startTime = time.time()

            pred_map.at[i,'time'] = startTime

            for actual_sentence in actual_sentences:
                pred_row = [source, target, role, multiplicity, generated_description, actual_sentence]
                isTrue = False

                for check_index, check in enumerate(checks):
                    checker = checkers[check]
                    check_res = check_results[(check, elements[index])]

                    results, res = checker.synchronous_run(actual_sentence, generated_description, source, target,
                                                           elements[index], multiplicity)
                    pred_row.append(res)
                    result = [actual_sentence, generated_description]
                    result.extend(results)
                    check_res.loc[len(check_res)] = result

                    # check if result is true, if it is true,
                    # 1. Do not check next test e.g. if equality test is true do not check for contradiction
                    # or inclusion
                    # 2. Also, do not check for rest of the matching sentences
                    if isinstance(res, bool):
                        if res:
                            isTrue = True
                            # This function add False value for remaining checks, this is done to avoid code
                            # break in next steps
                            add_dummy_values(check_index, pred_row)
                            pred_map.at[i, check] = True
                            execution_time_per_model_element = time.time() - startTime
                            pred_map.at[i, 'time'] = execution_time_per_model_element
                            break

                results_map.loc[len(results_map)] = pred_row

                if isTrue:
                    break

            if pred_map.at[i, 'time'] == startTime:
                pred_map[i, 'time'] = time.time() - startTime

        llm_results.append(results_map)

    return llm_results


# queries LLM in parallel for each matching sentence for a model element
# since queries are made in parallel, LLM will be queries for all matching sentences and all prompts
# @param individual_maps: contains maps for each type of model elements i.e. attributes, relationships and enums
# Each map contains information like model element, generated sentence and all matching sentences
# @param checkers: EqualityChecker, ContradictionChecker and ContainmentChecker instances
# @param check_results: dataframe to store results of each query made to LLM, based on element type and check

def asynchronous_execution(individual_maps, checkers, check_results):
    llm_results = []
    for index in range(len(individual_maps)):
        pred_map = individual_maps[index]
        results_map = pd.DataFrame(columns=pred_map.columns)
        for i, row in pred_map.iterrows():
            actual_sentences = row['actual_description']  # list of all matching sentences
            generated_description = row['generated_description']
            source = row.get('source', row['class_name'])
            target = row.get('target', row['attributes'])
            multiplicity = row.get('multiplicity', '')
            role = row.get('role', '')

            for actual_sentence in actual_sentences:
                pred_row = [source, target, role, multiplicity, generated_description, actual_sentence]
                isTrue = False

                for check_index, check in enumerate(checks):
                    checker = checkers[check]
                    check_res = check_results[(check, elements[index])]

                    results, res = checker.synchronous_run(actual_sentence, generated_description, source, target,
                                                           elements[index], multiplicity)
                    pred_row.append(res)
                    result = [actual_sentence, generated_description]
                    result.extend(results)
                    check_res.loc[len(check_res)] = result

                    # check if result is true, if it is true,
                    # 1. Do not check next test e.g. if equality test is true do not check for contradiction
                    # or inclusion
                    # 2. Also, do not check for rest of the matching sentences
                    if isinstance(res, bool):
                        if res:
                            isTrue = True
                            # This function add False value for remaining checks, this is done to avoid code
                            # break in next steps
                            add_dummy_values(check_index, pred_row)
                            pred_map.at[i, check] = True
                            break

                results_map.loc[len(results_map)] = pred_row
                if isTrue:
                    break


        llm_results.append(results_map)

    return llm_results


def synchronous_execution_all_matching_sentences(individual_maps, checkers, check_results):
    errors = []
    for index in range(len(individual_maps)):
        pred_map = individual_maps[index]
        for i, row in pred_map.iterrows():
            actual_description = row['actual_description']
            generated_description = row['generated_description']
            source = row.get('source', '')
            target = row.get('target', '')
            multiplicity = row.get('multiplicity', '')

            # each check
            for check_index, check in enumerate(checks):
                checker = checkers[check]
                check_res = check_results[(check, elements[index])]

                if True:
                    # if check not in pred_map.columns or pred_map.at[i, check] is None or pd.isna(pred_map.at[i,
                    # check]):
                    results, res = checker.run(actual_description, generated_description, source, target,
                                               elements[index], multiplicity)
                    pred_map.at[i, check] = res
                    result = [actual_description, generated_description]
                    result.extend(results)
                    check_res.loc[len(check_res)] = result

                    if isinstance(res, bool):
                        if res:
                            if check == 'contradiction':
                                errors.append({
                                    'actual_description': actual_description,
                                    'generated_description': generated_description
                                })

                                # This function add False value for remaining checks, this is done to avoid code
                                # break in next steps
                            add_dummy_values(check_index, pred_map, i)
                            break

    return individual_maps, errors
