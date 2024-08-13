# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import bpy
from bpy.types import Operator


class BIM_OT_cityjson2ifc(Operator):
    bl_idname = "bim.convert_cityjson2ifc"
    bl_label = "Convert CityJSON to IFC"
    bl_context = "scene"

    def execute(self, context):
        from cjio import cityjson
        from ifccityjson.cityjson2ifc.cityjson2ifc import Cityjson2ifc

        props = context.scene.ifccityjson_properties
        city_model = cityjson.load(props.input, transform=False)
        data = {
            "file_destination": props.output,
            "lod": props.lod,
            "split": props.split_lod,
        }
        if props.name != "":
            data["name_attribute"] = props.name

        converter = Cityjson2ifc()
        converter.configuration(**data)
        converter.convert(city_model)
        if props.load_after_convert:
            bpy.ops.bim.load_project(filepath=props.output)
        return {"FINISHED"}


class BIM_OT_find_cityjson_lod(Operator):
    bl_idname = "bim.find_cityjson_lod"
    bl_label = "Find LODs in CityJSON File"
    bl_context = "scene"

    def execute(self, context):
        from cjio import cityjson

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
        return {"FINISHED"}
