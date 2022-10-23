import bpy

import ifcopenshell
import ifcsverchok.helper
from ifcsverchok.ifcstore import SvIfcStore

import bpy
import json
import ifcopenshell

from bpy.props import StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode, flatten_data, repeat_last_for_length, ensure_min_nesting


class SvIfcAddSpatialElement(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcAddSpatialElement"
    bl_label = "IFC Add Spatial Element"
    Name: StringProperty(name="Name(s)", update=updateNode)
    IfcClass: StringProperty(name="IFC Class", update=updateNode, default="IfcSpace")
    Elements: StringProperty(name="Elements", update=updateNode)
    len_elements = 0

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "Name(s)").prop_name = "Name"
        self.inputs.new("SvStringsSocket", "IfcClass").prop_name = "IfcClass"
        self.inputs.new("SvStringsSocket", "Elements").prop_name = "Elements"
        self.outputs.new("SvStringsSocket", "Entities")
        self.outputs.new("SvStringsSocket", "file")

    def process(self):
        if not any(socket.is_linked for socket in self.outputs):
            return

        self.names = flatten_data(self.inputs["Name(s)"].sv_get(), target_level=1)
        self.ifc_class = self.inputs["IfcClass"].sv_get()[0][0]
        self.elements = ensure_min_nesting(self.inputs["Elements"].sv_get(), 2)
        self.elements = flatten_data(self.elements, target_level=2)
        print("elements: ", self.elements)
        self.file = SvIfcStore.get_file()
        self.elements = [[self.file.by_id(step_id) for step_id in element] for element in self.elements]
    
        print("len elements: ", len(self.elements))
        print("elements: ", self.elements)
        self.names = self.repeat_input_unique(self.names, len(self.elements))
        print("Names: ",self.names)

        if (self.node_id not in SvIfcStore.id_map) or (len(self.elements) != self.len_elements):
            print("\nRunning create")
            elements = self.create()
            self.len_elements = len(self.elements)
        else:
            elements = self.edit()
        print("\n ##### results: ", elements)
        self.outputs["Entities"].sv_set(elements)
        self.outputs["file"].sv_set([self.file])

    def create(self):
        results = []
        for i, element in enumerate(self.elements):
            print("element: ", element)
            result = ifcopenshell.api.run("root.create_entity", self.file, name=self.names[i], ifc_class=self.ifc_class)
            for items in element:
                print("items: ", items)
                ifcopenshell.api.run("spatial.assign_container", self.file, product=items, relating_structure=result)
                SvIfcStore.id_map[result.id()] = self.node_id
                SvIfcStore.id_map.setdefault(self.node_id, []).append(result.id())
            results.append(result)
        return results

    def edit(self):
        results = []
        results_ids = SvIfcStore.id_map[self.node_id]
        for result_id in results_ids:
            result = self.file.by_id(result_id)
            print("\n\nresult: ", result)
            subelements = set(ifcopenshell.util.element.get_decomposition(result))
            for element in self.elements:
                print("\nElement: ", element)
                element_set = set(element)
                print("\nRESULT: ", result)
                print("subelements: ", subelements)
                print("elements_set: ", element_set)
                for removed_element in subelements - element_set:
                    # Just realised I don't have a spatial.unassign_container, but if so we'd do it here
                    pass
                for added_element in element_set - subelements:
                    ifcopenshell.api.run("spatial.assign_container", self.file, product=added_element, relating_structure=result)
                    print("assigned container")
            results.append(result)
        return results

    def repeat_input_unique(self, input, count):
        input = repeat_last_for_length(input, count, deepcopy=False)
        if input[0]:
            input = [a if not (s:=sum(j == a for j in input[:i])) else f'{a}-{s+1}' for i, a in enumerate(input)]  # add number to duplicates
        return input

    def get_existing_element(self):
        entity_id = list(SvIfcStore.id_map.keys())[list(SvIfcStore.id_map.values()).index(self.node_id)]
        return self.file.by_id(entity_id)


def register():
    bpy.utils.register_class(SvIfcAddSpatialElement)


def unregister():
    bpy.utils.unregister_class(SvIfcAddSpatialElement)
    SvIfcStore.purge()
