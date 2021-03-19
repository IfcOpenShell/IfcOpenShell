import bpy
from bpy.types import Panel
from blenderbim.bim.module.geometry.data import Data
from blenderbim.bim.ifc import IfcStore


class BIM_PT_representations(Panel):
    bl_label = "IFC Representations"
    bl_idname = "BIM_PT_representations"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def draw(self, context):
        layout = self.layout
        props = context.active_object.BIMObjectProperties

        if props.ifc_definition_id not in Data.products:
            Data.load(props.ifc_definition_id)

        representations = Data.products[props.ifc_definition_id]
        if not representations:
            layout.label(text="No representations found")

        row = layout.row(align=True)
        row.prop(bpy.context.scene.BIMProperties, "contexts", text="")
        row.operator("bim.add_representation", icon="ADD", text="")

        for ifc_definition_id in representations:
            representation = Data.representations[ifc_definition_id]
            row = self.layout.row(align=True)
            row.label(text=representation["ContextOfItems"]["ContextType"])
            row.label(text=representation["ContextOfItems"]["ContextIdentifier"])
            row.label(text=representation["ContextOfItems"]["TargetView"])
            row.label(text=representation["RepresentationType"])
            op = row.operator("bim.switch_representation", icon="OUTLINER_DATA_MESH", text="")
            op.ifc_definition_id = ifc_definition_id
            op.disable_opening_subtractions = False
            row.operator("bim.remove_representation", icon="X", text="").representation_id = ifc_definition_id


class BIM_PT_mesh(Panel):
    bl_label = "IFC Representation"
    bl_idname = "BIM_PT_mesh"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == "MESH"
            and hasattr(context.active_object.data, "BIMMeshProperties")
            and context.active_object.data.BIMMeshProperties.ifc_definition_id
        )

    def draw(self, context):
        if not context.active_object.data:
            return
        layout = self.layout
        props = context.active_object.data.BIMMeshProperties

        row = layout.row(align=True)
        op = row.operator("bim.switch_representation", text="Bake Voids", icon="SELECT_SUBTRACT")
        op.ifc_definition_id = props.ifc_definition_id
        op.disable_opening_subtractions = False
        op = row.operator("bim.switch_representation", text="Dynamic Voids", icon="SELECT_INTERSECT")
        op.ifc_definition_id = props.ifc_definition_id
        op.disable_opening_subtractions = True

        row = layout.row()
        row.operator("bim.update_mesh_representation")

        row = layout.row()
        op = row.operator("bim.update_mesh_representation", text="Update Mesh As Rectangle Extrusion")
        op.ifc_representation_class = "IfcExtrudedAreaSolid/IfcRectangleProfileDef"

        row = layout.row()
        op = row.operator("bim.update_mesh_representation", text="Update Mesh As Circle Extrusion")
        op.ifc_representation_class = "IfcExtrudedAreaSolid/IfcCircleProfileDef"

        row = layout.row()
        op = row.operator("bim.update_mesh_representation", text="Update Mesh As Arbitrary Extrusion")
        op.ifc_representation_class = "IfcExtrudedAreaSolid/IfcArbitraryClosedProfileDef"

        row = layout.row()
        op = row.operator("bim.update_mesh_representation", text="Update Mesh As Arbitrary Extrusion With Voids")
        op.ifc_representation_class = "IfcExtrudedAreaSolid/IfcArbitraryProfileDefWithVoids"

        row = layout.row()
        row.operator("bim.get_representation_ifc_parameters")
        for index, ifc_parameter in enumerate(props.ifc_parameters):
            row = layout.row(align=True)
            row.prop(ifc_parameter, "name", text="")
            row.prop(ifc_parameter, "value", text="")
            row.operator("bim.update_parametric_representation", icon="FILE_REFRESH", text="").index = index


def BIM_PT_transform(self, context):
    if context.active_object and context.active_object.BIMObjectProperties.ifc_definition_id:
        row = self.layout.row()
        row.operator("bim.edit_object_placement")


class BIM_PT_workarounds(Panel):
    bl_label = "IFC Vendor Workarounds"
    bl_idname = "BIM_PT_workarounds"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == "MESH"
            and hasattr(context.active_object.data, "BIMMeshProperties")
            and context.active_object.data.BIMMeshProperties.ifc_definition_id
        )

    def draw(self, context):
        props = context.scene.BIMGeometryProperties
        row = self.layout.row()
        row.prop(props, "should_force_faceted_brep")
        row = self.layout.row()
        row.prop(props, "should_force_triangulation")
        row = self.layout.row()
        row.prop(props, "should_use_presentation_style_assignment")
