import bpy
from blenderbim.bim.prop import StrProperty, Attribute
from bpy.types import PropertyGroup
from bpy.props import (
    PointerProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    CollectionProperty,
)


class BIMGeoreferenceProperties(PropertyGroup):
    is_editing: BoolProperty(name="Is Editing")
    map_conversion: CollectionProperty(name="Map Conversion", type=Attribute)
    projected_crs: CollectionProperty(name="Projected CRS", type=Attribute)
    map_unit_type: EnumProperty(
        items=[(n, n, "") for n in ["IfcSIUnit", "IfcConversionBasedUnit"]],
        name="Map Unit Type",
        default="IfcSIUnit",
    )
    map_unit_si: EnumProperty(
        items=[(n, n.lower().capitalize(), "") for n in ["MILLIMETRE", "CENTIMETRE", "METRE", "KILOMETRE"]],
        name="Map Unit SI",
        default="METRE",
    )
    map_unit_imperial: EnumProperty(
        items=[(n, n.lower().capitalize(), "") for n in ["inch", "foot", "yard", "mile"]],
        name="Map Unit SI",
        default="foot",
    )
    is_map_unit_null: BoolProperty(name="Is Map Unit Null")
    coordinate_input: StringProperty(name="Coordinate Input")
    coordinate_output: StringProperty(name="Coordinate Output")
    has_blender_offset: BoolProperty(name="Has Blender Offset")
    blender_offset_type: EnumProperty(
        items=[(o, o, "") for o in ["OBJECT_PLACEMENT", "CARTESIAN_POINT"]],
        name="Blender Offset",
        default="OBJECT_PLACEMENT",
    )
    blender_eastings: StringProperty(name="Blender Eastings", default="0")
    blender_northings: StringProperty(name="Blender Northings", default="0")
    blender_orthogonal_height: StringProperty(name="Blender Orthogonal Height", default="0")
    blender_x_axis_abscissa: StringProperty(name="Blender X Axis Abscissa", default="1")
    blender_x_axis_ordinate: StringProperty(name="Blender X Axis Ordinate", default="0")
    has_true_north: BoolProperty(name="Has True North", default=True)
    true_north_abscissa: StringProperty(name="True North Abscissa")
    true_north_ordinate: StringProperty(name="True North Ordinate")
