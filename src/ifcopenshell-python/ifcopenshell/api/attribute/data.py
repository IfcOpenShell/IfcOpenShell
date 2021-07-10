import ifcopenshell
import ifcopenshell.util.attribute


class Data:
    products = {}

    @classmethod
    def purge(cls):
        cls.products = {}

    @classmethod
    def load(cls, file, product_id):
        if not file:
            return
        product = file.by_id(product_id)
        schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(file.schema)
        cls.products[product_id] = []
        declaration = schema.declaration_by_name(product.is_a())
        for attribute in declaration.all_attributes():
            data_type = ifcopenshell.util.attribute.get_primitive_type(attribute)
            value = getattr(product, attribute.name())
            list_type = None
            enum_items = ()

            if isinstance(data_type, tuple):
                list_type = data_type[1]
                data_type = data_type[0]

            if data_type in ["entity", "list", "string", "enum"]:
                value = None if value is None else str(value)
            elif data_type == "float":
                value = None if value is None else float(value)
            elif data_type == "integer":
                value = None if value is None else int(value)

            if data_type == "enum":
                enum_items = ifcopenshell.util.attribute.get_enum_items(attribute)

            cls.products[product_id].append({
                "name": attribute.name(),
                "value": value,
                "type": data_type,
                "enum_items": enum_items,
                "list_type": list_type,
                "is_optional": attribute.optional(),
                "is_null": getattr(product, attribute.name()) is None
            })
