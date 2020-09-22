import bpy
from sverchok.data_structure import zip_long_repeat

ifc_files = {}

class SvIfcCore():
    def process(self):
        sv_inputs_nested = []
        for name in self.sv_input_names:
            sv_inputs_nested.append(self.inputs[name].sv_get())
        for sv_input_nested in zip_long_repeat(*sv_inputs_nested):
            for sv_input in zip_long_repeat(*sv_input_nested):
                sv_input = list(sv_input)
                self.process_ifc(*sv_input)
