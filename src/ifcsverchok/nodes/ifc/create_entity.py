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

    def draw_buttons(self, context, layout):
        layout.operator("node.sv_ifc_tooltip", text="", icon="QUESTION", emboss=False).tooltip = "Create IFC Entity. Takes one or multiple inputs. \nIf 'Representation(s)' is given, that determines number of output entities. Otherwise, 'Names' is used."
        
        row = layout.row(align=True)
        row.prop(self, 'is_interactive', icon='SCENE_DATA', icon_only=True)
        row.prop(self, 'refresh_local', icon='FILE_REFRESH')




    def process(self):
        print("#"*20, "\n running create_entity3 PROCESS()... \n", "#"*20,)
        print("#"*20, "\n hash(self):", hash(self), "\n", "#"*20,)

        self.names = flatten_data(self.inputs["Names"].sv_get(), target_level=1)
        self.descriptions = flatten_data(self.inputs["Descriptions"].sv_get(), target_level=1)
        self.ifc_class = self.inputs["IfcClass"].sv_get()[0][0]
        self.representations = flatten_data(self.inputs["Representations"].sv_get(), target_level=1)
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

        print("\nrepresentations before convert: ", self.representations)
        
        self.file = SvIfcStore.get_file()
        if self.representations[0]:
            self.representations = [self.file.by_id(step_id) for step_id in self.representations]
            self.names = self.repeat_input_unique(self.names, len(self.representations))
            self.descriptions = self.repeat_input_unique(self.descriptions, len(self.representations))
        elif not self.representations[0]:
            self.descriptions = self.repeat_input_unique(self.descriptions, len(self.names))

        # print("REPRESENTATION: ", self.representations)
        # print("IfcClass: ",self.ifc_class)
        print("Names: ",self.names)
        print("Descriptions: ",self.descriptions)
        # print("\nrepresentations after convert: ", self.representations)

        if self.node_id not in SvIfcStore.id_map:
            entities = self.create()
        else:
            if edit is True:
                entities = self.edit()
            else:
                # entities = self.get_existing_element()
                entities = SvIfcStore.id_map[self.node_id]
        
        print("Entities: ", entities)
        print("SvIfcStore.id_map: ", SvIfcStore.id_map)

        self.outputs["Entities"].sv_set(entities)
        self.outputs["file"].sv_set([[self.file]])

    def create(self, index=None):
        entities_ids = []
        iterator = range(len(self.names))
        if index is not None:
            iterator = [index]
        for i in iterator:
            try:
                entity = ifcopenshell.api.run("root.create_entity", self.file, ifc_class=self.ifc_class, name=self.names[i], description=self.descriptions[i])
                try:
                    ifcopenshell.api.run("geometry.assign_representation", self.file, product=entity, representation=self.representations[i])
                except IndexError:
                    pass
                entities_ids.append(entity.id())
                SvIfcStore.id_map.setdefault(self.node_id, []).append(entity.id())
            except Exception as e: 
                raise Exception("Something went wrong. Cannot create entity.", e)
        return entities_ids

    def edit(self):
        entities_ids = []
        id_map_copy = SvIfcStore.id_map[self.node_id].copy()
        for i, _ in enumerate(self.names):
            try:
                step_id = id_map_copy[i]
            except IndexError:
                id = self.create(index=i)
                entities_ids.append(id[0])
                continue
            entity = self.file.by_id(step_id)
            entity.Name = self.names[i]
            entity.Description = self.descriptions[i]

            try:
                if self.representations[i] and not self.file.by_type("IFCPRODUCTDEFINITIONSHAPE"):
                    ifcopenshell.api.run("geometry.assign_representation", self.file, product=entity, representation=self.representations[i])
                elif self.representations[i]:
                    entity.Representation = self.representations[i]
            except IndexError:
                pass
            
            if entity.is_a() != self.ifc_class:
                SvIfcStore.id_map[self.node_id].remove(step_id)
                entity = ifcopenshell.util.schema.reassign_class(self.file, entity, self.ifc_class)
                SvIfcStore.id_map.setdefault(self.node_id, []).append(entity.id())
            entities_ids.append(entity.id())

        if id_map_copy>entities_ids:
            SvIfcStore.id_map[self.node_id] = entities_ids
        return entities_ids

    def repeat_input_unique(self, input, count):
        input = repeat_last_for_length(input, count, deepcopy=False)
        if input[0]:
            input = [a if not (s:=sum(j == a for j in input[:i])) else f'{a}-{s+1}' for i, a in enumerate(input)]  # add number to duplicates
        return input


    def get_existing_element(self):
        results = []
        for i, step_id in enumerate(SvIfcStore.id_map[self.node_id]):
            entity = self.file.by_id(step_id)
            results.append([entity])
        return results

    
    def sv_free(self):
        try:
            del SvIfcStore.id_map[self.node_id]
            del self.node_dict[hash(self)]
            print('Node was deleted')
        except KeyError or AttributeError:
            pass


def register():
    bpy.utils.register_class(SvIfcCreateEntity)


def unregister():
    bpy.utils.unregister_class(SvIfcCreateEntity)
