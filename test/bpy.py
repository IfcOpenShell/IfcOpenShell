###############################################################################
#                                                                             #
# This file is part of IfcOpenShell.                                          #
#                                                                             #
# IfcOpenShell is free software: you can redistribute it and/or modify        #
# it under the terms of the Lesser GNU General Public License as published by #
# the Free Software Foundation, either version 3.0 of the License, or         #
# (at your option) any later version.                                         #
#                                                                             #
# IfcOpenShell is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                #
# Lesser GNU General Public License for more details.                         #
#                                                                             #
# You should have received a copy of the Lesser GNU General Public License    #
# along with this program. If not, see <http://www.gnu.org/licenses/>.        #
#                                                                             #
###############################################################################

###############################################################################
#                                                                             #
# Do not run this script directly, it is called by run.py                     #
#                                                                             #
###############################################################################

import os
import bpy
import sys
import time
try: from io_import_scene_ifc import import_ifc
except: 
    print("[Error] Unable to import IfcOpenShell")
    sys.exit(1)
from mathutils import Vector as V
from math import radians

scn = bpy.context.scene

for ob in bpy.data.objects:
    scn.objects.unlink(ob)

if sys.argv[-2] != 'render': sys.exit(0)

fn = sys.argv[-1]
t1 = time.time()
succes = import_ifc(fn,True,False)
if not succes:
    print("[Error] Import of %s failed"%fn)
    sys.exit(1)

dt = time.time()-t1
print ("[Notice] Conversion took %.2f seconds"%dt) 
    
cam = bpy.data.cameras.new('cam')
cam.angle = radians(45)
cam_ob = bpy.data.objects.new('cam',cam)
scn.objects.link(cam_ob)
cam_ob.rotation_euler = (radians(67),0,radians(45))

scn.camera = cam_ob
scn.render.resolution_percentage = 100
scn.render.resolution_x = 2048
scn.render.resolution_y = 2048
scn.world.horizon_color = (1,1,1)
scn.world.ambient_color = (0.05,0.05,0.05)
try: scn.render.color_mode = 'RGBA'
except: scn.render.image_settings.color_mode = 'RGBA'

for m in bpy.data.materials: m.specular_intensity = 0
def material(name,settings):
    m = bpy.data.materials.get(name)
    if not m: return
    for k,v in settings.items():
        setattr(m,k,v)
        
material("IfcWall",{"diffuse_color":[1,1,1],"diffuse_intensity":1})
material("IfcWallStandardCase",{"diffuse_color":[1,1,1],"diffuse_intensity":1})
material("IfcSite",{"diffuse_color":[0.4,0.5,0.25]})
material("IfcSlab",{"diffuse_color":[0.2,0.2,0.2]})
material("IfcDoor",{"diffuse_color":[0.25,0.1,0.05]})
material("IfcWindow",{"diffuse_color":[0.5,0.7,0.5],"use_transparency":True,"alpha":0.3})
material("IfcRoof",{"diffuse_color":[0.35,0.2,0.2]})
material("IfcFurnishingElement",{"diffuse_color":[0.8,0.7,0.5]})
material("IfcBuildingElementPro",{"diffuse_intensity":0.6})

def create_lamp(eul):
    l = bpy.data.lamps.new('l','SUN')
    l.energy = 1.3
    l_ob =  bpy.data.objects.new('l',l)
    scn.objects.link(l_ob)
    l_ob.rotation_euler = [radians(e) for e in eul]

create_lamp((20,0,60))
create_lamp((0,-120,-50))

A = V([1e9]*3)
B = V([-1e9]*3)

for ob in scn.objects:
    if ob.type != 'MESH': continue
    if ob.hide: continue
    bb = [ob.matrix_world*V(x) for x in ob.bound_box]
    for b in bb:
        for i in range(3):
            if b[i] < A[i]: A[i] = b[i]
            if b[i] > B[i]: B[i] = b[i]

C = V((1.2,-1.2,0.6))
D = B-A
E = max(D)*C + (A+B)/2

cam_ob.location = E
cam.clip_end = max(D) * 10

scn.render.filepath = os.path.join("output",os.path.basename(fn)+".png")

bpy.ops.wm.save_mainfile(filepath=os.path.join("output",os.path.basename(fn)+".blend"),compress=True)

bpy.ops.render.render(write_still=True)

sys.exit(0)
