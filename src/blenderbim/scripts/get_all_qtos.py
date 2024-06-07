import json
import ifcopenshell.util.pset
import ifcopenshell.util.type


def order_dict(dictionary):
    # https://stackoverflow.com/questions/22721579/sorting-a-nested-ordereddict-by-key-recursively
    return {k: order_dict(v) if isinstance(v, dict) else v for k, v in sorted(dictionary.items())}


results = {}

psetqto = ifcopenshell.util.pset.get_template("IFC4")
for template in psetqto.templates:
    for pset_template in template.by_type("IfcPropertySetTemplate"):
        if not pset_template.Name.startswith("Qto_"):
            continue
        query = pset_template.ApplicableEntity
        results.setdefault(query, {})
        results[query].setdefault(pset_template.Name, {})
        for quantity in pset_template.HasPropertyTemplates:
            results[query][pset_template.Name][quantity.Name] = None

results = order_dict(results)
print(results)
with open("results.json", "w") as f:
    json.dump(results, f, indent=4)
