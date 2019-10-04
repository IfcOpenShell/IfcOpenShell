import bpy
import pprint
print('# Start')
cleaned_materials = {}
n = 0
for m in bpy.data.materials:
    r = m.diffuse_color[0]
    g = m.diffuse_color[1]
    b = m.diffuse_color[2]
    key = str(r) + '-' + str(g) + '-' + str(b)
    cleaned_materials[key] = {'name': 'name{}'.format(n)}
    n += 1

pprint.pprint(cleaned_materials)
print(len(bpy.data.materials.keys()))
print(len(cleaned_materials.keys()))

for rgb, data in cleaned_materials.items():
    m = bpy.data.materials.new(data['name'])
    print(rgb)
    m.diffuse_color = (
        float(rgb.split('-')[0]),
        float(rgb.split('-')[1]),
        float(rgb.split('-')[2]),
        1)
    data['material'] = m
        
for o in bpy.context.selected_objects:
    m = o.material_slots[0].material
    r = m.diffuse_color[0]
    g = m.diffuse_color[1]
    b = m.diffuse_color[2]
    key = str(r) + '-' + str(g) + '-' + str(b)
    o.material_slots[0].material = cleaned_materials[key]['material']