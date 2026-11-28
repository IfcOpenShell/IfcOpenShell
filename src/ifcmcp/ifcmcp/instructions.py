# This file was generated with the assistance of an AI coding tool.
"""Instructions the MCP server sends to the client when it connects."""

_INTRO = """\
MCP server for querying and editing IFC building models. Load a file with \
ifc_load, or start an empty model with ifc_new, then use the query and edit \
tools. Edits stay in memory until ifc_save writes them to disk.
"""

_WORKING = """
# Working with a model

Respect the existing structure and naming in a model. Inspect before you \
change anything, and never assume a value you have not read. Explore \
progressively: start with ifc_summary, then ifc_select for the classes you \
need, then ifc_info and ifc_relations on individual elements. On a large \
model, call ifc_tree with max_depth=4 to see the storeys with element \
counts, and page through ifc_select results with limit and offset.

Elements are identified by their STEP id, the integer `id` that query and \
edit results return. ifc_info, ifc_relations and ifc_clash also accept a \
GlobalId.
"""

_EDITING = """
# Editing

Find the right function with ifc_search, in the API's own terms ("assign \
container", "edit attributes"), or browse with ifc_list. Read its \
parameters with ifc_docs before calling ifc_edit. Prefer ifcopenshell.api functions over creating raw \
entities: they maintain the relationships that keep a model valid. Check \
the result of each edit with the query tools. {undo}

Pass entity arguments to ifc_edit as STEP ids, written as strings: "42", \
or "5,6,7" for a list.
"""

_CONCEPTS = """
# IFC concepts

* Spatial structure: IfcProject > IfcSite > IfcBuilding > \
IfcBuildingStorey (> IfcSpace). These are linked by aggregation \
(aggregate.assign_object). Physical elements such as walls are not \
aggregated into a storey; they are contained in it \
(spatial.assign_container). An element is contained in exactly one \
spatial element.
* Aggregation also builds assemblies: an element can decompose into parts.
* Types and occurrences: an IfcWallType holds what many walls share \
(properties, materials, often geometry); each IfcWall is an occurrence \
assigned to it (type.assign_type). Edit the type to change every \
occurrence, the occurrence to change one.
* root.create_entity only creates the entity. It has no placement, no \
geometry and no container until you add them.
* Properties are grouped in property sets (pset.add_pset, \
pset.edit_pset); quantities in quantity sets.
* A structural analysis model (IfcStructuralAnalysisModel) is a group, not \
part of the spatial structure, so ifc_tree does not show it. ifc_structural \
lists each one with its members, connections, load cases and load \
combinations.
"""

_UNITS = """
# Units, placement and geometry

* A model's length unit is whatever its IfcUnitAssignment says: millimetres \
are common, and unit.assign_unit with no arguments assigns millimetres. \
Check with ifc_select(query="IfcSIUnit") before reading or writing \
dimensions.
* Most ifcopenshell.api geometry functions take lengths in metres and \
convert them to the project unit: geometry.add_wall_representation, \
geometry.add_slab_representation, geometry.add_profile_representation, \
and geometry.edit_object_placement unless is_si is false. \
geometry.add_door_representation, geometry.add_window_representation and \
geometry.add_railing_representation take project units instead. Check a \
function's ifc_docs before passing lengths. ifc_info reports placements in \
project units.
* Placements are relative: an element's placement is usually relative to \
its container's placement.
* Geometry belongs to a representation context. A new model needs a Model \
context and a Body subcontext (context.add_context) before any geometry can \
be added; ifc_contexts lists those in the model.
"""

_SCHEMAS = """
# Schemas

ifc_new defaults to IFC4. IFC2X3 requires owner history on every rooted \
entity: in a new IFC2X3 model, create a person, an organisation, a person \
and organisation, and an application (the owner module) before anything \
else, or creating entities fails.

Use ifc_schema to look up what an IFC class means and which attributes and \
predefined types it has.
"""

INSTRUCTIONS = (
    _INTRO
    + _WORKING
    + _EDITING.format(
        undo="Each ifc_edit, ifc_shape and ifc_quantify call is one undo step: ifc_undo "
        "reverts it and ifc_redo reapplies it. A call that fails changes nothing."
    )
    + _CONCEPTS
    + _UNITS
    + _SCHEMAS
)

# ifcmcp --bonsai works on the model open in Bonsai, with BONSAI_TOOLS only.
BONSAI_INSTRUCTIONS = (
    """\
MCP server for working on the IFC model open in Bonsai, the Blender add-on. \
It works on the live session: each call sees the user's latest changes, \
including unsaved ones, and the user sees each edit in Bonsai as soon as it \
is made. Saving the model is left to the user.

# Bonsai

When the user refers to "this", "these" or "the selected" elements, call \
bonsai_selection to find out which. To show the user what you mean, select \
the elements with bonsai_select, which also zooms to them; bonsai_view \
turns the viewport to a standard direction. bonsai_screenshot shows you the \
3D viewport as the user sees it: use it to check the result of a geometry \
edit. These tools change the selection and the view, never the model.
"""
    + _WORKING
    + _EDITING.format(
        undo="Each ifc_edit, ifc_shape and ifc_quantify call is one step in Bonsai's "
        "undo history, which it shares with the user's own changes. ifc_undo reverts "
        "the last step only if it is one of these calls, and ifc_redo reapplies it; "
        "they never undo the user's work. A call that fails changes nothing."
    )
    + _CONCEPTS
    + _UNITS
    + """
# Schema

Use ifc_schema to look up what an IFC class means and which attributes and \
predefined types it has.
"""
)

EXECUTE_INSTRUCTIONS = """
# Running code

ifc_execute runs Python against the model, with `model` and the \
ifcopenshell api and util modules already imported. Use it for loops, \
bulk changes and ifcopenshell.util queries that would otherwise take many \
calls; prefer the dedicated tools for single queries and edits. Assign \
what you want back to `result`. Each call is one undo step, and code that \
raises is rolled back.
"""
