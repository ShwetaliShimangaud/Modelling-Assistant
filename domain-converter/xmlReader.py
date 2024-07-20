import xml.etree.ElementTree as ET

xml_file_path = 'Bank.domain_model.cdm'

# Parse the XML file
tree = ET.parse(xml_file_path)
root = tree.getroot()

# Extract namespaces
namespaces = {
    'classdiagram': 'http://cs.mcgill.ca/sel/cdm/1.0',
    'xmi': 'http://www.omg.org/XMI',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
}

xsi_id = '{http://www.w3.org/2001/XMLSchema-instance}type'
xmi_id = '{http://www.omg.org/XMI}id'

class_attributes = {}
associations_map = {}
associations = []
attribute_types_map = {}
enums = {}

print("\nTypes:")
for type_elem in root.findall('types', namespaces):
    type_name = type_elem.get(xsi_id).split(':')[-1]
    type_name = type_name.split("CD")[-1]
    type_id = type_elem.get(xmi_id)
    # print(f"Type: {type_name}, Type ID: {type_id}")
    attribute_types_map[type_id] = type_name

    if type_name == "Enum":
        name = type_elem.get('name')
        constants = []
        for enum_type_elem in type_elem.findall('literals'):
            constant = enum_type_elem.get('name')
            constants.append(constant)

        enums[name] = constants

print(attribute_types_map)

print("\nEnums:")
print(enums)

# Extract classes and their attributes and associations
print("\nClasses and their attributes:")


def get_upper_bound(upper_bound):
    if upper_bound == '-1':
        return '*'
    else:
        return upper_bound


for class_elem in root.findall('classes', namespaces):
    class_name = class_elem.get('name')
    # print(f"Class: {class_name}")
    attributes_list = []
    for attr_elem in class_elem.findall('attributes', namespaces):
        attr_name = attr_elem.get('name')
        attr_type = attr_elem.get('type')
        # print(f"  Attribute: {attr_name}, Type: {attr_type}")
        attributes_list.append(attr_name + ":" + attribute_types_map[attr_type])
    class_attributes[class_name] = attributes_list
    for assoc_end_elem in class_elem.findall('associationEnds', namespaces):
        assoc_name = assoc_end_elem.get('name')
        lower_bound = assoc_end_elem.get('lowerBound')
        upper_bound = assoc_end_elem.get('upperBound')
        assoc_id = assoc_end_elem.get(xmi_id)
        # print(f"  Association: {assoc_name}, Association ID: {assoc_id}")

        if lower_bound is None and upper_bound is None:
            cardinality = ''
        elif lower_bound is not None:
            cardinality = lower_bound

            if upper_bound is not None:
                cardinality += '..' + get_upper_bound(upper_bound)

            if int(lower_bound) == 0 and upper_bound is None:
                cardinality += '..*'
        elif lower_bound is None:
            cardinality = '0..' + get_upper_bound(upper_bound)

        associations_map[assoc_id] = {
            'assoc_name': assoc_name,
            'cardinality': cardinality
        }

print(class_attributes)
# Extract types


# Extract associations
print("\nAssociations:")
for assoc_elem in root.findall('associations', namespaces):
    assoc_name = assoc_elem.get('name')
    assoc_ends = assoc_elem.get('ends')
    # print(f"Association: {assoc_name}, Ends: {assoc_ends}")
    class_names = assoc_name.split("_")
    assoc_ends = assoc_ends.split(" ")
    association = {
        'class1': class_names[0],
        'class2': class_names[1],
        'role_class1': associations_map[assoc_ends[1]]['assoc_name'],
        'role_class2': associations_map[assoc_ends[0]]['assoc_name'],
        'cardinality_class1': associations_map[assoc_ends[1]]['cardinality'],
        'cardinality_class2': associations_map[assoc_ends[0]]['cardinality']
    }
    associations.append(association)

print(associations)
