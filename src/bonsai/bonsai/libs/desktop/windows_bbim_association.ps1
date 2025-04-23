param(
    [string]$BlenderPath = "BLENDER_EXE"
)

Start-Process cmd -ArgumentList `
    "/k ", `
    "ASSOC .IFC=", `
    "&", `
    "FTYPE BONSAI=""$BlenderPath"" --python-expr ""import bpy; bpy.ops.bim.load_project(filepath=r'%1')""",
    "&", `
    "echo. & echo. & echo To create an association between .IFC files and Bonsai", `
    "&", `
    "echo type the command below & echo.", `
    "&", `
    "echo ASSOC .IFC=BONSAI & echo." `
-Verb RunAs
