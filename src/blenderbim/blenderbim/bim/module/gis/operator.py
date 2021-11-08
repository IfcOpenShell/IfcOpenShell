import bpy
from bpy.types import Operator
from cjio import cityjson
from ifccityjson.cityjson2ifc.cityjson2ifc import Cityjson2ifc

class BIM_OT_cityjson2ifc(Operator):
    bl_idname = "bim.convert_cityjson2ifc"
    bl_label = "Convert CityJSON to IFC"
    bl_context = "scene"

    def execute(self, context):
        props = context.scene.ifccityjson_properties
        city_model = cityjson.load(props.input, transform=False)
        data = {
            "file_destination": props.output,
            "lod": props.lod,
            "split": props.split_lod,
        }
        if props.name is not "":
            data["name_attribute"] = props.name

        converter = Cityjson2ifc()
        converter.configuration(**data)
        converter.convert(city_model)
        if props.load_after_convert:
            bpy.ops.bim.load_project(filepath=props.output)
        return {'FINISHED'}


class BIM_OT_find_cityjson_lod(Operator):
    bl_idname = "bim.find_cityjson_lod"
    bl_label = "Find LODs in CityJSON file"
    bl_context = "scene"

    def execute(self, context):
        props = context.scene.ifccityjson_properties
        city_model = cityjson.load(props.input)
        lods = set()
        for obj_id, obj in city_model.get_cityobjects().items():
            for geometry in obj.geometry:
                lod = str(geometry.lod)
                if lod not in lods:
                    lods.add(lod)
                    props.lods.add()
                    props.lods[-1].name = lod
        props.is_lod_found = True
        return {'FINISHED'}
