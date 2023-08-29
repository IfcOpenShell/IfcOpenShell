# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import blenderbim.tool as tool
from bpy.types import Panel, Menu
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.helper import prop_with_search
from blenderbim.bim.module.geometry.data import RepresentationsData, ConnectionsData, DerivedPlacementsData


def object_menu(self, context):
    self.layout.separator()
    self.layout.operator("bim.override_object_duplicate_move", icon="PLUGIN")
    self.layout.operator("bim.override_object_delete", icon="PLUGIN")
    self.layout.operator("bim.override_paste_buffer", icon="PLUGIN")
    self.layout.menu("BIM_MT_object_set_origin", icon="PLUGIN")


class BIM_MT_object_set_origin(Menu):
    bl_idname = "BIM_MT_object_set_origin"
    bl_label = "IFC Set Origin"

    def draw(self, context):
        self.layout.operator(
            "bim.override_origin_set", icon="PLUGIN", text="IFC Geometry to Origin"
        ).origin_type = "GEOMETRY_ORIGIN"
        self.layout.operator(
            "bim.override_origin_set", icon="PLUGIN", text="IFC Origin to Geometry"
        ).origin_type = "ORIGIN_GEOMETRY"
        self.layout.operator(
            "bim.override_origin_set", icon="PLUGIN", text="IFC Origin to 3D Cursor"
        ).origin_type = "ORIGIN_CURSOR"
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


def BIM_PT_transform(self, context):
    if context.active_object and context.active_object.BIMObjectProperties.ifc_definition_id:
        row = self.layout.row(align=True)
        row.label(text="Blender Offset")
        row.label(text=context.active_object.BIMObjectProperties.blender_offset_type)

        row = self.layout.row()
        row.operator("bim.edit_object_placement")


class BIM_PT_derived_placements(Panel):
    bl_label = "Derived Placements"
    bl_idname = "BIM_PT_derived_placements"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_order = 1
    bl_parent_id = "OBJECT_PT_transform"

    def draw(self, context):
        if not DerivedPlacementsData.is_loaded:
            DerivedPlacementsData.load()

        row = self.layout.row(align=True)
        row.label(text="Min Global Z")
        row.label(text=DerivedPlacementsData.data["min_global_z"])
        row = self.layout.row(align=True)
        row.label(text="Max Global Z")
        row.label(text=DerivedPlacementsData.data["max_global_z"])

        if DerivedPlacementsData.data["has_collection"]:
            row = self.layout.row(align=True)
            row.label(text="Min Decomposed Z")
            row.label(text=DerivedPlacementsData.data["min_decomposed_z"])
            row = self.layout.row(align=True)
            row.label(text="Max Decomposed Z")
            row.label(text=DerivedPlacementsData.data["max_decomposed_z"])

        if DerivedPlacementsData.data["is_storey"]:
            row = self.layout.row(align=True)
            row.label(text="Storey Height")
            row.label(text=DerivedPlacementsData.data["storey_height"])


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
