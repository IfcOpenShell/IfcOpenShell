bl_info = {
    "name": "IFC for Sverchok",
    "author": "Dion Moult",
    "version": (0, 0, 0, 1),
    "blender": (2, 90, 0),
    "location": "Node Editor",
    "category": "Node",
    "description": "An extension to Sverchok to work with IFC data",
    "warning": "",
}

import sys
import importlib
import nodeitems_utils
import sverchok
from sverchok.core import sv_registration_utils, make_node_list
from sverchok.utils import auto_gather_node_classes, get_node_class_reference
from sverchok.menu import SverchNodeItem, SverchNodeCategory, register_node_panels
from sverchok.utils.extra_categories import register_extra_category_provider, unregister_extra_category_provider
from sverchok.ui.nodeview_space_menu import make_extra_category_menus
from sverchok.utils.logging import info, debug

def nodes_index():
    return [("IFC", [
        ("ifc.create_file", "SvIfcCreateFile"),
        ("ifc.read_file", "SvIfcReadFile"),
        ("ifc.write_file", "SvIfcWriteFile"),
        ("ifc.create_entity", "SvIfcCreateEntity"),
        ("ifc.create_shape", "SvIfcCreateShape"),
        ("ifc.read_entity", "SvIfcReadEntity"),
        ("ifc.by_id", "SvIfcById"),
        ("ifc.by_guid", "SvIfcByGuid"),
        ("ifc.by_type", "SvIfcByType"),
        ("ifc.by_query", "SvIfcByQuery"),
        ("ifc.add", "SvIfcAdd"),
        ("ifc.remove", "SvIfcRemove"),
        ("ifc.generate_guid", "SvIfcGenerateGuid"),
        ("ifc.get_property", "SvIfcGetProperty"),
        ("ifc.get_attribute", "SvIfcGetAttribute"),
        ("ifc.select_blender_objects", "SvIfcSelectBlenderObjects"),
    ])]

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
        identifier = "IFCSVERCHOK_" + category.replace(' ', '_')
        node_items = []
        for item in items:
            nodetype = item[1]
            rna = get_node_class_reference(nodetype)
            if not rna:
                info("Node `%s' is not available (probably due to missing dependencies).", nodetype)
            else:
                node_item = SverchNodeItem.new(nodetype)
                node_items.append(node_item)
        if node_items:
            cat = SverchNodeCategory(
                        identifier,
                        category,
                        items=node_items
                    )
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

    register_nodes()
    extra_nodes = importlib.import_module(".nodes", "ifcsverchok")
    auto_gather_node_classes(extra_nodes)
    menu = make_menu()
    menu_category_provider = SvExCategoryProvider("IFCSVERCHOK", menu)
    register_extra_category_provider(menu_category_provider) #if 'IFCSVERCHOK' in nodeitems_utils._node_categories:
    nodeitems_utils.register_node_categories("IFCSVERCHOK", menu)
    our_menu_classes = make_extra_category_menus()

def unregister():
    global our_menu_classes
    if 'IFCSVERCHOK' in nodeitems_utils._node_categories:
        nodeitems_utils.unregister_node_categories("IFCSVERCHOK")
    for clazz in our_menu_classes:
        try:
            bpy.utils.unregister_class(clazz)
        except Exception as e:
            print("Can't unregister menu class %s" % clazz)
            print(e)
    unregister_extra_category_provider("IFCSVERCHOK")
    unregister_nodes()
