import bpy
import mathutils
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.element
import ifcopenshell.util.representation
from . import wall, slab, profile
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.pset.data import Data as PsetData
from mathutils import Vector, Matrix
from bpy_extras.object_utils import AddObjectHelper


class AddEmptyType(bpy.types.Operator, AddObjectHelper):
    bl_idname = "bim.add_empty_type"
    bl_label = "Add Empty Type"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obj = bpy.data.objects.new("TYPEX", None)
        for project in [c for c in context.view_layer.layer_collection.children if "IfcProject" in c.name]:
            if not [c for c in project.children if "Types" in c.name]:
                types = bpy.data.collections.new("Types")
                project.collection.children.link(types)
            for collection in [c for c in project.children if "Types" in c.name]:
                collection.collection.objects.link(obj)
                break
            break
        context.scene.BIMRootProperties.ifc_product = "IfcElementType"
        bpy.ops.object.select_all(action="DESELECT")
        context.view_layer.objects.active = obj
        obj.select_set(True)
        return {"FINISHED"}


def add_empty_type_button(self, context):
    self.layout.operator(AddEmptyType.bl_idname, icon="FILE_3D")


class AddTypeInstance(bpy.types.Operator):
    bl_idname = "bim.add_type_instance"
    bl_label = "Add Type Instance"
    bl_options = {"REGISTER", "UNDO"}
    ifc_class: bpy.props.StringProperty()
    relating_type: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        tprops = context.scene.BIMTypeProperties
        ifc_class = self.ifc_class or tprops.ifc_class
        relating_type_id = self.relating_type or tprops.relating_type
        if not ifc_class or not relating_type_id:
            return {"FINISHED"}
        self.file = IfcStore.get_file()
        instance_class = ifcopenshell.util.type.get_applicable_entities(ifc_class, self.file.schema)[0]
        relating_type = self.file.by_id(int(relating_type_id))
        material = ifcopenshell.util.element.get_material(relating_type)
        if material.is_a("IfcMaterialProfileSet"):
            obj = profile.DumbProfileGenerator(relating_type).generate()
            if obj:
                return {"FINISHED"}
        elif material.is_a("IfcMaterialLayerSet"):
            layer_set_direction = None

            parametric = ifcopenshell.util.element.get_psets(relating_type).get("EPset_Parametric")
            if parametric:
                layer_set_direction = parametric.get("LayerSetDirection", layer_set_direction)
            if layer_set_direction is None:
                if ifc_class in ["IfcSlabType", "IfcRoofType", "IfcRampType", "IfcPlateType"]:
                    layer_set_direction = "AXIS3"
                else:
                    layer_set_direction = "AXIS2"

            if layer_set_direction == "AXIS3":
                obj = slab.DumbSlabGenerator(relating_type).generate()
            elif layer_set_direction == "AXIS2":
                obj = wall.DumbWallGenerator(relating_type).generate()
            else:
                obj = None  # Dumb block generator? Eh? :)

            if obj:
                return {"FINISHED"}
        # A cube
        verts = [
            Vector((-1, -1, -1)),
            Vector((-1, -1, 1)),
            Vector((-1, 1, -1)),
            Vector((-1, 1, 1)),
            Vector((1, -1, -1)),
            Vector((1, -1, 1)),
            Vector((1, 1, -1)),
            Vector((1, 1, 1)),
        ]
        edges = []
        faces = [
            [0, 2, 3, 1],
            [2, 3, 7, 6],
            [4, 5, 7, 6],
            [0, 1, 5, 4],
            [1, 3, 7, 5],
            [0, 2, 6, 4],
        ]
        mesh = bpy.data.meshes.new(name="Instance")
        mesh.from_pydata(verts, edges, faces)
        obj = bpy.data.objects.new("Instance", mesh)
        obj.location = context.scene.cursor.location
        collection = context.view_layer.active_layer_collection.collection
        collection.objects.link(obj)
        collection_obj = bpy.data.objects.get(collection.name)
        bpy.ops.bim.assign_class(obj=obj.name, ifc_class=instance_class)
        bpy.ops.bim.assign_type(relating_type=int(tprops.relating_type), related_object=obj.name)
        if collection_obj and collection_obj.BIMObjectProperties.ifc_definition_id:
            obj.location[2] = collection_obj.location[2] - min([v[2] for v in obj.bound_box])
        return {"FINISHED"}


class AlignProduct(bpy.types.Operator):
    bl_idname = "bim.align_product"
    bl_label = "Align Product"
    bl_options = {"REGISTER", "UNDO"}
    align_type: bpy.props.StringProperty()

    def execute(self, context):
        selected_objs = context.selected_objects
        if len(selected_objs) < 2 or not context.active_object:
            return {"FINISHED"}
        if self.align_type == "CENTERLINE":
            point = context.active_object.matrix_world @ (
                Vector(context.active_object.bound_box[0]) + (context.active_object.dimensions / 2)
            )
        elif self.align_type == "POSITIVE":
            point = context.active_object.matrix_world @ Vector(context.active_object.bound_box[6])
        elif self.align_type == "NEGATIVE":
            point = context.active_object.matrix_world @ Vector(context.active_object.bound_box[0])

        active_x_axis = context.active_object.matrix_world.to_quaternion() @ Vector((1, 0, 0))
        active_y_axis = context.active_object.matrix_world.to_quaternion() @ Vector((0, 1, 0))
        active_z_axis = context.active_object.matrix_world.to_quaternion() @ Vector((0, 0, 1))

        x_distances = self.get_axis_distances(point, active_x_axis, context)
        y_distances = self.get_axis_distances(point, active_y_axis, context)
        if abs(sum(x_distances)) < abs(sum(y_distances)):
            for i, obj in enumerate(selected_objs):
                obj.matrix_world = Matrix.Translation(active_x_axis * -x_distances[i]) @ obj.matrix_world
        else:
            for i, obj in enumerate(selected_objs):
                obj.matrix_world = Matrix.Translation(active_y_axis * -y_distances[i]) @ obj.matrix_world
        return {"FINISHED"}

    def get_axis_distances(self, point, axis, context):
        results = []
        for obj in context.selected_objects:
            if self.align_type == "CENTERLINE":
                obj_point = obj.matrix_world @ (Vector(obj.bound_box[0]) + (obj.dimensions / 2))
            elif self.align_type == "POSITIVE":
                obj_point = obj.matrix_world @ Vector(obj.bound_box[6])
            elif self.align_type == "NEGATIVE":
                obj_point = obj.matrix_world @ Vector(obj.bound_box[0])
            results.append(mathutils.geometry.distance_point_to_plane(obj_point, point, axis))
        return results


class DynamicallyVoidProduct(bpy.types.Operator):
    bl_idname = "bim.dynamically_void_product"
    bl_label = "Dynamically Void Product"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj)
        product = IfcStore.get_file().by_id(obj.BIMObjectProperties.ifc_definition_id)
        if not product.HasOpenings:
            return {"FINISHED"}
        if [m for m in obj.modifiers if m.type == "BOOLEAN"]:
            return {"FINISHED"}
        representation = ifcopenshell.util.representation.get_representation(product, "Model", "Body", "MODEL_VIEW")
        if not representation:
            return {"FINISHED"}
        was_edit_mode = obj.mode == "EDIT"
        if was_edit_mode:
            bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.bim.switch_representation(
            obj=obj.name,
            should_switch_all_meshes=True,
            should_reload=True,
            ifc_definition_id=representation.id(),
            disable_opening_subtractions=True,
        )
        if was_edit_mode:
            bpy.ops.object.mode_set(mode="EDIT")
        return {"FINISHED"}


def generate_box(usecase_path, ifc_file, settings):
    box_context = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Box", "MODEL_VIEW")
    if not box_context:
        return
    obj = settings["blender_object"]
    if 0 in list(obj.dimensions):
        return
    product = ifc_file.by_id(obj.BIMObjectProperties.ifc_definition_id)
    old_box = ifcopenshell.util.representation.get_representation(product, "Model", "Box", "MODEL_VIEW")
    if settings["context"].ContextType == "Model" and getattr(settings["context"], "ContextIdentifier") == "Body":
        if old_box:
            bpy.ops.bim.remove_representation(representation_id=old_box.id(), obj=obj.name)

        new_settings = settings.copy()
        new_settings["context"] = box_context
        new_box = ifcopenshell.api.run(
            "geometry.add_representation", ifc_file, should_run_listeners=False, **new_settings
        )
        ifcopenshell.api.run(
            "geometry.assign_representation",
            ifc_file,
            should_run_listeners=False,
            **{"product": product, "representation": new_box}
        )


def regenerate_profile_usage(usecase_path, ifc_file, settings):
    elements = []
    if ifc_file.schema == "IFC2X3":
        for rel in ifc_file.get_inverse(settings["usage"]):
            if not rel.is_a("IfcRelAssociatesMaterial"):
                continue
            for element in rel.RelatedObjects:
                elements.append(element)
    else:
        for rel in settings["usage"].AssociatedTo:
            for element in rel.RelatedObjects:
                elements.append(element)

    for element in elements:
        obj = IfcStore.get_element(element.id())
        if not obj:
            continue
        representation = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        if representation:
            bpy.ops.bim.switch_representation(
                obj=obj.name, ifc_definition_id=representation.id(), should_reload=True, should_switch_all_meshes=True
            )


def ensure_material_assigned(usecase_path, ifc_file, settings):
    if usecase_path == "material.assign_material":
        if not settings.get("Material", None):
            return
        elements = [self.settings["product"]]
    else:
        elements = []
        for rel in ifc_file.by_type("IfcRelAssociatesMaterial"):
            if rel.RelatingMaterial == settings["material"] or [
                e for e in ifc_file.traverse(rel.RelatingMaterial) if e == settings["material"]
            ]:
                elements.extend(rel.RelatedObjects)

    for element in elements:
        obj = IfcStore.get_element(element.GlobalId)
        if not obj or not obj.data:
            continue

        element_material = ifcopenshell.util.element.get_material(element)
        material = [m for m in ifc_file.traverse(element_material) if m.is_a("IfcMaterial")]

        object_material_ids = [
            om.BIMObjectProperties.ifc_definition_id
            for om in obj.data.materials
            if om is not None and om.BIMObjectProperties.ifc_definition_id
        ]

        if material[0].id() in object_material_ids:
            continue

        obj.data.materials.append(IfcStore.get_element(material[0].id()))
