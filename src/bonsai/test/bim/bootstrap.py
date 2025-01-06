# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import bpy
import pytest
import webbrowser
import bonsai.bim.handler
import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.representation
from bonsai.bim.ifc import IfcStore
from mathutils import Vector

# Monkey-patch webbrowser opening since we want to test headlessly
webbrowser.open = lambda x: True


variables = {"cwd": os.getcwd(), "ifc": "IfcStore.get_file()"}


class NewFile:
    @pytest.fixture(autouse=True)
    def setup(self):
        IfcStore.purge()
        bpy.ops.wm.read_homefile(app_template="")
        if bpy.data.objects:
            bpy.data.batch_remove(bpy.data.objects)
            bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        bonsai.bim.handler.load_post(None)


class NewIfc:
    @pytest.fixture(autouse=True)
    def setup(self):
        IfcStore.purge()
        bpy.ops.wm.read_homefile(app_template="")
        bpy.data.batch_remove(bpy.data.objects)
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        bonsai.bim.handler.load_post(None)
        bpy.ops.bim.create_project()


class NewIfc4X3:
    @pytest.fixture(autouse=True)
    def setup(self):
        IfcStore.purge()
        bpy.ops.wm.read_homefile(app_template="")
        bpy.data.batch_remove(bpy.data.objects)
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        bonsai.bim.handler.load_post(None)
        bpy.context.scene.BIMProjectProperties.export_schema = "IFC4X3_ADD2"
        bpy.ops.bim.create_project()


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
    i_deselect_all_objects()
    additionally_the_object_name_is_selected(name)


def additionally_the_object_name_is_selected(name):
    obj = bpy.context.scene.objects.get(name)
    if not obj:
        assert False, 'The object "{name}" could not be selected'
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)


def i_deselect_all_objects():
    bpy.context.view_layer.objects.active = None
    bpy.ops.object.select_all(action="DESELECT")


def i_am_on_frame_number(number):
    bpy.context.scene.frame_set(int(number))


def i_set_prop_to_value(prop, value):
    try:
        eval(f"bpy.context.{prop}")
    except:
        assert False, "Property does not exist"
    try:
        exec(f'bpy.context.{prop} = "{value}"')
    except:
        exec(f"bpy.context.{prop} = {value}")


def prop_is_value(prop, value):
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


def i_enable_prop(prop):
    exec(f"bpy.context.{prop} = True")


def i_press_operator(operator):
    if "(" in operator:
        exec(f"bpy.ops.{operator}")
    else:
        exec(f"bpy.ops.{operator}()")


def i_rename_the_object_name1_to_name2(name1, name2):
    the_object_name_exists(name1).name = name2


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


def an_ifc_file_does_not_exist():
    ifc = IfcStore.get_file()
    if ifc:
        assert False, "An IFC is available"


def the_object_name_does_not_exist(name):
    assert bpy.data.objects.get(name) is None, "Object exists"


def the_object_name_is_an_ifc_class(name, ifc_class):
    ifc = an_ifc_file_exists()
    element = ifc.by_id(the_object_name_exists(name).BIMObjectProperties.ifc_definition_id)
    assert element.is_a(ifc_class), f'Object "{name}" is an {element.is_a()}'


def the_object_name_is_not_an_ifc_element(name):
    id = the_object_name_exists(name).BIMObjectProperties.ifc_definition_id
    assert id == 0, f"The ID is {id}"


def the_object_name_is_in_the_collection_collection(name, collection):
    assert collection in [c.name for c in the_object_name_exists(name).users_collection]


def the_object_name_is_not_in_the_collection_collection(name, collection):
    assert collection not in [c.name for c in the_object_name_exists(name).users_collection]


def the_object_name_has_a_body_of_value(name, value):
    assert the_object_name_exists(name).data.body == value


def the_collection_name1_is_in_the_collection_name2(name1, name2):
    assert bpy.data.collections.get(name2).children.get(name1)


def the_collection_name1_is_not_in_the_collection_name2(name1, name2):
    assert not bpy.data.collections.get(name2).children.get(name1)


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
    bonsai.bim.handler.active_object_callback()


def i_delete_the_selected_objects():
    bpy.ops.object.delete()
    bonsai.bim.handler.active_object_callback()


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


def the_object_name_is_not_voided(name):
    ifc = IfcStore.get_file()
    element = ifc.by_id(the_object_name_exists(name).BIMObjectProperties.ifc_definition_id)
    if any(element.HasOpenings):
        assert False, "An opening was found"


def the_object_name_is_not_a_void(name):
    ifc = IfcStore.get_file()
    element = ifc.by_id(the_object_name_exists(name).BIMObjectProperties.ifc_definition_id)
    if any(element.VoidsElements):
        assert False, "A void was found"


def the_void_name_is_filled_by_filling(name, filling):
    ifc = IfcStore.get_file()
    element = ifc.by_id(the_object_name_exists(name).BIMObjectProperties.ifc_definition_id)
    if any(rel.RelatedBuildingElement.Name == filling for rel in element.HasFillings):
        return True
    assert False, "No filling found"


def the_void_name_is_not_filled_by_filling(name, filling):
    ifc = IfcStore.get_file()
    element = ifc.by_id(the_object_name_exists(name).BIMObjectProperties.ifc_definition_id)
    if any(rel.RelatedBuildingElement.Name == filling for rel in element.HasFillings):
        assert False, "A filling was found"


def the_object_name_is_not_a_filling(name):
    ifc = IfcStore.get_file()
    element = ifc.by_id(the_object_name_exists(name).BIMObjectProperties.ifc_definition_id)
    if any(element.FillsVoids):
        assert False, "A filling was found"


def the_object_name_should_display_as_mode(name, mode):
    assert the_object_name_exists(name).display_type == mode


def the_object_name_has_number_vertices(name, number):
    total = len(the_object_name_exists(name).data.vertices)
    assert total == int(number), f"We found {total} vertices"


def the_object_name_is_at_location(name, location):
    obj_location = the_object_name_exists(name).location
    assert (
        obj_location - Vector([float(co) for co in location.split(",")])
    ).length < 0.1, f"Object is at {obj_location}"


def the_variable_key_is_value(key, value):
    variables[key] = eval(value)


definitions = {
    'the variable "(.*)" is "(.*)"': the_variable_key_is_value,
    "an empty IFC project": an_empty_ifc_project,
    "I add a cube": i_add_a_cube,
    'I add a cube of size "([0-9]+)" at "(.*)"': i_add_a_cube_of_size_size_at_location,
    'the object "(.*)" is selected': the_object_name_is_selected,
    'additionally the object "(.*)" is selected': additionally_the_object_name_is_selected,
    "I deselect all objects": i_deselect_all_objects,
    'I am on frame "([0-9]+)"': i_am_on_frame_number,
    'I set "(.*)" to "(.*)"': i_set_prop_to_value,
    '"(.*)" is "(.*)"': prop_is_value,
    'I enable "(.*)"': i_enable_prop,
    'I press "(.*)"': i_press_operator,
    'I rename the object "(.*)" to "(.*)"': i_rename_the_object_name1_to_name2,
    'the object "(.*)" exists': the_object_name_exists,
    'the object "(.*)" does not exist': the_object_name_does_not_exist,
    'the object "(.*)" is an "(.*)"': the_object_name_is_an_ifc_class,
    'the object "(.*)" is not an IFC element': the_object_name_is_not_an_ifc_element,
    'the object "(.*)" is in the collection "(.*)"': the_object_name_is_in_the_collection_collection,
    'the object "(.*)" is not in the collection "(.*)"': the_object_name_is_not_in_the_collection_collection,
    'the object "(.*)" has a body of "(.*)"': the_object_name_has_a_body_of_value,
    'the collection "(.*)" is in the collection "(.*)"': the_collection_name1_is_in_the_collection_name2,
    'the collection "(.*)" is not in the collection "(.*)"': the_collection_name1_is_not_in_the_collection_name2,
    "an IFC file exists": an_ifc_file_exists,
    "an IFC file does not exist": an_ifc_file_does_not_exist,
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
    'the object "(.*)" is not a void': the_object_name_is_not_a_void,
    'the object "(.*)" is not voided': the_object_name_is_not_voided,
    'the object "(.*)" should display as "(.*)"': the_object_name_should_display_as_mode,
    'the object "(.*)" has "([0-9]+)" vertices': the_object_name_has_number_vertices,
    'the object "(.*)" is at "(.*)"': the_object_name_is_at_location,
    "nothing interesting happens": lambda: None,
    'the void "(.*)" is filled by "(.*)"': the_void_name_is_filled_by_filling,
    'the void "(.*)" is not filled by "(.*)"': the_void_name_is_not_filled_by_filling,
    'the object "(.*)" is not a filling': the_object_name_is_not_a_filling,
}


# Super lightweight Gherkin implementation
def run(scenario):
    keywords = ["Given", "When", "Then", "And", "But"]
    for line in scenario.split("\n"):
        for key, value in variables.items():
            line = line.replace("{" + key + "}", str(value))
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
