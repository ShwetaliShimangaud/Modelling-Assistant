import pandas as pd

from workflow import apiCaller

parent_folder = "./test_contradiction_for_cardinality"

prompts = [
    "Do these statements contradict each other?",
    "Are these statements mutually exclusive?",
    "Do these statements clash or conflict with each other?",
    "Are these statements at odds with each other?",
    "Do these statements negate each other?",
    "Are these statements inconsistent?",
    "Do these statements oppose each other?",
    "Are these statements in disagreement?",
    "Are these statements incompatible?",
    "Do these statements present conflicting viewpoints?"
]

relationship_map = pd.DataFrame(
    columns=['generated_description', 'actual_description', 'actual_answer',
             'predicted_answer'])

# generated_descriptions = [
#     "A machine produces exactly one piece.",
#     "A machine is operated by exactly one worker.",
#     "A factory has exactly one employee which is a worker.",
#     "A worker can have workplaces which are factories. ",
#     "A worker has exactly one workplace which is a factory."
# ]
#
# actual_descriptions = [
#     "A factory is composed of a number of machines that produce pieces.",
#     "Each machine is operated by one or more workers, and, "
#     "for each worker, we need to store their id, name and salary.",
#     "There are workers working at the factory.",
#     "There are workers working at the factory.",
#     "There are workers working at the factory."
# ]

# actual_answers = [
#     True, True, True, True, False
# ]

data = pd.read_csv(f"../test_contradiction_for_cardinality/updated_test_data.csv")

revised_prompt2 = ("The statements describe association between two classes in a class diagram. "
                   "Analyze each statement strictly within the context provided; there are no other contexts or "
                   "interpretations to consider."
                   "Please note the following rules carefully:-"
                   "'One-to-one' indicates a strict association where each instance of the first class "
                   "is linked to exactly one instance of the second class. This means no more, "
                   "no less—exactly one-to-one. The relationship must be reciprocal and not "
                   "interpreted as 'one or more' in any context."
                   "The use of 'a' or 'an' before a class indicates exactly one single instance of that class at "
                   "the respective end. This means exactly one, not at least one, and implies a one-to-one "
                   "association from that side."
                   "Clearly distinguish between one-to-one, one-to-many, and many-to-many relationships. An "
                   "'exactly one' relationship from any side strictly cannot be reconciled with any 'one or more' or "
                   "'many' relationship from the opposite side."
                   "Carefully evaluate each statement to determine the implied multiplicity at both ends of the "
                   "association."
                   "Explicitly compare the multiplicities derived from each statement to identify any inconsistencies."
                   "If the multiplicities differ in any ways that cause them to contradict each other (e.g., "
                   "one-to-one in both directions versus one-to-many in either direction),"
                   "classify it is a valid difference. Start the response with 'Yes' if multiplicities differs or 'No.'")

revised_prompt3 = (
    "The statements describe one end of association from {source} to {target} class in a class diagram. Analyze "
    "each statement strictly within the context provided; there are no other contexts or interpretations to "
    "consider. Please note the following rules carefully:"

    "- 'One-to-one' indicates a strict association where each instance of the first class is linked to "
    "exactly one instance of the second class. This means no more, no less—exactly one-to-one. The "
    "relationship must be reciprocal and not interpreted as 'one or more' in any context."

    "- The use of 'a' or 'an' before a class indicates exactly one single instance of that class at "
    "the respective end. This means exactly one, not at least one, and implies a one-to-one "
    "association from that side."

    "- If a class is referred to in the plural form without a specific quantity, understand it as a "
    "potential 'one or more' relationship from that side, suggesting a one-to-many or many-to-one "
    "relationship."

    "- Clearly distinguish between one-to-one, one-to-many, and many-to-many relationships. An "
    "'exactly one' relationship from any side strictly cannot be reconciled with any 'one or more' or "
    "'many' relationship from the opposite side."

    "Carefully evaluate each statement to determine the implied multiplicity at specified end of the "
    "association. Explicitly compare the multiplicities derived from each statement to identify any "
    "inconsistencies. If the multiplicities differ in any way that causes them to contradict each "
    "other (e.g., one-to-one in one direction versus one-to-many or many-to-one in that same "
    "direction), classify it as a valid difference. Start the response with 'Yes' if multiplicities "
    "differ by even a single discrepancy, or 'No' if they do not.")

revised_prompt4 = (
    "The statement 2 describes {multiplicity} relationship from {source} to {target} class in a class diagram."
    "Analyze statement 1 strictly within the context provided; there are no other contexts or interpretations to "
    "consider. Please note the following rules carefully:"

    "- 'One-to-one' indicates a strict association where one instance of the first class is linked to "
    "exactly one instance of the second class. This means no more, no less—exactly one-to-one. The "
    "relationship must be reciprocal and not interpreted as 'one or more' in any context."

    "- The use of 'a' or 'an' before a class indicates exactly one single instance of that class at "
    "the respective end. This means exactly one, not at least one."

    "- If a class is referred to in the plural form without a specific quantity, understand it as a "
    "potential 'one or more' relationship from that side, suggesting a one-to-many or many-to-one "
    "relationship."

    "- Clearly distinguish between one-to-one, one-to-many, and many-to-many relationships. An "
    "'exactly one' relationship from any side strictly cannot be reconciled with any 'one or more' or "
    "'many' relationship from the opposite side."

    "Carefully evaluate statement 1 to determine the implied multiplicity from {source} to {target} class."
    " If the multiplicity from statement 1 is not {multiplicity}"
    "(e.g., one-to-one versus one-to-many or many-to-one), classify it as a valid difference."
    "Provide rationale for the answer."
    "Start the response with 'Yes' if multiplicities differ, or 'No' if they do not.")

prompt_suffix = ("The statements describe associations between two classes in a class diagram."
                 " A contradiction occurs if the multiplicities at either end are inconsistent."
                 "Rules to follow:"
                 "'One-to-one' means exactly one, not 'at least one'."
                 "'A' or 'an' implies exactly one at that end."
                 "Carefully evaluate each statement to determine the implied multiplicity at both ends of the "
                 "association."
                 "Explicitly compare the multiplicities derived from each statement to identify any "
                 "inconsistencies."
                 "Determine if the two statements are contradictory. Start the response with 'Yes' if a"
                 " contradiction exists or 'No' if there is none.")

revised_prompt = ("Analyze the following two statements, each describing an association "
                  "between two classes in a class diagram:"
                  "A contradiction occurs if both statements describe the same pair of"
                  " classes but specify contradictory multiplicities or semantics at either end of the association."
                  "Rules to follow:"
                  "One-to-one: Means exactly one instance at each end, not 'at least one.'"
                  "'A' or 'An': Implies exactly one instance at that end of the association."
                  "Determine if the two statements are contradictory. Start the response with 'Yes' if a"
                  " contradiction exists or 'No' if there is none.")

revised_prompt5 = ("The statement 2 describes a {multiplicity} relationship from the {source} class to the {target} "
                   "class in a class diagram."
                   "Analyze statement 1 strictly within the given context; do not consider any other contexts or "
                   "interpretations."
                   "Please adhere to the following rules carefully:"
                   "1. One-to-One Relationship: This indicates a strict association where one instance of the first "
                   "class is linked to exactly one instance of the second class. There are no exceptions—it is "
                   "exactly one-to-one. The relationship must be reciprocal and should never be interpreted as 'one "
                   "or more'."
                   "2. Use of 'a' or 'an': When 'a' or 'an' precedes a class, it signifies exactly one single "
                   "instance of that class on the corresponding end. It strictly means one, not 'at least one'."
                   "3. Plural Forms: If a class is referred to in the plural (without a specific quantity), interpret "
                   "this as a 'one or more' relationship from that side, which may suggest a one-to-many or "
                   "many-to-one relationship."
                   "4. Distinguishing Relationships: Clearly differentiate between one-to-one, one-to-many, "
                   "and many-to-many relationships. An 'exactly one' relationship from any side cannot be reconciled "
                   "with any 'one or more' or 'many' relationships from the opposite side."
                   "Carefully evaluate statement 1 to determine the implied multiplicity from the {source} class to "
                   "the {target}  class. If the implied multiplicity in statement 1 differs from the {multiplicity} "
                   "(for example, one-to-one vs. one-to-many or many-to-one), classify it as a valid difference."
                   "Provide a rationale for your answer."
                   "Begin your response with 'Yes' if the multiplicities differ, or 'No' if they do not.")

revised_prompt6 = ("The statement 2 describes a {multiplicity} relationship from the {source} class to the {target} "
                   "class in a class diagram."
                   "Analyze statement 1 strictly within the given context, focusing only on the multiplicity from the "
                   "{source} class to the {target} class."
                   "Do not consider multiplicity in the reverse direction or any other contexts or interpretations."
                   "Please adhere to the following rules carefully:"
                   "1. One-to-One Relationship: This indicates a strict association where one instance of the {"
                   "source} class is linked to exactly one instance of the {target} class. There are no exceptions—it "
                   "is exactly one-to-one and pertains only from the {source} to the {target}."
                   "2. Use of 'a' or 'an': When 'a' or 'an' precedes a class, it signifies exactly one single "
                   "instance of that class on the corresponding end. It strictly means one, not 'at least one', "
                   "and should only be considered from the {source} to the {target}."
                   "3. Plural Forms: If the {target} class is referred to in the plural form (without a specific "
                   "quantity), interpret this as a 'one or more' relationship from the {source} class to the {target} "
                   "class, suggesting a one-to-many relationship."
                   "4. Distinguishing Relationships: Clearly differentiate between one-to-one, one-to-many, "
                   "and many-to-one relationships. An 'exactly one' relationship from the {source} to the {target} "
                   "cannot be reconciled with any 'one or more' or 'many' relationships if they were in reverse, "
                   "which should not be considered here."
                   "Carefully evaluate statement 1 to determine the implied multiplicity from the {source} class to "
                   "the {target} class. If the implied multiplicity in statement 1 differs from the {multiplicity} "
                   "relationship in statement 2 (for example, one-to-one vs. one-to-many), classify it as a valid "
                   "difference."
                   # start with rationale,  
                   
                   "Provide a rationale for your answer. "
                   "Begin your response with 'Yes' if the multiplicities differ from {source} to {target}, or 'No' if "
                   "they do not.")

columns = ['generated_description', 'actual_description', revised_prompt6]
# columns.extend(prompts)
domain_result = pd.DataFrame(columns=columns)


def format_string(template: str, multiplicity: str, source: str, target: str) -> str:
    return template.replace("{source}", source).replace("{target}", target).replace("{multiplicity}", multiplicity)


for index, row in data.iterrows():
    generated_description = row['generated_description']
    actual_description = row['actual_description']

    # yes_count = 0
    # no_count = 0
    # unclear_count = 0
    result = [generated_description, actual_description]

    res = apiCaller.call_api(actual_description, generated_description,
                             format_string(revised_prompt6, row['multiplicity'], row['source'], row['target']))
    result.append(res)
    domain_result.loc[len(domain_result)] = result

    if res.startswith("Yes") or res.startswith("yes"):
        data.loc[index, 'prediction'] = True
    elif res.startswith("No") or res.startswith("no"):
        data.loc[index, 'prediction'] = False
    else:
        data.loc[index, 'prediction'] = "not clear"

    # for prompt in prompts:
    #     res = apiCaller.call_api(actual_description, generated_description, revised_prompt)
    #     result.append(res)
    #
    #     if res.startswith("Yes") or res.startswith("yes"):
    #         yes_count = yes_count + 1
    #     elif res.startswith("No") or res.startswith("no"):
    #         no_count = no_count + 1
    #     else:
    #         unclear_count = unclear_count + 1
    #
    # domain_result.loc[len(domain_result)] = result
    # if yes_count > no_count and yes_count > unclear_count:
    #     data.loc[index, 'prediction'] = True
    # elif no_count > yes_count and no_count > unclear_count:
    #     data.loc[index, 'prediction'] = False
    # else:
    #     data.loc[index, 'prediction'] = "not clear"

data.to_csv(f"../test_contradiction_for_cardinality/relationship_results_gpt4o_system_prompt13.csv",
            index=False)
# relationship_map.to_csv(f"../{parent_folder}/contradiction-prompts-results-all-relationships.csv", index=False)
domain_result.to_csv(f"../test_contradiction_for_cardinality"
                     f"/relationship_results_detailed_gpt4o_system_prompt13.csv", index=False)
