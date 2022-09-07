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

from bpy.props import StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode


class SvIfcCreateEntity2(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcCreateEntity2"
    bl_label = "IFC Create Entity2"
    Name: StringProperty(name="Name", update=updateNode)
    Description: StringProperty(name="Description", update=updateNode)
    ifc_class: StringProperty(name="ifc_class", update=updateNode)
    representation: StringProperty(name="representation", update=updateNode)

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "Name").prop_name = "Name"
        self.inputs.new("SvTextSocket", "Description").prop_name = "Description"
        self.inputs.new("SvStringsSocket", "IfcClass").prop_name = "ifc_class"
        self.inputs.new("SvStringsSocket", "Representation").prop_name = "representation"
        self.outputs.new("SvStringsSocket", "entity")
        self.outputs.new("SvStringsSocket", "file") #only for testing

    def process(self):
        if not any(socket.is_linked for socket in self.outputs):
            return

        name = self.inputs["Name"].sv_get()[0][0]
        description = self.inputs['Description'].sv_get()[0][0]
        ifc_class = self.inputs['IfcClass'].sv_get()[0][0]
        representation = self.inputs['Representation'].sv_get()[0][0]
        
        if SvIfcStore.file is None:
            self.file = SvIfcStore.create_boilerplate()

        else:
            self.file = SvIfcStore.get_file()

        print("file: " , self.file)

        if self.node_id not in SvIfcStore.id_map.values():
            self.process_ifc(name, description, ifc_class, representation)
        else:
            entity_id = list(SvIfcStore.id_map.keys())[list(SvIfcStore.id_map.values()).index(self.node_id)]
            self.entity = self.file.by_id(entity_id)
            self.entity.Name = name
            self.entity.Description = description
            self.entity.Representation = representation

        SvIfcStore.file = self.file
        self.outputs["entity"].sv_set([[self.entity]])
        self.outputs["file"].sv_set([[self.file]]) #only for testing

    def process_ifc(self, name, description, ifc_class, representation):
        
        data = {
            'GlobalId': ifcopenshell.guid.new(),
            'Name': name,
            'Description': description,
            'Representation': representation

        }
        self.entity = self.file.create_entity(str(ifc_class), **data)
        print("entity: ", self.entity)
        SvIfcStore.id_map[self.entity.id()] = self.node_id
        print("id_map: ", SvIfcStore.id_map)


def register():
    bpy.utils.register_class(SvIfcCreateEntity2)


def unregister():
    bpy.utils.unregister_class(SvIfcCreateEntity2)
    SvIfcStore.purge()
