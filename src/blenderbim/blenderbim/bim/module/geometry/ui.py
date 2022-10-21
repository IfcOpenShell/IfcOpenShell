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
from bpy.types import Panel
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.helper import prop_with_search
from blenderbim.bim.module.geometry.data import RepresentationsData, ConnectionsData, DerivedPlacementsData


class BIM_PT_representations(Panel):
    bl_label = "IFC Representations"
    bl_idname = "BIM_PT_representations"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_parent_id = "BIM_PT_geometry_object"

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

        if not RepresentationsData.data["representations"]:
            layout.label(text="No representations found")

        row = layout.row(align=True)
        prop_with_search(row, context.scene.BIMRootProperties, "contexts", text="")
        row.operator("bim.add_representation", icon="ADD", text="")

        for representation in RepresentationsData.data["representations"]:
            row = self.layout.row(align=True)
            row.label(text=representation["ContextType"])
            row.label(text=representation["ContextIdentifier"])
            row.label(text=representation["TargetView"])
            row.label(text=representation["RepresentationType"])
            op = row.operator("bim.switch_representation", icon="OUTLINER_DATA_MESH", text="")
            op.should_switch_all_meshes = True
            op.should_reload = True
            op.ifc_definition_id = representation["id"]
            op.disable_opening_subtractions = False
            row.operator("bim.remove_representation", icon="X", text="").representation_id = representation["id"]


class BIM_PT_connections(Panel):
    bl_label = "IFC Connections"
    bl_idname = "BIM_PT_connections"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_parent_id = "BIM_PT_geometry_object"

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

        if not ConnectionsData.data["connections"]:
            layout.label(text="No connections found")

        for connection in ConnectionsData.data["connections"]:
            row = self.layout.row(align=True)
            row.label(text=connection["Name"], icon="SNAP_ON" if connection["is_relating"] else "SNAP_OFF")
            row.label(text=connection["ConnectionType"])
            op = row.operator("bim.select_connection", icon="RESTRICT_SELECT_OFF", text="")
            op.connection = connection["id"]
            op = row.operator("bim.remove_connection", icon="X", text="")
            op.connection = connection["id"]


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

        row = layout.row()
        row.operator("bim.copy_representation")

        row = layout.row()
        row.operator("bim.update_representation")

        row = layout.row()
        op = row.operator("bim.update_representation", text="Update Mesh As Tessellation")
        op.ifc_representation_class = "IfcTessellatedFaceSet"

        row = layout.row()
        op = row.operator("bim.update_representation", text="Update Mesh As Rectangle Extrusion")
        op.ifc_representation_class = "IfcExtrudedAreaSolid/IfcRectangleProfileDef"

        row = layout.row()
        op = row.operator("bim.update_representation", text="Update Mesh As Circle Extrusion")
        op.ifc_representation_class = "IfcExtrudedAreaSolid/IfcCircleProfileDef"

        row = layout.row()
        op = row.operator("bim.update_representation", text="Update Mesh As Arbitrary Extrusion")
        op.ifc_representation_class = "IfcExtrudedAreaSolid/IfcArbitraryClosedProfileDef"

        row = layout.row()
        op = row.operator("bim.update_representation", text="Update Mesh As Arbitrary Extrusion With Voids")
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
        row = self.layout.row(align=True)
        row.label(text="Blender Offset")
        row.label(text=context.active_object.BIMObjectProperties.blender_offset_type)

        row = self.layout.row()
        row.operator("bim.edit_object_placement")


class BIM_PT_derived_placements(Panel):
    bl_label = "IFC Derived Placements"
    bl_idname = "BIM_PT_derived_placements"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
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
