##############################################################################
#                                                                            #
#This file is part of IfcOpenShell.                                          #
#                                                                            #
#IfcOpenShell is free software: you can redistribute it and/or modify        #
#it under the terms of the Lesser GNU General Public License as published by #
#the Free Software Foundation, either version 3.0 of the License, or         #
#(at your option) any later version.                                         #
#                                                                            #
#IfcOpenShell is distributed in the hope that it will be useful,             #
#but WITHOUT ANY WARRANTY; without even the implied warranty of              #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                #
#Lesser GNU General Public License for more details.                         #
#                                                                            #
#You should have received a copy of the Lesser GNU General Public License    #
#along with this program. If not, see <http://www.gnu.org/licenses/>.        #
#                                                                            #
##############################################################################


bl_info = {
    "name": "IfcBlender",
    "description": "Import files in the "\
        "Industry Foundation Classes (.ifc) file format",
    "author": "Thomas Krijnen, IfcOpenShell",
    "blender": (2, 5, 6),
    "api": 32738,
    "location": "File > Import",
    "warning": "This addon requires several "\
        "Open CASCADE libraries to be installed",
    "wiki_url": "http://sourceforge.net/apps/"\
        "mediawiki/ifcopenshell/index.php",
    "tracker_url": "http://sourceforge.net/tracker/?group_id=543113",
    "category": "Import-Export"}


import bpy
import mathutils
from bpy.props import *
from io_utils import ImportHelper


class ImportIFC(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.ifc"
    bl_label = "Import .ifc file"

    filename_ext = ".ifc"
    filter_glob = StringProperty(default="*.ifc", options={'HIDDEN'})

    def execute(self, context):
        import IfcImport
        if not IfcImport.Init(self.filepath):
            return {'FINISHED'}
        ids = {}
        while True:
            ob = IfcImport.Get()
            if not ob.type in ['IFCSPACE', 'IFCOPENINGELEMENT']:
                f = ob.mesh.faces
                v = ob.mesh.verts
                m = ob.matrix
                if ob.mesh.id in ids:
                    me = ids[ob.mesh.id]
                else:
                    verts = []
                    faces = []
                    for i in range(0, len(f), 3):
                        faces.append([f[i + 0], f[i + 1], f[i + 2]])
                    for i in range(0, len(v), 3):
                        verts.append([v[i + 0], v[i + 1], v[i + 2]])
                    me = bpy.data.meshes.new('mesh%d' % ob.mesh.id)
                    me.from_pydata(verts, [], faces)
                    if ob.type in bpy.data.materials:
                        mat = bpy.data.materials[ob.type]
                        mat.use_fake_user = True
                    else:
                        mat = bpy.data.materials.new(ob.type)
                    me.materials.append(mat)
                    ids[ob.mesh.id] = me
                bob = bpy.data.objects.new(ob.name, me)
                bob.matrix_world = mathutils.Matrix(([m[0], m[1], m[2], 0],
                    [m[3], m[4], m[5], 0],
                    [m[6], m[7], m[8], 0],
                    [m[9], m[10], m[11], 1]))
                bpy.context.scene.objects.link(bob)
                me.update()
                bpy.ops.object.select_all(action='DESELECT')
                bpy.ops.object.select_name(name=bob.name)
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.normals_make_consistent()
                bpy.ops.object.mode_set(mode='OBJECT')
            if not IfcImport.Next():
                break
        return {'FINISHED'}


def menu_func_import(self, context):
    self.layout.operator(ImportIFC.bl_idname,
        text="Industry Foundation Classes (.ifc)")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
