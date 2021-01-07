import ifcopenshell
import blenderbim.bim.schema # TODO: refactor elsewhere
from blenderbim.bim.ifc import IfcStore


class Data:
    products = {}
    psets = {}

    @classmethod
    def load(cls, product_id):
        file = IfcStore.get_file()
        if not file:
            return
        product = file.by_id(product_id)
        cls.products[product_id] = set()
        if product.is_a("IfcElementType"):
            cls.add_type_product_psets(product, product_id)
        else:
            cls.add_product_psets(product, product_id)

    @classmethod
    def add_type_product_psets(cls, product, product_id):
        if not hasattr(product, "HasPropertySets") or not product.HasPropertySets:
            return # TODO
        for definition in product.HasPropertySets:
            if definition.is_a("IfcPropertySet"):
                cls.add_pset(definition, product_id)

    @classmethod
    def add_product_psets(cls, product, product_id):
        if not hasattr(product, "IsDefinedBy") or not product.IsDefinedBy:
            return
        for definition in product.IsDefinedBy:
            if not definition.is_a("IfcRelDefinesByProperties"):
                continue
            if definition.RelatingPropertyDefinition.is_a("IfcPropertySet"):
                cls.add_pset(definition.RelatingPropertyDefinition, product_id)

    @classmethod
    def add_pset(cls, pset, product_id):
        new_pset = {
            "Name": pset.Name,
            "is_expanded": True,
            "Properties": []
        }
        cls.products[product_id].add(int(pset.id()))
        cls.psets[int(pset.id())] = new_pset
        pset_template = blenderbim.bim.schema.ifc.psetqto.get_by_name(pset.Name)
        if pset_template:
            for prop_template in pset_template.HasPropertyTemplates:
                if not prop_template.is_a("IfcSimplePropertyTemplate"):
                    continue # Other types not yet supported
                enum_items = []
                if prop_template.TemplateType == "P_SINGLEVALUE":
                    data_type = str(IfcStore.get_schema().declaration_by_name(prop_template.PrimaryMeasureType))
                elif prop_template.TemplateType == "P_ENUMERATEDVALUE":
                    data_type = "enum"
                    enum_items = [v.wrappedValue for v in prop_template.Enumerators.EnumerationValues]
                else:
                    continue # Other types not yet supported
                if "<string>" in data_type:
                    data_type = "string"
                elif "<real>" in data_type:
                    data_type = "float"
                elif "<integer>" in data_type:
                    data_type = "integer"
                elif "<boolean>" in data_type:
                    data_type = "boolean"
                elif "<enumeration" in data_type:
                    data_type = "enum"
                    enum_items = attribute.type_of_attribute().declared_type().enumeration_items()
                new_pset["Properties"].append({
                    "Name": prop_template.Name,
                    "value": None,
                    "type": data_type,
                    "enum_items": enum_items,
                    "is_null": True
                })
        try:
            if hasattr(pset, "HasProperties"):
                props = pset.HasProperties
            elif hasattr(pset, "Properties"): # For IfcMaterialProperties
                props = pset.Properties
        except:
            return # I've seen ArchiCAD produce invalid IFCs with empty data
        # Invalid IFC, but some vendors like Solidworks do this so we accomodate it
        if not props:
            return
        for prop in props:
            if prop.is_a("IfcPropertySingleValue") and prop.NominalValue:
                has_existing_prop = False
                for existing_prop in new_pset["Properties"]:
                    if existing_prop["Name"] == prop.Name:
                        if prop.NominalValue is None:
                            existing_prop["value"] = None
                        elif existing_prop["type"] == "string":
                            existing_prop["value"] = str(prop.NominalValue.wrappedValue)
                        elif existing_prop["type"] == "float":
                            existing_prop["value"] = float(prop.NominalValue.wrappedValue)
                        elif existing_prop["type"] == "integer":
                            existing_prop["value"] = int(prop.NominalValue.wrappedValue)
                        elif existing_prop["type"] == "boolean":
                            existing_prop["value"] = bool(prop.NominalValue.wrappedValue)
                        elif existing_prop["type"] == "enum":
                            existing_prop["value"] = str(prop.NominalValue.wrappedValue)
                        existing_prop["is_null"] = prop.NominalValue.wrappedValue is None
                        has_existing_prop = True
                        break
                if not has_existing_prop:
                    value = prop.NominalValue.wrappedValue
                    if isinstance(value, str):
                        data_type = "string"
                    elif isinstance(value, float):
                        data_type = "float"
                    elif isinstance(value, bool):
                        data_type = "boolean"
                    elif isinstance(value, int):
                        data_type = "integer"
                    else:
                        data_type = "string"
                        value = str(value)
                    new_pset["Properties"].append({
                        "Name": prop.Name,
                        "value": value,
                        "type": data_type,
                        "enum_items": [],
                        "is_null": prop.NominalValue.wrappedValue is None
                    })
