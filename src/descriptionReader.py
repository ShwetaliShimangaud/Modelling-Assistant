
description_file_path = "D:\\Thesis\\modelling-assistant\\tests\\actual-description\\"


class DescriptionReader:
    def __init__(self, domain_name):
        self.actual_description = ""
        self.domain_name = domain_name

    def get_actual_description(self):
        with open(description_file_path+self.domain_name, 'r') as file:
            content = file.read()

        local_vars = {}

        exec(content, local_vars)

        self.actual_description = local_vars.get('description', "")
        return self.actual_description
