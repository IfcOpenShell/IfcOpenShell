def get_primitive_type(attribute_or_data_type):
    if hasattr(attribute_or_data_type, "type_of_attribute"):
        data_type = str(attribute_or_data_type.type_of_attribute())
    else:
        data_type = str(attribute_or_data_type)
    if "<select" in data_type:
        return "select"
    elif "<list" in data_type:
        return ("list", get_primitive_type(data_type.replace("<list", "")))
    elif "<entity" in data_type:
        return "entity"
    elif "<string>" in data_type:
        return "string"
    elif "<real>" in data_type:
        return "float"
    elif "<number>" in data_type or "<integer>" in data_type:
        return "integer"
    elif "<boolean>" in data_type or "<logical>" in data_type:
        return "boolean"
    elif "<enumeration" in data_type:
        return "enum"


def get_enum_items(attribute):
    return attribute.type_of_attribute().declared_type().enumeration_items()


def get_select_items(attribute):
    return attribute.type_of_attribute().declared_type().select_list()
