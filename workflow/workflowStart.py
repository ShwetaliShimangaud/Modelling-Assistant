from equalityChecker import EqualityChecker
from contradictionChecker import ContradictionChecker


class WorkflowStart():
    def __init__(self, actual_description, domain_state):
        self.actual_description = actual_description
        self.generated_description = domain_state
        self.equality_checker = EqualityChecker()
        self.contradiction_checker = ContradictionChecker()

    def run(self):
        pass
        # Take actual and generated sentence Run all the checkers one by one. if result of any checker is true then
        # accordingly add it in warnings or errors array, Run next checker only if result of previous checker is false
