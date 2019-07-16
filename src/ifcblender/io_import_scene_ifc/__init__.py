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
    "description": "Import files in the "
        "Industry Foundation Classes (.ifc) file format",
    "author": "Thomas Krijnen, IfcOpenShell",
    "blender": (2, 80, 0),
    "location": "File > Import",
    "tracker_url": "https://sourceforge.net/p/ifcopenshell/"
        "_list/tickets?source=navbar",
    "category": "Import-Export"}

if "bpy" in locals():
    import importlib
    if "ifcopenshell" in locals():
        importlib.reload(ifcopenshell)

import bpy
import mathutils
from collections import defaultdict
from bpy.props import StringProperty, IntProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper

major, minor = bpy.app.version[0:2]
transpose_matrices = minor >= 62

bpy.types.Object.ifc_id = IntProperty(
    name="IFC Entity ID",
    description="The STEP entity instance name")
bpy.types.Object.ifc_guid = StringProperty(
    name="IFC Entity GUID",
    description="The IFC Globally Unique Identifier")
bpy.types.Object.ifc_name = StringProperty(
    name="IFC Entity Name",
    description="The optional name attribute")
bpy.types.Object.ifc_type = StringProperty(
    name="IFC Entity Type",
    description="The STEP Datatype keyword")


def import_ifc(filename, use_names, process_relations, blender_booleans):
    from . import ifcopenshell
    from .ifcopenshell import geom as ifcopenshell_geom
    print(f"Reading {bpy.path.basename(filename)}...")
    settings = ifcopenshell_geom.settings()
    settings.set(settings.DISABLE_OPENING_SUBTRACTIONS, blender_booleans)
    iterator = ifcopenshell_geom.iterator(settings, filename)
    valid_file = iterator.initialize()
    if not valid_file:
        return False
    print("Done reading file")
    id_to_object = defaultdict(list)
    id_to_parent = {}
    id_to_matrix = {}
    openings = []
    old_progress = -1
    print("Creating geometry...")
    collection = bpy.data.collections.new(f"{bpy.path.basename(filename)}")
    bpy.context.scene.collection.children.link(collection)

    if  process_relations:
        rel_collection = bpy.data.collections.new("Relations")
        collection.children.link(rel_collection)
    while True:
        ob = iterator.get()

        f = ob.geometry.faces
        v = ob.geometry.verts
        mats = ob.geometry.materials
        matids = ob.geometry.material_ids
        m = ob.transformation.matrix.data
        t = ob.type[0:21]
        nm = ob.name if len(ob.name) and use_names else ob.guid
        # MESH CREATION
        # Depending on version, geometry.id will be either int or str
        mesh_name = 'mesh-%r' % ob.geometry.id
        if mesh_name in bpy.data.meshes:
            me = bpy.data.meshes[mesh_name]
        else:
            verts = [[v[i], v[i + 1], v[i + 2]]
                     for i in range(0, len(v), 3)]
            faces = [[f[i], f[i + 1], f[i + 2]]
                     for i in range(0, len(f), 3)]

            me = bpy.data.meshes.new(mesh_name)
            me.from_pydata(verts, [], faces)
            me.validate()
            # MATERIAL CREATION
            def add_material(mname, props):
                if mname in bpy.data.materials:
                    mat = bpy.data.materials[mname]
                    mat.use_fake_user = True
                else:
                    mat = bpy.data.materials.new(mname)
                    for k, v in props.items():
                        if k == 'transparency':
                            mat.blend_method = 'HASHED'
                            mat.use_screen_refraction = True
                            mat.refraction_depth = 0.1
                            mat.use_nodes = True
                            mat.node_tree.nodes["Principled BSDF"].inputs[15].default_value = v
                        else:
                            setattr(mat, k, v)
                me.materials.append(mat)

            needs_default = -1 in matids
            if needs_default:
                add_material(t, {})

            for mat in mats:
                props = {}
                if mat.has_diffuse:
                    alpha = 1.
                    if mat.has_transparency and mat.transparency > 0:
                        alpha = 1. - mat.transparency
                    props['diffuse_color'] = mat.diffuse + (alpha,)
                # @todo
                # if mat.has_specular:
                #     props['specular_color'] = mat.specular
                # if mat.has_specularity:
                #     props['specular_intensity'] = mat.specularity
                add_material(mat.name, props)

            faces = me.polygons if hasattr(me, 'polygons') else me.faces
            if len(faces) == len(matids):
                for face, matid in zip(faces, matids):
                    face.material_index = matid + (1 if needs_default else 0)

        # OBJECT CREATION
        bob = bpy.data.objects.new(nm, me)
        mat = mathutils.Matrix(([m[0], m[1], m[2], 0],
                                [m[3], m[4], m[5], 0],
                                [m[6], m[7], m[8], 0],
                                [m[9], m[10], m[11], 1]))
        if transpose_matrices:
            mat.transpose()

        if process_relations:
            id_to_matrix[ob.id] = mat
        else:
            bob.matrix_world = mat
        collection.objects.link(bob)

        bpy.context.view_layer.objects.active = bob
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.normals_make_consistent()
        bpy.ops.object.mode_set(mode='OBJECT')

        bob.ifc_id, bob.ifc_guid, bob.ifc_name, bob.ifc_type = \
            ob.id, ob.guid, ob.name, ob.type

        if ob.type == 'IfcSpace' or ob.type == 'IfcOpeningElement':
            if not (ob.type == 'IfcOpeningElement' and blender_booleans):
                bob.hide_viewport = bob.hide_render = True
            bob.display_type = 'WIRE'

        id_to_object[ob.id].append(bob)

        if ob.parent_id > 0:
            id_to_parent[ob.id] = ob.parent_id

        if blender_booleans and ob.type == 'IfcOpeningElement':
            openings.append(ob.id)

        progress = iterator.progress() // 2
        if progress > old_progress:
            print("\r[" + "#" * progress + " " * (50 - progress) + "]", end="")
            old_progress = progress
        if not iterator.next():
            break

    print("\rDone creating geometry" + " " * 30)

    id_to_parent_temp = dict(id_to_parent)

    if process_relations:
        print("Processing relations...")
        while len(id_to_parent_temp):
            id, parent_id = id_to_parent_temp.popitem()

            if parent_id in id_to_object:
                bob = id_to_object[parent_id][0]
            else:
                parent_ob = iterator.getObject(parent_id)
                if parent_ob.id == -1:
                    bob = None
                else:
                    m = parent_ob.transformation.matrix.data
                    nm = parent_ob.name if len(parent_ob.name) and use_names \
                        else parent_ob.guid
                    bob = bpy.data.objects.new(nm, None)

                    mat = mathutils.Matrix((
                        [m[0], m[1], m[2], 0],
                        [m[3], m[4], m[5], 0],
                        [m[6], m[7], m[8], 0],
                        [m[9], m[10], m[11], 1]))
                    if transpose_matrices:
                        mat.transpose()
                    id_to_matrix[parent_ob.id] = mat

                    rel_collection.objects.link(bob)

                    bob.ifc_id = parent_ob.id
                    bob.ifc_name, bob.ifc_type, bob.ifc_guid = \
                        parent_ob.name, parent_ob.type, parent_ob.guid

                    if parent_ob.parent_id > 0:
                        id_to_parent[parent_id] = parent_ob.parent_id
                        id_to_parent_temp[parent_id] = parent_ob.parent_id
                    id_to_object[parent_id].append(bob)
            if bob:
                for ob in id_to_object[id]:
                    ob.parent = bob

    id_to_matrix_temp = dict(id_to_matrix)

    while len(id_to_matrix_temp):
        id, matrix = id_to_matrix_temp.popitem()
        parent_id = id_to_parent.get(id, None)
        parent_matrix = id_to_matrix.get(parent_id, None)
        for ob in id_to_object[id]:
            if parent_matrix:
                ob.matrix_local = parent_matrix.inverted() @ matrix
            else:
                ob.matrix_world = matrix

    if process_relations:
        print("Done processing relations")

    for opening_id in openings:
        parent_id = id_to_parent[opening_id]
        if parent_id in id_to_object:
            parent_ob = id_to_object[parent_id][0]
            for opening_ob in id_to_object[opening_id]:
                mod = parent_ob.modifiers.new("opening", "BOOLEAN")
                mod.operation = "DIFFERENCE"
                mod.object = opening_ob

    if hasattr(iterator, 'getLog'):
        # @todo
        txt = bpy.data.texts.new(f"{bpy.path.basename(filename)}.log")
        txt.from_string(iterator.getLog())

    return True


class ImportIFC(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.ifc"
    bl_label = "Import .ifc file"

    filename_ext = ".ifc"
    filter_glob: StringProperty(default="*.ifc", options={'HIDDEN'})

    use_names: BoolProperty(name="Use entity names",
                            description="Use entity names rather than "
                            "GlobalIds for objects",
                            default=True)
    process_relations: BoolProperty(name="Process relations",
                                    description="Convert containment and "
                                    "aggregation relations to parenting"
                                    " (warning: may be slow on large files)",
                                    default=False)
    blender_booleans: BoolProperty(name="Use Blender booleans",
                                   description="Use Blender boolean modifiers "
                                   "for opening elements",
                                   default=False)

    def execute(self, context):
        if not import_ifc(self.filepath, self.use_names,
                          self.process_relations, self.blender_booleans):
            self.report({'ERROR'},
                        'Unable to parse .ifc file or no geometrical entities found'
                        )
        return {'FINISHED'}


def menu_func_import(self, context):
    self.layout.operator(ImportIFC.bl_idname,
                         text="Industry Foundation Classes (.ifc)")


classes = (
    ImportIFC,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
