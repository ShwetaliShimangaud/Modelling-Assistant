from equalityChecker import EqualityChecker
from contradictionChecker import ContradictionChecker
from containmentChecker import ContainmentChecker
from differenceFinder import DifferenceFinder


class WorkflowStart:
    def __init__(self, actual_description, domain_state):
        self.actual_description = actual_description
        self.generated_description = domain_state
        self.equality_checker = EqualityChecker()
        self.contradiction_checker = ContradictionChecker()
        self.containment_checker = ContainmentChecker()
        self.difference_finder = DifferenceFinder()

    def run(self):
        # Take actual and generated sentence Run all the checkers one by one. if result of any checker is true then
        # accordingly add it in warnings or errors array, Run next checker only if result of previous checker is false
        warnings = []
        errors = []
        for i in enumerate(self.actual_description):
            # TODO Check whether this can be list or dict
            sentence1 = self.actual_description[i]
            sentence2 = self.generated_description[i]

            if self.equality_checker.run(sentence1, sentence2):
                print("Semantically equal")

            elif self.contradiction_checker.run(sentence1, sentence2):
                print("Contradictory")
                # TODO Add exact class/attribute/relationship error
                errors.append("Error")

            elif self.containment_checker.run(sentence1, sentence2):
                print("Containment")
                errors.append("Actual description is more generic than modelled system")
                warnings.append("warning")

            else:
                difference = self.difference_finder.run(sentence1, sentence2)
                errors.append(difference)

        return warnings, errors
