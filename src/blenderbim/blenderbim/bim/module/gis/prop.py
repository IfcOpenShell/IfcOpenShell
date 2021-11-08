from bpy.types import PropertyGroup
from bpy.props import StringProperty, BoolProperty, EnumProperty, CollectionProperty
from blenderbim.bim.prop import StrProperty

class BIMCityJsonProperties(PropertyGroup):
    def get_lods(self, context):
        return [(item.name, "LOD" + item.name, "Level of Detail " + item.name) for item in self.lods]

    input: StringProperty(name="cj_input", default="", subtype='FILE_PATH')
    output: StringProperty(name="ifc_output", default="", subtype='FILE_PATH')
    name: StringProperty(name="identifier", default="")
    split_lod: BoolProperty(name="split_lod", default=True)
    lods: CollectionProperty(name="lods", type=StrProperty)
    lod: EnumProperty(name="lod", description="", items=get_lods, options={'ANIMATABLE'}, default=None)
    is_lod_found: BoolProperty(name="is_lod_found", default=False)
    load_after_convert: BoolProperty(name="load_after_convert", default=True)
