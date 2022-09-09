import bpy

import ifcopenshell
import ifcsverchok.helper
from ifcsverchok.ifcstore import SvIfcStore

import bpy
import json
import ifcopenshell

from bpy.props import StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode


class SvIfcAddSpatialElement(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcAddSpatialElement"
    bl_label = "IFC Add Spatial Element"
    Name: StringProperty(name="Name", update=updateNode)
    IfcClass: StringProperty(name="IFC Class", update=updateNode, default="IfcSpace")
    Elements: StringProperty(name="Elements", update=updateNode)

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "Name").prop_name = "Name"
        self.inputs.new("SvStringsSocket", "IfcClass").prop_name = "IfcClass"
        self.inputs.new("SvStringsSocket", "Elements").prop_name = "Elements"
        self.outputs.new("SvStringsSocket", "entity")
        self.outputs.new("SvStringsSocket", "file")

    def process(self):
        if not any(socket.is_linked for socket in self.outputs):
            return

        name = self.inputs["Name"].sv_get()[0][0]
        ifc_class = self.inputs["IfcClass"].sv_get()[0][0]
        elements = self.inputs["Elements"].sv_get()[0]

        if SvIfcStore.file is None:
            SvIfcStore.file = SvIfcStore.create_boilerplate()
        self.file = SvIfcStore.get_file()

        if self.node_id not in SvIfcStore.id_map.values():
            element = self.create(name, ifc_class, elements)
        else:
            element = self.edit(name, ifc_class, elements)

        self.outputs["entity"].sv_set([[element]])
        self.outputs["file"].sv_set([[self.file]])

    def create(self, name, ifc_class, elements):
        results = []
        result = ifcopenshell.api.run("root.create_entity", self.file, ifc_class=ifc_class)
        for element in elements:
            ifcopenshell.api.run("spatial.assign_container", self.file, product=element, relating_structure=result)
            SvIfcStore.id_map[result.id()] = self.node_id
            results.append(result)
        return result

    def edit(self, name, ifc_class, elements):
        result = self.get_existing_element()
        subelements = set(ifcopenshell.util.element.get_decomposition(result))
        elements_set = set(elements)
        for removed_element in subelements - elements_set:
            # Just realised I don't have a spatial.unassign_container, but if so we'd do it here
            pass
        for added_element in elements_set - subelements:
            ifcopenshell.api.run("spatial.assign_container", self.file, product=added_element, relating_structure=result)
        return result

    def get_existing_element(self):
        entity_id = list(SvIfcStore.id_map.keys())[list(SvIfcStore.id_map.values()).index(self.node_id)]
        return self.file.by_id(entity_id)


def register():
    bpy.utils.register_class(SvIfcAddSpatialElement)


def unregister():
    bpy.utils.unregister_class(SvIfcAddSpatialElement)
    SvIfcStore.purge()
