# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import bonsai.bim
import bonsai.tool as tool
from bpy.types import Panel, Menu, UIList
from bonsai.bim.ifc import IfcStore
from bonsai.bim.helper import prop_with_search
from bonsai.bim.module.geometry.data import (
    RepresentationsData,
    RepresentationItemsData,
    ConnectionsData,
    PlacementData,
    DerivedCoordinatesData,
)
from bonsai.bim.module.layer.data import LayersData


def mode_menu(self, context):
    if not tool.Ifc.get():
        return
    row = self.layout.row(align=True)
    if context.scene.BIMGeometryProperties.mode == "EDIT":
        row.operator("bim.override_mode_set_object", icon="CANCEL", text="Discard Changes").should_save = False
    row.prop(context.scene.BIMGeometryProperties, "mode", text="", icon_value=bonsai.bim.icons["IFC"].icon_id)


def object_menu(self, context):
    self.layout.separator()
    self.layout.operator("bim.override_object_duplicate_move", icon="PLUGIN")
    self.layout.operator("bim.override_object_delete", icon="PLUGIN")
    self.layout.operator("bim.override_paste_buffer", icon="PLUGIN")
    self.layout.menu("BIM_MT_object_set_origin", icon="PLUGIN")


def edit_mesh_menu(self, context):
    self.layout.separator()
    self.layout.menu("BIM_MT_separate", icon="PLUGIN")


class BIM_MT_separate(Menu):
    bl_idname = "BIM_MT_separate"
    bl_label = "IFC Separate"

    def draw(self, context):
        self.layout.operator("bim.override_mesh_separate", icon="PLUGIN", text="IFC Selection").type = "SELECTED"
        self.layout.operator("bim.override_mesh_separate", icon="PLUGIN", text="IFC By Material").type = "MATERIAL"
        self.layout.operator("bim.override_mesh_separate", icon="PLUGIN", text="IFC By Loose Parts").type = "LOOSE"


class BIM_MT_hotkey_separate(Menu):
    bl_idname = "BIM_MT_hotkey_separate"
    bl_label = "Separate"

    def draw(self, context):
        self.layout.label(text="IFC Separate", icon_value=bonsai.bim.icons["IFC"].icon_id)
        self.layout.operator("bim.override_mesh_separate", text="Selection").type = "SELECTED"
        self.layout.operator("bim.override_mesh_separate", text="By Material").type = "MATERIAL"
        self.layout.operator("bim.override_mesh_separate", text="By Loose Parts").type = "LOOSE"
        self.layout.separator()
        self.layout.label(text="Blender Separate", icon="BLENDER")
        self.layout.operator("mesh.separate", text="Selection").type = "SELECTED"
        self.layout.operator("mesh.separate", text="By Material").type = "MATERIAL"
        self.layout.operator("mesh.separate", text="By Loose Parts").type = "LOOSE"


class BIM_MT_object_set_origin(Menu):
    bl_idname = "BIM_MT_object_set_origin"
    bl_label = "IFC Set Origin"

    def draw(self, context):
        self.layout.operator("bim.override_origin_set", icon="PLUGIN", text="IFC Geometry to Origin").origin_type = (
            "GEOMETRY_ORIGIN"
        )
        self.layout.operator("bim.override_origin_set", icon="PLUGIN", text="IFC Origin to Geometry").origin_type = (
            "ORIGIN_GEOMETRY"
        )
        self.layout.operator("bim.override_origin_set", icon="PLUGIN", text="IFC Origin to 3D Cursor").origin_type = (
            "ORIGIN_CURSOR"
        )
        self.layout.operator(
            "bim.override_origin_set", icon="PLUGIN", text="IFC Origin to Center of Mass (Surface)"
        ).origin_type = "ORIGIN_CENTER_OF_MASS"
        self.layout.operator(
            "bim.override_origin_set", icon="PLUGIN", text="IFC Origin to Center of Mass (Volume)"
        ).origin_type = "ORIGIN_CENTER_OF_VOLUME"


def outliner_menu(self, context):
    self.layout.separator()
    self.layout.operator("bim.override_outliner_delete", icon="X")


class BIM_PT_representations(Panel):
    bl_label = "Representations"
    bl_idname = "BIM_PT_representations"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_order = 1
    bl_parent_id = "BIM_PT_tab_representations"
    bl_options = {"HIDE_HEADER"}

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        if not IfcStore.get_element(context.active_object.BIMObjectProperties.ifc_definition_id):
            return False
        return IfcStore.get_file()

    def draw(self, context):
        if not RepresentationsData.is_loaded:
            RepresentationsData.load()

        layout = self.layout
        props = context.active_object.BIMObjectProperties

        row = layout.row(align=True)
        prop_with_search(row, context.active_object.BIMGeometryProperties, "contexts", text="")
        row.operator("bim.add_representation", icon="ADD", text="")

        if not RepresentationsData.data["representations"]:
            layout.label(text="No Representations Found")
            return

        for representation in RepresentationsData.data["representations"]:
            row = self.layout.row(align=True)
            row.label(text=representation["ContextType"])
            row.label(text=representation["ContextIdentifier"])
            row.label(text=representation["TargetView"])
            row.label(text=representation["RepresentationType"])
            op = row.operator(
                "bim.switch_representation",
                icon="FILE_REFRESH" if representation["is_active"] else "OUTLINER_DATA_MESH",
                text="",
            )
            op.should_switch_all_meshes = True
            op.should_reload = True
            op.ifc_definition_id = representation["id"]
            op.disable_opening_subtractions = False
            row.operator("bim.remove_representation", icon="X", text="").representation_id = representation["id"]
            if representation["is_active"]:
                active_representation = representation

        layout.separator()
        if not LayersData.is_loaded:
            LayersData.load()
        if LayersData.data["active_layers"]:
            layout.label(text="Representation Presentation Layers:")
            for layer_name in LayersData.data["active_layers"].values():
                layout.label(text=layer_name, icon="STICKY_UVS_LOC")
        else:
            layout.label(text="Representation Has No Presentation Layers", icon="STICKY_UVS_LOC")


class BIM_PT_representation_items(Panel):
    bl_label = "Representation Items"
    bl_idname = "BIM_PT_representation_items"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_order = 1
    bl_parent_id = "BIM_PT_tab_representations"

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        if not IfcStore.get_element(context.active_object.BIMObjectProperties.ifc_definition_id):
            return False
        return IfcStore.get_file()

    def draw(self, context):
        if not RepresentationItemsData.is_loaded:
            RepresentationItemsData.load()

        props = context.active_object.BIMGeometryProperties
        layout = self.layout

        row = self.layout.row(align=True)
        row.label(text=f"{RepresentationItemsData.data['total_items']} Items Found")

        if props.is_editing:
            row.operator("bim.disable_editing_representation_items", icon="CANCEL", text="")
        else:
            row.operator("bim.enable_editing_representation_items", icon="IMPORT", text="")
            return

        self.layout.template_list("BIM_UL_representation_items", "", props, "items", props, "active_item_index")

        item_is_active = props.active_item_index < len(props.items)
        if not item_is_active:
            return

        active_item = props.items[props.active_item_index]
        surface_style = active_item.surface_style
        surface_style_id = active_item.surface_style_id
        shape_aspect = active_item.shape_aspect

        row = self.layout.row(align=True)
        if props.is_editing_item_style:
            # NOTE: we currently support 1 item having just 1 style
            # when IfcStyledItem can actually have multiple styles
            prop_with_search(row, props, "representation_item_style", icon="SHADING_RENDERED", text="")
            row.operator("bim.edit_representation_item_style", icon="CHECKMARK", text="")
            row.operator("bim.disable_editing_representation_item_style", icon="CANCEL", text="")
        else:
            if surface_style:
                row.label(text=surface_style, icon="SHADING_RENDERED")
                op = row.operator("bim.styles_ui_select", icon="ZOOM_SELECTED", text="")
                op.style_id = surface_style_id
            else:
                row.label(text="No Surface Style", icon="MESH_UVSPHERE")
            row.operator("bim.enable_editing_representation_item_style", icon="GREASEPENCIL", text="")
            if surface_style:
                row.operator("bim.unassign_representation_item_style", icon="X", text="")

        row = self.layout.row()
        row.label(text=active_item.layer or "No Presentation Layer", icon="STICKY_UVS_LOC")

        if active_item.name.endswith("FaceSet"):
            if "UV" in active_item.tags:
                text = "Has UV mapping"
            else:
                text = "Has no UV mapping"
            layout.label(text=text, icon="UV")

            if "Colour" in active_item.tags:
                text = "Has colour mapping"
            else:
                text = "Has no colour mapping"
            layout.label(text=text, icon="COLOR")

        row = self.layout.row(align=True)
        if props.is_editing_item_shape_aspect:
            row.prop(props, "representation_item_shape_aspect", icon="SHAPEKEY_DATA", text="")
            row.operator("bim.edit_representation_item_shape_aspect", icon="CHECKMARK", text="")
            row.operator("bim.disable_editing_representation_item_shape_aspect", icon="CANCEL", text="")

            shape_aspect_attrs = props.shape_aspect_attrs
            self.layout.label(text="Shape Aspect Attributes:")
            self.layout.prop(shape_aspect_attrs, "name")
            self.layout.prop(shape_aspect_attrs, "description")
        else:
            row.label(text=shape_aspect or "No Shape Aspect", icon="SHAPEKEY_DATA")
            row.operator("bim.enable_editing_representation_item_shape_aspect", icon="GREASEPENCIL", text="")
            if shape_aspect:
                row.operator("bim.remove_representation_item_from_shape_aspect", icon="X", text="")


class BIM_PT_connections(Panel):
    bl_label = "Connections"
    bl_idname = "BIM_PT_connections"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_order = 1
    bl_parent_id = "BIM_PT_tab_geometric_relationships"

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        if not IfcStore.get_element(context.active_object.BIMObjectProperties.ifc_definition_id):
            return False
        return IfcStore.get_file()

    def draw(self, context):
        if not ConnectionsData.is_loaded:
            ConnectionsData.load()

        layout = self.layout
        props = context.active_object.BIMObjectProperties

        if not ConnectionsData.data["connections"] and not ConnectionsData.data["is_connection_realization"]:
            layout.label(text="No connections found")

        for connection in ConnectionsData.data["connections"]:
            row = self.layout.row(align=True)
            row.label(text=connection["Name"], icon="SNAP_ON" if connection["is_relating"] else "SNAP_OFF")
            row.label(text=connection["ConnectionType"])
            op = row.operator("bim.select_connection", icon="RESTRICT_SELECT_OFF", text="")
            op.connection = connection["id"]
            op = row.operator("bim.remove_connection", icon="X", text="")
            op.connection = connection["id"]

            if connection["realizing_elements"]:
                row = self.layout.row(align=True)
                connection_type = connection["realizing_elements_connection_type"]
                connection_type = f" ({connection_type})" if connection_type else ""
                row.label(text=f"Realizing elements{connection_type}:")

                for element in connection["realizing_elements"]:
                    row = self.layout.row(align=True)
                    obj = tool.Ifc.get_object(element)
                    row.operator("bim.select_entity", text="", icon="RESTRICT_SELECT_OFF").ifc_id = element.id()
                    row.label(text=obj.name)

        # display connections where element is connection realization
        connections = ConnectionsData.data["is_connection_realization"]
        if not connections:
            return

        row = self.layout.row(align=True)
        row.label(text="Element is connections realization:")
        for connection in connections:
            # NOTE: not displayed yet
            connection_type = connection["realizing_elements_connection_type"]
            connection_type = f" ({connection_type})" if connection_type else ""

            row = self.layout.row(align=True)

            connected_from = connection["connected_from"]
            obj = tool.Ifc.get_object(connected_from)
            row.operator("bim.select_entity", text="", icon="RESTRICT_SELECT_OFF").ifc_id = connected_from.id()
            row.label(text=obj.name)

            row.label(text="", icon="FORWARD")

            connected_to = connection["connected_to"]
            obj = tool.Ifc.get_object(connected_to)
            row.operator("bim.select_entity", text="", icon="RESTRICT_SELECT_OFF").ifc_id = connected_to.id()
            row.label(text=obj.name)


class BIM_PT_mesh(Panel):
    bl_label = "Representation Utilities"
    bl_idname = "BIM_PT_mesh"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_order = 2
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "BIM_PT_tab_representations"

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
        row = self.layout.row()
        row.label(text="Advanced Users Only", icon="ERROR")

        layout = self.layout

        row = layout.row()
        text = "Manually Save Representation"
        if tool.Ifc.is_edited(context.active_object):
            text += "*"
        row.operator("bim.update_representation", text=text)

        row = layout.row()
        row.operator("bim.copy_representation", text="Copy Mesh From Active To Selected")

        row = layout.row()
        op = row.operator("bim.update_representation", text="Convert To Tessellation")
        op.ifc_representation_class = "IfcTessellatedFaceSet"

        row = layout.row()
        op = row.operator("bim.update_representation", text="Convert To Rectangle Extrusion")
        op.ifc_representation_class = "IfcExtrudedAreaSolid/IfcRectangleProfileDef"

        row = layout.row()
        op = row.operator("bim.update_representation", text="Convert To Circle Extrusion")
        op.ifc_representation_class = "IfcExtrudedAreaSolid/IfcCircleProfileDef"

        row = layout.row()
        op = row.operator("bim.update_representation", text="Convert To Arbitrary Extrusion")
        op.ifc_representation_class = "IfcExtrudedAreaSolid/IfcArbitraryClosedProfileDef"

        row = layout.row()
        op = row.operator("bim.update_representation", text="Convert To Arbitrary Extrusion With Voids")
        op.ifc_representation_class = "IfcExtrudedAreaSolid/IfcArbitraryProfileDefWithVoids"

        if context.active_object and context.active_object.data:
            mprops = context.active_object.data.BIMMeshProperties
            row = layout.row()
            row.operator("bim.get_representation_ifc_parameters")
            for index, ifc_parameter in enumerate(mprops.ifc_parameters):
                row = layout.row(align=True)
                row.prop(ifc_parameter, "name", text="")
                row.prop(ifc_parameter, "value", text="")
                row.operator("bim.update_parametric_representation", icon="FILE_REFRESH", text="").index = index


class BIM_PT_placement(Panel):
    bl_label = "Placement"
    bl_idname = "BIM_PT_placement"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_order = 1
    bl_parent_id = "BIM_PT_tab_placement"
    bl_options = {"HIDE_HEADER"}

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.BIMObjectProperties.ifc_definition_id

    def draw(self, context):
        if not PlacementData.is_loaded:
            PlacementData.load()

        if not PlacementData.data["has_placement"]:
            row = self.layout.row()
            row.label(text="No Object Placement Found")
            return

        row = self.layout.row()
        row.prop(context.active_object, "location", text="Location")
        row = self.layout.row()
        row.prop(context.active_object, "rotation_euler", text="Rotation")

        if context.active_object.BIMObjectProperties.blender_offset_type != "NONE":
            row = self.layout.row(align=True)
            row.label(text="Blender Offset", icon="TRACKING_REFINE_FORWARDS")
            row.label(text=context.active_object.BIMObjectProperties.blender_offset_type)

            if context.active_object.BIMObjectProperties.blender_offset_type != "NOT_APPLICABLE":
                row = self.layout.row(align=True)
                row.label(text=PlacementData.data["original_x"], icon="EMPTY_AXIS")
                row.label(text=PlacementData.data["original_y"])
                row.label(text=PlacementData.data["original_z"])


class BIM_PT_derived_coordinates(Panel):
    bl_label = "Derived Coordinates"
    bl_idname = "BIM_PT_derived_coordinates"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_order = 3
    bl_parent_id = "BIM_PT_tab_placement"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def draw(self, context):
        if not DerivedCoordinatesData.is_loaded:
            DerivedCoordinatesData.load()

        row = self.layout.row()
        text = "Edit Object Placement"
        if tool.Ifc.is_moved(context.active_object):
            text += "*"
        row.operator("bim.edit_object_placement", text=text, icon="EXPORT")

        row = self.layout.row()
        row.label(text="XYZ Dimensions")

        row = self.layout.row(align=True)
        row.enabled = False
        row.prop(context.active_object, "dimensions", text="X", index=0, slider=True)
        row.prop(context.active_object, "dimensions", text="Y", index=1, slider=True)
        row.prop(context.active_object, "dimensions", text="Z", index=2, slider=True)

        row = self.layout.row(align=True)
        row.label(text="Min Global Z")
        row.label(text=DerivedCoordinatesData.data["min_global_z"])
        row = self.layout.row(align=True)
        row.label(text="Max Global Z")
        row.label(text=DerivedCoordinatesData.data["max_global_z"])

        if DerivedCoordinatesData.data["has_collection"]:
            row = self.layout.row(align=True)
            row.label(text="Min Decomposed Z")
            row.label(text=DerivedCoordinatesData.data["min_decomposed_z"])
            row = self.layout.row(align=True)
            row.label(text="Max Decomposed Z")
            row.label(text=DerivedCoordinatesData.data["max_decomposed_z"])

        if DerivedCoordinatesData.data["is_storey"]:
            row = self.layout.row(align=True)
            row.label(text="Storey Height")
            row.label(text=DerivedCoordinatesData.data["storey_height"])


class BIM_PT_workarounds(Panel):
    bl_label = "Vendor Workarounds"
    bl_idname = "BIM_PT_workarounds"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_parent_id = "BIM_PT_tab_geometric_relationships"

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


class BIM_UL_representation_items(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            icon = "MATERIAL" if item.surface_style else "MESH_UVSPHERE"
            row = layout.row(align=True)
            item_name = item.name
            if item.shape_aspect:
                item_name = f"{item.shape_aspect} {item_name}"
            row.label(text=item_name, icon=icon)
            if item.layer:
                row.label(text="", icon="STICKY_UVS_LOC")
            op = row.operator("bim.remove_representation_item", icon="X", text="")
            op.representation_item_id = item.ifc_definition_id
