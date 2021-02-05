import json
import ifcopenshell
import ifcopenshell.util.selector

with open("../ifcblenderexport/blenderbim/bim/schema/entity_descriptions.json") as f:
    entity_descriptions = json.load(f)
with open("../ifcblenderexport/blenderbim/bim/schema/enum_descriptions.json") as f:
    enum_descriptions = json.load(f)

print('{|class="wikitable"')
print("! IFC Class")
print("! Predefined Type")


def print_entity(entity):
    print("|-")
    print("| " + entity.name())
    print("| ")
    if entity.name() in entity_descriptions:
        print(
            "{} ... [https://standards.buildingsmart.org/IFC/DEV/IFC4_3/RC1/HTML/link/{}.htm read more]".format(
                entity_descriptions[entity.name()], entity.name().lower()
            )
        )
    else:
        print(
            "No description provided ... [https://standards.buildingsmart.org/IFC/DEV/IFC4_3/RC1/HTML/link/{}.htm read more]".format(
                entity_descriptions[entity.name()], entity.name().lower()
            )
        )
    for attribute in entity.attributes():
        if attribute.name() == "PredefinedType":
            enum = attribute.type_of_attribute().declared_type()
            print("\nThe following predefined types are defined:\n")
            for item in enum.enumeration_items():
                # print('|-')
                # print('| ' + entity.name())
                # print('| ' + item)
                if enum.name() in enum_descriptions and item in enum_descriptions[enum.name()]:
                    print(
                        "* '''{}''' - {} ... [https://standards.buildingsmart.org/IFC/DEV/IFC4_3/RC1/HTML/link/{}.htm read more]".format(
                            item, enum_descriptions[enum.name()][item], enum.name().lower()
                        )
                    )
                else:
                    print(
                        "* '''{}''' - No description provided ... [https://standards.buildingsmart.org/IFC/DEV/IFC4_3/RC1/HTML/link/{}.htm read more]".format(
                            item, enum.name().lower()
                        )
                    )

    for subtype in entity.subtypes():
        print_entity(subtype)


for asset in ifcopenshell.util.selector.cobie_component_assets:
    schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name("IFC4")
    print_entity(schema.declaration_by_name(asset))

print("|}")
