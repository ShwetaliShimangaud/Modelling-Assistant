from src.assistant import Assistant
import pandas as pd


def test_equality_check():
    domain_name = "bank"
    assistant = Assistant(domain_name)
    assistant.run()

    print(assistant.attributes_map)
    print(assistant.relationships_map)

    attributes_true_result = pd.read_csv(f"{domain_name}//Attributes map.csv")
    relationship_true_result = pd.read_csv(f"{domain_name}//Relationships map.csv")

    # Here the assumption is that fields and relationships will come in same order

    # Equality check
    equality_check_accuracy_attributes = sum(true_label == pred_label for true_label, pred_label in
                                             zip(attributes_true_result['equal'],
                                                 assistant.attributes_map['equal'])) / len(
        attributes_true_result['equal'])
    equality_check_accuracy_relationships = sum(true_label == pred_label for true_label, pred_label in
                                                zip(relationship_true_result['equal'],
                                                    assistant.relationships_map['equal'])) / len(
        relationship_true_result['equal'])

    print("Equality check accuracy for attributes", equality_check_accuracy_attributes)
    print("Equality check accuracy for relationships", equality_check_accuracy_relationships)

    # Contradiction check
    contradiction_accuracy_attributes = sum(true_label == pred_label for true_label, pred_label in
                                            zip(attributes_true_result['contradiction'],
                                                assistant.attributes_map['contradiction'])) / len(
        attributes_true_result['contradiction'])
    contradiction_accuracy_relationships = sum(true_label == pred_label for true_label, pred_label in
                                               zip(relationship_true_result['contradiction'],
                                                   assistant.relationships_map['contradiction'])) / len(
        relationship_true_result['contradiction'])

    print("Contradiction accuracy for attributes", contradiction_accuracy_attributes)
    print("Contradiction accuracy for relationships", contradiction_accuracy_relationships)

    # Inclusion check
    inclusion_accuracy_attributes = sum(true_label == pred_label for true_label, pred_label in
                                        zip(attributes_true_result['inclusion'],
                                            assistant.attributes_map['inclusion'])) / len(
        attributes_true_result['inclusion'])
    inclusion_accuracy_relationships = sum(true_label == pred_label for true_label, pred_label in
                                           zip(relationship_true_result['inclusion'],
                                               assistant.relationships_map['inclusion'])) / len(
        relationship_true_result['inclusion'])

    print("Inclusion accuracy for attributes", inclusion_accuracy_attributes)
    print("Inclusion accuracy for relationships", inclusion_accuracy_relationships)

    # Assertions
    assert equality_check_accuracy_attributes == 1.0
    assert equality_check_accuracy_relationships == 1.0

    assert contradiction_accuracy_attributes == 1.0
    assert contradiction_accuracy_relationships == 1.0

    assert inclusion_accuracy_attributes == 1.0
    assert inclusion_accuracy_relationships == 1.0
