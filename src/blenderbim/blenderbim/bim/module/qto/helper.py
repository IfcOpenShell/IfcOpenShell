import bpy
import bmesh


def calculate_height(obj):
    return obj.dimensions[2]


def calculate_volume(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    result = bm.calc_volume()
    bm.free()
    return result


def calculate_formwork_area(objs, context):
    """
    Formwork is defined as the surface area required to cover all exposed
    surfaces of one or more objects, excluding top surfaces (i.e. that have a
    face normal with a significant Z component).
    """
    copied_objs = []
    result = 0

    for obj in objs:
        new_obj = obj.copy()
        new_obj.data = obj.data.copy()
        new_obj.animation_data_clear()
        context.collection.objects.link(new_obj)
        copied_objs.append(new_obj)

    context_override = {}
    context_override["object"] = context_override["active_object"] = copied_objs[0]
    context_override["selected_objects"] = context_override["selected_editable_objects"] = copied_objs
    bpy.ops.object.join(context_override)

    copied_objs[0].name = "Formwork"
    copied_objs[0].BIMObjectProperties.ifc_definition_id = 0
    modifier = copied_objs[0].modifiers.new("Formwork", "REMESH")
    modifier.mode = "SHARP"
    # This hardcoded value may be optimised through a better understanding of the octree division.
    # These values are based off some trial and error heuristics I've learned through experience.
    max_dim = max(copied_objs[0].dimensions)
    if max_dim > 45:
        modifier.octree_depth = 9
    elif max_dim > 35:
        modifier.octree_depth = 8
    elif max_dim > 12:
        modifier.octree_depth = 7
    elif max_dim > 5:
        modifier.octree_depth = 6
    else:
        modifier.octree_depth = 5

    mesh = copied_objs[0].evaluated_get(context.evaluated_depsgraph_get()).to_mesh()
    for polygon in mesh.polygons:
        if polygon.normal.z > 0.5:
            continue
        result += polygon.area
    return result
