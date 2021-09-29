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

import os
import bpy
from blenderbim.bim.ifc import IfcStore
from pytest_bdd import scenarios, given, when, then, parsers

scenarios("feature")

variables = {"cwd": os.getcwd(), "ifc": "IfcStore.get_file()"}


def replace_variables(value):
    for key, new_value in variables.items():
        value = value.replace("{" + key + "}", str(new_value))
    return value


@given("an empty IFC project")
def an_empty_ifc_project():
    IfcStore.purge()
    bpy.ops.wm.read_homefile(app_template="")
    while bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[0])
    bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
    bpy.ops.bim.create_project()


@when(parsers.parse('I press "{operator}"'))
def i_press_operator(operator):
    operator = replace_variables(operator)
    if "(" in operator:
        exec(f"bpy.ops.{operator}")
    else:
        exec(f"bpy.ops.{operator}()")


@when(parsers.parse('the variable "{key}" is "{value}"'))
def the_variable_key_is_value(key, value):
    variables[key] = eval(replace_variables(value))


@then("nothing happens")
def nothing_happens():
    pass


@then(parsers.parse('"{prop}" is "{value}"'))
def prop_is_value(prop, value):
    value = replace_variables(value)
    is_value = False
    try:
        exec(f'assert bpy.context.{prop} == "{value}"')
        is_value = True
    except:
        try:
            exec(f"assert bpy.context.{prop} == {value}")
            is_value = True
        except:
            try:
                exec(f"assert list(bpy.context.{prop}) == {value}")
                is_value = True
            except:
                pass
    if not is_value:
        actual_value = eval(f"bpy.context.{prop}")
        assert False, f"Value is {actual_value}"
