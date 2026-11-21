# IfcClash

IFC clash detection library to handle intersections, collisions, and clearance checks between building elements in IFC models.

## Features

- **Multiple detection modes**: intersection, collision, and clearance checking
- **Flexible clash sets**: Compare elements within a single model or between multiple IFC files
- **Smart grouping**: Automatically group related clashes
- **Export options**: Export clash results to BCF-XML or JSON formats
- **Element filtering**: Use selectors to specify which elements to check for clashes

## Stable JSON key order

Use `python -m ifcclash clashsets.json -o report.json --sort-keys` to sort JSON object
keys for easier report comparisons. In Python, set `settings.sort_json_keys = True`.
The option defaults to `False`, preserving the existing JSON serialization.

Sorting preserves every exported field, directed A/B pairs, p1/p2, numeric values,
and array positions. Reports with identical values and array order receive the
same key order; the option concerns serialization of the computed clash results.
