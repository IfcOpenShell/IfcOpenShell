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
    node_dict = {}
 
    n_id: StringProperty()
    Name: StringProperty(name="Name(s)", update=updateNode)
    IfcClass: StringProperty(name="IFC Class", update=updateNode, default="IfcSpace")
    Elements: StringProperty(name="Elements", update=updateNode)
    len_elements = 0

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "Names").prop_name = "Name"
        self.inputs.new("SvStringsSocket", "IfcClass").prop_name = "IfcClass"
        self.inputs.new("SvStringsSocket", "Elements").prop_name = "Elements"
        self.outputs.new("SvStringsSocket", "Entities")

    def process(self):
        print("#"*20, "\n running add_spatial_element PROCESS()... \n", "#"*20,)
        print("#"*20, "\n hash(self):", hash(self), "\n", "#"*20,)
        if not any(socket.is_linked for socket in self.outputs):
            return

        self.names = flatten_data(self.inputs["Names"].sv_get(), target_level=1)
        self.ifc_class = flatten_data(self.inputs["IfcClass"].sv_get(), target_level=1)[0]
        self.elements = ensure_min_nesting(self.inputs["Elements"].sv_get(), 2)
        self.elements = flatten_data(self.elements, target_level=2)
        if not self.elements[0][0]:
            raise Exception('Mandatory input "Element(s)" is missing.')
            return
        print("elements: ", self.elements)
        self.file = SvIfcStore.get_file()
        self.elements = [[self.file.by_id(step_id) for step_id in element] for element in self.elements]
    
        print("len elements: ", len(self.elements))
        print("elements: ", self.elements)
        self.names = self.repeat_input_unique(self.names, len(self.elements))
        print("Names: ",self.names)
        print("IfcClass: ",self.ifc_class)

        self.sv_input_names = [i.name for i in self.inputs]
        if hash(self) not in self.node_dict:
            self.node_dict[hash(self)] = {} #happens if node is already on canvas when blender loads
        if not self.node_dict[hash(self)]:
            self.node_dict[hash(self)].update(dict.fromkeys(self.sv_input_names, 0))

        print("node_dict: ", self.node_dict)
        edit = False
        for i in range(len(self.inputs)):
            input = self.inputs[i].sv_get(deepcopy=False)
            if isinstance(self.node_dict[hash(self)][self.inputs[i].name], list) and input != self.node_dict[hash(self)][self.inputs[i].name]:
                edit = True
                print("Edit = True")
            self.node_dict[hash(self)][self.inputs[i].name] = input


        if (self.node_id not in SvIfcStore.id_map) or (len(self.elements) != self.len_elements):
            print("\nRunning create")
            elements = self.create()
            self.len_elements = len(self.elements)
        else:
            if edit is True:
                elements = self.edit()
            else:
                elements = SvIfcStore.id_map[self.node_id]
        print("\n ##### results: ", elements)
        self.outputs["Entities"].sv_set(elements)

    def create(self):
        results = []
        for i, element in enumerate(self.elements):
            print("element: ", element)
            result = ifcopenshell.api.run("root.create_entity", self.file, name=self.names[i], ifc_class=self.ifc_class)
            for items in element:
                print("items: ", items)
                if items.is_a("IfcSpatialElement") or items.is_a("IfcSpatialStructureElement"):
                    ifcopenshell.api.run("aggregate.assign_object", self.file, product=items, relating_object=result)
                else:
                    ifcopenshell.api.run("spatial.assign_container", self.file, product=items, relating_structure=result)
                SvIfcStore.id_map[result.id()] = self.node_id
                SvIfcStore.id_map.setdefault(self.node_id, []).append(result.id())
            results.append(result.id())
        return results

    def edit(self):
        results = []
        results_ids = SvIfcStore.id_map[self.node_id]
        print("#"*20, "\n running add_spatial_element edit()... \n", "#"*20,)
        print("#"*20, "\n results_ids:", results_ids, "\n", "#"*20,)
        for result_id in results_ids:
            result = self.file.by_id(result_id)
            print("#"*20, "\n result", result, "\n", "#"*20,)
            subelements = set(ifcopenshell.util.element.get_decomposition(result))
            for element in self.elements:
                print("\n\n\n","#"*50)
                print("\nElement: ", element)
                element_set = set(element)
                print("\nRESULT: ", result)
                print("subelements: ", subelements)
                print("elements_set: ", element_set)
                for removed_element in subelements - element_set:
                    # Just realised I don't have a spatial.unassign_container, but if so we'd do it here
                    if removed_element.is_a("IfcSpatialElement") or removed_element.is_a("IfcSpatialStructureElement"):
                        ifcopenshell.api.run("aggregate.unassign_object", self.file, product=removed_element, relating_object=result)
                    else:
                        pass
                for added_element in element_set - subelements:
                    if added_element.is_a("IfcSpatialElement") or added_element.is_a("IfcSpatialStructureElement"):
                        ifcopenshell.api.run("aggregate.assign_object", self.file, product=added_element, relating_object=result)
                    else:
                        ifcopenshell.api.run("spatial.assign_container", self.file, product=added_element, relating_structure=result)
                    print("assigned container")
            results.append(result.id())
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
