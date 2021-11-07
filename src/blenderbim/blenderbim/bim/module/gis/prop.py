from bpy.types import PropertyGroup
from bpy.props import StringProperty, BoolProperty, EnumProperty, CollectionProperty

class BIM_PT_existing_lods(PropertyGroup):
    name: StringProperty(name="name")

class BIM_PT_ifccityjson_properties(PropertyGroup):
    def get_lods(self, context):
        return [(item.name, "LOD" + item.name, "Level of Detail " + item.name) for item in self.lods]

    input: StringProperty(name="cj_input", default="", subtype='FILE_PATH')
    output: StringProperty(name="ifc_output", default="", subtype='FILE_PATH')
    name: StringProperty(name="identifier", default="")
    split_lod: BoolProperty(name="split_lod", default=True)
    lods: CollectionProperty(name="lods", type=BIM_PT_existing_lods)
    lod: EnumProperty(name="lod", description="", items=get_lods, options={'ANIMATABLE'}, default=None)
    is_lod_found: BoolProperty(name="is_lod_found", default=False)
