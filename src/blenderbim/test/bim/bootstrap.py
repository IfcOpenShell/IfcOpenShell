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
import re
import bpy
import pytest
import webbrowser
import blenderbim
import ifcopenshell
import ifcopenshell.util.representation
from blenderbim.bim.ifc import IfcStore

# Monkey-patch webbrowser opening since we want to test headlessly
webbrowser.open = lambda x: True


class NewFile:
    @pytest.fixture(autouse=True)
    def setup(self):
        IfcStore.purge()
        bpy.ops.wm.read_homefile(app_template="")


def scenario(function):
    def subfunction(self):
        run(function(self))

    return subfunction


def scenario_debug(function):
    def subfunction(self):
        run_debug(function(self))

    return subfunction


def an_empty_ifc_project():
    bpy.ops.bim.create_project()


def i_add_a_cube():
    bpy.ops.mesh.primitive_cube_add()


def i_add_a_cube_of_size_size_at_location(size, location):
    bpy.ops.mesh.primitive_cube_add(size=float(size), location=[float(co) for co in location.split(",")])


def the_object_name_is_selected(name):
    bpy.ops.object.select_all(action="DESELECT")
    additionally_the_object_name_is_selected(name)


def additionally_the_object_name_is_selected(name):
    obj = bpy.context.scene.objects.get(name)
    if not obj:
        assert False, 'The object "{name}" could not be selected'
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)


def i_set_prop_to_value(prop, value):
    try:
        exec(f'bpy.context.{prop} = "{value}"')
    except:
        exec(f"bpy.context.{prop} = {value}")


def i_enable_prop(prop):
    exec(f"bpy.context.{prop} = True")


def i_press_operator(operator):
    if "(" in operator:
        exec(f"bpy.ops.{operator}")
    else:
        exec(f"bpy.ops.{operator}()")


def the_object_name_exists(name):
    obj = bpy.data.objects.get(name)
    if not obj:
        assert False, f'The object "{name}" does not exist'
    return obj


def an_ifc_file_exists():
    ifc = IfcStore.get_file()
    if not ifc:
        assert False, "No IFC file is available"
    return ifc


def the_object_name_is_an_ifc_class(name, ifc_class):
    ifc = an_ifc_file_exists()
    element = ifc.by_id(the_object_name_exists(name).BIMObjectProperties.ifc_definition_id)
    assert element.is_a(ifc_class), f'Object "{name}" is a {element.is_a()}'


def the_object_name_is_not_an_ifc_element(name):
    id = the_object_name_exists(name).BIMObjectProperties.ifc_definition_id
    assert id == 0, f"The ID is {id}"


def the_object_name_is_in_the_collection_collection(name, collection):
    assert collection in [c.name for c in the_object_name_exists(name).users_collection]


def the_collection_name1_is_in_the_collection_name2(name1, name2):
    assert bpy.data.collections.get(name2).children.get(name1)


def the_object_name_is_placed_in_the_collection_collection(name, collection):
    obj = the_object_name_exists(name)
    [c.objects.unlink(obj) for c in obj.users_collection]
    bpy.data.collections.get(collection).objects.link(obj)


def the_object_name_has_a_type_representation_of_context(name, type, context):
    ifc = an_ifc_file_exists()
    element = ifc.by_id(the_object_name_exists(name).BIMObjectProperties.ifc_definition_id)
    context, subcontext, target_view = context.split("/")
    assert ifcopenshell.util.representation.get_representation(
        element, context, subcontext or None, target_view or None
    )


def the_object_name_is_contained_in_container_name(name, container_name):
    ifc = an_ifc_file_exists()
    element = ifc.by_id(the_object_name_exists(name).BIMObjectProperties.ifc_definition_id)
    container = ifcopenshell.util.element.get_container(element)
    if not container:
        assert False, f'Object "{name}" is not in any container'
    assert container.Name == container_name, f'Object "{name}" is in {container}'


def i_duplicate_the_selected_objects():
    bpy.ops.object.duplicate_move()
    blenderbim.bim.handler.active_object_callback()


def i_delete_the_selected_objects():
    bpy.ops.object.delete()
    blenderbim.bim.handler.active_object_callback()


def the_object_name1_and_name2_are_different_elements(name1, name2):
    ifc = an_ifc_file_exists()
    element1 = ifc.by_id(the_object_name_exists(name1).BIMObjectProperties.ifc_definition_id)
    element2 = ifc.by_id(the_object_name_exists(name2).BIMObjectProperties.ifc_definition_id)
    assert element1 != element2, f"Objects {name1} and {name2} have same elements {element1} and {element2}"


def the_file_name_should_contain_value(name, value):
    with open(name, "r") as f:
        assert value in f.read()


def the_object_name1_has_a_boolean_difference_by_name2(name1, name2):
    obj = the_object_name_exists(name1)
    for modifier in obj.modifiers:
        if modifier.type == "BOOLEAN" and modifier.object and modifier.object.name == name2:
            return True
    assert False, "No boolean found"


def the_object_name1_has_no_boolean_difference_by_name2(name1, name2):
    obj = the_object_name_exists(name1)
    for modifier in obj.modifiers:
        if modifier.type == "BOOLEAN" and modifier.object and modifier.object.name == name2:
            assert False, "A boolean was found"


def the_object_name_is_voided_by_void(name, void):
    ifc = IfcStore.get_file()
    element = ifc.by_id(the_object_name_exists(name).BIMObjectProperties.ifc_definition_id)
    for rel in element.HasOpenings:
        if rel.RelatedOpeningElement.Name == void:
            return True
    assert False, "No void found"


def the_object_name_is_not_voided_by_void(name, void):
    ifc = IfcStore.get_file()
    element = ifc.by_id(the_object_name_exists(name).BIMObjectProperties.ifc_definition_id)
    for rel in element.HasOpenings:
        if rel.RelatedOpeningElement.Name == void:
            assert False, "A void was found"


def the_object_name_should_display_as_mode(name, mode):
    assert the_object_name_exists(name).display_type == mode


def the_object_name_has_number_vertices(name, number):
    total = len(the_object_name_exists(name).data.vertices)
    assert total == int(number), f"We found {total} vertices"


definitions = {
    "an empty IFC project": an_empty_ifc_project,
    "I add a cube": i_add_a_cube,
    'I add a cube of size "([0-9]+)" at "(.*)"': i_add_a_cube_of_size_size_at_location,
    'the object "(.*)" is selected': the_object_name_is_selected,
    'additionally the object "(.*)" is selected': additionally_the_object_name_is_selected,
    'I set "(.*)" to "(.*)"': i_set_prop_to_value,
    'I enable "(.*)"': i_enable_prop,
    'I press "(.*)"': i_press_operator,
    'the object "(.*)" is an "(.*)"': the_object_name_is_an_ifc_class,
    'the object "(.*)" is not an IFC element': the_object_name_is_not_an_ifc_element,
    'the object "(.*)" is in the collection "(.*)"': the_object_name_is_in_the_collection_collection,
    'the collection "(.*)" is in the collection "(.*)"': the_collection_name1_is_in_the_collection_name2,
    "an IFC file exists": an_ifc_file_exists,
    'the object "(.*)" has a "(.*)" representation of "(.*)"': the_object_name_has_a_type_representation_of_context,
    'the object "(.*)" is placed in the collection "(.*)"': the_object_name_is_placed_in_the_collection_collection,
    'the object "(.*)" is contained in "(.*)"': the_object_name_is_contained_in_container_name,
    "I duplicate the selected objects": i_duplicate_the_selected_objects,
    "I delete the selected objects": i_delete_the_selected_objects,
    'the object "(.*)" and "(.*)" are different elements': the_object_name1_and_name2_are_different_elements,
    'the file "(.*)" should contain "(.*)"': the_file_name_should_contain_value,
    'the object "(.*)" has a boolean difference by "(.*)"': the_object_name1_has_a_boolean_difference_by_name2,
    'the object "(.*)" has no boolean difference by "(.*)"': the_object_name1_has_no_boolean_difference_by_name2,
    'the object "(.*)" is voided by "(.*)"': the_object_name_is_voided_by_void,
    'the object "(.*)" is not voided by "(.*)"': the_object_name_is_not_voided_by_void,
    'the object "(.*)" should display as "(.*)"': the_object_name_should_display_as_mode,
    'the object "(.*)" has "([0-9]+)" vertices': the_object_name_has_number_vertices,
}


# Super lightweight Gherkin implementation
def run(scenario):
    keywords = ["Given", "When", "Then", "And", "But"]
    for line in scenario.split("\n"):
        line = line.replace("{cwd}", os.getcwd())
        for keyword in keywords:
            line = line.replace(keyword, "")
        line = line.strip()
        if not line:
            continue
        match = None
        for definition, callback in definitions.items():
            match = re.search("^" + definition + "$", line)
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
