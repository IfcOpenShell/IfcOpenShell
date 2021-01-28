import bpy
import bmesh
import pprint

material_volumes = {}

for obj in bpy.context.selected_objects:
    if not obj.data or not isinstance(obj.data, bpy.types.Mesh):
        continue
    material_polygons = {}
    for polygon in obj.data.polygons:
        material_polygons.setdefault(polygon.material_index, []).append(polygon.vertices)
    verts = [v.co for v in obj.data.vertices]
    for index, polygons in material_polygons.items():
        mesh = bpy.data.meshes.new("Temporary Mesh")
        mesh.from_pydata(verts, [], polygons)
        bm = bmesh.new()
        bm.from_mesh(mesh)
        material_name = obj.data.materials[index].name
        material_volumes.setdefault(material_name, 0)
        material_volumes[material_name] += bm.calc_volume()
        bm.free()
        bpy.data.meshes.remove(mesh)

pprint.pprint(material_volumes)
