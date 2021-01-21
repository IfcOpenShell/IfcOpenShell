import bpy
from . import ui, prop, operator

classes = (
    operator.AddCsvAttribute,
    operator.RemoveCsvAttribute,
    operator.ExportIfcCsv,
    operator.ImportIfcCsv,
    operator.EyedropIfcCsv,
    prop.CsvProperties,
    ui.BIM_PT_ifccsv,
)



def register():
    bpy.types.Scene.CsvProperties = bpy.props.PointerProperty(type=prop.CsvProperties)


def unregister():
    del bpy.types.Scene.CsvProperties

