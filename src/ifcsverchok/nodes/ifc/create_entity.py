import bpy
import ifcopenshell
import ifcsverchok.helper
from bpy.props import StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode


class SvIfcCreateEntity(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcCreateEntity"
    bl_label = "IFC Create Entity"
    file: StringProperty(name="file", update=updateNode)
    ifc_class: StringProperty(name="ifc_class", update=updateNode)
    current_ifc_class: StringProperty(name="current_ifc_class")

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "file").prop_name = "file"
        self.inputs.new("SvStringsSocket", "ifc_class").prop_name = "ifc_class"
        self.outputs.new("SvStringsSocket", "file")
        self.outputs.new("SvStringsSocket", "entity")

    def process(self):
        self.sv_input_names = ["file", "ifc_class"]
        ifc_class = self.inputs["ifc_class"].sv_get()[0][0]
        if ifc_class:
            file = self.inputs["file"].sv_get()[0][0]
            if file:
                schema_name = file.wrapped_data.schema
            else:
                schema_name = "IFC4"
            self.schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(schema_name)
            self.entity_schema = self.schema.declaration_by_name(ifc_class)

            if ifc_class != self.current_ifc_class:
                self.generate_inputs(ifc_class)
            try:
                for i in range(0, len(self.inputs)):
                    self.inputs[i].sv_get()
            except:
                # This occurs when a blender save file is reloaded
                self.generate_inputs(ifc_class)

            for i in range(0, self.entity_schema.attribute_count()):
                self.sv_input_names.append(self.entity_schema.attribute_by_index(i).name())
        super().process()

    def generate_inputs(self, ifc_class):
        while len(self.inputs) > 2:
            self.inputs.remove(self.inputs[-1])
        for i in range(0, self.entity_schema.attribute_count()):
            name = self.entity_schema.attribute_by_index(i).name()
            setattr(SvIfcCreateEntity, name, StringProperty(name=name))
            self.inputs.new("SvStringsSocket", name).prop_name = name
        self.current_ifc_class = ifc_class

    def process_ifc(self, file, ifc_class, *attributes):
        entity = file.create_entity(ifc_class)
        for i in range(0, len(entity)):
            try:
                value = attributes[i]
                if isinstance(value, str) and value == "":
                    value = None
            except:
                value = None
            if value is None and entity.is_a("IfcRoot") and i == 0:
                value = ifcopenshell.guid.new()
            if value is not None:
                value = self.cast_value(self.entity_schema.attribute_by_index(i), value)
            try:
                entity[i] = value
            except:
                raise Exception(
                    "The IFC class {} requires a valid value for {} - you provided {}".format(
                        ifc_class, entity.attribute_name(i), value
                    )
                )
        self.outputs["file"].sv_set([[file]])
        self.outputs["entity"].sv_set([[entity]])

    def cast_value(self, attribute, value):
        data_type = self.get_attribute_data_type(attribute.type_of_attribute())
        if data_type == "integer":
            value = int(value)
        return value

    def get_attribute_data_type(self, data_type):
        if hasattr(data_type, "declared_type"):
            return self.get_attribute_data_type(data_type.declared_type())
        return data_type


def register():
    bpy.utils.register_class(SvIfcCreateEntity)


def unregister():
    bpy.utils.unregister_class(SvIfcCreateEntity)
