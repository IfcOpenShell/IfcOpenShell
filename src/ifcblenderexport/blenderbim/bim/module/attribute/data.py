import ifcopenshell
from blenderbim.bim.ifc import IfcStore


class Data:
    products = {}

    @classmethod
    def purge(cls):
        cls.products = {}

    @classmethod
    def load(cls, product_id):
        file = IfcStore.get_file()
        if not file:
            return
        product = file.by_id(product_id)
        cls.products[product_id] = []
        declaration = IfcStore.get_schema().declaration_by_name(product.is_a())
        for attribute in declaration.all_attributes():
            data_type = str(attribute.type_of_attribute())
            value = getattr(product, attribute.name())
            list_type = None
            enum_items = ()
            if "<entity" in data_type:
                data_type = "entity"
                value = None if value is None else str(value)
            elif "<list" in data_type:
                if "<entity" in data_type:
                    list_type = "entity"
                elif "<string>" in data_type:
                    list_type = "string"
                elif "<real>" in data_type:
                    list_type = "float"
                elif "<integer>" in data_type:
                    list_type = "integer"
                data_type = "list"
                value = None if value is None else str(value)
            elif "<string>" in data_type:
                data_type = "string"
                value = None if value is None else str(value)
            elif "<real>" in data_type:
                data_type = "float"
                value = None if value is None else float(value)
            elif "<integer>" in data_type:
                data_type = "integer"
                value = None if value is None else int(value)
            elif "<enumeration" in data_type:
                data_type = "enum"
                value = None if value is None else str(value)
                enum_items = attribute.type_of_attribute().declared_type().enumeration_items()
            cls.products[product_id].append({
                "name": attribute.name(),
                "value": value,
                "type": data_type,
                "enum_items": enum_items,
                "list_type": list_type,
                "is_optional": attribute.optional(),
                "is_null": getattr(product, attribute.name()) is None
            })
