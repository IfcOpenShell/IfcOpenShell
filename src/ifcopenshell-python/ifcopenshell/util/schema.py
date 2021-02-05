import os
import json
import time
import ifcopenshell

# This is highly experimental and incomplete, however, it may work for simple datasets.
# In this simple implementation, we only support 2X3<->4 right now

cwd = os.path.dirname(os.path.realpath(__file__))


def is_a(entity, ifc_class):
    ifc_class = ifc_class.lower()
    if entity.name_lc() == ifc_class:
        return True
    if entity.supertype():
        return is_a(entity.supertype(), ifc_class)
    return False


def reassign_class(ifc_file, element, new_class):
    try:
        new_element = ifc_file.create_entity(new_class)
    except:
        print(f"Class of {element} could not be changed to {new_class}")
        return element
    new_attributes = [new_element.attribute_name(i) for i, attribute in enumerate(new_element)]
    for i, attribute in enumerate(element):
        try:
            new_element[new_attributes.index(element.attribute_name(i))] = attribute
        except:
            continue
    for inverse in ifc_file.get_inverse(element):
        ifcopenshell.util.element.replace_attribute(inverse, element, new_element)
    ifc_file.remove(element)
    return new_element



class Migrator:
    def __init__(self):
        self.migrated_ids = {}
        self.class_4_to_2x3 = json.load(open(os.path.join(cwd, "class_4_to_2x3.json"), "r"))

        # IFC4 classes, and their IFC4 attribute : IFC2X3 attributes
        self.attribute_4_to_2x3 = json.load(open(os.path.join(cwd, "attribute_4_to_2x3.json"), "r"))

        self.default_values = {
            "ChangeAction": "NOCHANGE",
            "CompositionType": "ELEMENT",
            "CrossSectionArea": 1,
            "DataValue": 0,
            "DefinedValues": [0],
            "DefiningValues": [0],
            "DestabilizingLoad": False,
            "Edition": "",
            "EndParam": 1.0,
            "EnumerationValues": [0],
            "GeodeticDatum": "",
            "Intent": "",
            "IsHeading": False,
            "ListValues": [0],
            "LongitudinalBarCrossSectionArea": 1,
            "LongitudinalBarNominalDiameter": 1,
            "LongitudinalBarSpacing": 1,
            "Name": "",
            "NominalDiameter": 1,
            "PredefinedType": "NOTDEFINED",
            "RowCells": [0],
            "SequenceType": "NOTDEFINED",
            "Source": "",
            "StartParam": 0.0,
            "TransverseBarCrossSectionArea": 1,
            "TransverseBarNominalDiameter": 1,
            "TransverseBarSpacing": 1,
            # Manual additions from experience
            "InteriorOrExteriorSpace": "NOTDEFINED",
        }
        self.default_entities = {
            "CurrentValue": None,
            "DepreciatedValue": None,
            "Jurisdiction": None,
            "OriginalValue": None,
            "Owner": None,
            "OwnerHistory": None,
            "Position": None,
            "PropertyReference": None,
            "RepresentationContexts": None,
            "ResponsiblePerson": None,
            "ResponsiblePersons": None,
            "Rows": None,
            "TotalReplacementCost": None,
            "UnitsInContext": None,
            "User": None,
        }

    def migrate(self, element, new_file):
        try:
            return new_file.by_id(self.migrated_ids[element.id()])
        except:
            pass
        # print("Migrating", element)
        schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(new_file.schema)
        new_element = self.migrate_class(element, new_file)
        # print("Migrated class from {} to {}".format(element, new_element))
        new_element_schema = schema.declaration_by_name(new_element.is_a())
        if not hasattr(new_element_schema, "all_attributes"):
            return element  # The element has no attributes, so migration is done
        new_element = self.migrate_attributes(element, new_file, new_element, new_element_schema)
        self.migrated_ids[element.id()] = new_element.id()
        return new_element

    def migrate_class(self, element, new_file):
        try:
            new_element = new_file.create_entity(element.is_a())
        except:
            # The element does not exist in this schema
            # Complex migration is not yet supported (e.g. polygonal face set to faceted brep)
            if new_file.schema == "IFC2X3":
                new_element = new_file.create_entity(self.class_4_to_2x3[element.is_a()])
            elif new_file.schema == "IFC4":
                print("Class migration to IFC4 not yet supported for", element)
                pass
        return new_element

    def migrate_attributes(self, element, new_file, new_element, new_element_schema):
        for i, attribute in enumerate(new_element_schema.all_attributes()):
            if new_element_schema.derived()[i]:
                continue
            self.migrate_attribute(attribute, element, new_file, new_element, new_element_schema)
        return new_element

    def migrate_attribute(self, attribute, element, new_file, new_element, new_element_schema):
        # print("Migrating attribute", element, new_element, attribute.name())
        if hasattr(element, attribute.name()):
            value = getattr(element, attribute.name())
            # print("Attribute names matched", value)
        elif new_file.schema == "IFC2X3":
            # IFC4 to IFC2X3: We know the IFC2X3 attribute name, but not its IFC4 equivalent
            # print("Searching for an equivalent", new_element, attribute.name())
            try:
                equivalent_map = self.attribute_4_to_2x3[new_element.is_a()]
                equivalent = list(equivalent_map.keys())[list(equivalent_map.values()).index(attribute.name())]
                if hasattr(element, equivalent):
                    # print("Equivalent found", equivalent)
                    value = getattr(element, equivalent)
                else:
                    return
            except:
                print(
                    "Unable to find equivalent attribute of {} to migrate from {} to {}".format(
                        attribute.name(), element, new_element
                    )
                )
                return  # We tried our best
        elif new_file.schema == "IFC4":
            # IFC2X3 to IFC4: We know the IFC4 attribute name, but not its IFC2X3 equivalent
            # print("Searching for an equivalent", element, new_element, attribute.name())
            try:
                equivalent = self.attribute_4_to_2x3[new_element.is_a()][attribute.name()]
                # print("Searching for equivalent", equivalent)
                if hasattr(element, equivalent):
                    value = getattr(element, equivalent)
                else:
                    return
            except:
                print(
                    "Unable to find equivalent attribute of {} to migrate from {} to {}".format(
                        attribute.name(), element, new_element
                    )
                )
                return  # We tried our best

        # print("Continuing migration of {} to migrate from {} to {}".format(attribute.name(), element, new_element))
        if value is None and not attribute.optional():
            value = self.generate_default_value(attribute, new_file)
            if value is None:
                print("Failed to generate default value for {} on {}".format(attribute.name(), element))
        elif isinstance(value, ifcopenshell.entity_instance):
            value = self.migrate(value, new_file)
        elif isinstance(value, (list, tuple)):
            if value and isinstance(value[0], ifcopenshell.entity_instance):
                new_value = []
                for item in value:
                    new_value.append(self.migrate(item, new_file))
                value = new_value
        setattr(new_element, attribute.name(), value)

    def generate_default_value(self, attribute, new_file):
        if attribute.name() in self.default_values:
            return self.default_values[attribute.name()]
        elif self.default_entities[attribute.name()]:
            return self.default_entities[attribute.name()]
        elif attribute.name() == "OwnerHistory":
            self.default_entities[attribute.name()] = new_file.create_entity(
                "IfcOwnerHistory",
                **{
                    "OwningUser": new_file.create_entity(
                        "IfcPersonAndOrganization",
                        **{
                            "ThePerson": new_file.create_entity("IfcPerson"),
                            "TheOrganization": new_file.create_entity(
                                "IfcOrganization", **{"Name": "IfcOpenShell Migrator"}
                            ),
                        }
                    ),
                    "OwningApplication": new_file.create_entity(
                        "IfcApplication",
                        **{
                            "ApplicationDeveloper": new_file.create_entity(
                                "IfcOrganization", **{"Name": "IfcOpenShell Migrator"}
                            ),
                            "Version": "Works for me",
                            "ApplicationFullName": "IfcOpenShell Migrator",
                            "ApplicationIdentifier": "IfcOpenShell Migrator",
                        }
                    ),
                    "ChangeAction": "NOCHANGE",
                    "CreationDate": int(time.time()),
                }
            )
        return self.default_entities[attribute.name()]
