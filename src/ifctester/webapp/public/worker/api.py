import ifcopenshell
import ifcopenshell.util
import ifcopenshell.util.attribute
import ifcopenshell.util.pset
import ifcopenshell.util.schema
import xml.etree.ElementTree as ET
from xmlschema.validators.exceptions import XMLSchemaValidationError
from ifctester.ids import Ids, IdsXmlValidationError, get_schema

# https://github.com/buildingSMART/IDS/blob/9914d568c7ac037acd97e58a0d16e9f93c3e3416/Schema/ids.xsd#L232
ifc_schemas = ["IFC2X3", "IFC4", "IFC4X3_ADD2"]


def get_predefined_types_for_entity(schema_name, entity_name):
    """Get a list of predefined types for a given entity."""

    schema = ifcopenshell.schema_by_name(schema_name)

    try:
        entity = schema.declaration_by_name(entity_name)
    except:
        return []

    if not entity or not entity.as_entity():
        print(f"Entity {entity_name} not found")
        return []

    entity = entity.as_entity()
    predefined_type_attr = None

    # Check all attributes for "PredefinedType"
    for attr in entity.all_attributes():
        if attr.name() == "PredefinedType":
            predefined_type_attr = attr
            break

    if not predefined_type_attr:
        return []

    param_type = predefined_type_attr.type_of_attribute()

    if param_type.as_named_type():
        enum_decl = param_type.as_named_type().declared_type()
        if enum_decl.as_enumeration_type():
            return enum_decl.as_enumeration_type().enumeration_items()

    return []


def get_all_entity_classes(schema_name):
    """Get all IFC entity classes in the given schema."""

    schema = ifcopenshell.schema_by_name(schema_name)
    entities = []

    for entity in schema.entities():
        entities.append(entity.name())

    # Sort alphabetically
    entities.sort()
    return entities


def get_all_data_types(schema_name):
    """Get all data types in the given schema."""

    schema = ifcopenshell.schema_by_name(schema_name)
    return {
        d.name(): ifcopenshell.util.attribute.get_primitive_type(d)
        for d in schema.declarations()
        if d.as_type_declaration()
    }


def get_entity_attributes(schema_name, entity_name):
    """Get all attributes for a given entity."""

    schema = ifcopenshell.schema_by_name(schema_name)

    try:
        entity = schema.declaration_by_name(entity_name)
    except:
        return []

    if not entity or not entity.as_entity():
        print(f"Entity {entity_name} not found")
        return []

    entity = entity.as_entity()
    attributes = []
    for attr in entity.all_attributes():
        attributes.append(
            {
                "name": attr.name(),
                # "type": attr.type_of_attribute() # TODO Types of attribute
            }
        )

    return attributes


def get_applicable_psets(schema_name, entity_name, predefined_type=""):
    """Get all applicable property and quantity sets for a given entity."""

    pset_qto = ifcopenshell.util.pset.PsetQto(schema_name)
    pset_names = pset_qto.get_applicable_names(entity_name, predefined_type)

    return pset_names


def get_all_psets(schema_name):
    """Get all property sets and quantity sets defined in an IFC schema"""

    pset_qto = ifcopenshell.util.pset.PsetQto(schema_name)
    result = {}

    for template_file in pset_qto.templates:
        for pset_template in template_file.by_type("IfcPropertySetTemplate"):
            pset_name = pset_template.Name
            properties = []

            # Get property templates for this pset
            if pset_template.HasPropertyTemplates:
                for prop_template in pset_template.HasPropertyTemplates:
                    prop_info = {
                        "name": prop_template.Name,
                        # "description": prop_template.Description
                    }

                    # Extract type information
                    if prop_template.is_a("IfcSimplePropertyTemplate"):
                        if prop_template.PrimaryMeasureType:
                            prop_info["type"] = prop_template.PrimaryMeasureType
                        else:
                            prop_info["type"] = str(prop_template.TemplateType)
                    elif prop_template.is_a("IfcComplexPropertyTemplate"):
                        prop_info["type"] = None  # Complex properties are not supported
                    else:
                        prop_info["type"] = None

                    properties.append(prop_info)
            result[pset_name] = properties

    return result


def get_material_categories():
    return ["concrete", "steel", "aluminium", "block", "brick", "stone", "wood", "glass", "gypsum", "plastic", "earth"]


def get_standard_classification_systems():
    return {
        "BB/SfB (3/4 cijfers)": {"source": "Regie der Gebouwen", "tokens": ["."]},
        "BIMTypeCode": {"source": "BIMStockholm", "tokens": None},
        "Common Arrangement of Work Sections (CAWS)": {"source": "NBS", "tokens": ["/"]},
        "CBI Classification - Level 2": {"source": "Masterspec", "tokens": None},
        "CBI Classification - Level 4": {"source": "Masterspec", "tokens": None},
        "Rumsfunktionskoder CC001 - 001": {"source": "BIMAlliance", "tokens": ["-"]},
        "CCS": {"source": "Molio", "tokens": None},
        "CCTB": {"source": "CCT-Bâtiments", "tokens": ["."]},
        "Funktionskoder Regionservice CD001 - 001": {"source": "BIMAlliance", "tokens": None},
        "Rumsfunktion Blekinge CD002 - 001": {"source": "BIMAlliance", "tokens": None},
        "EcoQuaestor Codetabel": {"source": "EcoQuaestor", "tokens": [".", "-"]},
        "GuBIMclass CA": {"source": "GuBIMClass", "tokens": ["."]},
        "GuBIMclass ES": {"source": "GuBIMClass", "tokens": ["."]},
        "MasterFormat": {"source": "CSI", "tokens": [" ", "."]},
        "NATSPEC Worksections": {"source": "NATSPEC", "tokens": None},
        "NBS Create": {"source": "NBS", "tokens": ["_", "/"]},
        "NL/SfB (4 cijfers)": {"source": "BIMLoket", "tokens": ["."]},
        "NS 3451 - Bygningsdelstabell": {"source": "Standard Norge", "tokens": None},
        "OmniClass": {"source": "OmniClass", "tokens": ["-", " "]},
        "ÖNORM 6241-2": {"source": "freeBIM 2", "tokens": None},
        "RICS NRM1": {"source": "RICS", "tokens": ["."]},
        "RICS NRM3": {"source": "RICS", "tokens": ["."]},
        "SFG20": {"source": "SFG20", "tokens": ["-"]},
        "SINAPI": {"source": "Caixa", "tokens": ["/"]},
        "STABU-Element": {"source": "STABU", "tokens": ["."]},
        "TALO 2000 Building Component Classification": {"source": "Rakennustieto", "tokens": ["."]},
        "TALO 2000 Hankenimikkeistö": {"source": "Rakennustieto", "tokens": ["."]},
        "Uniclass": {"source": "RIBA Enterprises Ltd", "tokens": ["_"]},
        "Uniclass 2015": {"source": "RIBA Enterprises Ltd", "tokens": ["_"]},
        "UniFormat": {"source": "UniFormat", "tokens": ["."]},
        "Uniformat": {"source": "UniFormat", "tokens": ["."]},
        "VMSW": {"source": "VMSW", "tokens": ["."]},
    }


def ids_from_xml_string(xml: str, validate: bool = False) -> Ids:
    try:
        decode = get_schema().decode(
            xml, strip_namespaces=True, namespaces={"": "http://standards.buildingsmart.org/IDS"}
        )
    except XMLSchemaValidationError as e:
        raise IdsXmlValidationError(e, "Provided XML appears to be invalid. See details above.")
    return Ids().parse(decode)
