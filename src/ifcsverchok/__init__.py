# IfcSverchok - IFC Sverchok extension
# Copyright (C) 2022, 2023 Martina Jakubowska <martina@jakubowska.dk>
#
# This file is part of IfcSverchok.
#
# IfcSverchok is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcSverchok is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with IfcSverchok.  If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "IFC for Sverchok",
    "author": "Martina Jakubowska, Dion Moult",
    "version": (0, 0, 0),
    "blender": (3, 1, 0),
    "location": "Node Editor",
    "category": "Node",
    "description": "An extension to Sverchok to work with IFC data",
    "tracker_url": "https://github.com/IfcOpenShell/IfcOpenShell/issues",
    "warning": "",
}

import importlib
import logging
import types
import bpy

logger = logging.getLogger("sverchok.ifc")


def get_blender_addon_package_by_name(addon_name: str) -> types.ModuleType:
    # Check for legacy addons.
    if addon_name in bpy.context.preferences.addons:
        return importlib.import_module(addon_name)
    elif bpy.app.version < (4, 2, 0):
        raise ModuleNotFoundError

    # Check for Blender extensions.
    addon_package = None
    for package_name in bpy.context.preferences.addons.keys():
        if package_name.endswith(f".{addon_name}"):
            try:
                addon_package = importlib.import_module(package_name)
            except ModuleNotFoundError:
                pass
    if addon_package is None:
        raise ModuleNotFoundError
    return addon_package


def ensure_addons_are_enabled(*addon_names: str) -> None:
    errors = []
    for addon_name in addon_names:
        try:
            module = get_blender_addon_package_by_name(addon_name)
            # `__addon_enabled__` is not present if addon wasn't enabled before
            if not getattr(module, "__addon_enabled__", False):
                errors.append(f"- Addon {addon_name} appears to be disabled, it should be enabled before IFC Sverchok.")
        except ModuleNotFoundError:
            errors.append(f"- Addon {addon_name} is not installed.")

    if errors:
        raise Exception("Some issues were found trying to enable IFC Sverchok:\n" + "\n".join(errors))


ensure_addons_are_enabled("bonsai", "sverchok")


from sverchok.ui.nodeview_space_menu import add_node_menu


def nodes_index():
    return [
        (
            "IFC",
            [
                ("ifc.create_file", "SvIfcCreateFile"),
                ("ifc.read_file", "SvIfcReadFile"),
                ("ifc.write_file", "SvIfcWriteFile"),
                ("ifc.create_entity", "SvIfcCreateEntity"),
                ("ifc.create_shape", "SvIfcCreateShape"),
                ("ifc.read_entity", "SvIfcReadEntity"),
                ("ifc.pick_ifc_class", "SvIfcPickIfcClass"),
                ("ifc.by_id", "SvIfcById"),
                ("ifc.by_guid", "SvIfcByGuid"),
                ("ifc.by_type", "SvIfcByType"),
                ("ifc.by_query", "SvIfcByQuery"),
                ("ifc.add", "SvIfcAdd"),
                ("ifc.add_pset", "SvIfcAddPset"),
                ("ifc.add_spatial_element", "SvIfcAddSpatialElement"),
                ("ifc.remove", "SvIfcRemove"),
                ("ifc.generate_guid", "SvIfcGenerateGuid"),
                ("ifc.get_property", "SvIfcGetProperty"),
                ("ifc.get_attribute", "SvIfcGetAttribute"),
                ("ifc.select_blender_objects", "SvIfcSelectBlenderObjects"),
                ("ifc.api", "SvIfcApi"),
                ("ifc.bmesh_to_ifc", "SvIfcBMeshToIfcRepr"),
                ("ifc.sverchok_to_ifc", "SvIfcSverchokToIfcRepr"),
                ("ifc.create_project", "SvIfcCreateProject"),
                ("ifc.quick_project_setup", "SvIfcQuickProjectSetup"),
            ],
        )
    ]


def make_node_categories() -> list[dict[str, list[str]]]:
    node_categories = [{}]
    for category, nodes in nodes_index():
        nodes = [node_name for idname, node_name in nodes]
        node_categories[0][category] = nodes
    return node_categories


node_categories = make_node_categories()


def make_node_list():
    modules = []
    base_name = "ifcsverchok.nodes"
    index = nodes_index()
    for category, items in index:
        for module_name, node_name in items:
            module = importlib.import_module(f".{module_name}", base_name)
            modules.append(module)
    return modules


imported_modules = make_node_list()

reload_event = False

from os.path import splitext
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.element
from ifcsverchok.ifcstore import SvIfcStore


class IFC_Sv_UpdateCurrent(bpy.types.Operator):
    """Update current Sverchok node tree"""

    bl_idname = "ifc.sverchok_update_current"
    bl_label = "Update Current Node Tree"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node_group: bpy.props.StringProperty(default="")
    force_mode: bpy.props.BoolProperty(default=False)

    # FIXME For now it's fine to center around buildings.
    # But for the future it'd be good to also allow other
    # infra-related spatial structure elements, such as IfcBridge.
    # https://github.com/IfcOpenShell/IfcOpenShell/pull/2576#discussion_r1016261407
    def execute(self, context):
        self.file = SvIfcStore.purge()
        node_tree = context.space_data.node_tree
        if node_tree:
            if self.force_mode or node_tree.sv_process:
                try:
                    bpy.context.window.cursor_set("WAIT")
                    node_tree.force_update()
                finally:
                    bpy.context.window.cursor_set("DEFAULT")
        self.report({"INFO"}, "Node tree updated.")
        return {"FINISHED"}


class IFC_Sv_write_file(bpy.types.Operator):
    bl_idname = "ifc.write_file_panel"
    bl_label = "Write File"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "File path to write to."
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    node_group: bpy.props.StringProperty(default="")
    force_mode: bpy.props.BoolProperty(default=False)

    @classmethod
    def poll(cls, context):
        space = context.space_data
        if not isinstance(space, bpy.types.SpaceNodeEditor):
            return False
        return any("IFC" in n for n in space.edit_tree.nodes.keys())

    def ensure_hirarchy(self, file: ifcopenshell.file) -> None:
        elements_in_buildings: set[ifcopenshell.entity_instance] = set()
        if len(file.by_type("IfcBuilding")) == 0:
            my_building = ifcopenshell.api.run("root.create_entity", file, ifc_class="IfcBuilding", name="My Building")
            elements = ifcopenshell.util.element.get_decomposition(my_building)
        else:
            for building in file.by_type("IfcBuilding"):
                elements = ifcopenshell.util.element.get_decomposition(building)
                elements_in_buildings.update(elements)

        for spatial in file.by_type("IfcSpatialElement") or file.by_type("IfcSpatialStructureElement"):
            if not (spatial.is_a("IfcSite") or spatial.is_a("IfcBuilding")) and (spatial not in elements_in_buildings):
                elements = ifcopenshell.util.element.get_decomposition(spatial)
                ifcopenshell.api.run(
                    "aggregate.assign_object", file, products=[spatial], relating_object=file.by_type("IfcBuilding")[0]
                )

        for building in file.by_type("IfcBuilding"):
            elements = ifcopenshell.util.element.get_decomposition(building)
            elements_in_buildings.update(elements)

        elements = file.by_type("IfcElement")
        for element in elements:
            if element not in elements_in_buildings:
                ifcopenshell.api.run(
                    "spatial.assign_container",
                    file,
                    products=[element],
                    relating_structure=file.by_type("IfcBuilding")[0],
                )

        for building in file.by_type("IfcBuilding"):
            elements = ifcopenshell.util.element.get_decomposition(building)
            if not building.Decomposes:
                if len(file.by_type("IfcSite")) == 0:
                    ifcopenshell.api.run("root.create_entity", file, ifc_class="IfcSite", name="My Site")
                ifcopenshell.api.run(
                    "aggregate.assign_object", file, products=[building], relating_object=file.by_type("IfcSite")[0]
                )
                try:
                    if file.by_type("IfcSite")[0].Decomposes[0].RelatingObject.is_a("IfcProject"):
                        continue
                except IndexError:
                    pass
                ifcopenshell.api.run(
                    "aggregate.assign_object",
                    file,
                    products=[file.by_type("IfcSite")[0]],
                    relating_object=file.by_type("IfcProject")[0],
                )
        self.file = file
        return

    def execute(self, context):
        self.file = SvIfcStore.file
        if not self.file:
            raise Exception("No IFC file in SvIfcStore.")
        _, ext = splitext(self.filepath)
        # FIXME checking for extension not necessary
        if not ext:
            raise Exception("Bad path. Provide a path to a file ending with a file extension.")
        else:
            self.ensure_hirarchy(self.file)
            self.file.write(self.filepath)
            self.report({"INFO"}, f"File written to: {self.filepath}")
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class IFC_PT_write_file_panel(bpy.types.Panel):
    bl_idname = "IFC_PT_write_file_panel"
    bl_label = "Write IFC to File"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "IfcSverchok"

    @classmethod
    def poll(cls, context):
        if context.space_data.edit_tree and any("IFC" in n for n in context.space_data.edit_tree.nodes.keys()):
            return True
        return False

    def draw(self, context):
        ng = context.space_data.node_tree
        layout = self.layout
        row = layout.split(factor=0.2, align=True)
        row = layout.row()
        row2 = layout.row()
        row.operator("ifc.sverchok_update_current", text="IFC Re-run all nodes")
        row2.operator("ifc.write_file_panel")


CLASSES = [IFC_Sv_UpdateCurrent, IFC_Sv_write_file, IFC_PT_write_file_panel]


class SvExCategoryProvider(object):
    def __init__(self, identifier, menu):
        self.identifier = identifier
        self.menu = menu

    def get_categories(self):
        return self.menu


our_menu_classes = []

add_node_menu.append_from_config(node_categories)


def register():
    node_modules = make_node_list()
    for module in node_modules:
        module.register()
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    add_node_menu.register()


def unregister():
    global imported_modules
    for module in reversed(imported_modules):
        module.unregister()
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
