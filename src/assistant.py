from descriptionReader import DescriptionReader
from sentence_generator.descriptionGenerator import DescriptionGenerator
from workflow.workflowStart import WorkflowStart


class Assistant:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.description_reader = DescriptionReader()
        self.description_generator = DescriptionGenerator()

    def get_errors(self):
        return self.errors

    def get_warnings(self):
        return self.warnings

    def run(self):
        actual_description = self.description_reader.get_actual_description()
        # TODO : Create a map where you will store generated description of each class against it's attributes and
        #  relationships.
        domain_state = self.description_generator.get_description()
        workflow = WorkflowStart(actual_description, domain_state)
        self.warnings, self.errors = workflow.run()

