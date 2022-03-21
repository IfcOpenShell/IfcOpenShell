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
import webbrowser
import ifcopenshell
import blenderbim.tool as tool
import blenderbim.bim
from blenderbim.bim.ifc import IfcStore
from pytest_bdd import scenarios, given, when, then, parsers
from mathutils import Vector

scenarios("feature")

variables = {"cwd": os.getcwd(), "ifc": "IfcStore.get_file()"}

# Monkey-patch webbrowser opening since we want to test headlessly
webbrowser.open = lambda x: True


def replace_variables(value):
    for key, new_value in variables.items():
        value = value.replace("{" + key + "}", str(new_value))
    return value


@given("an untestable scenario")
def an_untestable_scenario():
    pass


@given("an empty Blender session")
@when("an empty Blender session is started")
def an_empty_ifc_project():
    IfcStore.purge()
    bpy.ops.wm.read_homefile(app_template="")
    if len(bpy.data.objects) > 0:
        bpy.data.batch_remove(bpy.data.objects)
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)


@given("an empty IFC project")
def an_empty_ifc_project():
    IfcStore.purge()
    bpy.ops.wm.read_homefile(app_template="")
    if len(bpy.data.objects) > 0:
        bpy.data.batch_remove(bpy.data.objects)
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
    bpy.ops.bim.create_project()


@when("I load a new pset template file")
def i_load_a_new_pset_template_file():
    IfcStore.pset_template_path = os.path.join(
        bpy.context.scene.BIMProperties.data_dir,
        "pset",
        bpy.context.scene.BIMPsetTemplateProperties.pset_template_files + ".ifc",
    )
    IfcStore.pset_template_file = ifcopenshell.open(IfcStore.pset_template_path)


@given("I add a cube")
@when("I add a cube")
def i_add_a_cube():
    bpy.ops.mesh.primitive_cube_add()


@given("I add an empty")
@when("I add an empty")
def i_add_an_empty():
    bpy.ops.object.empty_add()


@given("I add a sun")
@when("I add an sun")
def i_add_a_sun():
    bpy.ops.object.light_add(type="SUN")


@given("I add a material")
@when("I add a material")
def i_add_a_material():
    bpy.context.active_object.active_material = bpy.data.materials.new("Material")


@given(parsers.parse('the material "{name}" colour is set to "{colour}"'))
@when(parsers.parse('the material "{name}" colour is set to "{colour}"'))
def the_material_name_colour_is_set_to_colour(name, colour):
    obj = the_material_name_exists(name)
    obj.diffuse_color = [float(c) for c in colour.split(",")]
    blenderbim.bim.handler.color_callback(obj, None)


@given("I add an array modifier")
def i_add_a_cube():
    bpy.ops.object.modifier_add(type="ARRAY")


@given(parsers.parse('I add a cube of size "{size}" at "{location}"'))
@when(parsers.parse('I add a cube of size "{size}" at "{location}"'))
def i_add_a_cube_of_size_size_at_location(size, location):
    bpy.ops.mesh.primitive_cube_add(size=float(size), location=[float(co) for co in location.split(",")])


@given(parsers.parse('I add a plane of size "{size}" at "{location}"'))
@when(parsers.parse('I add a plane of size "{size}" at "{location}"'))
def i_add_a_plane_of_size_size_at_location(size, location):
    bpy.ops.mesh.primitive_plane_add(size=float(size), location=[float(co) for co in location.split(",")])


@given(parsers.parse('I press "{operator}"'))
@when(parsers.parse('I press "{operator}"'))
def i_press_operator(operator):
    operator = replace_variables(operator)
    if "(" in operator:
        exec(f"bpy.ops.{operator}")
    else:
        exec(f"bpy.ops.{operator}()")


@when("I duplicate the selected objects")
def i_duplicate_the_selected_objects():
    bpy.ops.object.duplicate_move()
    blenderbim.bim.handler.active_object_callback()


@when("I deselect all objects")
def i_deselect_all_objects():
    bpy.context.view_layer.objects.active = None
    bpy.ops.object.select_all(action="DESELECT")


@given(parsers.parse('the object "{name}" is selected'))
@when(parsers.parse('the object "{name}" is selected'))
def the_object_name_is_selected(name):
    i_deselect_all_objects()
    additionally_the_object_name_is_selected(name)


@then(parsers.parse('the object "{name}" is selected'))
def then_the_object_name_is_selected(name):
    obj = the_object_name_exists(name)
    assert obj in bpy.context.selected_objects


@given(parsers.parse('the object "{name}" is moved to "{location}"'))
@when(parsers.parse('the object "{name}" is moved to "{location}"'))
def the_object_name_is_moved_to_location(name, location):
    the_object_name_exists(name).location += Vector([float(co) for co in location.split(",")])


@given(parsers.parse('the object "{name}" is scaled to "{scale}"'))
@when(parsers.parse('the object "{name}" is scaled to "{scale}"'))
def the_object_name_is_scaled_to_scale(name, scale):
    the_object_name_exists(name).scale *= float(scale)


@given(parsers.parse('the object "{name}" is placed in the collection "{collection}"'))
@when(parsers.parse('the object "{name}" is placed in the collection "{collection}"'))
def the_object_name_is_placed_in_the_collection_collection(name, collection):
    obj = the_object_name_exists(name)
    [c.objects.unlink(obj) for c in obj.users_collection]
    bpy.data.collections.get(collection).objects.link(obj)


@given(parsers.parse('additionally the object "{name}" is selected'))
@when(parsers.parse('additionally the object "{name}" is selected'))
def additionally_the_object_name_is_selected(name):
    obj = bpy.context.scene.objects.get(name)
    if not obj:
        assert False, f'The object "{name}" could not be selected'
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)


@given(parsers.parse('I rename the object "{name1}" to "{name2}"'))
@when(parsers.parse('I rename the object "{name1}" to "{name2}"'))
def i_rename_the_object_name1_to_name2(name1, name2):
    the_object_name_exists(name1).name = name2


@given(parsers.parse('I set "{prop}" to "{value}"'))
@when(parsers.parse('I set "{prop}" to "{value}"'))
def i_set_prop_to_value(prop, value):
    value = replace_variables(value)
    try:
        eval(f"bpy.context.{prop}")
    except:
        assert False, "Property does not exist"
    try:
        exec(f'bpy.context.{prop} = r"{value}"')
    except:
        exec(f"bpy.context.{prop} = {value}")


@given(parsers.parse('I set "{prop}" to ""'))
@when(parsers.parse('I set "{prop}" to ""'))
def i_set_prop_to_value(prop):
    try:
        eval(f"bpy.context.{prop}")
    except:
        assert False, "Property does not exist"
    try:
        exec(f'bpy.context.{prop} = r""')
    except:
        pass


@when(parsers.parse('I am on frame "{number}"'))
def i_am_on_frame_number(number):
    bpy.context.scene.frame_set(int(number))


@when("I delete the selected objects")
def i_delete_the_selected_objects():
    bpy.ops.object.delete()


@given(parsers.parse('the variable "{key}" is "{value}"'))
@when(parsers.parse('the variable "{key}" is "{value}"'))
@then(parsers.parse('the variable "{key}" is "{value}"'))
def the_variable_key_is_value(key, value):
    variables[key] = eval(replace_variables(value))


@then("nothing happens")
def nothing_happens():
    pass


@then(parsers.parse('the object "{name}" exists'))
def the_object_name_exists(name) -> bpy.types.Object:
    obj = bpy.data.objects.get(name)
    if not obj:
        assert False, f'The object "{name}" does not exist'
    return obj


@then(parsers.parse('the object "{name1}" and "{name2}" are different elements'))
def the_object_name1_and_name2_are_different_elements(name1, name2):
    ifc = an_ifc_file_exists()
    element1 = ifc.by_id(the_object_name_exists(name1).BIMObjectProperties.ifc_definition_id)
    element2 = ifc.by_id(the_object_name_exists(name2).BIMObjectProperties.ifc_definition_id)
    assert element1 != element2, f"Objects {name1} and {name2} have same elements {element1} and {element2}"


@then(parsers.parse('the object "{name}" has a body of "{value}"'))
def the_object_name_has_a_body_of_value(name, value):
    assert the_object_name_exists(name).data.body == value


@given(parsers.parse('the object "{name}" has a "{type}" representation of "{context}"'))
@then(parsers.parse('the object "{name}" has a "{type}" representation of "{context}"'))
def the_object_name_has_a_representation_type_of_context(name, type, context):
    ifc = an_ifc_file_exists()
    element = ifc.by_id(the_object_name_exists(name).BIMObjectProperties.ifc_definition_id)
    context, subcontext, target_view = context.split("/")
    rep = ifcopenshell.util.representation.get_representation(element, context, subcontext or None, target_view or None)
    assert rep
    assert rep.RepresentationType == type


@given(parsers.parse('the object "{name}" data is a "{type}" representation of "{context}"'))
@then(parsers.parse('the object "{name}" data is a "{type}" representation of "{context}"'))
def the_object_name_has_a_representation_type_of_context(name, type, context):
    ifc = an_ifc_file_exists()
    context, subcontext, target_view = context.split("/")
    rep = ifc.by_id(the_object_name_exists(name).data.BIMMeshProperties.ifc_definition_id)
    assert rep
    assert rep.RepresentationType == type
    assert rep.ContextOfItems.ContextType == context
    assert rep.ContextOfItems.ContextIdentifier == subcontext
    assert rep.ContextOfItems.TargetView == target_view


@then(parsers.parse('the material "{name}" exists'))
def the_material_name_exists(name) -> bpy.types.Material:
    obj = bpy.data.materials.get(name)
    if not obj:
        assert False, f'The material "{name}" does not exist'
    return obj


@then(parsers.parse('the material "{name}" does not exist'))
def the_material_name_does_not_exist(name):
    assert bpy.data.materials.get(name) is None, "Material exists"


@then("an IFC file does not exist")
def an_ifc_file_does_not_exist():
    ifc = IfcStore.get_file()
    if ifc:
        assert False, "An IFC is available"


@then("an IFC file exists")
def an_ifc_file_exists():
    ifc = IfcStore.get_file()
    if not ifc:
        assert False, "No IFC file is available"
    return ifc


@then(parsers.parse('the object "{name}" should display as "{mode}"'))
def the_object_name_should_display_as_mode(name, mode):
    obj = the_object_name_exists(name)
    assert obj.display_type == mode


@then(parsers.parse('the object "{name1}" has a boolean difference by "{name2}"'))
def the_object_name1_has_a_boolean_difference_by_name2(name1, name2):
    obj = the_object_name_exists(name1)
    has_mod = any((m for m in obj.modifiers if m.type == "BOOLEAN" and m.object and m.object.name == name2))
    assert has_mod, "No boolean found"


@then(parsers.parse('the object "{name1}" has no boolean difference by "{name2}"'))
def the_object_name1_has_no_boolean_difference_by_name2(name1, name2):
    try:
        the_object_name1_has_a_boolean_difference_by_name2(name1, name2)
    except AssertionError:
        return
    assert False, "A boolean was found"


@then(parsers.parse('the object "{name}" is voided by "{void}"'))
def the_object_name_is_voided_by_void(name, void):
    ifc = IfcStore.get_file()
    element = ifc.by_id(the_object_name_exists(name).BIMObjectProperties.ifc_definition_id)
    assert any((rel for rel in element.HasOpenings if rel.RelatedOpeningElement.Name == void)), "No void found"


@then(parsers.parse('the object "{name}" is not voided by "{void}"'))
def the_object_name_is_not_voided_by_void(name, void):
    try:
        the_object_name_is_voided_by_void(name, void)
    except AssertionError:
        return
    assert False, "A void was found"


@then(parsers.parse('the object "{name}" is not voided'))
def the_object_name_is_not_voided(name):
    ifc = IfcStore.get_file()
    element = ifc.by_id(the_object_name_exists(name).BIMObjectProperties.ifc_definition_id)
    assert not element.HasOpenings, "A void was found"


@then(parsers.parse('the object "{name}" is not a void'))
def the_object_name_is_a_void(name):
    ifc = IfcStore.get_file()
    obj = the_object_name_exists(name)
    element = ifc.by_id(obj.BIMObjectProperties.ifc_definition_id)
    assert any((element.VoidsElements)), "No void was found"


@then(parsers.parse('the object "{name}" is not a void'))
def the_object_name_is_not_a_void(name):
    try:
        the_object_name_is_a_void(name)
    except AssertionError:
        return
    assert False, "A void was found"


@then(parsers.parse('the object "{name}" is an "{ifc_class}"'))
def the_object_name_is_an_ifc_class(name, ifc_class):
    ifc = an_ifc_file_exists()
    element = ifc.by_id(the_object_name_exists(name).BIMObjectProperties.ifc_definition_id)
    assert element.is_a(ifc_class), f'Object "{name}" is an {element.is_a()}'


@then(parsers.parse('the object "{name}" is not an IFC element'))
def the_object_name_is_not_an_ifc_element(name):
    id = the_object_name_exists(name).BIMObjectProperties.ifc_definition_id
    assert id == 0, f"The ID is {id}"


@then(parsers.parse('the object "{name}" has no data'))
def the_object_name_has_no_data(name):
    assert the_object_name_exists(name).data is None


@then(parsers.parse('the object "{name}" has data which is an IFC representation'))
def the_object_name_is_not_an_ifc_element(name):
    id = the_object_name_exists(name).data.BIMMeshProperties.ifc_definition_id
    assert id != 0, f"The ID is {id}"


@then(parsers.parse('the material "{name}" is an IFC material'))
def the_material_name_is_not_an_ifc_material(name):
    id = the_material_name_exists(name).BIMObjectProperties.ifc_definition_id
    assert id != 0, f"The ID is {id}"


@then(parsers.parse('the material "{name}" is not an IFC material'))
def the_material_name_is_not_an_ifc_material(name):
    id = the_material_name_exists(name).BIMObjectProperties.ifc_definition_id
    assert id == 0, f"The ID is {id}"


@then(parsers.parse('the material "{name}" is not an IFC style'))
def the_material_name_is_not_an_ifc_material(name):
    id = the_material_name_exists(name).BIMMaterialProperties.ifc_style_id
    assert id == 0, f"The ID is {id}"


@then(parsers.parse('the material "{name}" colour is "{colour}"'))
def the_material_name_colour_is_set_to_colour(name, colour):
    diffuse_color = list(the_material_name_exists(name).diffuse_color)
    assert diffuse_color == [float(c) for c in colour.split(",")], f"The colour is {diffuse_color}"


@then(parsers.parse('the object "{name}" has "{number}" vertices'))
def the_object_name_has_number_vertices(name, number):
    total = len(the_object_name_exists(name).data.vertices)
    assert total == int(number), f"We found {total} vertices"


@then(parsers.parse('the void "{name}" is filled by "{filling}"'))
def the_void_name_is_filled_by_filling(name, filling):
    ifc = IfcStore.get_file()
    element = ifc.by_id(the_object_name_exists(name).BIMObjectProperties.ifc_definition_id)
    assert any((rel.RelatedBuildingElement.Name == filling for rel in element.HasFillings)), "No filling found"


@then(parsers.parse('the void "{name}" is not filled by "{filling}"'))
def the_void_name_is_not_filled_by_filling(name, filling):
    try:
        the_void_name_is_filled_by_filling(name, filling)
    except AssertionError:
        return
    assert False, "A filling was found"


@when(parsers.parse('the object "{name}" is not a filling'))
@then(parsers.parse('the object "{name}" is not a filling'))
def the_object_name_is_not_a_filling(name):
    ifc = IfcStore.get_file()
    element = ifc.by_id(the_object_name_exists(name).BIMObjectProperties.ifc_definition_id)
    assert not any(element.FillsVoids), "A filling was found"


@then(parsers.parse('"{prop}" is "{value}"'))
def prop_is_value(prop, value):
    prop = replace_variables(prop)
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


@then(parsers.parse('the object "{name}" has the material "{material}"'))
def the_object_name_has_the_material_material(name, material):
    assert material in [ms.material.name for ms in the_object_name_exists(name).material_slots]


@then(parsers.parse('the object "{name}" is in the collection "{collection}"'))
def the_object_name_is_in_the_collection_collection(name, collection):
    assert collection in [c.name for c in the_object_name_exists(name).users_collection]


@then(parsers.parse('the collection "{name1}" is in the collection "{name2}"'))
def the_collection_name1_is_in_the_collection_name2(name1, name2):
    assert bpy.data.collections.get(name2).children.get(name1)


@then(parsers.parse('the object "{name}" does not exist'))
def the_object_name_does_not_exist(name):
    assert bpy.data.objects.get(name) is None, "Object exists"


@then(parsers.parse('the object "{name}" is at "{location}"'))
def the_object_name_is_at_location(name, location):
    obj_location = the_object_name_exists(name).location
    assert (
        obj_location - Vector([float(co) for co in location.split(",")])
    ).length < 0.1, f"Object is at {obj_location}"


@then(parsers.parse('the object "{name}" has no scale'))
def the_object_name_has_no_scale(name):
    assert the_object_name_exists(name).scale == Vector(
        (
            1.0,
            1.0,
            1.0,
        )
    )


@then(parsers.parse('the object "{name}" dimensions are "{dimensions}"'))
def the_object_name_dimensions_are_dimensions(name, dimensions):
    assert list(the_object_name_exists(name).dimensions) == [float(co) for co in dimensions.split(",")]


@then(parsers.parse('the object "{name}" bottom left corner is at "{location}"'))
def the_object_name_is_at_location(name, location):
    obj_corner = Vector(the_object_name_exists(name).bound_box[0])
    assert (
        obj_corner - Vector([float(co) for co in location.split(",")])
    ).length < 0.1, f"Object has corner {obj_corner}"


@then(parsers.parse('the object "{name}" is contained in "{container_name}"'))
def the_object_name_is_contained_in_container_name(name, container_name):
    ifc = an_ifc_file_exists()
    element = ifc.by_id(the_object_name_exists(name).BIMObjectProperties.ifc_definition_id)
    container = ifcopenshell.util.element.get_container(element)
    if not container:
        assert False, f'Object "{name}" is not in any container'
    assert container.Name == container_name, f'Object "{name}" is in {container}'


@then(parsers.parse('the file "{name}" should contain "{value}"'))
def the_file_name_should_contain_value(name, value):
    name = replace_variables(name)
    with open(name, "r") as f:
        assert value in f.read()


@then(parsers.parse('the object "{name}" has no modifiers'))
def the_object_name_has_no_modifiers(name):
    assert len(the_object_name_exists(name).modifiers) == 0
