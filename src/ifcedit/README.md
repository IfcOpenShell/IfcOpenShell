<!-- This file was generated with the assistance of an AI coding tool. -->
# ifcedit

A CLI wrapper that exposes all 350+ `ifcopenshell.api` mutation functions as
shell commands. Functions are auto-discovered at runtime via introspection --
no hardcoded list to maintain.

## Installation

```bash
pip install ifcedit
```

Requires `ifcopenshell`.

## Usage

```
ifcedit <command> [options] [--format json|text]
```

Three subcommands: `list` to discover functions, `docs` to read their
documentation, and `run` to execute them.

## Subcommands

### list

Discover available API modules and their functions.

**List all modules:**

```bash
ifcedit list
```

```json
[
  {
    "module": "root",
    "description": "Functions for creating project-level entities",
    "functions": ["create_entity", "remove_product", "copy_class"],
    "count": 3
  },
  {
    "module": "spatial",
    "description": "Functions for managing spatial relationships",
    "functions": ["assign_container", "unassign_container"],
    "count": 2
  }
]
```

**List functions in a module:**

```bash
ifcedit list root
```

```json
[
  {
    "name": "create_entity",
    "description": "Create an IFC entity with optional initial attributes",
    "params": [
      {"name": "ifc_class", "type": "str", "required": true},
      {"name": "name", "type": "Optional[str]"}
    ]
  }
]
```

### docs

Show full documentation for a specific function, including parameter
descriptions from docstrings and return type.

```bash
ifcedit docs root.create_entity
```

```json
{
  "module": "root",
  "function": "create_entity",
  "description": "Create an IFC entity with optional initial attributes",
  "long_description": "This function creates a new entity instance...",
  "params": [
    {
      "name": "ifc_class",
      "type": "str",
      "required": true,
      "description": "The IFC class name (e.g. 'IfcWall', 'IfcProject')"
    },
    {
      "name": "name",
      "type": "Optional[str]",
      "description": "Optional name attribute"
    }
  ],
  "return_type": "ifcopenshell.entity_instance",
  "return_description": "The newly created entity instance"
}
```

### run

Execute an API function against an IFC file. Parameters are passed as
`--key value` pairs after the function name.

```bash
ifcedit run model.ifc root.create_entity --ifc_class IfcWall --name "My Wall"
```

```json
{
  "ok": true,
  "result": {"id": 42, "type": "IfcWall", "name": "My Wall"}
}
```

**Options:**

- `-o, --output <path>` -- write to a different file instead of overwriting the input
- `--dry-run` -- validate parameters without executing or saving

```bash
# Save to a new file
ifcedit run model.ifc root.create_entity -o out.ifc --ifc_class IfcWall

# Validate without executing
ifcedit run model.ifc root.create_entity --dry-run --ifc_class IfcWall
```

Dry-run output shows the resolved parameters:

```json
{
  "ok": true,
  "dry_run": true,
  "module": "root",
  "function": "create_entity",
  "args": {"ifc_class": "IfcWall", "name": "My Wall"}
}
```

## Parameter type coercion

CLI strings are automatically converted to the types expected by each API
function, using the function's type annotations:

| Type | CLI input | Python value |
|------|-----------|--------------|
| `str` | `"hello"` | `"hello"` |
| `int` | `"42"` or `"#42"` | `42` |
| `float` | `"3.14"` | `3.14` |
| `bool` | `"true"`, `"1"`, `"yes"` | `True` |
| `Optional[X]` | `"none"` | `None` |
| `entity_instance` | `"42"` or `"#42"` | resolved from model by step ID |
| `list[entity_instance]` | `"5,6,7"` or `"[5, 6, 7]"` | list of resolved entities |
| `dict` | `'{"key": "val"}'` | parsed JSON object |
| `Literal["A", "B"]` | `"A"` | validated against allowed values |

## Examples

```bash
# Create a project
ifcedit run model.ifc root.create_entity --ifc_class IfcProject --name "My Project"

# Assign an element to a storey
ifcedit run model.ifc spatial.assign_container --products 10 --relating_structure 4

# Assign multiple elements at once
ifcedit run model.ifc aggregate.assign_object --products "5,6,7" --relating_object 1

# Add a property set
ifcedit run model.ifc pset.add_pset --product 10 --name "Pset_WallCommon"

# Edit properties
ifcedit run model.ifc pset.edit_pset --pset 15 \
    --properties '{"IsExternal": true, "FireRating": "2HR"}'
```

### foreach

Apply an API function to each element in a JSON array read from stdin.
`{field}` placeholders in argument values are substituted with fields from
each JSON object. The model is opened once and saved once regardless of how
many elements are processed.

```bash
ifcquery model.ifc select 'IfcWindow' | ifcedit foreach model.ifc root.remove_product --product '{id}'
```

```json
{"ok": true, "count": 36, "errors": []}
```

Placeholder tokens match the fields emitted by `ifcquery` — typically `{id}`,
`{type}`, and `{name}`:

```bash
ifcquery model.ifc select 'IfcDoor' | ifcedit foreach model.ifc attribute.edit_attributes \
    --product '{id}' --attributes '{"Name": "Door"}'
```

**Options:**

- `-o, --output <path>` -- write to a different file instead of overwriting the input

**Output:**

- `count` -- number of elements successfully processed
- `errors` -- list of per-element failures, each with `index`, `item`, and `error`; processing continues past errors

```json
{
  "ok": false,
  "count": 34,
  "errors": [
    {"index": 2, "item": {"id": 55, "type": "IfcWindow", "name": "W03"}, "error": "Entity #55 not found in model"}
  ]
}
```

Exit code is 1 if any element failed.

### quantify

Run quantity take-off (QTO) on an IFC file, computing physical measurements
(volume, area, length, count, weight) and writing them back as
`IfcElementQuantity` property sets. Uses `ifc5d` rules.

**List available rules:**

```bash
ifcedit quantify list
```

```json
[
  {"name": "IFC4QtoBaseQuantities"},
  {"name": "IFC4X3QtoBaseQuantities"}
]
```

**Run QTO on a file:**

```bash
ifcedit quantify run model.ifc IFC4QtoBaseQuantities
ifcedit quantify run model.ifc IFC4QtoBaseQuantities --selector IfcWall
ifcedit quantify run model.ifc IFC4QtoBaseQuantities -o model_qto.ifc
```

```json
{"ok": true, "rule": "IFC4QtoBaseQuantities", "elements_quantified": 42}
```

Options:

- `--selector <query>` -- ifcopenshell selector to restrict elements (default: all `IfcElement` and `IfcSpace`)
- `-o, --output <path>` -- write to a different file instead of overwriting the input

Note: `quantify run` writes geometry-based measurements and requires the
IfcOpenShell C++ geometry bindings for elements with computed quantities.

## Error handling

Errors are reported in the JSON response:

```json
{
  "ok": false,
  "error": "Entity #999 not found in model"
}
```

Exit code is 0 on success, 1 on error.

## Relationship to ifcquery

`ifcedit` and `ifcquery` are complementary tools:

- **ifcquery** reads and inspects IFC models (summary, tree, info, select, relations, clash, validate, schedule, cost, schema, contexts, materials, plot, render)
- **ifcedit** modifies IFC models by wrapping `ifcopenshell.api` functions, and runs QTO via `quantify`

A typical workflow: inspect with `ifcquery`, look up the right API function
with `ifcedit docs`, then apply changes with `ifcedit run`.

The two tools also compose directly in shell scripts. Use `ifcquery --format ids`
to feed a list of IDs into a `run` parameter, or pipe `ifcquery select` JSON
into `ifcedit foreach` to apply an operation to every matching element:

```bash
# Aggregate — pass all IDs as a list parameter
ifcedit run model.ifc spatial.unassign_container \
    --products "$(ifcquery model.ifc --format ids select 'IfcWall')"

# Fan-out — one operation per element, model opened and saved once
ifcquery model.ifc select 'IfcWindow' | ifcedit foreach model.ifc root.remove_product --product '{id}'
```

## License

LGPLv3+ -- see the IfcOpenShell project license.
