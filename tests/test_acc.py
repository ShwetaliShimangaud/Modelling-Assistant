import unittest


def determine_answer(row):
    if row['equal']:
        return 'equality'
    elif row['contradiction']:
        return 'contradiction'
    elif row['inclusion']:
        return 'inclusion'
    else:
        return 'exact difference'


def test_accuracy():
    domain_name = "factory"
    import pandas as pd

    attributes_true_result = pd.read_csv(f"{domain_name}//Attributes map.csv")
    relationship_true_result = pd.read_csv(f"{domain_name}//Relationships map.csv")

    attributes_true_result['Final answer'] = attributes_true_result.apply(determine_answer, axis=1)
    relationship_true_result['Final answer'] = relationship_true_result.apply(determine_answer, axis=1)

    # GPT 3.5
    print("GPT 3.5 results -----")
    predicted_attributes_map = pd.read_csv(f"without-sentence-generator-results//{domain_name}-logs"
                                           f"//predicted_attributes_map.csv")
    predicted_relationships_map = pd.read_csv(
        f"without-sentence-generator-results//{domain_name}-logs//predicted_relationship_map.csv")

    predicted_attributes_map['Final answer'] = predicted_attributes_map.apply(determine_answer, axis=1)
    predicted_relationships_map['Final answer'] = predicted_relationships_map.apply(determine_answer, axis=1)

    # Equality check
    equality_check_accuracy_attributes = sum(true_label == pred_label for true_label, pred_label in
                                             zip(attributes_true_result['equal'],
                                                 predicted_attributes_map['equal'])) / len(
        attributes_true_result['equal'])

    equality_check_accuracy_relationships = sum(true_label == pred_label for true_label, pred_label in
                                                zip(relationship_true_result['equal'],
                                                    predicted_relationships_map['equal'])) / len(
        relationship_true_result['equal'])

    print("Equality check accuracy for attributes", equality_check_accuracy_attributes)
    print("Equality check accuracy for relationships", equality_check_accuracy_relationships)

    # Contradiction check
    contradiction_accuracy_attributes = sum(true_label == pred_label for true_label, pred_label in
                                            zip(attributes_true_result['contradiction'],
                                                predicted_attributes_map['contradiction'])) / len(
        attributes_true_result['contradiction'])
    contradiction_accuracy_relationships = sum(true_label == pred_label for true_label, pred_label in
                                               zip(relationship_true_result['contradiction'],
                                                   predicted_relationships_map['contradiction'])) / len(
        relationship_true_result['contradiction'])

    print("Contradiction accuracy for attributes", contradiction_accuracy_attributes)
    print("Contradiction accuracy for relationships", contradiction_accuracy_relationships)

    # Inclusion check
    inclusion_accuracy_attributes = sum(true_label == pred_label for true_label, pred_label in
                                        zip(attributes_true_result['inclusion'],
                                            predicted_attributes_map['inclusion'])) / len(
        attributes_true_result['inclusion'])
    inclusion_accuracy_relationships = sum(true_label == pred_label for true_label, pred_label in
                                           zip(relationship_true_result['inclusion'],
                                               predicted_relationships_map['inclusion'])) / len(
        relationship_true_result['inclusion'])

    print("Inclusion accuracy for attributes", inclusion_accuracy_attributes)
    print("Inclusion accuracy for relationships", inclusion_accuracy_relationships)

    final_accuracy_attributes = sum(true_label == pred_label for true_label, pred_label in
                                    zip(attributes_true_result['Final answer'],
                                        predicted_attributes_map['Final answer'])) / len(
        attributes_true_result['Final answer'])
    final_accuracy_relationships = sum(true_label == pred_label for true_label, pred_label in
                                       zip(relationship_true_result['Final answer'],
                                           predicted_relationships_map['Final answer'])) / len(
        relationship_true_result['Final answer'])

    print("Final accuracy for attributes", final_accuracy_attributes)
    print("Final accuracy for relationships", final_accuracy_relationships)

    # GPT 4
    print("GPT 4 results -----")
    predicted_attributes_map = pd.read_csv(f"without-sentence-generator-results//{domain_name}-logs-gpt4"
                                           f"//predicted_attributes_map.csv")
    predicted_relationships_map = pd.read_csv(
        f"without-sentence-generator-results//{domain_name}-logs-gpt4//predicted_relationship_map.csv")

    predicted_attributes_map['Final answer'] = predicted_attributes_map.apply(determine_answer, axis=1)
    predicted_relationships_map['Final answer'] = predicted_relationships_map.apply(determine_answer, axis=1)

    # Equality check
    equality_check_accuracy_attributes = sum(true_label == pred_label for true_label, pred_label in
                                             zip(attributes_true_result['equal'],
                                                 predicted_attributes_map['equal'])) / len(
        attributes_true_result['equal'])
    equality_check_accuracy_relationships = sum(true_label == pred_label for true_label, pred_label in
                                                zip(relationship_true_result['equal'],
                                                    predicted_relationships_map['equal'])) / len(
        relationship_true_result['equal'])

    print("Equality check accuracy for attributes", equality_check_accuracy_attributes)
    print("Equality check accuracy for relationships", equality_check_accuracy_relationships)

    # Contradiction check
    contradiction_accuracy_attributes = sum(true_label == pred_label for true_label, pred_label in
                                            zip(attributes_true_result['contradiction'],
                                                predicted_attributes_map['contradiction'])) / len(
        attributes_true_result['contradiction'])
    contradiction_accuracy_relationships = sum(true_label == pred_label for true_label, pred_label in
                                               zip(relationship_true_result['contradiction'],
                                                   predicted_relationships_map['contradiction'])) / len(
        relationship_true_result['contradiction'])

    print("Contradiction accuracy for attributes", contradiction_accuracy_attributes)
    print("Contradiction accuracy for relationships", contradiction_accuracy_relationships)

    # Inclusion check
    inclusion_accuracy_attributes = sum(true_label == pred_label for true_label, pred_label in
                                        zip(attributes_true_result['inclusion'],
                                            predicted_attributes_map['inclusion'])) / len(
        attributes_true_result['inclusion'])
    inclusion_accuracy_relationships = sum(true_label == pred_label for true_label, pred_label in
                                           zip(relationship_true_result['inclusion'],
                                               predicted_relationships_map['inclusion'])) / len(
        relationship_true_result['inclusion'])

    print("Inclusion accuracy for attributes", inclusion_accuracy_attributes)
    print("Inclusion accuracy for relationships", inclusion_accuracy_relationships)

    final_accuracy_attributes = sum(true_label == pred_label for true_label, pred_label in
                                    zip(attributes_true_result['Final answer'],
                                        predicted_attributes_map['Final answer'])) / len(
        attributes_true_result['Final answer'])
    final_accuracy_relationships = sum(true_label == pred_label for true_label, pred_label in
                                       zip(relationship_true_result['Final answer'],
                                           predicted_relationships_map['Final answer'])) / len(
        relationship_true_result['Final answer'])

    print("Final accuracy for attributes", final_accuracy_attributes)
    print("Final accuracy for relationships", final_accuracy_relationships)

    # Assertions
    # assert equality_check_accuracy_attributes == 1.0
    # assert equality_check_accuracy_relationships == 1.0
    #
    # assert contradiction_accuracy_attributes == 1.0
    # assert contradiction_accuracy_relationships == 1.0
    #
    # assert inclusion_accuracy_attributes == 1.0
    # assert inclusion_accuracy_relationships == 1.0