description_file_path = "D:\\Thesis\\modelling-assistant\\test\\actual-description\\factory"


class DescriptionReader:
    def __init__(self):
        self.actual_description = ""

    def get_actual_description(self):
        with open(description_file_path, 'r') as file:
            content = file.read()

        local_vars = {}

        exec(content, local_vars)

        self.actual_description = local_vars.get('description', "")
        return self.actual_description

