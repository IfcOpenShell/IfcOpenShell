<!-- This file was generated with the assistance of an AI coding tool. -->
# ifcquery

A CLI tool for querying and inspecting IFC building models. All output is
structured JSON (or human-readable text), making it easy to pipe into other
tools or scripts.

## Installation

```bash
pip install ifcquery
```

Requires `ifcopenshell`. The `clash` subcommand additionally requires the
IfcOpenShell C++ geometry bindings (`ifcopenshell.geom`).

## Usage

```
ifcquery <ifc_file> <command> [options] [--format json|text]
```

The `--format` flag controls output. Default is `json`; use `text` for
indented human-readable output.

## Subcommands

### summary

Get a model overview: schema version, entity counts, and project info.

```bash
ifcquery model.ifc summary
```

```json
{
  "schema": "IFC4",
  "total_entities": 1847,
  "project": {
    "id": 1,
    "name": "Office Building",
    "description": null
  },
  "types": {
    "IfcWall": 42,
    "IfcSlab": 12,
    "IfcWindow": 36
  }
}
```

### tree

Display the spatial hierarchy from IfcProject down through sites, buildings,
storeys, and their contained elements.

```bash
ifcquery model.ifc tree
```

```json
{
  "id": 1,
  "type": "IfcProject",
  "name": "Office Building",
  "children": [
    {
      "id": 2,
      "type": "IfcSite",
      "name": "Default Site",
      "children": [
        {
          "id": 3,
          "type": "IfcBuilding",
          "name": "Main Building",
          "children": [
            {
              "id": 4,
              "type": "IfcBuildingStorey",
              "name": "Ground Floor",
              "elements": [
                {"id": 10, "type": "IfcWall", "name": "Wall001"},
                {"id": 11, "type": "IfcSlab", "name": "Floor001"}
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

### info

Get detailed information about a specific element by step ID.

```bash
ifcquery model.ifc info 10
ifcquery model.ifc info '#10'
```

Returns attributes, property sets, type relationship, material assignment,
spatial container, and placement matrix.

```json
{
  "id": 10,
  "type": "IfcWall",
  "attributes": {
    "Name": "Wall001",
    "Description": null,
    "ObjectType": "LOADBEARING"
  },
  "property_sets": {
    "Pset_WallCommon": {
      "IsExternal": true,
      "FireRating": "2HR"
    }
  },
  "element_type": {"id": 50, "type": "IfcWallType", "name": "Standard"},
  "material": {"id": 60, "type": "IfcMaterial", "name": "Concrete"},
  "container": {"id": 4, "type": "IfcBuildingStorey", "name": "Ground Floor"},
  "placement": [
    [1.0, 0.0, 0.0, 5.0],
    [0.0, 1.0, 0.0, 0.0],
    [0.0, 0.0, 1.0, 0.0],
    [0.0, 0.0, 0.0, 1.0]
  ]
}
```

### select

Filter elements using the ifcopenshell selector syntax.

```bash
ifcquery model.ifc select 'IfcWall'
ifcquery model.ifc select 'IfcWall, IfcSlab'
```

```json
[
  {"id": 10, "type": "IfcWall", "name": "Wall001"},
  {"id": 11, "type": "IfcWall", "name": "Wall002"},
  {"id": 20, "type": "IfcSlab", "name": "Floor001"}
]
```

Results are sorted by ID.

### relations

Show all relationships for an element, organized by category: hierarchy,
children, type relationships, groups, systems, material, and connections.

```bash
ifcquery model.ifc relations 10
```

```json
{
  "id": 10,
  "type": "IfcWall",
  "name": "Wall001",
  "hierarchy": {
    "parent": {"id": 4, "type": "IfcBuildingStorey", "name": "Ground Floor"},
    "container": {"id": 4, "type": "IfcBuildingStorey", "name": "Ground Floor"}
  },
  "children": {
    "openings": [{"id": 30, "type": "IfcOpeningElement", "name": "Opening01"}]
  },
  "type_relationship": {
    "type_of": {"id": 50, "type": "IfcWallType", "name": "Standard"}
  },
  "material": {"id": 60, "type": "IfcMaterial", "name": "Concrete"}
}
```

Empty categories are omitted from output.

Use `--traverse up` to walk the spatial hierarchy from the element up to
IfcProject:

```bash
ifcquery model.ifc relations 10 --traverse up
```

```json
[
  {"id": 10, "type": "IfcWall", "name": "Wall001"},
  {"id": 4, "type": "IfcBuildingStorey", "name": "Ground Floor"},
  {"id": 3, "type": "IfcBuilding", "name": "Main Building"},
  {"id": 2, "type": "IfcSite", "name": "Default Site"},
  {"id": 1, "type": "IfcProject", "name": "Office Building"}
]
```

### clash

Check a single element for geometric intersections and clearance violations
against other elements.

```bash
ifcquery model.ifc clash 10
ifcquery model.ifc clash 10 --clearance 0.5
ifcquery model.ifc clash 10 --scope all --tolerance 0.001
```

Options:

- `--clearance <meters>` -- minimum clearance distance to check
- `--tolerance <meters>` -- intersection tolerance (default: 0.002)
- `--scope {storey,all}` -- check against same-storey elements or all elements (default: storey)

```json
{
  "element": {"id": 10, "type": "IfcWall", "name": "Wall001"},
  "scope": "storey",
  "pass": false,
  "checks": {
    "intersection": {
      "pass": false,
      "tolerance": 0.002,
      "clashes": [
        {
          "element": {"id": 11, "type": "IfcWall", "name": "Wall002"},
          "type": "intersection",
          "distance": 0.0,
          "p1": [2.5, 2.5, 1.5],
          "p2": [2.5, 2.5, 1.5]
        }
      ]
    },
    "clearance": {
      "pass": true,
      "clearance": 0.5,
      "clashes": []
    }
  }
}
```

Requires the IfcOpenShell C++ geometry bindings.

## Error handling

Errors are written to stderr. Exit code is 0 on success, 1 on error.

## License

LGPLv3+ -- see the IfcOpenShell project license.
