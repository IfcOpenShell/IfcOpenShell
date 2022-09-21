import sys
import json
import bpy, bmesh
import time
import logging
from ifcclash import ifcclash
from mathutils.bvhtree import BVHTree

# start_ifc_clash = time.time()
# settings = ifcclash.ClashSettings()
# settings.output = "settings.json"
# settings.logger = logging.getLogger("Clash")
# settings.logger.setLevel(logging.DEBUG)
# clasher = ifcclash.Clasher(settings)

# clasher.clash_sets = [{
#         "name": "Clash Set A",
#         "a": [
#             {
#                 "file": "E:\PORR\Sample Files for blender\AC20-FZK-Haus.ifc",
#                 "selector": "#25fsbPyk15VvuXI$yNKenK",
#                 "mode": "i"
#             }
#         ],
#         "b": [
#             {
#                 "file": "E:\PORR\Sample Files for blender\AC20-FZK-Haus.ifc",
#                 "selector": ".IfcWall",
#                 "mode": "i"
#             }
#         ]
#     }]

# test = clasher.clash()
# end_ifc_clash = time.time()
from mathutils import Vector, Matrix, Euler
normal = Vector((0.0000, -0.5000, -0.8660))

test = Vector((0,3,5))

euler = Euler(normal).OrthoProjection(normal)

print(euler)
# obj = bpy.context.object
# obj_mesh = bmesh.new()
# obj_mesh.from_mesh(obj.data)
# obj_mesh.transform(obj.matrix_world)
# obj_tree = BVHTree.FromBMesh(obj_mesh)

# touching_objects = []

# for o in bpy.context.selectable_objects:
#     o_mesh = bmesh.new()
#     try:
#         o_mesh.from_mesh(o.data)
#     except:
#         continue
#     o_mesh.transform(o.matrix_world)
#     o_tree = BVHTree.FromBMesh(o_mesh)
    
#     if len(obj_tree.overlap(o_tree)) > 0:
#         touching_objects.append({
#             "contact_object":o,
#             "reference_polygons":[i[0] for i in obj_tree.overlap(o_tree)],
#             "contact_polygons":[i[1] for i in obj_tree.overlap(o_tree)]
#         })

# print(touching_objects)




# '# select a object in object mode first
# import bpy

# obj = bpy.context.selected_objects[0]
# collection = bpy.data.collections.get('QtoCalculator', bpy.data.collections.new('QtoCalculator'))
# bpy.context.scene.collection.children.link(collection)


# no_of_contacts = 0

# for o in bpy.context.selectable_objects:
#     if o == obj or "IfcWall" not in o.name:
#         continue
#     no_of_contacts += 1
#     try:
#         copied_obj = obj.copy()
#         copied_obj.data = obj.data.copy()
        
#         copied_o = o.copy()
#         copied_o.data = o.data.copy()
        
#         collection.objects.link(copied_obj)
#         collection.objects.link(copied_o)
#     except AttributeError:
#         #obj hasn't got a copy attribute
#         continue
    
#     copied_obj.animation_data_clear()
#     copied_obj.name = f"ContactFace: {no_of_contacts}, {obj.name}"
    
#     copied_o.animation_data_clear()
#     copied_o.name = f"ContactFace: {no_of_contacts}, {o.name}"
    
#     modifier = copied_obj.modifiers.new(type="BOOLEAN", name="Boolean")
#     modifier.operation = "INTERSECT"
#     modifier.object = o
#     modifier.solver = "FAST"
#     bpy.ops.object.modifier_apply({"object": copied_obj}, modifier="Boolean")
    
#     modifier = copied_o.modifiers.new(type="BOOLEAN", name="Boolean")
#     modifier.operation = "INTERSECT"
#     modifier.object = obj
#     modifier.solver = "FAST"
#     bpy.ops.object.modifier_apply({"object": copied_o}, modifier="Boolean")

#     if len(copied_obj.data.polygons) == 0:
#         bpy.data.objects.remove(copied_obj, do_unlink=True)
        
#     if len(copied_o.data.polygons) == 0:
#         bpy.data.objects.remove(copied_o, do_unlink=True)'