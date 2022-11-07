# IfcSverchok - IFC Sverchok extension
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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
    "author": "Dion Moult",
    "version": (0, 0, 999999),
    "blender": (2, 90, 0),
    "location": "Node Editor",
    "category": "Node",
    "description": "An extension to Sverchok to work with IFC data",
    "tracker_url": "https://github.com/IfcOpenShell/IfcOpenShell/issues",
    "warning": "",
}

import sys
import importlib
import nodeitems_utils
import sverchok
from sverchok.core import sv_registration_utils, make_node_list
from sverchok.utils import auto_gather_node_classes, get_node_class_reference
from sverchok.menu import SverchNodeItem, SverchNodeCategory, register_node_panels
from sverchok.utils.extra_categories import (
    register_extra_category_provider,
    unregister_extra_category_provider,
)
from sverchok.ui.nodeview_space_menu import make_extra_category_menus
from sverchok.utils.logging import info, debug
import asyncio
import time

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
                ("ifc.api_WIP", "SvIfcApiWIP"),
                ("ifc.bmesh_to_ifc", "SvIfcBMeshToIfcRepr"),
                ("ifc.sverchok_to_ifc", "SvIfcSverchokToIfcRepr"),
                ("ifc.create_project", "SvIfcCreateProject"),
                ("ifc.quick_project_setup", "SvIfcQuickProjectSetup")

            ],
        )
    ]


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

import bpy
import os
from os.path import abspath, splitext
import ifcopenshell
from ifcsverchok.ifcstore import SvIfcStore
from sverchok.data_structure import flatten_data

class IFC_Sv_UpdateCurrent(bpy.types.Operator):
    """Update current Sverchok node tree"""
    bl_idname = "ifc.sverchok_update_current"
    bl_label = "Update current node tree"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    node_group: bpy.props.StringProperty(default="")
    force_mode: bpy.props.BoolProperty(default=False)

    def execute(self, context):
        print("#"*10, "Update current node tree")
        self.file = SvIfcStore.purge()
        self.file = SvIfcStore.get_file()
        self.file.write("/Users/martina/Documents/GSoC/CodeTests/IfcFileTest_7_11_purged.ifc")
        node_tree = context.space_data.node_tree
        if node_tree:
            print("### \tupdate tree", node_tree)
            if self.force_mode or node_tree.sv_process:
                print("### \tforce update")
                try:
                    bpy.context.window.cursor_set("WAIT")
                    node_tree.force_update()
                finally:
                    bpy.context.window.cursor_set("DEFAULT")
        print("### \tupdate tree done")
        self.report({"INFO"}, "Node tree updated")
        return {'FINISHED'}

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
        return any("IFC" in n for n in context.space_data.edit_tree.nodes.keys())

    def ensure_hirarchy(self, file):
        elements_in_buildings = []
        if not 0 <= 0 < len(file.by_type("IfcBuilding")):
            my_building = ifcopenshell.api.run("root.create_entity", file, ifc_class="IfcBuilding", name="My Building")
            elements = ifcopenshell.util.element.get_decomposition(my_building)
        else:
            for building in file.by_type("IfcBuilding"):
                elements = ifcopenshell.util.element.get_decomposition(building)
                elements_in_buildings.extend(elements)

        for spatial in (file.by_type("IfcSpatialElement") or file.by_type("IfcSpatialStructureElement")):
            if (not (spatial.is_a("IfcSite") or spatial.is_a("IfcBuilding")) and (spatial not in elements_in_buildings)):
                elements = ifcopenshell.util.element.get_decomposition(spatial)
                ifcopenshell.api.run("aggregate.assign_object", file, product=spatial, relating_object=file.by_type("IfcBuilding")[0])

        elements_in_buildings_after = []
        for building in file.by_type("IfcBuilding"):
            elements = ifcopenshell.util.element.get_decomposition(building)
            elements_in_buildings_after.extend(elements)

        elements = file.by_type("IfcElement")
        for element in elements:
            if element not in elements_in_buildings:
                ifcopenshell.api.run("spatial.assign_container", file, product=element, relating_structure=file.by_type("IfcBuilding")[0])


        for building in file.by_type("IfcBuilding"):
            elements = ifcopenshell.util.element.get_decomposition(building)
            if not building.Decomposes:
                if not 0 <= 0 < len(file.by_type("IfcSite")):
                    ifcopenshell.api.run("root.create_entity", file, ifc_class="IfcSite", name="My Site")
                ifcopenshell.api.run("aggregate.assign_object", file, product=building, relating_object=file.by_type("IfcSite")[0])
                try:
                    if file.by_type("IfcSite")[0].Decomposes[0].RelatingObject.is_a("IfcProject"):
                        continue
                except IndexError:
                    pass
                ifcopenshell.api.run("aggregate.assign_object", file, product=file.by_type("IfcSite")[0], relating_object=file.by_type("IfcProject")[0])
        self.file = file
        return

    def execute(self, context):
        self.file = SvIfcStore.file
        if not self.file:
            raise Exception("No IFC file in SvIfcStore.")
        _, ext = splitext(self.filepath)
        if not ext:
            raise Exception("Bad path. Provide a path to a file.")
        else:
            self.ensure_hirarchy(self.file)
            print("### \thirarchy ensured")
            # if not (self.file.by_type("IfcSpatialElement") or self.file.by_type("IfcSpatialStructureElement")):
            #     self.report({"INFO"},"No Ifc Spatial Element found. Adding all elements to IfcBuilding.")
            #     elements = self.file.by_type("IfcElement")
            #     building = ifcopenshell.api.run("root.create_entity", self.file, name="DefaultBuilding", ifc_class="IfcBuilding")
            #     for element in elements:
            #         ifcopenshell.api.run("spatial.assign_container", self.file, product=element, relating_structure=building)
            self.file.write(self.filepath)
            self.report({"INFO"}, f"File written to: {self.filepath}")
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

class IFC_PT_write_file_panel(bpy.types.Panel):
    bl_idname = "IFC_PT_write_file_panel"
    bl_label = "Write IFC to file"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "IfcSverchok"

    @classmethod
    def poll(cls, context):
        if context.space_data.edit_tree and any("IFC" in n for n in context.space_data.edit_tree.nodes.keys()):
            return True

    def draw(self, context):
        ng = context.space_data.node_tree
        layout = self.layout
        row = layout.split(factor=0.2, align=True)
        row = layout.row()
        row.operator('ifc.sverchok_update_current', text='IFC Re-run all nodes')
        row.operator("ifc.write_file_panel")

CLASSES = [IFC_Sv_UpdateCurrent,IFC_Sv_write_file, IFC_PT_write_file_panel]

def register_nodes():
    node_modules = make_node_list()
    for module in node_modules:
        module.register()
    info("Registered %s nodes", len(node_modules))


def unregister_nodes():
    global imported_modules
    for module in reversed(imported_modules):
        module.unregister()


def make_menu():
    menu = []
    index = nodes_index()
    for category, items in index:
        identifier = "IFCSVERCHOK_" + category.replace(" ", "_")
        node_items = []
        for item in items:
            nodetype = item[1]
            rna = get_node_class_reference(nodetype)
            if not rna:
                info(
                    "Node `%s' is not available (probably due to missing dependencies).",
                    nodetype,
                )
            else:
                node_item = SverchNodeItem.new(nodetype)
                node_items.append(node_item)
        if node_items:
            cat = SverchNodeCategory(identifier, category, items=node_items)
            menu.append(cat)
    return menu


class SvExCategoryProvider(object):
    def __init__(self, identifier, menu):
        self.identifier = identifier
        self.menu = menu

    def get_categories(self):
        return self.menu


our_menu_classes = []


def register():
    global our_menu_classes

    debug("Registering ifcsverchok")
    for klass in CLASSES:
        bpy.utils.register_class(klass)
    register_nodes()
    extra_nodes = importlib.import_module(".nodes", "ifcsverchok")
    auto_gather_node_classes(extra_nodes)
    menu = make_menu()
    menu_category_provider = SvExCategoryProvider("IFCSVERCHOK", menu)
    register_extra_category_provider(
        menu_category_provider
    )  # if 'IFCSVERCHOK' in nodeitems_utils._node_categories:
    nodeitems_utils.register_node_categories("IFCSVERCHOK", menu)
    our_menu_classes = make_extra_category_menus()


def unregister():
    global our_menu_classes
    if "IFCSVERCHOK" in nodeitems_utils._node_categories:
        nodeitems_utils.unregister_node_categories("IFCSVERCHOK")
    for clazz in our_menu_classes:
        try:
            bpy.utils.unregister_class(clazz)
        except Exception as e:
            print("Can't unregister menu class %s" % clazz)
            print(e)
    unregister_extra_category_provider("IFCSVERCHOK")
    unregister_nodes()
    for klass in CLASSES:
        bpy.utils.unregister_class(klass)
