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

### validate

Check the model for schema and constraint violations.

```bash
ifcquery model.ifc validate
ifcquery model.ifc validate --rules
```

Options:

- `--rules` -- also run the slower EXPRESS rules check (default: off)

```json
{
  "valid": true,
  "issues": []
}
```

On an invalid model:

```json
{
  "valid": false,
  "issues": [
    {"level": "ERROR", "message": "Entity #42 IfcWall.GlobalId is not a valid IfcGloballyUniqueId"}
  ]
}
```

### schedule

List all work schedules and their task trees from the model.

```bash
ifcquery model.ifc schedule
ifcquery model.ifc schedule --depth 1
```

Options:

- `--depth N` -- expand at most N levels of subtasks (default: unlimited). At the
  cutoff, `subtasks` is replaced with `{"truncated": true, "count": N}`.

```json
[
  {
    "id": 42,
    "name": "Construction Schedule",
    "predefined_type": "BASELINE",
    "tasks": [
      {
        "id": 55,
        "name": "Phase 1",
        "start": "2024-01-01T09:00:00",
        "finish": "2024-06-30T17:00:00",
        "is_milestone": false,
        "outputs": [{"id": 10, "type": "IfcWall", "name": "Wall A"}],
        "subtasks": [
          {"id": 56, "name": "Foundations", "start": null, "finish": null,
           "is_milestone": false, "outputs": [], "subtasks": []}
        ]
      }
    ]
  }
]
```

### cost

List all cost schedules and their cost item trees from the model.

```bash
ifcquery model.ifc cost
ifcquery model.ifc cost --depth 2
```

Options:

- `--depth N` -- expand at most N levels of subitems (default: unlimited). At the
  cutoff, `subitems` is replaced with `{"truncated": true, "count": N}`.

```json
[
  {
    "id": 100,
    "name": "Bill of Quantities",
    "predefined_type": "COSTPLAN",
    "items": [
      {
        "id": 110,
        "name": "Concrete Works",
        "values": [{"formula": "1200.00 = material(1200.0)", "category": "material"}],
        "subitems": [
          {"id": 111, "name": "Formwork", "values": [], "subitems": []}
        ]
      }
    ]
  }
]
```

### schema

Show IFC class documentation for any entity type, using the schema version of
the loaded model.

```bash
ifcquery model.ifc schema IfcWall
ifcquery model.ifc schema IfcBuildingStorey
```

```json
{
  "description": "The wall represents a vertical construction ...",
  "predefined_types": {"STANDARD": "A standard wall, extruded vertically ..."},
  "spec_url": "https://standards.buildingsmart.org/...",
  "attributes": {
    "Name": "Optional name for use by the participating software systems",
    "ObjectPlacement": "Placement of the product in space ..."
  }
}
```

Returns `{"error": "Unknown entity: Foo"}` for unrecognised types.

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
