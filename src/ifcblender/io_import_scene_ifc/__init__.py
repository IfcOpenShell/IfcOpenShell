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

# <pep8 compliant>

###############################################################################
#                                                                             #
# Based on the Wavefront OBJ File importer by Campbell Barton                 #
#                                                                             #
###############################################################################

bl_info = {
    "name": "IfcBlender",
    "description": "Import files in the "\
        "Industry Foundation Classes (.ifc) file format",
    "author": "Thomas Krijnen, IfcOpenShell",
    "blender": (2, 5, 8),
    "api": 37702,
    "location": "File > Import",
    "warning": "",
    "wiki_url": "http://sourceforge.net/apps/"\
        "mediawiki/ifcopenshell/index.php",
    "tracker_url": "http://sourceforge.net/tracker/?group_id=543113",
    "category": "Import-Export"}

if "bpy" in locals():
    import imp
    if "IfcImport" in locals():
        imp.reload(IfcImport)

import bpy
import mathutils
from bpy.props import StringProperty, IntProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper

bpy.types.Object.ifc_id = IntProperty(name="IFC Entity ID",
    description="The STEP entity instance name")
bpy.types.Object.ifc_guid = StringProperty(name="IFC Entity GUID",
    description="The IFC Globally Unique Identifier")
bpy.types.Object.ifc_name = StringProperty(name="IFC Entity Name",
    description="The optional name attribute")
bpy.types.Object.ifc_type = StringProperty(name="IFC Entity Type",
    description="The STEP Datatype keyword")


class ImportIFC(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.ifc"
    bl_label = "Import .ifc file"

    filename_ext = ".ifc"
    filter_glob = StringProperty(default="*.ifc", options={'HIDDEN'})

    use_names = BoolProperty(name="Use entity names",
        description="Use entity names rather than GlobalIds for objects",
        default=True)
    process_relations = BoolProperty(name="Process relations",
        description="Convert containment and aggregation relations to parenting",
        default=True)

    def execute(self, context):
        from . import IfcImport
        if not IfcImport.Init(self.filepath):
            return {'FINISHED'}
        id_to_object = {}
        id_to_parent = {}
        while True:
            ob = IfcImport.Get()
            if ob.type != 'IfcOpeningElement':
                f = ob.mesh.faces
                v = ob.mesh.verts
                m = ob.matrix
                t = ob.type[0:21]
                nm = ob.name if len(ob.name) and self.use_names else ob.guid

                verts = [[v[i], v[i + 1], v[i + 2]] \
                    for i in range(0, len(v), 3)]
                faces = [[f[i], f[i + 1], f[i + 2]] \
                    for i in range(0, len(f), 3)]

                me = bpy.data.meshes.new('mesh%d' % ob.mesh.id)
                me.from_pydata(verts, [], faces)
                if t in bpy.data.materials:
                    mat = bpy.data.materials[t]
                    mat.use_fake_user = True
                else:
                    mat = bpy.data.materials.new(t)
                me.materials.append(mat)

                bob = bpy.data.objects.new(nm, me)
                bob.matrix_world = mathutils.Matrix(([m[0], m[1], m[2], 0],
                    [m[3], m[4], m[5], 0],
                    [m[6], m[7], m[8], 0],
                    [m[9], m[10], m[11], 1]))
                bpy.context.scene.objects.link(bob)

                bpy.ops.object.select_all(action='DESELECT')
                bpy.ops.object.select_name(name=bob.name)
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.normals_make_consistent()
                bpy.ops.object.mode_set(mode='OBJECT')

                bob.ifc_id, bob.ifc_guid, bob.ifc_name, bob.ifc_type = \
                    ob.id, ob.guid, ob.name, ob.type

                bob.hide = ob.type == 'IfcSpace'
                id_to_object[ob.id] = bob

                if ob.parent_id > 0:
                    id_to_parent[ob.id] = ob.parent_id
            if not IfcImport.Next():
                break

        while len(id_to_parent) and self.process_relations:
            id, parent_id = id_to_parent.popitem()

            if parent_id in id_to_object:
                bob = id_to_object[parent_id]
            else:
                parent_ob = IfcImport.GetObject(parent_id)
                if parent_ob.id == -1:
                    bob = None
                else:
                    m = parent_ob.matrix
                    nm = parent_ob.name if len(parent_ob.name) and self.use_names \
                        else parent_ob.guid
                    bob = bpy.data.objects.new(nm, None)
                    bob.matrix_world = mathutils.Matrix(([m[0], m[1], m[2], 0],
                        [m[3], m[4], m[5], 0],
                        [m[6], m[7], m[8], 0],
                        [m[9], m[10], m[11], 1]))
                    bpy.context.scene.objects.link(bob)

                    bob.ifc_id = parent_ob.id
                    bob.ifc_guid = parent_ob.guid
                    bob.ifc_name = parent_ob.name
                    bob.ifc_type = parent_ob.type

                    if parent_ob.parent_id > 0:
                        id_to_parent[parent_id] = parent_ob.parent_id
                    id_to_object[parent_id] = bob
            if bob:
                ob = id_to_object[id]
                ob.matrix_world = bob.matrix_world.inverted() * ob.matrix_world
                ob.parent = bob

        IfcImport.CleanUp()
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
