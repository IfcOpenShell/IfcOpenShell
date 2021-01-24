import bpy
import numpy as np
import ifcopenshell
import logging
import blenderbim.bim.module.geometry.edit_object_placement as edit_object_placement
import blenderbim.bim.module.geometry.add_representation as add_representation
import blenderbim.bim.module.geometry.assign_styles as assign_styles
import blenderbim.bim.module.geometry.assign_representation as assign_representation
import blenderbim.bim.module.geometry.remove_representation as remove_representation
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim import import_ifc
from blenderbim.bim.module.geometry.data import Data


class EditObjectPlacement(bpy.types.Operator):
    bl_idname = "bim.edit_object_placement"
    bl_label = "Edit Object Placement"
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        self.file = IfcStore.get_file()
        # TODO: determine how to deal with this module dependency
        props = bpy.context.scene.BIMGeoreferenceProperties
        matrix = np.array(obj.matrix_world)
        if props.has_blender_offset and props.blender_offset_type == "OBJECT_PLACEMENT":
            self.calculate_unit_scale()
            # TODO: np.array? Why not matrix?
            matrix = np.array(
                ifcopenshell.util.geolocation.local2global(
                    np.matrix(obj.matrix_world),
                    float(props.blender_eastings) * self.unit_scale,
                    float(props.blender_northings) * self.unit_scale,
                    float(props.blender_orthogonal_height) * self.unit_scale,
                    float(props.blender_x_axis_abscissa),
                    float(props.blender_x_axis_ordinate),
                )
            )
        edit_object_placement.Usecase(
            self.file,
            {
                "product": self.file.by_id(obj.BIMObjectProperties.ifc_definition_id),
                "matrix": matrix,
            },
        ).execute()
        return {"FINISHED"}

    def calculate_unit_scale(self):
        self.unit_scale = 1
        units = self.file.by_type("IfcUnitAssignment")[0]
        for unit in units.Units:
            if not hasattr(unit, "UnitType") or unit.UnitType != "LENGTHUNIT":
                continue
            while unit.is_a("IfcConversionBasedUnit"):
                self.unit_scale *= unit.ConversionFactor.ValueComponent.wrappedValue
                unit = unit.ConversionFactor.UnitComponent
            if unit.is_a("IfcSIUnit"):
                self.unit_scale *= ifcopenshell.util.unit.get_prefix_multiplier(unit.Prefix)


class AddRepresentation(bpy.types.Operator):
    bl_idname = "bim.add_representation"
    bl_label = "Add Representation"
    obj: bpy.props.StringProperty()
    context_id: bpy.props.IntProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        self.file = IfcStore.get_file()
        context_id = self.context_id or int(bpy.context.scene.BIMProperties.contexts)

        bpy.ops.bim.edit_object_placement(obj=obj.name)

        if obj.data:
            result = add_representation.Usecase(
                self.file,
                {
                    "context": self.file.by_id(context_id),
                    "blender_object": obj,
                    "geometry": obj.data,
                    "total_items": max(1, len(obj.material_slots)),
                    "should_force_faceted_brep": context.scene.BIMGeometryProperties.should_force_faceted_brep,
                    "should_force_triangulation": context.scene.BIMGeometryProperties.should_force_triangulation
                },
            ).execute()
            if not result:
                print("Failed to write shape representation")
                return {"FINISHED"}
            assign_styles.Usecase(
                self.file,
                {
                    "shape_representation": result,
                    "styles": [
                        self.file.by_id(s.material.BIMMaterialProperties.ifc_style_id)
                        for s in obj.material_slots
                        if s.material
                    ],
                    "should_use_presentation_style_assignment": context.scene.BIMGeometryProperties.should_use_presentation_style_assignment
                },
            ).execute()
            assign_representation.Usecase(
                self.file,
                {"product": self.file.by_id(obj.BIMObjectProperties.ifc_definition_id), "representation": result},
            ).execute()

            existing_mesh = obj.data
            mesh = obj.data.copy()
            mesh.name = "{}/{}".format(context_id, result.id())
            mesh.BIMMeshProperties.ifc_definition_id = int(result.id())
            obj.data = mesh
        Data.load(obj.BIMObjectProperties.ifc_definition_id)
        return {"FINISHED"}


class SwitchRepresentation(bpy.types.Operator):
    bl_idname = "bim.switch_representation"
    bl_label = "Switch Representation"
    ifc_definition_id: bpy.props.IntProperty()

    def execute(self, context):
        self.obj = bpy.context.active_object

        self.file = IfcStore.get_file()
        context_of_items = self.file.by_id(self.ifc_definition_id).ContextOfItems
        self.mesh_name = "{}/{}".format(context_of_items.id(), self.ifc_definition_id)

        mesh = bpy.data.meshes.get(self.mesh_name)
        if mesh:
            self.obj.data.user_remap(mesh)
        self.pull_mesh_from_ifc()
        return {"FINISHED"}

    def pull_mesh_from_ifc(self):
        self.file = IfcStore.get_file()
        logger = logging.getLogger("ImportIFC")
        ifc_import_settings = import_ifc.IfcImportSettings.factory(bpy.context, IfcStore.path, logger)
        element = self.file.by_id(self.obj.BIMObjectProperties.ifc_definition_id)
        settings = ifcopenshell.geom.settings()
        settings.set(settings.INCLUDE_CURVES, True)
        shape = ifcopenshell.geom.create_shape(settings, self.file.by_id(self.ifc_definition_id))
        ifc_importer = import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.file = self.file
        mesh = ifc_importer.create_mesh(element, shape)
        mesh.name = self.mesh_name
        mesh.BIMMeshProperties.ifc_definition_id = self.ifc_definition_id
        self.obj.data.user_remap(mesh)
        material_creator = import_ifc.MaterialCreator(ifc_import_settings, ifc_importer)
        material_creator.create(element, self.obj, mesh)


class RemoveRepresentation(bpy.types.Operator):
    bl_idname = "bim.remove_representation"
    bl_label = "Remove Representation"
    ifc_definition_id: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        representation = self.file.by_id(self.ifc_definition_id)
        obj = bpy.context.active_object
        mesh = bpy.data.meshes.get("{}/{}".format(representation.ContextOfItems.id(), representation.id()))
        if mesh:
            if obj.data == mesh:
                # TODO we can do better than this
                void_mesh = bpy.data.meshes.get("Void")
                if not void_mesh:
                    void_mesh = bpy.data.meshes.new("Void")
                obj.data = void_mesh
            bpy.data.meshes.remove(mesh)
        remove_representation.Usecase(self.file, {"representation": representation}).execute()
        Data.load(obj.BIMObjectProperties.ifc_definition_id)
        return {"FINISHED"}


class UpdateMeshRepresentation(bpy.types.Operator):
    bl_idname = "bim.update_mesh_representation"
    bl_label = "Update Mesh Representation"
    obj: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        self.file = IfcStore.get_file()

        bpy.ops.bim.edit_object_placement(obj=obj.name)

        old_representation = self.file.by_id(obj.data.BIMMeshProperties.ifc_definition_id)
        new_representation = add_representation.Usecase(
            self.file,
            {
                "context": old_representation.ContextOfItems,
                "blender_object": obj,
                "geometry": obj.data,
                "total_items": max(1, len(obj.material_slots)),
                "should_force_faceted_brep": context.scene.BIMGeometryProperties.should_force_faceted_brep,
                "should_force_triangulation": context.scene.BIMGeometryProperties.should_force_triangulation
            },
        ).execute()
        if not new_representation:
            print("Failed to write shape representation")
            return {"FINISHED"}

        assign_styles.Usecase(
            self.file,
            {
                "shape_representation": new_representation,
                "styles": [
                    self.file.by_id(s.material.BIMMaterialProperties.ifc_style_id)
                    for s in obj.material_slots
                    if s.material
                ],
                "should_use_presentation_style_assignment": context.scene.BIMGeometryProperties.should_use_presentation_style_assignment
            },
        ).execute()

        # TODO: move this into a replace_representation usecase or something
        for inverse in self.file.get_inverse(old_representation):
            ifcopenshell.util.element.replace_attribute(inverse, old_representation, new_representation)

        obj.data.BIMMeshProperties.ifc_definition_id = int(new_representation.id())
        obj.data.name = f"{old_representation.ContextOfItems.id()}/{new_representation.id()}"
        bpy.ops.bim.remove_representation(ifc_definition_id=old_representation.id())
        Data.load(obj.BIMObjectProperties.ifc_definition_id)
        return {"FINISHED"}


class UpdateParametricRepresentation(bpy.types.Operator):
    bl_idname = "bim.update_parametric_representation"
    bl_label = "Update Parametric Representation"
    index: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        obj = bpy.context.active_object
        props = obj.data.BIMMeshProperties
        parameter = props.ifc_parameters[self.index]
        element = IfcStore.get_file().by_id(parameter.step_id)[parameter.index] = parameter.value
        bpy.ops.bim.switch_representation(ifc_definition_id=props.ifc_definition_id)
        return {"FINISHED"}


class GetRepresentationIfcParameters(bpy.types.Operator):
    bl_idname = "bim.get_representation_ifc_parameters"
    bl_label = "Get Representation IFC Parameters"

    def execute(self, context):
        self.file = IfcStore.get_file()
        obj = bpy.context.active_object
        props = obj.data.BIMMeshProperties
        elements = IfcStore.get_file().traverse(IfcStore.get_file().by_id(props.ifc_definition_id))
        for element in elements:
            if not element.is_a("IfcRepresentationItem"):
                continue
            for i in range(0, len(element)):
                if element.attribute_type(i) == "DOUBLE":
                    new = props.ifc_parameters.add()
                    new.name = "{}/{}".format(element.is_a(), element.attribute_name(i))
                    new.step_id = element.id()
                    new.type = element.attribute_type(i)
                    new.index = i
                    if element[i]:
                        new.value = element[i]
        return {"FINISHED"}
