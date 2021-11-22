from blenderbim.bim.ifc import IfcStore
import bpy
import json
import blenderbim.core.tool  #TODO check this
import blenderbim.tool as tool  #TODO check this
import ifcopenshell
import blenderbim.bim.helper
from blenderbim.bim.module.georeference.data import GeoreferenceData
from ifcopenshell.api.unit.data import Data as UnitData #TODO Connect new module data
from math import radians, degrees, atan, tan, cos, sin

class Georeference(blenderbim.core.tool.Georeference):
    @classmethod
    def set_georeferencing(cls, georeferencing):
        bpy.context.scene.BIMGeoreferenceProperties.active_georeferencing_id = georeferencing.id()

    @classmethod
    def import_georeferencing_attributes(cls):
        georeferencing = tool.Ifc.get().by_id(bpy.context.scene.BIMGeoreferenceProperties.active_georeferencing_id)  #TODO IS IT NECESSARY?

        props = bpy.context.scene.BIMGeoreferenceProperties

        props.projected_crs.clear()

        blenderbim.bim.helper.import_attributes(
            "IfcProjectedCRS", props.projected_crs, GeoreferenceData.data["projected_crs"], cls.import_projected_crs_attributes
        )

        props.map_conversion.clear()
        blenderbim.bim.helper.import_attributes(
            "IfcMapConversion", props.map_conversion, GeoreferenceData.data["map_conversion"], cls.import_map_conversion_attributes
        )

        props.has_true_north = bool(GeoreferenceData.data["true_north"])
        if GeoreferenceData.data["true_north"]:
            props.true_north_abscissa = str(GeoreferenceData.data["true_north"][0])
            props.true_north_ordinate = str(GeoreferenceData.data["true_north"][1])
        
        props.is_editing = True
    
    @classmethod
    def import_projected_crs_attributes(cls, name, prop, data):
        props = bpy.context.scene.BIMGeoreferenceProperties
        if name == "MapUnit":
            new = props.projected_crs.add()
            new.name = name
            new.data_type = "enum"
            new.is_null = data[name] is None
            new.is_optional = True
            new.enum_items = json.dumps(
                {u["id"]: u["Name"] for u in UnitData.units.values() if u["UnitType"] == "LENGTHUNIT"}
            )
            if data["MapUnit"]:
                new.enum_value = str(data["MapUnit"]["id"])
            return True

    @classmethod
    def import_map_conversion_attributes(cls, name, prop, data):
        if name not in ["SourceCRS", "TargetCRS"]:
            # Enforce a string data type to prevent data loss in single-precision Blender props
            prop.data_type = "string"
            prop.string_value = "" if prop.is_null else str(data[name])
            return True
    
    @classmethod
    def clear_georeferencing(cls):
        bpy.context.scene.BIMGeoreferenceProperties.active_georeferencing_id = 0
        props = bpy.context.scene.BIMGeoreferenceProperties
        props.is_editing = False
        

    @classmethod
    def get_georeferencing(cls):
        return tool.Ifc().get().by_id(bpy.context.scene.BIMGeoreferenceProperties.active_georeferencing_id)
    
    @classmethod
    def export_georeferencing_attributes(cls):
        props = bpy.context.scene.BIMGeoreferenceProperties
        file = IfcStore.get_file()

        projected_crs = blenderbim.bim.helper.export_attributes(props.projected_crs, cls.export_crs_attributes)
        map_conversion = blenderbim.bim.helper.export_attributes(props.map_conversion, cls.export_map_attributes)

        true_north = None
        if props.has_true_north:
            try:
                true_north = [float(props.true_north_abscissa), float(props.true_north_ordinate)]
            except ValueError:
                cls.report({"ERROR"}, "True North Abscissa and Ordinate expect a number")

        #TODO is it correct to run the api here??? Other modules runs api in core
        
        ifcopenshell.api.run(
            "georeference.edit_georeferencing",
            file,
            **{
                "map_conversion": map_conversion,
                "projected_crs": projected_crs,
                "true_north": true_north,
            }
        )

    @classmethod
    def export_map_attributes(self, attributes, prop):
        if not prop.is_null and prop.data_type == "string":
            # We store our floats as string to prevent single precision data loss
            attributes[prop.name] = float(prop.string_value)
            return True

    @classmethod
    def export_crs_attributes(self, attributes, prop):
        if not prop.is_null and prop.name == "MapUnit":
            attributes[prop.name] = self.file.by_id(int(prop.enum_value))
            return True
    
    @classmethod
    def add_georeferencing(cls):
        file = IfcStore.get_file()
        ifcopenshell.api.run("georeference.add_georeferencing", file)

    @classmethod
    def remove_georeferencing(cls):
        file = IfcStore.get_file()
        ifcopenshell.api.run("georeference.remove_georeferencing", file)

    @classmethod
    def set_blender_grid_north(cls):
        bpy.context.scene.sun_pos_properties.north_offset = -radians(
            ifcopenshell.util.geolocation.xaxis2angle(
                float(bpy.context.scene.BIMGeoreferenceProperties.map_conversion.get("XAxisAbscissa").string_value),
                float(bpy.context.scene.BIMGeoreferenceProperties.map_conversion.get("XAxisOrdinate").string_value),
            )
        )
