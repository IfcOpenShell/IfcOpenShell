# ifcmcp

An MCP (Model Context Protocol) server that wraps `ifcquery` and `ifcedit`,
holding the IFC model in memory across tool calls for fast interactive editing
sessions.

## Installation

```bash
pip install ifcmcp
```

Requires `ifcopenshell`, `ifcquery`, `ifcedit`, and `mcp`.

## Running the server

```bash
python3 -m ifcmcp
```

This starts the server on stdio transport, suitable for use with Claude Code
or any MCP client.

### Claude Code configuration

Use the `claude mcp add` command:

```bash
claude mcp add --transport stdio ifc -- python3 -m ifcmcp
```

Or create a `.mcp.json` file in your project root:

```json
{
  "mcpServers": {
    "ifc": {
      "type": "stdio",
      "command": "python3",
      "args": ["-m", "ifcmcp"]
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

#### ifc_load

Open an IFC file into memory.

```
ifc_load(path="/path/to/model.ifc")
-> "Loaded /path/to/model.ifc: schema IFC4, 1847 entities"
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
3. **Find** the right API function: `ifc_list`, `ifc_docs`
4. **Edit** the model: `ifc_edit`
5. **Verify** changes with query tools
6. **Save** when satisfied: `ifc_save`

The model stays in memory across all calls, so multi-step editing sessions
are fast -- no file I/O between operations.

## License

LGPLv3+ -- see the IfcOpenShell project license.
