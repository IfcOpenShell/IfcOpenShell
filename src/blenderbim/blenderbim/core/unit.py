# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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


def assign_scene_units(ifc, unit):
    length_name = unit.get_scene_unit_name("length")
    area_name = unit.get_scene_unit_name("area")
    volume_name = unit.get_scene_unit_name("volume")

    if unit.is_scene_unit_metric():
        prefix = unit.get_scene_unit_si_prefix()
        lengthunit = ifc.run("unit.add_si_unit", unit_type="LENGTHUNIT", name=length_name, prefix=prefix)
        areaunit = ifc.run("unit.add_si_unit", unit_type="AREAUNIT", name=area_name, prefix=prefix)
        volumeunit = ifc.run("unit.add_si_unit", unit_type="VOLUMEUNIT", name=volume_name, prefix=prefix)
    else:
        lengthunit = ifc.run("unit.add_conversion_based_unit", name=length_name)
        areaunit = ifc.run("unit.add_conversion_based_unit", name=area_name)
        volumeunit = ifc.run("unit.add_conversion_based_unit", name=volume_name)

    planeangleunit = ifc.run("unit.add_conversion_based_unit", name="degree")

    ifc.run("unit.assign_unit", units=[lengthunit, areaunit, volumeunit, planeangleunit])


def assign_unit(ifc, unit_tool, unit=None):
    ifc.run("unit.assign_unit", units=[unit])
    unit_tool.import_units()


def unassign_unit(ifc, unit_tool, unit=None):
    ifc.run("unit.unassign_unit", units=[unit])
    unit_tool.import_units()


def load_units(unit):
    unit.import_units()
    unit.enable_editing_units()


def disable_unit_editing_ui(unit):
    unit.disable_editing_units()


def remove_unit(ifc, unit_tool, unit=None):
    ifc.run("unit.remove_unit", unit=unit)
    unit_tool.import_units()


def add_monetary_unit(ifc, unit):
    result = ifc.run("unit.add_monetary_unit")
    unit.import_units()
    return result


def add_si_unit(ifc, unit, unit_type=None):
    result = ifc.run("unit.add_si_unit", unit_type=unit_type, name=unit.get_si_name_from_unit_type(unit_type))
    unit.import_units()
    return result


def add_context_dependent_unit(ifc, unit, unit_type=None, name=None):
    result = ifc.run("unit.add_context_dependent_unit", unit_type=unit_type, name=name)
    unit.import_units()
    return result


def add_conversion_based_unit(ifc, unit, name=None):
    result = ifc.run("unit.add_conversion_based_unit", name=name)
    unit.import_units()
    return result


def enable_editing_unit(unit_tool, unit=None):
    unit_tool.set_active_unit(unit)
    unit_tool.import_unit_attributes(unit)


def disable_editing_unit(unit):
    unit.clear_active_unit()


def edit_unit(ifc, unit_tool, unit=None):
    attributes = unit_tool.export_unit_attributes()
    if unit_tool.is_unit_class(unit, "IfcMonetaryUnit"):
        ifc.run("unit.edit_monetary_unit", unit=unit, attributes=attributes)
    elif unit_tool.is_unit_class(unit, "IfcDerivedUnit"):
        ifc.run("unit.edit_derived_unit", unit=unit, attributes=attributes)
    elif unit_tool.is_unit_class(unit, "IfcNamedUnit"):
        ifc.run("unit.edit_named_unit", unit=unit, attributes=attributes)
    unit_tool.import_units()
    unit_tool.clear_active_unit()
