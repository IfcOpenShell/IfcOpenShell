import ifcopenshell
import blenderbim.bim.schema # TODO: refactor elsewhere
from blenderbim.bim.ifc import IfcStore


class Data:
    products = {}
    psets = {}
    qtos = {}

    @classmethod
    def load(cls, product_id):
        file = IfcStore.get_file()
        if not file:
            return
        product = file.by_id(product_id)
        cls.products[product_id] = {"psets": set(), "qtos": set()}
        if product.is_a("IfcElementType"):
            cls.add_type_product_psets(product, product_id)
        elif product.is_a("IfcMaterialDefinition"):
            cls.add_material_psets(product, product_id)
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
    def add_material_psets(cls, product, product_id):
        if not product.HasProperties:
            return
        for pset in product.HasProperties:
            cls.add_pset(pset, product_id)

    @classmethod
    def add_product_psets(cls, product, product_id):
        if not hasattr(product, "IsDefinedBy") or not product.IsDefinedBy:
            return
        for definition in product.IsDefinedBy:
            if not definition.is_a("IfcRelDefinesByProperties"):
                continue
            if definition.RelatingPropertyDefinition.is_a("IfcPropertySet"):
                cls.add_pset(definition.RelatingPropertyDefinition, product_id)
            elif definition.RelatingPropertyDefinition.is_a("IfcElementQuantity"):
                cls.add_qto(definition.RelatingPropertyDefinition, product_id)

    @classmethod
    def add_pset(cls, pset, product_id):
        new_pset = {
            "Name": pset.Name,
            "is_expanded": True,
            "Properties": cls.get_properties_from_template(pset.Name) or []
        }
        cls.products[product_id]["psets"].add(int(pset.id()))
        cls.psets[int(pset.id())] = new_pset
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

    @classmethod
    def add_qto(cls, qto, product_id):
        new_qto = {
            "Name": qto.Name,
            "is_expanded": True,
            "Properties": cls.get_properties_from_template(qto.Name) or []
        }
        cls.products[product_id]["qtos"].add(int(qto.id()))
        cls.qtos[int(qto.id())] = new_qto
        for prop in qto.Quantities or []:
            if prop.is_a("IfcPhysicalSimpleQuantity"):
                value = prop[3]
                has_existing_prop = False
                for existing_prop in new_qto["Properties"]:
                    if existing_prop["Name"] == prop.Name:
                        existing_prop["value"] = float(value)
                        existing_prop["is_null"] = value is None
                        has_existing_prop = True
                        break
                if not has_existing_prop:
                    new_qto["Properties"].append({
                        "Name": prop.Name,
                        "value": float(value),
                        "type": "float",
                        "enum_items": [],
                        "is_null": value is None
                    })

    @classmethod
    def get_properties_from_template(cls, name):
        template = blenderbim.bim.schema.ifc.psetqto.get_by_name(name)
        if not template:
            return
        properties = []
        for prop_template in template.HasPropertyTemplates:
            if not prop_template.is_a("IfcSimplePropertyTemplate"):
                continue # Other types not yet supported
            enum_items = []

            if prop_template.TemplateType == "P_SINGLEVALUE":
                try:
                    data_type = str(IfcStore.get_schema().declaration_by_name(prop_template.PrimaryMeasureType or "IfcLabel"))
                except:
                    # TODO: Occurs if the data type is something that exists in IFC4 and not in IFC2X3. To fully fix
                    # this we need to generate the IFC2X3 pset template definitions.
                    continue
            elif prop_template.TemplateType == "P_ENUMERATEDVALUE":
                data_type = "enum"
                enum_items = [v.wrappedValue for v in prop_template.Enumerators.EnumerationValues]
            elif prop_template.TemplateType in ["Q_LENGTH", "Q_AREA", "Q_VOLUME", "Q_WEIGHT", "Q_TIME"]:
                data_type = "float"
            elif prop_template.TemplateType == "Q_COUNT":
                data_type = "integer"
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
            properties.append({
                "Name": prop_template.Name,
                "value": None,
                "type": data_type,
                "enum_items": enum_items,
                "is_null": True
            })
        return properties
