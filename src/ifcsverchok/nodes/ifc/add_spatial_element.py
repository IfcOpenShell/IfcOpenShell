import bpy

import ifcopenshell
import ifcsverchok.helper
from ifcsverchok.ifcstore import SvIfcStore

from bpy.props import StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode, flatten_data, repeat_last_for_length, ensure_min_nesting


class SvIfcAddSpatialElement(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcAddSpatialElement"
    bl_label = "IFC Add Spatial Element"
    node_dict2 = {}
 
    Names: StringProperty(name="Name(s)", update=updateNode)
    IfcClass: StringProperty(name="IFC Class", update=updateNode, default="IfcSpace")
    Elements: StringProperty(name="Elements", update=updateNode)

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "Names").prop_name = "Names"
        self.inputs.new("SvStringsSocket", "IfcClass").prop_name = "IfcClass"
        self.inputs.new("SvStringsSocket", "Elements").prop_name = "Elements"
        self.outputs.new("SvStringsSocket", "Entities")
        self.node_dict2[hash(self)] = {}
    
    def draw_buttons(self, context, layout):
        layout.operator("node.sv_ifc_tooltip", text="", icon="QUESTION", emboss=False).tooltip = "Ifc entity by type."

    def process(self):
        print("#"*20, "\n running add_spatial_element PROCESS()... \n", "#"*20,)
        print("#"*20, "\n hash(self):", hash(self), "\n", "#"*20,)
        try:
            print("SvIfcStore.id_map: ", SvIfcStore.id_map)
            print("self-node_id: ",self.node_id)
            print("#"*20, "\n node_dict2 before before... \n", self.node_dict2, "\n", "#"*20,)
        except:
            pass
        self.sv_input_names = [i.name for i in self.inputs]
        if hash(self) not in self.node_dict2:
            self.node_dict2[hash(self)] = {} #happens if node is already on canvas when blender loads
        if not self.node_dict2[hash(self)]:
            self.node_dict2[hash(self)].update(dict.fromkeys(self.sv_input_names, 0))

        print("#"*20, "\n node_dict2 before... \n", self.node_dict2, "\n", "#"*20,)
        if not any(socket.is_linked for socket in self.outputs):
            return
        edit = False
        edit_elements = False
        for i in range(len(self.inputs)):
            print(f"current node_dict2 iter:{i}: ", self.node_dict2[hash(self)])
            input = self.inputs[self.sv_input_names[i]].sv_get(deepcopy=True, default =[])
            print("current input: ", input)
            print("previous input: ", self.node_dict2[hash(self)][self.inputs[i].name])
            if isinstance(self.node_dict2[hash(self)][self.inputs[i].name], list) and input != self.node_dict2[hash(self)][self.inputs[i].name]:
                edit = True
                print("Edit = True")
                if self.inputs[i].name == "Elements":
                    edit_elements = True
                    print("edit_elements = True")
            self.node_dict2[hash(self)][self.inputs[i].name] = input.copy()
        print("#"*20, "\n node_dict2 after... \n", self.node_dict2,"\n", "#"*20,)

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
    

        if "len" not in self.node_dict2[hash(self)]:
            self.node_dict2[hash(self)]["len"] = 0
        print("len elements: ", len(self.elements), "stored len_elements: ", self.node_dict2[hash(self)]["len"])
        print("elements: ", self.elements)
        self.names = self.repeat_input_unique(self.names, len(self.elements))
        print("Names: ",self.names)
        print("IfcClass: ",self.ifc_class)
        print("node_dict2: ", self.node_dict2)


        if (self.node_id not in SvIfcStore.id_map) or (len(self.elements) != self.node_dict2[hash(self)]["len"]):
            print("\nRunning create")
            self.remove()
            elements = self.create()
            self.node_dict2[hash(self)]["len"] = len(self.elements)
            print("stored len_elements: ", self.node_dict2[hash(self)]["len"])
        else:
            if edit is True:
                elements = self.edit(edit_elements)
            else:
                print("No changes")
                elements = SvIfcStore.id_map[self.node_id]
        print("\n ##### spatial element results: ", elements)
        self.outputs["Entities"].sv_set(elements)

    def create(self, index=None):
        print("#"*20, "\n running add_spatial_element create()... \n", "#"*20,)
        spatial_ids = []
        iterator = range(len(self.elements))
        if index is not None:
            iterator = [index]
        for i in iterator:
            print("element: ", self.elements[i])
            result = ifcopenshell.api.run("root.create_entity", self.file, name=self.names[i], ifc_class=self.ifc_class)
            for items in self.elements[i]:
                print("items: ", items)
                if items.is_a("IfcSpatialElement") or items.is_a("IfcSpatialStructureElement"):
                    ifcopenshell.api.run("aggregate.assign_object", self.file, product=items, relating_object=result)
                else:
                    ifcopenshell.api.run("spatial.assign_container", self.file, product=items, relating_structure=result)
                # SvIfcStore.id_map[result.id()] = self.node_id
            SvIfcStore.id_map.setdefault(self.node_id, []).append(result.id())
            spatial_ids.append(result.id())
        return spatial_ids

    def edit(self, edit_elements):
        spatial_ids = []
        id_map = SvIfcStore.id_map[self.node_id]
        id_map_copy = SvIfcStore.id_map[self.node_id].copy()
        print("#"*20, "\n running add_spatial_element edit()... \n", "#"*20,)
        print("#"*20, "\n id_map:", id_map, "\n", "#"*20,)
        for i, element in enumerate(self.elements):
            try:
                result_id = id_map_copy[i]
            except IndexError:
                id = self.create(index=i)
                spatial_ids.append(id[0])
                continue
            result = self.file.by_id(result_id)
            print("#"*20, "\n result", result, "\n", "#"*20,)
            result.Name = self.names[i]
            if edit_elements:
                subelements = ifcopenshell.util.element.get_decomposition(result)
                print("subelements: ", subelements)
                subelements = set(subelements)
                print("subelements after: ", subelements)
                for element in self.elements[i]:
                    print("\n\n\n","#"*50)
                    print("\nElement: ", element)
                    element_set = set([element])
                    print("\nRESULT: ", result)
                    print("subelements: ", subelements)
                    print("elements_set: ", element_set)
                    for removed_element in subelements - element_set:
                        # Just realised I don't have a spatial.unassign_container, but if so we'd do it here
                        print("removed_element: ", removed_element)
                        if removed_element.is_a("IfcSpatialElement") or removed_element.is_a("IfcSpatialStructureElement"):
                            ifcopenshell.api.run("aggregate.unassign_object", self.file, product=removed_element, relating_object=result)
                        else:
                            # ifcopenshell.api.run("spatial.unassign_container", self.file, product=removed_element, relating_object=result)
                            self.unassign_container(removed_element)
                    for added_element in element_set - subelements:
                        print("added_element: ", added_element)
                        if added_element.is_a("IfcSpatialElement") or added_element.is_a("IfcSpatialStructureElement"):
                            ifcopenshell.api.run("aggregate.assign_object", self.file, product=added_element, relating_object=result)
                        else:
                            ifcopenshell.api.run("spatial.assign_container", self.file, product=added_element, relating_structure=result)
                        print("assigned container")
            spatial_ids.append(result.id())
        SvIfcStore.id_map[self.node_id] = spatial_ids
        return spatial_ids

    def unassign_container(self, product):
        for rel in product.ContainedInStructure or []:
            related_elements = list(rel.RelatedElements)
            related_elements.remove(product)
            if related_elements:
                rel.RelatedElements = related_elements
                ifcopenshell.api.run("owner.update_owner_history", self.file, element=rel)
            else:
                self.file.remove(rel)

    def remove(self):
        print("#"*20, "\n running add_spatial_element remove()... \n", "#"*20,)
        if self.node_id in SvIfcStore.id_map:
            print(SvIfcStore.id_map[self.node_id])
            for element_id in SvIfcStore.id_map[self.node_id]:
                element = self.file.by_id(element_id)
                print("\nremoving element: ", element)
                self.file.write("/Users/martina/Documents/GSoC/CodeTests/IfcFileTest_6_11_before_remove.ifc")
                ifcopenshell.api.run("root.remove_product", self.file, product=element)
            del SvIfcStore.id_map[self.node_id]

    def repeat_input_unique(self, input, count):
        input = repeat_last_for_length(input, count, deepcopy=False)
        if input[0]:
            input = [a if not (s:=sum(j == a for j in input[:i])) else f'{a}-{s+1}' for i, a in enumerate(input)]  # add number to duplicates
        return input

    def sv_free(self):
        try:
            del SvIfcStore.id_map[self.node_id]
            del self.node_dict2[hash(self)]
            print('Node was deleted')
        except KeyError or AttributeError:
            pass

def register():
    bpy.utils.register_class(SvIfcAddSpatialElement)


def unregister():
    bpy.utils.unregister_class(SvIfcAddSpatialElement)
    SvIfcStore.purge()
