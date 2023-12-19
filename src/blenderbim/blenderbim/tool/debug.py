# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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
import bpy
import ifcopenshell.express
import blenderbim.core.tool
import blenderbim.tool as tool
from blenderbim.bim.ifc import IfcStore


class Debug(blenderbim.core.tool.Debug):
    @classmethod
    def add_schema_identifier(cls, schema):
        IfcStore.schema_identifiers.append(schema.schema_name)

    @classmethod
    def load_express(cls, filename):
        schema = ifcopenshell.express.parse(filename)
        ifcopenshell.register_schema(schema)
        return schema

    @classmethod
    def purge_hdf5_cache(cls):
        cache_dir = os.path.join(bpy.context.scene.BIMProperties.data_dir, "cache")
        filelist = [f for f in os.listdir(cache_dir) if f.endswith(".h5")]
        for f in filelist:
            os.remove(os.path.join(cache_dir, f))

    @classmethod
    def debug_geometry(cls, verts=[], edges=[], name="Debug"):
        mesh = bpy.data.meshes.new("Debug")
        mesh.from_pydata(verts, edges, [])
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.scene.collection.objects.link(obj)
        return obj

    @classmethod
    def remove_unused_elements(cls, elements):
        ifc_file = tool.Ifc.get()
        for element in elements:
            ifcopenshell.util.element.remove_deep2(ifc_file, element)

    @classmethod
    def print_unused_elements_stats(cls, requested_ifc_class="", ignore_classes=tuple()):
        ifc_file = tool.Ifc.get()

        # get list of ifc classes used in model
        classes = set()
        requested_ifc_classes = set()
        for el in ifc_file:
            if any(el.is_a(i) for i in ignore_classes):
                continue
            classes.add(el.is_a())
            if requested_ifc_class and el.is_a(requested_ifc_class):
                requested_ifc_classes.add(el.is_a())

        # count unused elements for each class
        unused = dict()
        for c in classes:
            uses = [i for i in ifc_file.by_type(c) if ifc_file.get_total_inverses(i) == 0]
            if not uses:
                continue
            unused[c] = len(uses)

        # print classes and their unsued elements in ascending order
        if unused:
            print("Unused elements by classes:")
            for ifc_class in sorted(unused.keys(), key=lambda x: unused[x]):
                class_string = ifc_class
                if ifc_class in requested_ifc_classes:
                    class_string = "---> " + class_string
                print(f"{class_string: <50} {unused[ifc_class]: >5}")

        return sum(unused.values())
