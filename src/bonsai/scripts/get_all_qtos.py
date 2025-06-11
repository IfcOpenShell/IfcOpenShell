"""Update ifc5d json files with qtos from the provided pset templates path."""

import json
import ifcopenshell.util.pset
import ifcopenshell.util.type
import ifc5d
from collections import defaultdict
from pathlib import Path
from typing import Union


def order_dict(dictionary):
    # https://stackoverflow.com/questions/22721579/sorting-a-nested-ordereddict-by-key-recursively
    return {k: order_dict(v) if isinstance(v, dict) else v for k, v in sorted(dictionary.items())}


PSET_TEMPLATES_FOLDER = Path(ifcopenshell.util.__file__).parent / "schema"
JSON_FOLDER = Path(ifc5d.__file__).parent
QueriesData = dict[str, dict[str, dict[str, Union[str, None]]]]


def main() -> None:
    # Update IFC4X3 json files from pset templates.
    update_json_with_qtos_from_template_file(
        JSON_FOLDER / "IFC4X3QtoBaseQuantities.json", PSET_TEMPLATES_FOLDER / "Pset_IFC4X3.ifc"
    )
    update_json_with_qtos_from_template_file(
        JSON_FOLDER / "IFC4X3QtoBaseQuantitiesBlender.json", PSET_TEMPLATES_FOLDER / "Pset_IFC4X3.ifc"
    )
    # Reuse methods defined in IFC4 in IFC4X3 calculators.
    reuse_methods_from_other_json_file(
        JSON_FOLDER / "IFC4QtoBaseQuantities.json", JSON_FOLDER / "IFC4X3QtoBaseQuantities.json"
    )
    reuse_methods_from_other_json_file(
        JSON_FOLDER / "IFC4QtoBaseQuantitiesBlender.json", JSON_FOLDER / "IFC4X3QtoBaseQuantitiesBlender.json"
    )


def update_json_with_qtos_from_template_file(json_filepath: Path, ifc_filepath: Path) -> None:
    """Add missing qtos and properties to the json file from the provided pset template file."""
    qto_templates: dict[str, list[ifcopenshell.entity_instance]] = defaultdict(list)
    qto_props: dict[str, set[str]] = defaultdict(set)
    ifc_file: ifcopenshell.file
    ifc_file = ifcopenshell.open(ifc_filepath)
    for template in ifc_file.by_type("IfcPropertySetTemplate"):
        template_name = template.Name
        if not template_name.startswith("Qto_"):
            continue
        qto_templates[template_name].append(template)
        for prop in template.HasPropertyTemplates:
            qto_props[template_name].add(prop.Name)

    qto_base_quantities_data = json.loads(json_filepath.read_text())

    calculator_queries_data: QueriesData
    added_qtos: set[str] = set()

    for calculator, calculator_queries_data in qto_base_quantities_data["calculators"].items():
        # Gather all supported QTOs.
        calculator_supported_qtos: set[str] = set()
        for selector_query, query_qtos_data in calculator_queries_data.items():
            for qto_name in query_qtos_data:
                calculator_supported_qtos.add(qto_name)

        # Check for missing QTOs.
        for template_name in qto_templates:
            template = qto_templates[template_name][0]

            applicable_entity_value: str
            applicable_entity_value = template.ApplicableEntity
            applicable_entities = ifcopenshell.util.pset.parse_applicable_entity(applicable_entity_value)

            selector_query = ifcopenshell.util.pset.convert_applicable_entities_to_query(applicable_entities)
            # Add missing selector queries and qtos.
            query_qtos_data = calculator_queries_data.setdefault(selector_query, {})
            qto_props_data = query_qtos_data.setdefault(template_name, {})

            # Add missing properties.
            for prop_name in qto_props[template_name]:
                if prop_name in qto_props_data:
                    continue
                qto_props_data[prop_name] = None
                added_qtos.add(template_name)

        if not added_qtos:
            print(f"No Qtos updates for calculator '{calculator}'.")
            continue

        # Sort dict alphabetically to keep it looking nice.
        # Don't sort the entire json to keep the header structure.
        qto_base_quantities_data["calculators"][calculator] = order_dict(calculator_queries_data)
        print(f"Added Qtos for {calculator}: {added_qtos}")
        json_filepath.write_text(json.dumps(qto_base_quantities_data, indent=4) + "\n")


def reuse_methods_from_other_json_file(json_source_filepath: Path, json_target_filepath: Path) -> None:
    json_source_data = json.loads(json_source_filepath.read_text())
    json_target_data = json.loads(json_target_filepath.read_text())
    queries_data: QueriesData
    queries_data_target: QueriesData
    for calculator, queries_data in json_source_data["calculators"].items():
        for selector_query, query_qtos_data in queries_data.items():
            queries_data_target = json_target_data["calculators"][calculator]
            # Don't match exactly since queries between IFC4 and IFC4X3 are not in sync currently.
            target_query = next((q for q in queries_data_target if q.startswith(selector_query)), None)
            if target_query is None:
                continue
            query_qtos_data_target = queries_data_target[target_query]
            for qto_name in query_qtos_data:
                if qto_name not in query_qtos_data_target:
                    continue
                props_data = query_qtos_data[qto_name]
                props_data_target = query_qtos_data_target[qto_name]
                for prop_name in props_data:
                    if prop_name not in props_data_target:
                        continue
                    props_data_target[prop_name] = props_data[prop_name]

    json_target_filepath.write_text(json.dumps(json_target_data, indent=4) + "\n")


if __name__ == "__main__":
    main()
