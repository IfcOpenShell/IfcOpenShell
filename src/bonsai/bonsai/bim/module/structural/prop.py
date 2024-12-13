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

from math import radians
import bpy
import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore
from bonsai.bim.prop import StrProperty, Attribute
from bonsai.bim.module.structural.data import StructuralLoadCasesData, StructuralLoadsData, BoundaryConditionsData, LoadGroupDecorationData
from bpy.types import PropertyGroup
from bpy.props import (
    PointerProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    CollectionProperty,
)

def get_load_groups_to_show(self, context):
    if not LoadGroupDecorationData.is_loaded:
        LoadGroupDecorationData.load()
    return LoadGroupDecorationData.data["load groups to show"]

def update_activity_type(self, context):
    LoadGroupDecorationData.is_loaded = False

def get_applicable_structural_load_types(self, context):
    if not StructuralLoadCasesData.is_loaded:
        StructuralLoadCasesData.load()
    return StructuralLoadCasesData.data["applicable_structural_load_types"]


def updateApplicableStructuralLoadTypes(self, context):
    StructuralLoadCasesData.data["applicable_structural_load_types"] = (
        StructuralLoadCasesData.applicable_structural_load_types()
    )


def get_applicable_structural_loads(self, context):
    if not StructuralLoadCasesData.is_loaded:
        StructuralLoadCasesData.load()
    return StructuralLoadCasesData.data["applicable_structural_loads"]


def get_structural_load_types(self, context):
    if not StructuralLoadsData.is_loaded:
        StructuralLoadsData.load()
    return StructuralLoadsData.data["structural_load_types"]


def get_boundary_condition_types(self, context):
    if not BoundaryConditionsData.is_loaded:
        BoundaryConditionsData.load()
    return BoundaryConditionsData.data["boundary_condition_types"]


def updateAxisAngle(self, context):
    if not self.axis_empty:
        return
    obj = context.active_object
    empty = self.axis_empty
    x_axis = obj.data.vertices[1].co - obj.data.vertices[0].co
    empty.location = obj.data.vertices[0].co
    empty.rotation_mode = "QUATERNION"
    empty.rotation_quaternion = x_axis.to_track_quat("X", "Z")
    empty.rotation_mode = "XYZ"
    empty.rotation_euler[0] = radians(self.axis_angle)


def updateConnectionCS(self, context):
    if not self.ccs_empty:
        return
    obj = context.active_object
    empty = self.ccs_empty
    empty.location = obj.data.vertices[0].co
    empty.rotation_mode = "XYZ"
    empty.rotation_euler[0] = radians(self.ccs_x_angle)
    empty.rotation_euler[1] = radians(self.ccs_y_angle)
    empty.rotation_euler[2] = radians(self.ccs_z_angle)


class StructuralAnalysisModel(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


class StructuralActivity(PropertyGroup):
    name: StringProperty(name="Name")
    applied_load_class: StringProperty(name="Applied Load Class")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


class StructuralLoad(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    number_of_inverse_references: IntProperty(name="Number of Inverse References")


class BoundaryCondition(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    number_of_inverse_references: IntProperty(name="Number of Inverse References")


class BIMStructuralProperties(PropertyGroup):
    structural_analysis_model_attributes: CollectionProperty(
        name="Structural Analysis Model Attributes", type=Attribute
    )
    is_editing: BoolProperty(name="Is Editing", default=False)
    structural_analysis_models: CollectionProperty(name="Structural Analysis Models", type=StructuralAnalysisModel)
    active_structural_analysis_model_index: IntProperty(name="Active Structural Analysis Model Index")
    active_structural_analysis_model_id: IntProperty(name="Active Structural Analysis Model Id")
    load_case_editing_type: StringProperty(name="Load Case Editing Type")
    load_case_attributes: CollectionProperty(name="Load Case Attributes", type=Attribute)
    active_load_case_id: IntProperty(name="Active Load Case Id")
    load_group_editing_type: StringProperty(name="Load Group Editing Type")
    # load_group_attributes: CollectionProperty(name="Load Group Attributes", type=Attribute)
    active_load_group_id: IntProperty(name="Active Load Group Id")
    applicable_structural_load_types: EnumProperty(
        items=get_applicable_structural_load_types,
        name="Applicable Structural Load Types",
        update=updateApplicableStructuralLoadTypes,
    )
    applicable_structural_loads: EnumProperty(items=get_applicable_structural_loads, name="Applicable Structural Loads")
    load_group_activities: CollectionProperty(name="Load Group Activities", type=StructuralActivity)
    active_load_group_activity_index: IntProperty(name="Active Load Group Activity Index")

    structural_loads: CollectionProperty(name="Structural Loads", type=StructuralLoad)
    active_structural_load_index: IntProperty(name="Active Structural Load Index")
    active_structural_load_id: IntProperty(name="Active Structural Load Id")
    is_editing_loads: BoolProperty(name="Is Editing Loads", default=False)
    structural_load_types: EnumProperty(items=get_structural_load_types, name="Structural Load Types")
    structural_load_attributes: CollectionProperty(name="Structural Load Attributes", type=Attribute)
    filtered_structural_loads: BoolProperty(name="Filtered Structural Loads", default=False)

    boundary_conditions: CollectionProperty(name="Boundary Conditions", type=BoundaryCondition)
    active_boundary_condition_index: IntProperty(name="Active Boundary Condition Index")
    active_boundary_condition_id: IntProperty(name="Active Boundary Condition Id")
    is_editing_boundary_conditions: BoolProperty(name="Is Editing Boundary Conditions", default=False)
    boundary_condition_types: EnumProperty(items=get_boundary_condition_types, name="Boundary Condition Types")
    boundary_condition_attributes: CollectionProperty(name="Boundary Condition Attributes", type=Attribute)
    filtered_boundary_conditions: BoolProperty(name="Filtered Boundary Conditions", default=False)

    show_loads: BoolProperty(name="Show Loads", default=False)
    update_load_repr: BoolProperty(name="Update Load Representation", default=False)
    enable_repr_auto_update: BoolProperty(name="Auto Update", default=False)
    reference_frame: EnumProperty(items=[("GLOBAL_COORDS","Global","Show loads in global reference frame"),
                                   ("LOCAL_COORDS","Local","Show loads in local reference frame")], name= "Reference Frame")
    activity_type: EnumProperty(items=[("Action","Actions","Show actions loads"),
                                 ("External Reaction","External Reactions","Show reactions on boundary conditions"),
                                 ("Internal Reactions","Internal Reactions","Show internal reactions on members")],
                                 name="Activity Type",
                                 update=update_activity_type)
    load_group_to_show: EnumProperty(items=get_load_groups_to_show, name="Load Groups")


class BIMObjectStructuralProperties(PropertyGroup):
    boundary_condition_attributes: CollectionProperty(name="Boundary Condition Attributes", type=Attribute)
    active_boundary_condition: IntProperty(name="Active Boundary Condition")
    active_connects_structural_member: IntProperty(name="Active Connects Structural Member")
    relating_structural_member: PointerProperty(name="Relating Structural Member", type=bpy.types.Object)
    is_editing_axis: BoolProperty(name="Is Editing Axis", default=False)
    axis_angle: FloatProperty(name="Axis Angle", update=updateAxisAngle)
    axis_empty: PointerProperty(name="Axis Empty", type=bpy.types.Object)

    # relating_structural_activity: PointerProperty(name="Relating Structural Activity", type=bpy.types.Object)
    is_editing_connection_cs: BoolProperty(name="Is Editing Connection CS", default=False)
    ccs_x_angle: FloatProperty(name="Connection CS X Angle", update=updateConnectionCS)
    ccs_y_angle: FloatProperty(name="Connection CS Y Angle", update=updateConnectionCS)
    ccs_z_angle: FloatProperty(name="Connection CS Z Angle", update=updateConnectionCS)
    ccs_empty: PointerProperty(name="CCS Empty", type=bpy.types.Object)
