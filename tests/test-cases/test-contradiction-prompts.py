import pandas as pd

from sentence_generator import util
from sentence_generator.util import is_singular
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

revised_prompt7 = ("The statement 2 describes a {multiplicity} relationship from the {source} class to the {target} "
                   "class in a class diagram."
                   "Analyze statement 1 strictly within the given context, focusing only on the multiplicity from the "
                   "{source} class to the {target} class."
                   "Do not consider multiplicity in the reverse direction or any other contexts or interpretations."
                   "Please adhere to the following rules carefully:"
                   "1. One-to-One Relationship: This indicates a strict association where one instance of the {"
                   "source} class is linked to exactly one instance of the {target} class. There are no exceptions. "
                   "It is exactly one-to-one and pertains only from the {source} to the {target}."
                   "2. Use of 'a' or 'an': When 'a' or 'an' precedes a class, it signifies exactly one single "
                   "instance of that class on the corresponding end. It strictly means one, not 'at least one', "
                   "and should only be considered from the {source} to the {target}."
                   "3. Plural Forms: If the {target} class is referred to in the plural form (without a specific "
                   "quantity), interpret this as a 'one or more' relationship from the {source} class to the {target} "
                   "class, suggesting a one-to-many relationship."
                   "4. Ambiguity in Implied Multiplicity: If the implied multiplicity in statement 1 is ambiguous and "
                   "it cannot be concluded with certainty from the {source} class to the {target} class based on the "
                   "provided context, do not consider it as a valid difference. Ambiguity does not provide sufficient "
                   "grounds for classification as a valid difference."
                   "Clearly differentiate between one-to-one and one-to-many relationships."
                   "Carefully evaluate statement 1 to determine the implied multiplicity from the {source} class to "
                   "the {target} class. If the implied multiplicity in statement 1 differs from the {multiplicity} "
                   "relationship in statement 2 (for example, one-to-one vs. one-to-many), classify it as a valid "
                   "difference."
                   "Begin the response by providing reasoning, and conclude with 'Yes' if the multiplicity of the "
                   "association from the {source} class to the {target} class differs, or 'No' if they are the same.")
revised_prompt8 = (
    "In a textual domain description, statement 1 states that the {source} class is associated with {multiplicity} "
    "{instance} of the {target} class."
    "Analyze statement 2 to determine the multiplicity that statement 2 implies from the {source} class to the {"
    "target} class, if any, and report whether that multiplicity differs from the one described in statement 1."
    "Begin the response by providing reasoning, and conclude with 'Conclusion:Yes' if the determined multiplicity of "
    "statement 2 differs from the one described in statement 1,or ‘Conclusion:No’ if the multiplicities are the same "
    "or in the case where statement 2 does not provide clear insight into the multiplicity from the {source} class to "
    "the {target} class.")

revised_prompt9 = ("In a textual domain description, there is one statement (statement 1) that says:"
                   "Statement 1: {Statement1} "
                   "This states that an instance of type {source} is associated with {multiplicity} {instance} of type "
                   "{target}."
                   "We also have a second statement (statement 2) that says:"
                   "Statement 2: {Statement2} "
                   "Please, analyze statement 2 to determine the multiplicity from {source} to the {target}, "
                   "if there is an association between them."
                   "Furthermore, report whether that multiplicity differs from the multiplicity described in "
                   "statement 1."
                   "Begin your response by providing reasoning, and conclude:"
                   "- 'Conclusion:Yes' if the multiplicity of statement 2 differs from the one described in statement "
                   "1, or"
                   "- 'Conclusion:No' if the multiplicities are the same or if statement 2 does not provide clear "
                   "insight into the multiplicity from {source} to {target}.")

revised_prompt10 = ("Consider you are a domain modeling assistant."
                    "I want to draw a class diagram from its textual description."
                    "There is an association from the {source} class to the {target} class."
                    "I want you to find the multiplicity for this association from the perspective of the {source} "
                    "class to the {target} class,i.e., how many {target_plural} can be associated with one {source}."
                    "Here are few statements from the textual description which are relevant to this association:"
                    "'{statement2}'. "
                    "Only consider these statements as context and do not use any other general knowledge beyond what "
                    "is stated in these statements."
                    "Carefully evaluate these statements and find the multiplicity of the association from {source} "
                    "to {target} class,"
                    "from the perspective of how many {target_plural} can be associated with one {source}."
                    "The possible multiplicities could be 'exactly one', 'one or more', 'zero or more', 'at most "
                    "one', 'N', 'N to M'."
                    "If these statements do not provide clear insight  for the multiplicity of the association from {"
                    "source} to {target} class,from the perspective of how many {target_plural} can be associated "
                    "with one {source}, then respond with 'No'.")

revised_prompt11 = ("In a textual domain description, there is one statement (statement 1) that says:"
                    "Statement 1: {statement1}. "
                    "This states that an instance of type {source} is associated with {multiplicity} {instance} of type"
                    " {target}."
                    "We also have a second statement (statement 2) that says:"
                    "Statement 2: {statement2}. "
                    "Please, analyze statement 2 to determine the multiplicity from {source} to the {target}, "
                    "if there is an association between them."
                    "Furthermore, report whether that multiplicity differs from the multiplicity described in "
                    "statement 1."
                    "Begin your response by providing reasoning, and conclude:"
                    "- 'Conclusion:Yes' if the multiplicity of statement 2 differs from the one described in statement "
                    "1,"
                    "- 'Conclusion:No' if the multiplicities are the same,"
                    "- 'Conclusion:Not Sure' if statement 2 does not provide enough details to determine the "
                    "multiplicity from {source} to {target}.")

inheritance_prompt1 = ("In a textual domain description, there is one statement (statement 1) that says:"
                       "Statement 1: {statement1}. "
                       "We also have a second statement (statement 2) that says:"
                       "Statement 2: {statement2}. "
                       "Please, analyze statement 2 to determine whether {target} is a kind of {source}."
                       "Begin your response by providing reasoning, and conclude:"
                       "- 'Conclusion:Yes' if {target} is a kind of {source}"
                       "- 'Conclusion:No' if {target} is not a kind of {source},"
                       "- 'Conclusion:Not Sure' if statement 2 does not provide enough details to determine whether {"
                       "target} is a kind of {source}.")


# inheritance_prompt2 = ("In a textual domain description, there is one statement (statement 1) that says:"
#                        "Statement 1: {statement1}. "
#                        "We also have a second statement (statement 2) that says:"
#                        "Statement 2: {statement2}. "
#                        "Please, analyze statement 2 to determine whether {target} is a kind of {source}."
#                        "Begin your response by providing reasoning, and conclude:"
#                        "- 'Conclusion:No' if {target} is not a kind of {source}"
#                        "- 'Conclusion:Yes' if {target} is a kind of {source}, or if statement 2 does not provide"
#                        " enough details to determine whether {target} is a kind of {source}.")

data = pd.read_csv(f"../test_contradiction_for_cardinality/test_data_strategic_conquest2.csv")
columns = ['generated_description', 'actual_description', inheritance_prompt1]
# columns.extend(prompts)
domain_result = pd.DataFrame(columns=columns)


def transform_multiplicity(multiplicity):
    if multiplicity == '1':
        return 'exactly one'
    elif multiplicity == '0..*':
        return 'zero or more'
    elif multiplicity == '1..*':
        return 'one or more'
    else:
        raise ValueError("invalid multiplicity")


def format_value(multiplicity):
    if is_singular(multiplicity):
        return 'instance'
    else:
        return 'instances'


def format_string(template: str, source: str, target: str, multiplicity="",
                  statement1="", statement2="", target_plural="") -> str:
    formatted_template = (template.replace("{source}", source)
                          .replace("{target}", target))

    # formatted_template = formatted_template.replace("{multiplicity}", transform_multiplicity(multiplicity))
    # formatted_template = formatted_template.replace("{instance}", format_value(multiplicity))
    formatted_template = formatted_template.replace("{statement1}", statement1).replace("{statement2}", statement2)
    # formatted_template = formatted_template.replace("{target_plural}", target_plural)
    return formatted_template


for index, row in data.iterrows():
    generated_description = row['generated_description']
    actual_description = row['actual_description']

    # yes_count = 0
    # no_count = 0
    # unclear_count = 0
    # result = [generated_description, actual_description, row['multiplicity']]
    # res = apiCaller.call_api(generated_description, actual_description,
    #                          format_string(inheritance_prompt1, row['multiplicity'], row['source'], row['target'],
    #                                        generated_description, actual_description, util.get_plural(row['target'])))

    result = [generated_description, actual_description]

    res = apiCaller.call_api(generated_description, actual_description,
                             format_string(inheritance_prompt1, row['source'], row['target'],
                                           statement1=generated_description, statement2=actual_description))
    result.append(res)
    domain_result.loc[len(domain_result)] = result

    response = res.replace('*', '').lower()
    if 'conclusion: yes' in response:
        # TODO specifically for inheritance contradiction
        data.loc[index, 'prediction'] = False
    elif 'conclusion: not sure' in response:
        data.loc[index, 'prediction'] = "not sure"
    elif 'conclusion: no' in response:
        # TODO specifically for inheritance contradiction
        data.loc[index, 'prediction'] = True
    else:
        data.loc[index, 'prediction'] = "not clear"

    # if res.startswith("Yes") or res.startswith("yes"):
    #     data.loc[index, 'prediction'] = True
    # elif res.startswith("No") or res.startswith("no"):
    #     data.loc[index, 'prediction'] = False
    # else:
    #     data.loc[index, 'prediction'] = "not clear"

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

data.to_csv(f"../test_contradiction_for_cardinality/relationship_results_gpt4o_inheritance_strategic_conquest.csv",
            index=False)
# relationship_map.to_csv(f"../{parent_folder}/contradiction-prompts-results-all-relationships.csv", index=False)
domain_result.to_csv(f"../test_contradiction_for_cardinality"
                     f"/relationship_results_detailed_inheritance_strategic_conquest.csv", index=False)
