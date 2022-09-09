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
    Name: StringProperty(name="Name",default="", update=updateNode)
    Description: StringProperty(name="Description", default="", update=updateNode)
    ifc_class: StringProperty(name="IfcClass", update=updateNode)
    representation: StringProperty(name="representation", default="", update=updateNode)
    properties: StringProperty(name="properties", update=updateNode)

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "Name").prop_name = "Name"
        self.inputs.new("SvStringsSocket", "Description").prop_name = "Description"
        self.inputs.new("SvStringsSocket", "IfcClass").prop_name = "ifc_class"
        self.inputs.new("SvStringsSocket", "Representation").prop_name = "representation"
        self.inputs.new("SvStringsSocket", "Properties").prop_name = "properties"
        self.outputs.new("SvStringsSocket", "entity")
        self.outputs.new("SvStringsSocket", "file") #only for testing

    def process(self):
        if not self.inputs['IfcClass'].is_linked:
            return

        self.sv_input_names = [i.name for i in self.inputs]

        name = self.inputs["Name"].sv_get()[0][0]
        description = self.inputs['Description'].sv_get()[0][0]
        ifc_class = self.inputs['IfcClass'].sv_get()[0][0]
        representation = self.inputs['Representation'].sv_get()[0][0]            

        self.file = SvIfcStore.get_file()
        print("file: " , self.file)
        print(SvIfcStore.file)

        if self.node_id not in SvIfcStore.id_map.values():
            self.process_ifc(name, description, ifc_class, representation)
        else:
            entity_id = list(SvIfcStore.id_map.keys())[list(SvIfcStore.id_map.values()).index(self.node_id)]
            self.entity = self.file.by_id(entity_id)
            print(name)
            self.entity.Name = name
            self.entity.Description = description

            if representation and not self.file.by_type("IFCPRODUCTDEFINITIONSHAPE"):
                ifcopenshell.api.run("geometry.assign_representation", self.file, product=self.entity, representation=representation)
            elif representation:
                self.entity.Representation = representation
            else:
                pass
            
            if self.entity.is_a() != ifc_class:
                # This crashes blender
                ifcopenshell.util.schema.reassign_class(self.file, self.entity, ifc_class)

        SvIfcStore.file = self.file
        self.outputs["entity"].sv_set([[self.entity]])
        self.outputs["file"].sv_set([[self.file]]) #only for testing

    def process_ifc(self, name, description, ifc_class, representation):
        
        try:
            self.entity = ifcopenshell.api.run("root.create_entity", self.file, ifc_class=ifc_class, name=name, description=description)
            if representation:
                ifcopenshell.api.run("geometry.assign_representation", self.file, product=self.entity, representation=representation)
        except: 
            raise Exception("Something went wrong. Cannot create entity.")

        print("entity: ", self.entity)
        SvIfcStore.id_map[self.entity.id()] = self.node_id
        print("id_map: ", SvIfcStore.id_map)


    def sv_free(self):
        try:
            SvIfcStore.id_map.pop(self.entity.id())
        except KeyError or AttributeError:
            print("Either KeyError or AttributeError occurred.")
            pass

        print("I'm free!")


def register():
    bpy.utils.register_class(SvIfcCreateEntity2)


def unregister():
    bpy.utils.unregister_class(SvIfcCreateEntity2)
