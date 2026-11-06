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

import os
import re
from types import SimpleNamespace
from typing import TYPE_CHECKING

import bpy
import ifcopenshell.util.unit

import bonsai.bim.handler
import bonsai.bim.import_ifc as import_ifc
import bonsai.core.unit as core
import bonsai.tool as tool

if TYPE_CHECKING:
    from bpy.stub_internal import rna_enums


class AssignSceneUnits(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_scene_units"
    bl_label = "Assign Scene Units"
    bl_description = "Add new units based on the current Blender scene units and assign them as project default."
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.assign_scene_units(tool.Ifc, tool.Unit)
        core.load_units(tool.Unit)


class AssignUnit(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_unit"
    bl_label = "Assign Unit"
    bl_description = "Assign provided unit as the default project unit for it's unit type."
    bl_options = {"REGISTER", "UNDO"}
    unit: bpy.props.IntProperty()

    def _execute(self, context):
        core.assign_unit(tool.Ifc, tool.Unit, unit=tool.Ifc.get().by_id(self.unit))


class UnassignUnit(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_unit"
    bl_label = "Unassign Unit"
    bl_description = "Unassign the specified unit as the project default."
    bl_options = {"REGISTER", "UNDO"}
    unit: bpy.props.IntProperty()

    def _execute(self, context):
        core.unassign_unit(tool.Ifc, tool.Unit, unit=tool.Ifc.get().by_id(self.unit))


class LoadUnits(bpy.types.Operator):
    bl_idname = "bim.load_units"
    bl_label = "Load Units"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Open the loaded units"

    def execute(self, context) -> set["rna_enums.OperatorReturnItems"]:
        core.load_units(tool.Unit)
        return {"FINISHED"}


class DisableUnitEditingUI(bpy.types.Operator):
    bl_idname = "bim.disable_unit_editing_ui"
    bl_label = "Disable Unit Editing UI"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Close the editing units mode"

    def execute(self, context) -> set["rna_enums.OperatorReturnItems"]:
        core.disable_unit_editing_ui(tool.Unit)
        return {"FINISHED"}


class RemoveUnit(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_unit"
    bl_label = "Remove Unit"
    bl_options = {"REGISTER", "UNDO"}
    unit: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_unit(tool.Ifc, tool.Unit, unit=tool.Ifc.get().by_id(self.unit))


class AddConversionBasedUnit(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_conversion_based_unit"
    bl_label = "Add Conversion Based Unit"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.StringProperty()

    def _execute(self, context):
        core.add_conversion_based_unit(tool.Ifc, tool.Unit, name=self.name)


class AddMonetaryUnit(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_monetary_unit"
    bl_label = "Add Monetary Unit"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.add_monetary_unit(tool.Ifc, tool.Unit)


class AddSIUnit(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_si_unit"
    bl_label = "Add SI Unit"
    bl_options = {"REGISTER", "UNDO"}
    unit_type: bpy.props.StringProperty()

    def _execute(self, context):
        core.add_si_unit(tool.Ifc, tool.Unit, unit_type=self.unit_type)


class AddContextDependentUnit(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_context_dependent_unit"
    bl_label = "Add Context Dependent Unit"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.StringProperty()
    unit_type: bpy.props.StringProperty()

    def _execute(self, context):
        core.add_context_dependent_unit(tool.Ifc, tool.Unit, unit_type=self.unit_type, name=self.name)


class AddDerivedUnitElement(bpy.types.Operator):
    bl_idname = "bim.add_derived_unit_element"
    bl_label = "Add Derived Unit Element"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add a new named unit and exponent to the derived unit definition"

    def execute(self, context) -> set["rna_enums.OperatorReturnItems"]:
        props = tool.Unit.get_unit_props()
        props.derived_unit_elements.add()
        return {"FINISHED"}


class RemoveDerivedUnitElement(bpy.types.Operator):
    bl_idname = "bim.remove_derived_unit_element"
    bl_label = "Remove Derived Unit Element"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Remove this named unit and exponent from the derived unit definition"
    index: bpy.props.IntProperty()

    def execute(self, context) -> set["rna_enums.OperatorReturnItems"]:
        props = tool.Unit.get_unit_props()
        props.derived_unit_elements.remove(self.index)
        return {"FINISHED"}


class AddDerivedUnit(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_derived_unit"
    bl_label = "Add Derived Unit"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add a derived unit built from the defined named units and exponents"

    def _execute(self, context):
        props = tool.Unit.get_unit_props()
        elements = {}
        for element in props.derived_unit_elements:
            if not element.unit:
                self.report({"ERROR"}, "No named unit selected. Add a named unit (e.g. an SI unit) first.")
                return {"CANCELLED"}
            unit = tool.Ifc.get().by_id(int(element.unit))
            if unit in elements:
                self.report({"ERROR"}, f"Unit '{unit.Name}' is used in more than one element.")
                return {"CANCELLED"}
            elements[unit] = element.exponent
        if not elements:
            self.report({"ERROR"}, "A derived unit requires at least one element. Click 'Add Element' first.")
            return {"CANCELLED"}
        core.add_derived_unit(tool.Ifc, tool.Unit, unit_type=props.derived_unit_types, elements=elements)
        props.derived_unit_elements.clear()


class EnableEditingUnit(bpy.types.Operator):
    bl_idname = "bim.enable_editing_unit"
    bl_label = "Enable Editing Unit"
    bl_options = {"REGISTER", "UNDO"}
    unit: bpy.props.IntProperty()

    def execute(self, context) -> set["rna_enums.OperatorReturnItems"]:
        core.enable_editing_unit(tool.Unit, unit=tool.Ifc.get().by_id(self.unit))
        return {"FINISHED"}


class DisableEditingUnit(bpy.types.Operator):
    bl_idname = "bim.disable_editing_unit"
    bl_label = "Disable Editing Unit"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context) -> set["rna_enums.OperatorReturnItems"]:
        core.disable_editing_unit(tool.Unit)
        return {"FINISHED"}


class EditUnit(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_unit"
    bl_label = "Edit Unit"
    bl_options = {"REGISTER", "UNDO"}
    unit: bpy.props.IntProperty()

    def _execute(self, context):
        core.edit_unit(tool.Ifc, tool.Unit, unit=tool.Ifc.get().by_id(self.unit))


# Identifiers are what each converter takes: a length name for LENGTHUNIT, else "PREFIX/NAME" or a
# conversion based unit name. KEEP leaves the unit as it is.
KEEP = ("KEEP", "Unchanged", "Keep the current unit")
CONVERTIBLE_UNITS = {
    "LENGTHUNIT": (
        "Length",
        [
            ("MILLIMETER", "Millimeter", ""),
            ("CENTIMETER", "Centimeter", ""),
            ("DECIMETER", "Decimeter", ""),
            ("METER", "Meter", ""),
            ("KILOMETER", "Kilometer", ""),
            ("INCH", "Inch", ""),
            ("FOOT", "Foot", ""),
            ("MILE", "Mile", ""),
        ],
    ),
    "AREAUNIT": (
        "Area",
        [
            ("MILLI/SQUARE_METRE", "Square Millimeter", ""),
            ("CENTI/SQUARE_METRE", "Square Centimeter", ""),
            ("SQUARE_METRE", "Square Meter", ""),
            ("KILO/SQUARE_METRE", "Square Kilometer", ""),
            ("square inch", "Square Inch", ""),
            ("square foot", "Square Foot", ""),
            ("square yard", "Square Yard", ""),
            ("acre", "Acre", ""),
            ("square mile", "Square Mile", ""),
        ],
    ),
    "VOLUMEUNIT": (
        "Volume",
        [
            ("MILLI/CUBIC_METRE", "Cubic Millimeter", ""),
            ("CENTI/CUBIC_METRE", "Cubic Centimeter", ""),
            ("CUBIC_METRE", "Cubic Meter", ""),
            ("litre", "Liter", ""),
            ("cubic inch", "Cubic Inch", ""),
            ("cubic foot", "Cubic Foot", ""),
            ("cubic yard", "Cubic Yard", ""),
            ("gallon US", "Gallon (US)", ""),
            ("gallon UK", "Gallon (UK)", ""),
        ],
    ),
    "FORCEUNIT": (
        "Force",
        [
            ("NEWTON", "Newton", ""),
            ("KILO/NEWTON", "Kilonewton", ""),
            ("MEGA/NEWTON", "Meganewton", ""),
            ("lbf", "Pound-Force", ""),
            ("kip", "Kip", ""),
        ],
    ),
    "MASSUNIT": (
        "Mass",
        [
            ("GRAM", "Gram", ""),
            ("KILO/GRAM", "Kilogram", ""),
            ("tonne", "Tonne", ""),
            ("ounce", "Ounce", ""),
            ("pound", "Pound", ""),
            ("ton US", "Ton (US)", ""),
            ("ton UK", "Ton (UK)", ""),
        ],
    ),
    "PRESSUREUNIT": (
        "Pressure",
        [
            ("PASCAL", "Pascal", ""),
            ("KILO/PASCAL", "Kilopascal", ""),
            ("MEGA/PASCAL", "Megapascal", ""),
            ("psi", "PSI", ""),
            ("ksi", "KSI", ""),
        ],
    ),
    "TIMEUNIT": (
        "Time",
        [
            ("SECOND", "Second", ""),
            ("minute", "Minute", ""),
            ("hour", "Hour", ""),
            ("day", "Day", ""),
        ],
    ),
}
# Without an assigned unit, values are in SI units.
DEFAULT_UNITS = {
    "AREAUNIT": "SQUARE_METRE",
    "VOLUMEUNIT": "CUBIC_METRE",
    "FORCEUNIT": "NEWTON",
    "MASSUNIT": "KILO/GRAM",
    "PRESSUREUNIT": "PASCAL",
    "TIMEUNIT": "SECOND",
}


def unit_property(unit_type: str) -> bpy.props.EnumProperty:
    label, items = CONVERTIBLE_UNITS[unit_type]
    return bpy.props.EnumProperty(name=label, items=[KEEP, *items])


class ConvertUnits(bpy.types.Operator):
    bl_idname = "bim.convert_units"
    bl_label = "Convert Units"
    bl_description = (
        "Convert the project's length, area, volume, force, mass, pressure or time values to other units, "
        "and save it over the IFC file or as a new file"
    )
    bl_options = {"REGISTER"}
    lengthunit: unit_property("LENGTHUNIT")
    areaunit: unit_property("AREAUNIT")
    volumeunit: unit_property("VOLUMEUNIT")
    forceunit: unit_property("FORCEUNIT")
    massunit: unit_property("MASSUNIT")
    pressureunit: unit_property("PRESSUREUNIT")
    timeunit: unit_property("TIMEUNIT")
    save_as_new_file: bpy.props.BoolProperty(
        name="Save as New File",
        description="Save the converted project as a new IFC file and leave the current one untouched",
        default=False,
    )
    filepath: bpy.props.StringProperty(
        name="File",
        description="Leave empty to save next to the current IFC file, named after the new units",
        subtype="FILE_PATH",
        options={"SKIP_SAVE"},
    )

    @classmethod
    def poll(cls, context):
        if not tool.Ifc.get():
            cls.poll_message_set("No IFC project loaded.")
            return False
        if not tool.Ifc.get_path():
            cls.poll_message_set("Save the IFC project first.")
            return False
        return True

    def get_current_unit(self, unit_type: str) -> str:
        if not (unit := ifcopenshell.util.unit.get_project_unit(tool.Ifc.get(), unit_type)):
            return DEFAULT_UNITS.get(unit_type, KEEP[0])
        if unit_type == "LENGTHUNIT":
            return ifcopenshell.util.unit.get_full_unit_name(unit).replace("METRE", "METER")
        if unit.is_a("IfcSIUnit") and unit.Prefix:
            return f"{unit.Prefix}/{unit.Name}"
        return unit.Name

    def get_changes(self) -> list[tuple[str, str]]:
        changes = []
        for unit_type in CONVERTIBLE_UNITS:
            unit = getattr(self, unit_type.lower())
            if unit != KEEP[0] and unit != self.get_current_unit(unit_type):
                changes.append((unit_type, unit))
        return changes

    def get_unit_label(self, unit_type: str, unit: str) -> str:
        return next(label for identifier, label, _ in CONVERTIBLE_UNITS[unit_type][1] if identifier == unit)

    def invoke(self, context, event):
        for unit_type, (_, items) in CONVERTIBLE_UNITS.items():
            current_unit = self.get_current_unit(unit_type)
            setattr(self, unit_type.lower(), current_unit if current_unit in [i[0] for i in items] else KEEP[0])
        return context.window_manager.invoke_props_dialog(self, width=350, confirm_text="Convert and Save")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        for unit_type in CONVERTIBLE_UNITS:
            row = layout.row()
            row.prop(self, unit_type.lower())
            if getattr(self, unit_type.lower()) == KEEP[0]:
                unit = ifcopenshell.util.unit.get_project_unit(tool.Ifc.get(), unit_type)
                row.label(text=getattr(unit, "Name", None) or "Not assigned")
        layout.separator()
        layout.prop(self, "save_as_new_file")
        if self.save_as_new_file:
            layout.prop(self, "filepath")
            layout.label(text=f"Saves as {os.path.basename(self.get_filepath())}", icon="FILE")
        else:
            layout.label(text="The IFC file is converted and saved over.", icon="ERROR")
            layout.label(text="This cannot be undone.")

    def get_filepath(self) -> str:
        path = tool.Ifc.get_path()
        if not self.save_as_new_file:
            return path
        if self.filepath:
            return bpy.path.abspath(self.filepath)
        stem, ext = os.path.splitext(path)
        labels = [self.get_unit_label(t, u).lower() for t, u in self.get_changes()] or ["converted"]
        return f"{stem}_{'_'.join(re.findall(r'[a-z0-9]+', ' '.join(labels)))}{ext}"

    def execute(self, context):
        if not (changes := self.get_changes()):
            self.report({"ERROR"}, "No unit was changed.")
            return {"CANCELLED"}

        filepath = self.get_filepath()
        if self.save_as_new_file and os.path.normcase(os.path.abspath(filepath)) == os.path.normcase(
            os.path.abspath(tool.Ifc.get_path())
        ):
            self.report({"ERROR"}, "Choose a different file than the one currently loaded.")
            return {"CANCELLED"}

        converted = tool.Ifc.get()
        for unit_type, unit in changes:
            if unit_type == "LENGTHUNIT":
                converted = ifcopenshell.util.unit.convert_file_length_units(converted, unit)
            else:
                prefix, _, name = unit.rpartition("/")
                converted = ifcopenshell.util.unit.convert_file_units(converted, unit_type, name, prefix or None)
        converted.write(filepath)

        # The conversion keeps every entity id and Blender geometry is always in meters,
        # so relink the open session to the converted file rather than reloading the project.
        # This keeps the workspace, viewports and drawing state as they are.
        props = tool.Blender.get_bim_props()
        if self.save_as_new_file:
            is_relative = props.ifc_file and not os.path.isabs(props.ifc_file) and bpy.data.is_saved
            props.ifc_file = bpy.path.relpath(filepath) if is_relative else filepath
        bonsai.bim.handler.loadIfcStore(context.scene)
        tool.Blender.clear_undo_history()
        tool.Loader.set_unit_scale(ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get()))
        import_ifc.IfcImporter.set_units(SimpleNamespace(file=tool.Ifc.get()))
        # Annotation decorations still hold data from the old file until the drawing is activated again.
        if tool.Drawing.is_drawing_active() and (drawing_id := tool.Drawing.get_document_props().active_drawing_id):
            bpy.ops.bim.activate_drawing(drawing=drawing_id, should_view_from_camera=False)
        summary = ", ".join(
            f"{CONVERTIBLE_UNITS[t][0].lower()} to {self.get_unit_label(t, u).lower()}" for t, u in changes
        )
        self.report({"INFO"}, f"Converted {summary}")
        return {"FINISHED"}
