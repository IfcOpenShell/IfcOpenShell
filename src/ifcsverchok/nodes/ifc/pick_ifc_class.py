# IfcSverchok - IFC Sverchok extension
# Copyright (C) 2022 Martina Jakubowska <martina@jakubowska.dk>
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

import bpy
import ifcopenshell
import ifcsverchok.helper
from bpy.props import EnumProperty
from ifcsverchok.ifcstore import SvIfcStore
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode


def get_ifc_products(self, context):
    ifc_products = getattr(self, "ifc_products", [])
    file = SvIfcStore.get_file()
    if not file:
        return []
    if ifc_products and file:
        return ifc_products
    ifc_products = []
    ifc_products.extend(
        [
            (e, e, "")
            for e in [
                "IfcElement",
                "IfcElementType",
                "IfcSpatialElement",
                "IfcGroup",
                "IfcStructuralItem",
                "IfcContext",
                "IfcAnnotation",
            ]
        ]
    )
    if file.schema == "IFC2X3":
        ifc_products[2] = ("IfcSpatialStructureElement", "IfcSpatialStructureElement", "")
    return ifc_products


def update_ifc_products(self, context):
    if hasattr(self, "ifc_classes"):
        self.ifc_classes.clear()


def get_ifc_classes(self, context):
    ifc_classes = getattr(self, "ifc_classes", [])
    if ifc_classes:
        return self.ifc_classes
    file = SvIfcStore.get_file()
    if not file:
        return []
    schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(file.schema_identifier)
    declaration = schema.declaration_by_name(self.ifc_product)

    def get_classes(declaration):
        results = []
        if not declaration.is_abstract():
            results.append(declaration.name())
        for subtype in declaration.subtypes():
            results.extend(get_classes(subtype))
        return results

    classes = get_classes(declaration)
    ifc_classes.extend([(c, c, "") for c in sorted(classes)])
    return ifc_classes


class SvIfcPickIfcClass(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcPickIfcClass"
    bl_label = "IFC Class Picker"
    ifc_product: EnumProperty(
        items=get_ifc_products,
        name="IfcProduct",
        description="Pick an IfcProduct from drop-down.",
        update=update_ifc_products,
    )
    ifc_class: EnumProperty(
        items=get_ifc_classes, name="IfcClass", description="Pick an IfcClass from drop-down.", update=updateNode
    )

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "ifc_product").prop_name = "ifc_product"
        self.inputs.new("SvStringsSocket", "ifc_class").prop_name = "ifc_class"
        self.outputs.new("SvStringsSocket", "IfcClass")
        self.width = 200

    def draw_buttons(self, context, layout):
        layout.operator("node.sv_ifc_tooltip", text="", icon="QUESTION", emboss=False).tooltip = "Ifc Class Picker"

    def process(self):
        ifc_class = self.inputs["ifc_class"].sv_get()[0][0]
        self.outputs["IfcClass"].sv_set([ifc_class])


def register():
    bpy.utils.register_class(SvIfcPickIfcClass)


def unregister():
    bpy.utils.unregister_class(SvIfcPickIfcClass)
