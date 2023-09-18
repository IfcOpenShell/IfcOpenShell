param(
    [string]$BlenderPath = "BLENDER_EXE"
)

Start-Process cmd -ArgumentList `
    "/k ", `
    "ASSOC .IFC=", `
    "&", `
    "FTYPE BLENDERBIM=""$BlenderPath"" --python-expr ""import bpy; bpy.ops.bim.load_project(filepath=r'%1')""",
    "&", `
    "echo. & echo. & echo To create an association between .IFC files and BlenderBIM", `
    "&", `
    "echo type the command below & echo.", `
    "&", `
    "echo ASSOC .IFC=BLENDERBIM & echo." `
-Verb RunAs