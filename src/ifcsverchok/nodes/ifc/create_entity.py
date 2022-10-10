import bpy

# from helper import SayHello
import ifcopenshell
import ifcsverchok.helper
from ifcsverchok.ifcstore import SvIfcStore

# import ifcsverchok.ifc_store
# from bpy.props import StringProperty
# from sverchok.node_tree import SverchCustomTreeNode
# from sverchok.data_structure import updateNode

import bpy
import ifcopenshell

from bpy.props import StringProperty, EnumProperty, IntProperty, BoolProperty, PointerProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode, flatten_data, repeat_last_for_length

input_map = {}


class SvIfcCreateEntity(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcCreateEntity"
    bl_label = "IFC Create Entity"
    node_dict = {}

    is_scene_dependent = True  # if True and is_interactive then the node will be updated upon scene changes

    def refresh_node(self, context):
        if self.refresh_local:
            self.process()
            self.refresh_local = False

    refresh_local: BoolProperty(name="Update Node", description="Update Node", update=refresh_node)

    Names: StringProperty(name="Names", default="", update=updateNode)
    Descriptions: StringProperty(name="Descriptions", default="", update=updateNode)
    IfcClass: StringProperty(name="IfcClass", update=updateNode)
    Representations: StringProperty(name="Representations", default="", update=updateNode)
    Properties: StringProperty(name="properties", update=updateNode)

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "Names").prop_name = "Names"
        self.inputs.new("SvStringsSocket", "Descriptions").prop_name = "Descriptions"
        self.inputs.new("SvStringsSocket", "IfcClass").prop_name = "IfcClass"
        self.inputs.new("SvStringsSocket", "Representations").prop_name = "Representations"
        self.inputs.new("SvStringsSocket", "Properties").prop_name = "Properties"
        self.outputs.new("SvStringsSocket", "Entities")
        self.outputs.new("SvStringsSocket", "file")  # only for testing
        self.node_dict[hash(self)] = {}

    def process(self):
        print("#"*20, "\n running create_entity3 PROCESS()... \n", "#"*20,)
        print("#"*20, "\n hash(self):", hash(self), "\n", "#"*20,)

        self.names = self.inputs["Names"].sv_get()
        self.descriptions = self.inputs["Descriptions"].sv_get()
        self.ifc_class = self.inputs["IfcClass"].sv_get()[0][0]
        self.representations = self.inputs["Representations"].sv_get()
        self.properties = self.inputs["Properties"].sv_get()
    

        self.sv_input_names = [i.name for i in self.inputs]

        if hash(self) not in self.node_dict:
            self.node_dict[hash(self)] = {} #happens if node is already on canvas when blender loads
        if not self.node_dict[hash(self)]:
            self.node_dict[hash(self)].update(dict.fromkeys(self.sv_input_names, 0))
        print("node_dict: ", self.node_dict)
        if not self.inputs["IfcClass"].sv_get()[0][0]:
            raise Exception("Insert IfcClass")
            return

        edit = False
        for i in range(len(self.inputs)):
            input = self.inputs[self.sv_input_names[i]].sv_get(deepcopy=False)
            # print("input: ", input)
            # print("self.node_dict[hash(self)][self.inputs[i].name]: ", self.node_dict[hash(self)][self.inputs[i].name])
            if isinstance(self.node_dict[hash(self)][self.inputs[i].name], list) and input != self.node_dict[hash(self)][self.inputs[i].name]:
                edit = True
            self.node_dict[hash(self)][self.inputs[i].name] = input

        if self.refresh_local:
            edit = True


        self.names = repeat_last_for_length(self.names, len(self.representations), deepcopy=False)
        self.descriptions = repeat_last_for_length(self.descriptions, len(self.representations), deepcopy=False)
        # print("REPRESENTATION: ", self.representations)
        # print("IfcClass: ",self.ifc_class)
        print("Names: ",self.names)
        print("Descriptions: ",self.descriptions)
        


        self.file = SvIfcStore.get_file()

        if self.node_id not in SvIfcStore.id_map:
            enities = self.create()
        else:
            if edit is True:
                enities = self.edit()
            else:
                enities = self.get_existing_element()
        
        print("Entities: ", enities)
        print("SvIfcStore.id_map: ", SvIfcStore.id_map)

        self.outputs["Entities"].sv_set(enities)
        self.outputs["file"].sv_set([[self.file]])

    def create(self):
        # print("#"*20, "\n running create entity CREATE()... \n")
        results = []
        for i, name in enumerate(self.names):
            print(type(self.names[i][0]))
            try:
                self.entity = ifcopenshell.api.run("root.create_entity", self.file, ifc_class=self.ifc_class, name=self.names[i][0], description=self.descriptions[i][0])
                try:
                    ifcopenshell.api.run("geometry.assign_representation", self.file, product=self.entity, representation=self.representations[i][0])
                except IndexError:
                    pass
                results.append([self.entity])
                SvIfcStore.id_map.setdefault(self.node_id, []).append(self.entity.id())
            except: 
                raise Exception("Something went wrong. Cannot create entity.")
        return results

    def edit(self):
        results = []
        id_map_copy = SvIfcStore.id_map[self.node_id].copy()
        for i, step_id in enumerate(id_map_copy):
            self.entity = self.file.by_id(step_id)
            self.entity.Name = self.names[i][0]
            self.entity.Description = self.descriptions[i][0]

            if self.representations[i][0] and not self.file.by_type("IFCPRODUCTDEFINITIONSHAPE"):
                ifcopenshell.api.run("geometry.assign_representation", self.file, product=self.entity, representation=self.representations[i][0])
            elif self.representations[i][0]:
                self.entity.Representation = self.representations[i][0]
            else:
                pass
            
            if self.entity.is_a() != self.ifc_class:
                SvIfcStore.id_map[self.node_id].remove(step_id)
                self.entity = ifcopenshell.util.schema.reassign_class(self.file, self.entity, self.ifc_class)
                SvIfcStore.id_map.setdefault(self.node_id, []).append(self.entity.id())
            results.append([self.entity])

        return results

    def get_existing_element(self):
        # print("#"*20, "\n running create entity get_existing_element()... \n", "#"*20,)
        results = []
        for i, step_id in enumerate(SvIfcStore.id_map[self.node_id]):
            self.entity = self.file.by_id(step_id)
            results.append([self.entity])
        return results

    
    def sv_free(self):
        
        try:
            print('DELETING')
            del SvIfcStore.id_map[self.node_id]
            del self.node_dict[hash(self)]
            print('Node was deleted')
        except KeyError or AttributeError:
            pass


def register():
    bpy.utils.register_class(SvIfcCreateEntity)


def unregister():
    bpy.utils.unregister_class(SvIfcCreateEntity)
