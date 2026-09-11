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

import logging
from unittest import mock

import bpy
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.guid
import ifcopenshell.util.representation
from ifcopenshell.util.shape_builder import ShapeBuilder, V

import bonsai.bim.import_ifc as import_ifc
import bonsai.tool as tool
from test.bim.bootstrap import NewFile


class FakeIterator:
    """Stands in for ifcopenshell.geom.iterator so a silently-skipped element
    can be simulated without depending on a specific geometry kernel bug."""

    def __init__(self, shapes):
        self.shapes = shapes
        self.index = 0

    def initialize(self):
        return True

    def progress(self):
        return 100

    def set_cache(self, cache):
        pass

    def get(self):
        return self.shapes[self.index] if self.index < len(self.shapes) else None

    def next(self):
        self.index += 1
        return self.index < len(self.shapes)


class TestCreateProducts(NewFile):
    def test_warns_about_elements_the_iterator_silently_dropped(self, caplog):
        bpy.ops.bim.create_project()
        ifc_file = tool.Ifc.get()

        body_context = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Body", "MODEL_VIEW")
        builder = ShapeBuilder(ifc_file)
        curve = builder.rectangle(size=V(1.0, 1.0))
        profile = ifc_file.createIfcArbitraryClosedProfileDef(ProfileType="AREA", OuterCurve=curve)
        solid = builder.extrude(profile, magnitude=1.0)
        rep = ifc_file.createIfcShapeRepresentation(
            ContextOfItems=body_context, RepresentationIdentifier="Body", RepresentationType="SweptSolid", Items=[solid]
        )
        pds = ifc_file.createIfcProductDefinitionShape(Representations=[rep])
        wall_ok = ifc_file.createIfcWall(GlobalId=ifcopenshell.guid.new(), Representation=pds)
        wall_dropped = ifc_file.createIfcWall(GlobalId=ifcopenshell.guid.new(), Representation=pds)

        settings = ifcopenshell.geom.settings()
        real_shape = ifcopenshell.geom.create_shape(settings, wall_ok)
        assert real_shape.id == wall_ok.id()

        import_settings = import_ifc.IfcImportSettings.factory(bpy.context, None, logging.getLogger("ImportIFC"))
        import_settings.geometry_library = "cgal"
        importer = import_ifc.IfcImporter(import_settings)
        importer.file = ifc_file

        fake_iterator = FakeIterator([real_shape, None])
        with mock.patch("ifcopenshell.geom.iterator", return_value=fake_iterator):
            with caplog.at_level(logging.ERROR, logger="ImportIFC"):
                results = importer.create_products({wall_ok, wall_dropped}, settings)

        assert results == {wall_ok}
        messages = " ".join(record.message for record in caplog.records)
        assert f"#{wall_dropped.id()}={wall_dropped.is_a()}" in messages
        assert "cgal" in messages
