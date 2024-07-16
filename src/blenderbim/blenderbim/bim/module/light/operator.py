# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import os

try:
    import pyradiance as pr
except ImportError:
    print("PyRadiance is not available. Rendering functionality will be disabled.")
    pr = None

import bpy
import blenderbim.tool as tool
from pathlib import Path
from typing import Union, Optional, Sequence
import json
import ifcopenshell
import ifcopenshell.geom
import multiprocessing



class ExportOBJ(bpy.types.Operator):
    """Exports the IFC File to OBJ"""
    bl_idname = "export_scene.radiance"
    bl_label = "Export"
    bl_description = "Export the IFC to OBJ"

    def execute(self, context):

        # Get the output directory
        should_load_from_memory = context.scene.radiance_exporter_properties.should_load_from_memory
        output_dir = context.scene.radiance_exporter_properties.output_dir
        json_file = context.scene.radiance_exporter_properties.json_file


        # Conversion from IFC to OBJ
        # Settings for obj
        settings = ifcopenshell.geom.settings()
        serializer_settings = ifcopenshell.geom.serializer_settings()
        
        settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.SURFACES_AND_SOLIDS)
        settings.set("apply-default-materials", True)
        serializer_settings.set("use-element-guids", True)
        settings.set("use-world-coords", True)

        if should_load_from_memory:
            ifc_file_path = tool.Ifc.get_path()
            
        else:
            ifc_file_path = context.scene.radiance_exporter_properties.ifc_file
        
        ifc_file = ifcopenshell.open(ifc_file_path)
        for material in ifc_file.by_type("IfcMaterial"):
            self.report({'INFO'}, f"Material: {material.Name}, ID: {material.id()}")

        obj_file_path = os.path.join(output_dir, "model.obj")
        mtl_file_path = os.path.join(output_dir, "model.mtl")
        
        serialiser = ifcopenshell.geom.serializers.obj(obj_file_path, mtl_file_path, settings, serializer_settings)
        serialiser.setFile(ifc_file)
        serialiser.setUnitNameAndMagnitude("METER", 1.0)
        serialiser.writeHeader()

        iterator = ifcopenshell.geom.iterator(settings, ifc_file, multiprocessing.cpu_count())
        if iterator.initialize():
            while True:
                serialiser.write(iterator.get())
                if not iterator.next():
                    break
        serialiser.finalize()

        return {'FINISHED'}


class RadianceRender(bpy.types.Operator):
    """Radiance Rendering"""
    bl_idname = "render_scene.radiance"
    bl_label = "Render"
    bl_description = "Renders the scene using Radiance"

    def execute(self, context):
        if pr is None:
            self.report({'ERROR'}, "PyRadiance is not available. Cannot perform rendering.")
            return {'CANCELLED'}
        
        # Get the resolution from the user input
        resolution_x, resolution_y = self.getResolution(context)
        quality = context.scene.radiance_exporter_properties.radiance_quality.upper()
        detail = context.scene.radiance_exporter_properties.radiance_detail.upper()
        variability = context.scene.radiance_exporter_properties.radiance_variability.upper()

        should_load_from_memory = context.scene.radiance_exporter_properties.should_load_from_memory
        output_dir = context.scene.radiance_exporter_properties.output_dir
        json_file = context.scene.radiance_exporter_properties.json_file

        obj_file_path = os.path.join(output_dir, "model.obj")

        if should_load_from_memory:
            ifc_file_path = tool.Ifc.get_path()
            
        else:
            ifc_file_path = context.scene.radiance_exporter_properties.ifc_file
        
        # style = []
        # ifc_file = ifcopenshell.open(ifc_file_path)
        # for material in ifc_file.by_type("IfcSurfaceStyle"):
        #     self.report({'INFO'}, f"Material: {material.Name}, ID: {material.id()}")
        #     if material.id() == 17449 or material.id() == 20871 or material.id() == 15008:
        #         continue
        #     else:
        #         style.append("surface-style-"+str(material.id())+"-"+material.Name)
        

        # Material processing
        style = []
        
        with open(obj_file_path, "r") as obj_file:
            for line in obj_file:
                if line.startswith("usemtl"):
                    l = line.strip().split(" ")
                    style.append(l[1])


        with open(json_file, 'r') as file:
            data = json.load(file)
        
        # Create materials.rad file
        materials_file = os.path.join(output_dir, "materials.rad")
        with open(materials_file, "w") as file:
            file.write("void plastic white\n0\n0\n5 0.6 0.6 0.6 0 0\n")
            file.write("void plastic blue_plastic\n0\n0\n5 0.1 0.2 0.8 0.05 0.1\n")
            file.write("void plastic red_plastic\n0\n0\n5 0.8 0.1 0.2 0.05 0.1\n")
            file.write("void metal silver_metal\n0\n0\n5 0.8 0.8 0.8 0.9 0.1\n")
            file.write("void glass clear_glass\n0\n0\n3 0.96 0.96 0.96\n")
            file.write("void light white_light\n0\n0\n3 1.0 1.0 1.0\n")
            file.write("void trans olive_trans\n0\n0\n7 0.6 0.7 0.4 0.05 0.05 0.7 0.2\n")

            for i in set(style):
                file.write("inherit alias " + i + " " + data.get(i, "white") + "\n")

        self.report({'INFO'}, "Exported Materials Rad file to: {}".format(materials_file))

        # Run obj2mesh
        rtm_file_path = os.path.join(output_dir, "model.rtm")
        mesh_file_path = save_obj2mesh_output(obj_file_path, rtm_file_path,  matfiles=[materials_file])
        # subprocess.run(["obj2mesh", "-a", materials_file, obj_file_path, rtm_file_path])
        self.report({'INFO'}, "obj2mesh output: {}".format(mesh_file_path))
        scene_file = os.path.join(output_dir, "scene.rad")
        with open(scene_file, "w") as file:
            file.write("void mesh model\n1 " + rtm_file_path + "\n0\n0\n")

        self.report({'INFO'}, "Exported Scene file to: {}".format(scene_file))

        # Py Radiance Rendering code
        scene = pr.Scene("ascene")

        material_path = os.path.join(output_dir, "materials.rad")
        scene_path = os.path.join(output_dir, "scene.rad")

        scene.add_material(material_path)
        scene.add_surface(scene_path)

        aview = pr.View(position=(1, 1.5, 1), direction=(1, 0, 0))
        scene.add_view(aview)

        image = pr.render(scene, ambbounce=1, resolution=(resolution_x, resolution_y),
                          quality=quality, detail=detail, variability=variability)
        
        raw_hdr_path = os.path.join(output_dir, "raw.hdr")
        with open(raw_hdr_path, "wb") as wtr:
            wtr.write(image)

        self.report({'INFO'}, "Radiance rendering completed. Output: {}".format(raw_hdr_path))
        return {'FINISHED'}

    def getResolution(self, context):
        scene = context.scene
        props = scene.radiance_exporter_properties
        resolution_x = props.radiance_resolution_x
        resolution_y = props.radiance_resolution_y
        return resolution_x, resolution_y

def save_obj2mesh_output(inp: Union[bytes, str, Path], output_file: str, **kwargs):
    output_bytes = pr.obj2mesh(inp, **kwargs)

    with open(output_file, 'wb') as f:
        f.write(output_bytes)
    return output_file