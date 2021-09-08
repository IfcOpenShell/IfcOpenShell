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


import re
import bpy
import pytest
from blenderbim.bim.ifc import IfcStore


class NewFile:
    @pytest.fixture(autouse=True)
    def setup(self):
        IfcStore.purge()
        bpy.ops.wm.read_homefile(app_template="")


def scenario(function):
    def subfunction(self):
        run(function(self))

    return subfunction


def an_empty_ifc_project():
    bpy.ops.bim.create_project()


def i_add_a_cube():
    bpy.ops.mesh.primitive_cube_add()


def the_object_named_name_is_selected(name):
    obj = bpy.context.scene.objects.get(name)
    if not obj:
        assert False, 'The object "{name}" could not be selected'
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)


def i_select_value_in_prop(value, prop):
    exec(f'bpy.context.{prop} = "{value}"')


def i_press_operator(operator):
    exec(f"bpy.ops.{operator}()")


def the_object_named_name_exists(name):
    obj = bpy.data.objects.get(name)
    if not obj:
        assert False, f'The object "{name}" does not exist'
    return obj


def an_ifc_file_exists():
    ifc = IfcStore.get_file()
    if not ifc:
        assert False, "No IFC file is available"
    return ifc


def the_object_named_name_is_an_ifc_class(name, ifc_class):
    ifc = an_ifc_file_exists()
    element = ifc.by_id(the_object_named_name_exists(name).BIMObjectProperties.ifc_definition_id)
    assert element.is_a(ifc_class), f'Object "{name}" is a {element.is_a()}'


definitions = {
    "an empty IFC project": an_empty_ifc_project,
    "I add a cube": i_add_a_cube,
    'the object named "(.*)" is selected': the_object_named_name_is_selected,
    'I select "(.*)" in "(.*)"': i_select_value_in_prop,
    'I press "(.*)"': i_press_operator,
    'the object named "(.*)" is an "(.*)"': the_object_named_name_is_an_ifc_class,
    "an IFC file exists": an_ifc_file_exists,
}


# Super lightweight Gherkin implementation
def run(scenario):
    for line in scenario.split("\n"):
        line = line.strip()
        if not line:
            continue
        match = None
        for definition, callback in definitions.items():
            match = re.search(definition, line)
            if match:
                try:
                    callback(*match.groups())
                except AssertionError as e:
                    assert False, f"Failed: {line}, with error: {e}"
                break
        if not match:
            assert False, f"Definition not implemented: {line}"
    return True


def run_debug(scenario, blend_filepath=None):
    try:
        result = run(scenario)
    except Exception as e:
        if blend_filepath:
            bpy.ops.wm.save_as_mainfile(filepath=blend_filepath)
        assert False, e
    if blend_filepath:
        bpy.ops.wm.save_as_mainfile(filepath=blend_filepath)
    return result
