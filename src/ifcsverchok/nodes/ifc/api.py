import bpy
import ifcopenshell
import ifcopenshell.api
import ifcsverchok.helper
from bpy.props import StringProperty, EnumProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode
#from blenderbim.bim.module.root.prop import getIfcClasses, getIfcProducts, refreshClasses, refreshPredefinedTypes


class SvIfcApi(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcApi"
    bl_label = "IFC API"
    usecase: StringProperty(name="Usecase", update=updateNode)
    #schema: StringProperty(name="schema", update=updateNode, default="IFC4")
    #ifc_product: EnumProperty(items=getIfcProducts, name="Products", update=refreshClasses)
    #ifc_class: EnumProperty(items=getIfcClasses, name="Class", update=refreshPredefinedTypes)
    #custom_ifc_class: StringProperty(name="Custom Ifc Class", update=updateNode)

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "usecase").prop_name = "usecase"
        #self.inputs.new("SvStringsSocket", "schema").prop_name = "schema"
        #self.inputs.new("SvStringsSocket", "ifc_product").prop_name = "ifc_product"
        #self.inputs.new("SvStringsSocket", "ifc_class").prop_name = "ifc_class"
        #self.inputs.new("SvStringsSocket", "custom_ifc_class").prop_name = "custom_ifc_class"
        self.outputs.new("SvVerticesSocket", "file")

    def process(self):
        print('process')
        #self.sv_input_names = ["file", "ifc_product", "ifc_class", "custom_ifc_class"]
        usecase = self.inputs["usecase"].sv_get()[0][0]
        if usecase:
            self.generate_node(*usecase.split("."))
        self.sv_input_names = ["usecase"]
        super().process()

    def generate_node(self, module, usecase):
        try:
            node_data = ifcopenshell.api.extract_docs(module, usecase)
        except:
            print("Node not yet implemented:", module, usecase)
            return
        while len(self.inputs) > 1:
            self.inputs.remove(self.inputs[-1])

        for name, data in node_data["inputs"].items():
            setattr(SvIfcApi, name, StringProperty(name=name))
            self.inputs.new("SvStringsSocket", name).prop_name = name

    #def process_ifc(self, file, ifc_product, ifc_class, custom_ifc_class):
    def process_ifc(self, usecase):
        print('run')
        #self.outputs["file"].sv_set([ifcopenshell.api.run("project.create_file", version=schema)])
        #if custom_ifc_class:
        #    self.outputs["entity"].sv_set([file.by_type(custom_ifc_class)])
        #else:
        #    self.outputs["entity"].sv_set([file.by_type(ifc_class)])


def register():
    bpy.utils.register_class(SvIfcApi)


def unregister():
    bpy.utils.unregister_class(SvIfcApi)
