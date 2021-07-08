import bpy
import numpy as np
import ifcopenshell
import ifcopenshell.util.unit
import ifcopenshell.util.element
import ifcopenshell.util.representation
import logging
import ifcopenshell.api
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim import import_ifc
from ifcopenshell.api.geometry.data import Data
from ifcopenshell.api.context.data import Data as ContextData
from ifcopenshell.api.void.data import Data as VoidData
from mathutils import Vector


class EditObjectPlacement(bpy.types.Operator):
    bl_idname = "bim.edit_object_placement"
    bl_label = "Edit Object Placement"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        objs = [bpy.data.objects.get(self.obj)] if self.obj else bpy.context.selected_objects
        self.file = IfcStore.get_file()
        # TODO: determine how to deal with this module dependency
        props = bpy.context.scene.BIMGeoreferenceProperties
        for obj in objs:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            matrix = np.array(obj.matrix_world)
            if props.has_blender_offset and obj.BIMObjectProperties.blender_offset_type == "OBJECT_PLACEMENT":
                unit_scale = ifcopenshell.util.unit.calculate_unit_scale(self.file)
                # TODO: np.array? Why not matrix?
                matrix = np.array(
                    ifcopenshell.util.geolocation.local2global(
                        np.matrix(obj.matrix_world),
                        float(props.blender_eastings) * unit_scale,
                        float(props.blender_northings) * unit_scale,
                        float(props.blender_orthogonal_height) * unit_scale,
                        float(props.blender_x_axis_abscissa),
                        float(props.blender_x_axis_ordinate),
                    )
                )
            ifcopenshell.api.run(
                "geometry.edit_object_placement",
                self.file,
                **{
                    "product": self.file.by_id(obj.BIMObjectProperties.ifc_definition_id),
                    "matrix": matrix,
                },
            )
        return {"FINISHED"}


class AddRepresentation(bpy.types.Operator):
    bl_idname = "bim.add_representation"
    bl_label = "Add Representation"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    context_id: bpy.props.IntProperty()
    ifc_representation_class: bpy.props.StringProperty()
    profile_set_usage: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        self.file = IfcStore.get_file()

        bpy.ops.bim.edit_object_placement(obj=obj.name)

        if not obj.data:
            return {"FINISHED"}

        product = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)

        context_id = self.context_id or int(bpy.context.scene.BIMProperties.contexts)
        context_of_items = self.file.by_id(context_id)

        gprop = context.scene.BIMGeoreferenceProperties
        coordinate_offset = None
        if gprop.has_blender_offset and obj.BIMObjectProperties.blender_offset_type == "CARTESIAN_POINT":
            coordinate_offset = Vector(
                (
                    float(gprop.blender_eastings),
                    float(gprop.blender_northings),
                    float(gprop.blender_orthogonal_height),
                )
            )

        representation_data = {
            "context": context_of_items,
            "blender_object": obj,
            "geometry": obj.data,
            "coordinate_offset": coordinate_offset,
            "total_items": max(1, len(obj.material_slots)),
            "should_force_faceted_brep": context.scene.BIMGeometryProperties.should_force_faceted_brep,
            "should_force_triangulation": context.scene.BIMGeometryProperties.should_force_triangulation,
            "ifc_representation_class": self.ifc_representation_class,
            "profile_set_usage": self.file.by_id(self.profile_set_usage) if self.profile_set_usage else None,
        }

        result = ifcopenshell.api.run("geometry.add_representation", self.file, **representation_data)

        if not result:
            print("Failed to write shape representation")
            return {"FINISHED"}

        [
            bpy.ops.bim.add_style(material=s.material.name)
            for s in obj.material_slots
            if s.material and not s.material.BIMMaterialProperties.ifc_style_id
        ]

        ifcopenshell.api.run(
            "geometry.assign_styles",
            self.file,
            **{
                "shape_representation": result,
                "styles": [
                    self.file.by_id(s.material.BIMMaterialProperties.ifc_style_id)
                    for s in obj.material_slots
                    if s.material
                ],
                "should_use_presentation_style_assignment": context.scene.BIMGeometryProperties.should_use_presentation_style_assignment,
            },
        )
        ifcopenshell.api.run(
            "geometry.assign_representation", self.file, **{"product": product, "representation": result}
        )

        existing_mesh = obj.data
        mesh = obj.data.copy()
        mesh.name = "{}/{}".format(context_id, result.id())
        mesh.BIMMeshProperties.ifc_definition_id = int(result.id())
        obj.data = mesh
        Data.load(IfcStore.get_file(), obj.BIMObjectProperties.ifc_definition_id)

        if product.is_a("IfcTypeProduct"):
            if self.file.schema == "IFC2X3":
                types = product.ObjectTypeOf
            else:
                types = product.Types
            if types:
                for element in types[0].RelatedObjects:
                    Data.load(IfcStore.get_file(), element.id())
        return {"FINISHED"}


class SwitchRepresentation(bpy.types.Operator):
    bl_idname = "bim.switch_representation"
    bl_label = "Switch Representation"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    ifc_definition_id: bpy.props.IntProperty()
    should_reload: bpy.props.BoolProperty()
    disable_opening_subtractions: bpy.props.BoolProperty()

    def execute(self, context):
        self.element_obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        self.oprops = self.element_obj.BIMObjectProperties

        self.file = IfcStore.get_file()
        self.context_of_items = self.file.by_id(self.ifc_definition_id).ContextOfItems
        self.mesh_name = self.get_mesh_name()

        mesh = bpy.data.meshes.get(self.mesh_name)
        if mesh:
            self.element_obj.data.user_remap(mesh)
        if not mesh or self.should_reload:
            self.pull_mesh_from_ifc()
        return {"FINISHED"}

    def get_mesh_name(self):
        representation = self.resolve_mapped_representation(self.file.by_id(self.ifc_definition_id))
        return "{}/{}".format(self.context_of_items.id(), representation.id())

    def resolve_mapped_representation(self, representation):
        if representation.RepresentationType == "MappedRepresentation":
            return self.resolve_mapped_representation(representation.Items[0].MappingSource.MappedRepresentation)
        return representation

    def pull_mesh_from_ifc(self):
        logger = logging.getLogger("ImportIFC")
        ifc_import_settings = import_ifc.IfcImportSettings.factory(bpy.context, IfcStore.path, logger)
        element = self.file.by_id(self.oprops.ifc_definition_id)
        settings = ifcopenshell.geom.settings()

        if self.context_of_items.ContextIdentifier == "Body":
            if element.is_a("IfcTypeProduct") or self.disable_opening_subtractions:
                shape = ifcopenshell.geom.create_shape(settings, self.file.by_id(self.ifc_definition_id))
            else:
                shape = ifcopenshell.geom.create_shape(settings, self.file.by_id(self.oprops.ifc_definition_id))
        else:
            settings.set(settings.INCLUDE_CURVES, True)
            shape = ifcopenshell.geom.create_shape(settings, self.file.by_id(self.ifc_definition_id))

        ifc_importer = import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.file = self.file
        mesh = ifc_importer.create_mesh(element, shape)
        mesh.name = self.mesh_name
        mesh.BIMMeshProperties.ifc_definition_id = self.ifc_definition_id
        self.element_obj.data.user_remap(mesh)
        material_creator = import_ifc.MaterialCreator(ifc_import_settings, ifc_importer)
        material_creator.load_existing_materials()
        material_creator.create(element, self.element_obj, mesh)

        if self.disable_opening_subtractions and self.context_of_items.ContextIdentifier == "Body":
            if self.oprops.ifc_definition_id not in VoidData.products:
                VoidData.load(IfcStore.get_file(), self.oprops.ifc_definition_id)
            for opening_id in VoidData.products[self.oprops.ifc_definition_id]:
                opening = IfcStore.get_element(opening_id)
                if not opening:
                    continue
                modifier = self.element_obj.modifiers.new("IfcOpeningElement", "BOOLEAN")
                modifier.operation = "DIFFERENCE"
                modifier.object = opening
        else:
            for modifier in self.element_obj.modifiers:
                if modifier.type == "BOOLEAN" and "IfcOpeningElement" in modifier.name:
                    self.element_obj.modifiers.remove(modifier)


class RemoveRepresentation(bpy.types.Operator):
    bl_idname = "bim.remove_representation"
    bl_label = "Remove Representation"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    representation_id: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        representation = self.file.by_id(self.representation_id)
        obj = bpy.data.objects.get(self.obj) if self.obj else bpy.context.active_object
        is_mapped_representation = representation.RepresentationType == "MappedRepresentation"
        if is_mapped_representation:
            mesh_name = "{}/{}".format(
                representation.ContextOfItems.id(), representation.Items[0].MappingSource.MappedRepresentation.id()
            )
        else:
            mesh_name = "{}/{}".format(representation.ContextOfItems.id(), representation.id())
        mesh = bpy.data.meshes.get(mesh_name)
        if mesh:
            if obj.data == mesh:
                # TODO we can do better than this
                void_mesh = bpy.data.meshes.get("Void")
                if not void_mesh:
                    void_mesh = bpy.data.meshes.new("Void")
                obj.data = void_mesh
            if not is_mapped_representation:
                bpy.data.meshes.remove(mesh)
        product = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
        ifcopenshell.api.run(
            "geometry.unassign_representation", self.file, **{"product": product, "representation": representation}
        )
        ifcopenshell.api.run("geometry.remove_representation", self.file, **{"representation": representation})
        Data.load(IfcStore.get_file(), product.id())
        return {"FINISHED"}


class UpdateRepresentation(bpy.types.Operator):
    bl_idname = "bim.update_representation"
    bl_label = "Update Representation"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()
    ifc_representation_class: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        if not ContextData.is_loaded:
            ContextData.load(IfcStore.get_file())

        objs = [bpy.data.objects.get(self.obj)] if self.obj else bpy.context.selected_objects
        self.file = IfcStore.get_file()

        for obj in objs:
            self.update_obj_mesh_representation(context, obj)
            IfcStore.edited_objs.discard(obj)
        return {"FINISHED"}

    def update_obj_mesh_representation(self, context, obj):
        product = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)

        if product.is_a("IfcGridAxis"):
            ifcopenshell.api.run("grid.create_axis_curve", self.file, **{"axis_curve": obj, "grid_axis": product})
            return

        bpy.ops.bim.edit_object_placement(obj=obj.name)

        old_representation = self.file.by_id(obj.data.BIMMeshProperties.ifc_definition_id)
        context_of_items = old_representation.ContextOfItems

        gprop = context.scene.BIMGeoreferenceProperties
        coordinate_offset = None
        if gprop.has_blender_offset and obj.BIMObjectProperties.blender_offset_type == "CARTESIAN_POINT":
            coordinate_offset = Vector(
                (
                    float(gprop.blender_eastings),
                    float(gprop.blender_northings),
                    float(gprop.blender_orthogonal_height),
                )
            )

        representation_data = {
            "context": context_of_items,
            "blender_object": obj,
            "geometry": obj.data,
            "coordinate_offset": coordinate_offset,
            "total_items": max(1, len(obj.material_slots)),
            "should_force_faceted_brep": context.scene.BIMGeometryProperties.should_force_faceted_brep,
            "should_force_triangulation": context.scene.BIMGeometryProperties.should_force_triangulation,
            "ifc_representation_class": self.ifc_representation_class,
        }

        new_representation = ifcopenshell.api.run("geometry.add_representation", self.file, **representation_data)

        [
            bpy.ops.bim.add_style(material=s.material.name)
            for s in obj.material_slots
            if s.material and not s.material.BIMMaterialProperties.ifc_style_id
        ]

        ifcopenshell.api.run(
            "geometry.assign_styles",
            self.file,
            **{
                "shape_representation": new_representation,
                "styles": [
                    self.file.by_id(s.material.BIMMaterialProperties.ifc_style_id)
                    for s in obj.material_slots
                    if s.material
                ],
                "should_use_presentation_style_assignment": context.scene.BIMGeometryProperties.should_use_presentation_style_assignment,
            },
        )

        # TODO: move this into a replace_representation usecase or something
        for inverse in self.file.get_inverse(old_representation):
            ifcopenshell.util.element.replace_attribute(inverse, old_representation, new_representation)

        obj.data.BIMMeshProperties.ifc_definition_id = int(new_representation.id())
        obj.data.name = f"{old_representation.ContextOfItems.id()}/{new_representation.id()}"
        bpy.ops.bim.remove_representation(representation_id=old_representation.id(), obj=obj.name)
        Data.load(IfcStore.get_file(), obj.BIMObjectProperties.ifc_definition_id)


class UpdateParametricRepresentation(bpy.types.Operator):
    bl_idname = "bim.update_parametric_representation"
    bl_label = "Update Parametric Representation"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        obj = bpy.context.active_object
        props = obj.data.BIMMeshProperties
        parameter = props.ifc_parameters[self.index]
        element = IfcStore.get_file().by_id(parameter.step_id)[parameter.index] = parameter.value
        bpy.ops.bim.switch_representation(ifc_definition_id=props.ifc_definition_id, should_reload=True)
        return {"FINISHED"}


class GetRepresentationIfcParameters(bpy.types.Operator):
    bl_idname = "bim.get_representation_ifc_parameters"
    bl_label = "Get Representation IFC Parameters"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.file = IfcStore.get_file()
        obj = bpy.context.active_object
        props = obj.data.BIMMeshProperties
        elements = IfcStore.get_file().traverse(IfcStore.get_file().by_id(props.ifc_definition_id))
        for element in elements:
            if element.is_a("IfcRepresentationItem") or element.is_a("IfcParameterizedProfileDef"):
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
