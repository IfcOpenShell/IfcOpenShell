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

from typing import TYPE_CHECKING

import bpy

from bpy.types import PropertyGroup
from bpy.props import (
    IntProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    IntVectorProperty
)
#from .util import Settings, LoadSelection, NumberFormatting, NumberingSystems, SaveNumber, Storeys

class BIMNumberingProperties(PropertyGroup):
    settings_name: StringProperty(
        name="Settings name",
        description="Name for saving the current settings",
        default=""
    ) # pyright: ignore[reportInvalidTypeForm]

    # def get_saved_settings_items(self, context):
    #     settings_names = Settings.get_settings_names()
    #     if not settings_names:
    #         return [("NONE", "No saved settings", "")]
    #     return [(name, name, "") for name in settings_names]

    # saved_settings : EnumProperty(
    #     name="Load settings",
    #     description="Select which saved settings to load",
    #     items=get_saved_settings_items
    # ) # pyright: ignore[reportInvalidTypeForm]

    # selected_toggle: BoolProperty(
    #     name="Selected only",
    #     description="Only number selected objects",
    #     default=False,
    #     update=NumberFormatting.update_format_preview
    # ) # pyright: ignore[reportInvalidTypeForm]

    # visible_toggle: BoolProperty(
    #     name="Visible only",
    #     description="Only number visible objects",
    #     default=False,
    #     update=NumberFormatting.update_format_preview
    # ) # pyright: ignore[reportInvalidTypeForm]
    
    # parent_type: EnumProperty(
    #     name="Parent Type",
    #     description="Select the parent type for numbering",
    #     items=[
    #         ("IfcElement", "IfcElement", "Number IFC elements"),
    #         ("IfcProduct", "IfcProduct", "Number IFC products"),
    #         ("IfcGridAxis", "IfcGridAxis", "Number IFC grid axes"),
    #         ("Other", "Other", "Input which IFC entities to number")
    #     ],
    #     default="IfcElement",
    #     update = LoadSelection.update_objects
    # ) # pyright: ignore[reportInvalidTypeForm]

    # parent_type_other : StringProperty(
    #     name="Other Parent Type",
    #     description="Input which IFC entities to number",
    #     default="IfcElement",
    #     update = LoadSelection.update_objects
    # ) # pyright: ignore[reportInvalidTypeForm]

    # def update_selected_types(self, context):
    #     NumberFormatting.update_format_preview(self, context)
    #     SaveNumber.update_pset_names(self, context)

    # selected_types: EnumProperty(
    #     name="Of type",
    #     description="Select which types of elements to number",
    #     items= LoadSelection.get_possible_types,
    #     options={'ENUM_FLAG'},
    #     update=update_selected_types
    # ) # pyright: ignore[reportInvalidTypeForm]

    # x_direction: EnumProperty(
    #     name="X",
    #     description="Select axis direction for numbering elements",
    #     items=[
    #         ("1", "+", "Number elements in order of increasing X coordinate"),
    #         ("-1", "-", "Number elements in order of decreasing X coordinate")
    #     ],
    #     default="1",
    # ) # pyright: ignore[reportInvalidTypeForm]

    # y_direction: EnumProperty(
    #     name="Y",
    #     description="Select axis direction for numbering elements",
    #     items=[
    #         ("1", "+", "Number elements in order of increasing Y coordinate"),
    #         ("-1", "-", "Number elements in order of decreasing Y coordinate")
    #     ],
    #     default="1"
    # ) # pyright: ignore[reportInvalidTypeForm]

    # z_direction: EnumProperty(
    #     name="Z",
    #     description="Select axis direction for numbering elements",
    #     items=[
    #         ("1", "+", "Number elements in order of increasing Z coordinate"),
    #         ("-1", "-", "Number elements in order of decreasing Z coordinate")
    #     ],
    #     default="1"
    # ) # pyright: ignore[reportInvalidTypeForm]

    # axis_order: EnumProperty(
    #     name="Axis order",
    #     description="Order of axes in numbering elements",
    #     items=[
    #         ("XYZ", "X, Y, Z", "Number elements in X, Y, Z order"),
    #         ("XZY", "X, Z, Y", "Number elements in X, Z, Y order"),
    #         ("YXZ", "Y, X, Z", "Number elements in Y, X, Z order"),
    #         ("YZX", "Y, Z, X", "Number elements in Y, Z, X order"),
    #         ("ZXY", "Z, X, Y", "Number elements in Z, X, Y order"),
    #         ("ZYX", "Z, Y, X", "Number elements in Z, Y, X order")
    #     ],
    #     default="ZYX"
    # ) # pyright: ignore[reportInvalidTypeForm]

    # location_type: EnumProperty(
    #     name="Reference location",
    #     description="Location to use for sorting elements",
    #     items=[
    #         ("CENTER", "Center", "Use object center for sorting"),
    #         ("BOUNDING_BOX", "Bounding Box", "Use object bounding box for sorting"),
    #     ],
    #     default="BOUNDING_BOX"
    # ) # pyright: ignore[reportInvalidTypeForm]

    # precision: IntVectorProperty(
    #     name="Precision",
    #     description="Precision for sorting elements in X, Y and Z direction",
    #     default=(1, 1, 1),
    #     min=1,
    #     size=3
    # ) # pyright: ignore[reportInvalidTypeForm]

    # initial_element_number: IntProperty(
    #     name="{E}",
    #     description="Initial number for numbering elements",
    #     default=1,
    #     update=NumberFormatting.update_format_preview
    # ) # pyright: ignore[reportInvalidTypeForm]

    # initial_type_number: IntProperty(
    #     name="{T}",
    #     description="Initial number for numbering elements within type",
    #     default=1,
    #     update=NumberFormatting.update_format_preview
    # ) # pyright: ignore[reportInvalidTypeForm]

    # initial_storey_number: IntProperty(
    #     name="{S}",
    #     description="Initial number for numbering storeys",
    #     default=0,
    #     update=NumberFormatting.update_format_preview
    # ) # pyright: ignore[reportInvalidTypeForm]

    # numberings_enum = lambda self, initial : [
    #         ("number", NumberingSystems.get_numbering_preview("number", initial), "Use numbers. Negative numbers are shown with brackets"),
    #         ("number_ext", NumberingSystems.get_numbering_preview("number_ext", initial), "Use numbers padded with zeroes to a fixed length based on the number of objects selected. Negative numbers are shown with brackets."),
    #         ("lower_letter", NumberingSystems.get_numbering_preview("lower_letter", initial), "Use lowercase letters, continuing with aa, ab, ... where negative numbers are shown with brackets."),
    #         ("upper_letter", NumberingSystems.get_numbering_preview("upper_letter", initial), "Use uppercase letters, continuing with AA, AB, ... where negative numbers are shown with brackets."),
    # ]

    # custom_storey_enum = [("custom", "Custom", "Use custom numbering for storeys")]

    # element_numbering: EnumProperty(
    #     name="{E}",
    #     description="Select numbering system for element numbering",
    #     items=lambda self, context: self.numberings_enum(self.initial_element_number),
    #     update=NumberFormatting.update_format_preview
    # )    # pyright: ignore[reportInvalidTypeForm]

    # type_numbering: EnumProperty(
    #     name="{T}",
    #     description="Select numbering system for numbering within types",
    #     items=lambda self, context: self.numberings_enum(self.initial_type_number),
    #     update=NumberFormatting.update_format_preview
    # )    # pyright: ignore[reportInvalidTypeForm]

    # def update_storey_numbering(self, context):
    #     if self.storey_numbering == "custom":
    #         self.initial_storey_number = 0
    
    # storey_numbering: EnumProperty(
    #     name="{S}",
    #     description="Select numbering system for numbering storeys. Storeys are numbered in positive Z-order by default.",
    #     items=lambda self, context: self.numberings_enum(self.initial_storey_number) + self.custom_storey_enum,
    #     update=update_storey_numbering
    # )    # pyright: ignore[reportInvalidTypeForm]

    # custom_storey: EnumProperty(
    #     name = "Storey",
    #     description = "Select storey to number",
    #     items = lambda self, _: [(storey.Name, storey.Name, f"{storey.Name}\nID: {storey.GlobalId}") for storey in Storeys.get_storeys(Settings.to_dict(self))],
    #     update = Storeys.update_custom_storey
    # ) # pyright: ignore[reportInvalidTypeForm]

    # custom_storey_number: IntProperty(
    #     name = "Storey number",
    #     description = f"Set custom storey number for selected storey, stored in {Storeys.settings['pset_name']} in the IFC element",
    #     get = Storeys.get_custom_storey_number,
    #     set = Storeys.set_custom_storey_number
    # ) # pyright: ignore[reportInvalidTypeForm]
    
    # format: StringProperty(
    #     name="Format",
    #     description="Format string for selected IFC type.\n" \
    #     "{E}: element number \n" \
    #     "{T}: number within type \n" \
    #     "{S}: number of storey\n" \
    #     "[T]: first letter of type name\n" \
    #     "[TT] : all capitalized letters in type name\n" \
    #     "[TF]: full type name",
    #     default="E{E}S{S}[T]{T}",
    #     update=NumberFormatting.update_format_preview
    # ) # pyright: ignore[reportInvalidTypeForm]

    # save_type : EnumProperty(
    #     name="Type of number storage",
    #     items = [("Attribute", "Attribute", "Store number in an attribute of the IFC element"),
    #              ("Pset", "Pset", "Store number in a Pset of the IFC element")
    #     ],
    #     default = "Attribute",
    #     update = SaveNumber.update_pset_names
    # ) # pyright: ignore[reportInvalidTypeForm]

    # attribute_name : EnumProperty(
    #     name="Attribute name",
    #     description="Name of the attribute to store the number",
    #     items = [("Tag", "Tag", "Store number in IFC Tag attribute"),
    #              ("Name", "Name", "Store number in IFC Name attribute"),
    #              ("Description", "Description", "Store number in IFC Description attribute"),
    #              ("AxisTag", "AxisTag", "Store number in IFC AxisTag attribute, used for IFCGridAxis"),
    #              ("Other", "Other", "Input in which IFC attribute to store the number")
    #             ],
    #     default="Tag"
    # ) # pyright: ignore[reportInvalidTypeForm]

    # attribute_name_other : StringProperty(
    #     name="Other attribute name",
    #     description="Name of the other attribute to store the number",
    #     default="Tag"
    # ) # pyright: ignore[reportInvalidTypeForm]

    # def get_pset_names(self, context):
    #     return SaveNumber.pset_names
    
    # pset_name : EnumProperty(
    #     name="Pset name",
    #     description="Name of the Pset to store the number",
    #     items = get_pset_names
    # ) # pyright: ignore[reportInvalidTypeForm]

    # property_name : StringProperty(
    #     name="Property name",
    #     description="Name of the property to store the number",
    #     default="Number"
    # ) # pyright: ignore[reportInvalidTypeForm]

    # custom_pset_name : StringProperty(
    #     name="Custom Pset name",
    #     description="Name of the custom Pset to store the number",
    #     default="Pset_Numbering"
    # ) # pyright: ignore[reportInvalidTypeForm]

    # remove_toggle: BoolProperty(
    #     name="Remove numbers from unselected objects",
    #     description="Remove numbers from unselected objects in the scene",
    #     default=True
    # ) # pyright: ignore[reportInvalidTypeForm]

    # check_duplicates_toggle: BoolProperty(
    #     name="Check for duplicate numbers",
    #     description="Check for duplicate numbers in all objects in the scene",
    #     default=True
    # ) # pyright: ignore[reportInvalidTypeForm]

    if TYPE_CHECKING:
        settings_name: str
