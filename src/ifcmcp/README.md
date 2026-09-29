<!-- This file was generated with the assistance of an AI coding tool. -->
# ifcmcp

An MCP (Model Context Protocol) server that wraps `ifcquery` and `ifcedit`,
holding the IFC model in memory across tool calls for fast interactive editing
sessions.

## Installation

```bash
pip install ifcopenshell-mcp
```

Requires `ifcopenshell`, `ifcquery`, and `ifcedit`. The `mcp` package is an optional dependency needed to run the server; install it with `pip install ifcopenshell-mcp[mcp]` or add `mcp` separately.

## Running the server

```bash
ifcmcp
```

This starts the server on stdio transport, suitable for use with Claude Code
or any MCP client.

### Claude Code configuration

Use the `claude mcp add` command:

```bash
claude mcp add --transport stdio ifc -- ifcmcp
```

Or create a `.mcp.json` file in your project root:

```json
{
  "mcpServers": {
    "ifc": {
      "type": "stdio",
      "command": "ifcmcp"
    }
  }
}
```

After adding the server, restart Claude Code for the tools to become available.
Then load a model by asking Claude to use `ifc_load`:

```
load model.ifc using ifc_load
```

## Tools

### Session

#### ifc_new

Create a new empty IFC model in memory, replacing any currently loaded model.

```
ifc_new()
ifc_new(schema="IFC4X3")
```

Default schema is `IFC4`.

#### ifc_load

Open an IFC file into memory.

```
ifc_load(path="/path/to/model.ifc")
-> "Loaded /path/to/model.ifc: schema IFC4, 1847 entities"
```

#### ifc_reset

Unload the current model from memory, freeing all session state.

```
ifc_reset()
```

#### ifc_save

Write the in-memory model to disk. Empty path overwrites the original file.

```
ifc_save()
ifc_save(path="/path/to/output.ifc")
```

### Query tools

All query tools require a model to be loaded first via `ifc_load`.

#### ifc_summary

Model overview: schema, entity counts, project info.

```json
{
  "schema": "IFC4",
  "total_entities": 1847,
  "project": {"id": 1, "name": "Office Building"},
  "types": {"IfcWall": 42, "IfcSlab": 12, "IfcWindow": 36}
}
```

#### ifc_tree

Full spatial hierarchy from IfcProject down through sites, buildings, storeys,
and contained elements.

```json
{
  "id": 1,
  "type": "IfcProject",
  "name": "Office Building",
  "children": [
    {
      "id": 2,
      "type": "IfcSite",
      "children": [{"id": 3, "type": "IfcBuilding", "children": ["..."]}]
    }
  ]
}
```

#### ifc_info

Deep inspection of an entity by step ID: attributes, property sets, type,
material, container, and 4x4 placement matrix.

```
ifc_info(element_id=10)
```

#### ifc_select

Filter elements using ifcopenshell selector syntax.

```
ifc_select(query="IfcWall")
ifc_select(query="IfcWindow")
```

Returns a sorted list of `{"id", "type", "name"}` references.

#### ifc_relations

Show all relationships for an element: hierarchy, children, type, groups,
systems, material, connections.

```
ifc_relations(element_id=10)
ifc_relations(element_id=10, traverse="up")
```

With `traverse="up"`, walks the hierarchy from element up to IfcProject.

#### ifc_contexts

List all geometric representation contexts and subcontexts in the loaded model.

```
ifc_contexts()
```

#### ifc_materials

List all materials and material sets in the loaded model, with their assigned elements.

```
ifc_materials()
```

#### ifc_clash

Check an element for geometric intersections and clearance violations.

```
ifc_clash(element_id=10)
ifc_clash(element_id=10, clearance=0.5, scope="all")
```

Parameters:

- `clearance` -- minimum clearance distance in meters (0.0 = no clearance check)
- `tolerance` -- intersection tolerance in meters (default: 0.002)
- `scope` -- `"storey"` or `"all"` (default: `"storey"`)

#### ifc_validate

Check the model for schema and constraint violations.

```
ifc_validate()
ifc_validate(express_rules=True)
```

Returns `{"valid": true, "issues": []}` or `{"valid": false, "issues": [{"level": "ERROR", "message": "..."}]}`.

#### ifc_schedule

List all work schedules and their nested task trees.

```
ifc_schedule()
ifc_schedule(max_depth=1)   # top-level phases only
```

`max_depth` limits subtask expansion. At the cutoff, `subtasks` is replaced
with `{"truncated": true, "count": N}` so you know children exist without
fetching them all. Omit for unlimited depth.

#### ifc_cost

List all cost schedules and their nested cost item trees.

```
ifc_cost()
ifc_cost(max_depth=2)   # top two levels of the BoQ
```

`max_depth` limits cost item expansion, same truncation convention as
`ifc_schedule`.

#### ifc_schema

Return IFC class documentation for any entity type, using the loaded model's
schema version.

```
ifc_schema(entity_type="IfcWall")
ifc_schema(entity_type="IfcBuildingStorey")
```

Returns description, predefined types, spec URL, and attribute descriptions.
Returns `{"error": "Unknown entity: Foo"}` for unrecognised types.

#### ifc_quantify

Run quantity take-off (QTO) on the loaded model using an `ifc5d` rule.
Computes physical measurements (volume, area, length, count, weight) and
writes them back as `IfcElementQuantity` property sets. Modifies the model
in-place -- call `ifc_save()` when done.

```
ifc_quantify(rule="IFC4QtoBaseQuantities")
ifc_quantify(rule="IFC4QtoBaseQuantities", selector="IfcWall")
```

Available rules: `IFC4QtoBaseQuantities`, `IFC4X3QtoBaseQuantities`.

`selector` is an optional ifcopenshell selector to restrict which elements
are quantified (default: all `IfcElement` and `IfcSpace`).

Returns `{"ok": true, "rule": "...", "elements_quantified": 42}`.

### Drawing and rendering tools

#### ifc_plot

Generate a 2D technical drawing of the loaded model and return it as an inline image.

```
ifc_plot()
ifc_plot(selector="IfcWall", view="floorplan", scale=0.01, output_path="/tmp/plan.svg")
ifc_plot(element_ids=[10, 11], view="floorplan")
```

Parameters:

- `selector` -- ifcopenshell selector to restrict plotted elements
- `element_ids` -- step IDs of elements to highlight; others are faded
- `view` -- `"floorplan"` (default), `"elevation"`, `"section"`, or `"auto"`
- `width_mm`, `height_mm` -- paper size in mm (default: 297 x 420)
- `scale` -- model-to-paper ratio (default: 0.01 = 1:100)
- `png_width`, `png_height` -- raster output size in pixels (default: 1024 x 1024)
- `output_path` -- optional path to also save to disk (`.svg` for vector, otherwise PNG)

Returns an inline PNG the LLM can inspect. Requires `ifcopenshell.draw`.

#### ifc_render

Render the loaded model to a 3D PNG image.

```
ifc_render()
ifc_render(selector="IfcWall", view="iso", output_path="/tmp/model.png")
ifc_render(element_ids=[10, 11], view="south")
```

Parameters:

- `selector` -- ifcopenshell selector to restrict rendered elements
- `element_ids` -- step IDs of elements to highlight; others are shown translucent
- `view` -- `"iso"` (default), `"top"`, `"south"`, `"north"`, `"east"`, or `"west"`
- `output_path` -- optional path to save the PNG to disk

Returns an inline PNG. Requires `pyvista` and the IfcOpenShell C++ geometry bindings.

### Shape builder tools

#### ifc_shape_list

List all available `ShapeBuilder` methods with brief descriptions.

```
ifc_shape_list()
```

#### ifc_shape_docs

Show full documentation for a specific `ShapeBuilder` method.

```
ifc_shape_docs(method="extrude")
ifc_shape_docs(method="create_ellipse")
```

#### ifc_shape

Execute a `ShapeBuilder` method on the loaded model.

```
ifc_shape(method="extrude", params='{"profile": "42", "magnitude": 3.0}')
```

`params` is a JSON string; entity references are resolved by step ID (same coercion as `ifc_edit`).

### Edit discovery tools

#### ifc_list

List all API modules, or functions within a specific module.

```
ifc_list()              # all modules
ifc_list(module="root") # functions in the root module
```

#### ifc_docs

Show full documentation for an API function including parameters, types,
defaults, and descriptions.

```
ifc_docs(function_path="root.create_entity")
```

### Edit execution

#### ifc_edit

Execute an `ifcopenshell.api` mutation function. Parameters are passed as a
JSON string with string values that get coerced by ifcedit's type system.

```
ifc_edit(
    function_path="root.create_entity",
    params='{"ifc_class": "IfcWall", "name": "My Wall"}'
)
```

Returns `{"ok": true, "result": ...}` or `{"ok": false, "error": "..."}`.

Does NOT auto-save -- call `ifc_save()` when ready to write changes to disk.

**Parameter coercion:**

| Type | JSON value | Python value |
|------|------------|--------------|
| `entity_instance` | `"42"` | resolved from model by step ID |
| `list[entity_instance]` | `"5,6,7"` | list of resolved entities |
| `dict` | `'{"key": "val"}'` | parsed JSON object |
| `bool` | `"true"` | `True` |
| `Optional[X]` | `"none"` | `None` |

## Typical workflow

1. **Load** a model: `ifc_load`
2. **Inspect** with query tools: `ifc_summary`, `ifc_tree`, `ifc_select`, `ifc_info`, `ifc_relations`
3. **Validate** if needed: `ifc_validate`
4. **Browse schedules / costs**: `ifc_schedule`, `ifc_cost` (use `max_depth=1` first on large projects)
5. **Look up IFC classes**: `ifc_schema`
6. **Find** the right API function: `ifc_list`, `ifc_docs`
7. **Edit** the model: `ifc_edit`
8. **Quantify** elements: `ifc_quantify` (writes QTO psets in-place)
9. **Verify** changes with query tools
10. **Save** when satisfied: `ifc_save`

The model stays in memory across all calls, so multi-step editing sessions
are fast -- no file I/O between operations.

## License

LGPLv3+ -- see the IfcOpenShell project license.
