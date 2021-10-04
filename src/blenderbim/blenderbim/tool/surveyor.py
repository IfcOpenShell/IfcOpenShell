import bpy
import ifcopenshell.api
import blenderbim.core.tool
import blenderbim.tool as tool
import numpy as np


class Surveyor(blenderbim.core.tool.surveyor.Surveyor):
    @classmethod
    def get_absolute_matrix(cls, obj):
        matrix = np.array(obj.matrix_world)
        props = bpy.context.scene.BIMGeoreferenceProperties
        if props.has_blender_offset and obj.BIMObjectProperties.blender_offset_type == "OBJECT_PLACEMENT":
            unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
            matrix = np.array(
                ifcopenshell.util.geolocation.local2global(
                    matrix,
                    float(props.blender_eastings) * unit_scale,
                    float(props.blender_northings) * unit_scale,
                    float(props.blender_orthogonal_height) * unit_scale,
                    float(props.blender_x_axis_abscissa),
                    float(props.blender_x_axis_ordinate),
                )
            )
        return matrix
