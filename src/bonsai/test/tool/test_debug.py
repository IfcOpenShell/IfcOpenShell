# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

import os
import bpy
import ifcopenshell
import ifcopenshell.api.style
import ifcopenshell.util.schema
import bonsai.core.tool
import bonsai.tool as tool
from test.bim.bootstrap import NewFile
from bonsai.tool.debug import Debug as subject
from bonsai.bim.ifc import IfcStore
from pathlib import Path


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Debug)


class TestAddSchemaIdentifier(NewFile):
    def test_run(self):
        cwd = os.path.dirname(os.path.realpath(__file__))
        schema_path = os.path.join(cwd, "..", "files", "test.exp")
        schema = subject.load_express(schema_path)
        subject.add_schema_identifier(schema)
        assert IfcStore.schema_identifiers[-1] == "IFCROGUE"
        os.remove(schema_path + ".cache.dat")


class TestLoadExpress(NewFile):
    def test_run(self):
        cwd = os.path.dirname(os.path.realpath(__file__))
        schema_path = os.path.join(cwd, "..", "files", "test.exp")
        schema = subject.load_express(schema_path)
        assert schema.schema_name == "IFCROGUE"
        os.remove(schema_path + ".cache.dat")


class TestPurgeHdf5Cache(NewFile):
    def test_run(self):
        cache_dir = Path(bpy.context.scene.BIMProperties.cache_dir)
        test_file = cache_dir / "test.h5"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.touch()

        # Ensure it can skip currently loaded cache.
        loaded_file_path = test_file.with_stem("test_loaded")
        loaded_file = open(loaded_file_path, "w")

        subject.purge_hdf5_cache()
        # On Unix loaded files are not locked.
        paths = [loaded_file_path] if os.name == "nt" else []
        assert [f for f in cache_dir.iterdir() if f.suffix == ".h5"] == paths


class TestMergeIdenticalObject(NewFile):
    def test_merge_identical_styles(self):
        tool.Ifc.set(ifc := ifcopenshell.file())
        declaration = tool.Ifc.schema().declaration_by_name("IfcPresentationStyle")
        style_types = [d.name() for d in ifcopenshell.util.schema.get_subtypes(declaration)]
        for style_type in style_types:
            ifc.create_entity(style_type, Name=style_type)
            ifc.create_entity(style_type, Name=style_type)
            ifc.create_entity(style_type, Name="NotToMerge")
            if style_type == "IfcSurfaceStyle":
                for style in ifc.by_type(style_type):
                    style.Styles = (ifc.create_entity("IfcSurfaceStyleShading"),)
            elif style_type == "IfcFillAreaStyle":
                for style in ifc.by_type(style_type):
                    style.FillStyles = (ifc.create_entity("IfcFillAreaStyleHatching"),)

        merge_data = subject.merge_identical_objects("STYLE")
        assert merge_data == {style_type: [style_type] for style_type in style_types}

    def test_merge_identical_materials(self):
        tool.Ifc.set(ifc := ifcopenshell.file())
        context = ifc.create_entity("IfcGeometricRepresentationContext")
        style = ifc.create_entity("IfcSurfaceStyle")
        element_types = ["IfcMaterial"]
        for element_type in element_types:
            ifc.create_entity(element_type, Name=element_type, Category="Category")
            ifc.create_entity(element_type, Name=element_type, Category="Category")
            ifc.create_entity(element_type, Name="NotToMerge", Category="Category")

            for material in ifc.by_type(element_type):
                ifcopenshell.api.style.assign_material_style(ifc, material, style, context)

        merge_data = subject.merge_identical_objects("MATERIAL")
        assert merge_data == {element_type: [element_type] for element_type in element_types}
