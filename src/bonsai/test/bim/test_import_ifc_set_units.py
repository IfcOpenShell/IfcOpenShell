# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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
#
# This file was modified with the assistance of an AI coding tool.

"""Regression tests for ``IfcImporter`` crashing on entities with an
optional attribute left unset.

- ``set_units``: a hand-crafted or otherwise invalid IFC file can carry
  an ``IfcConversionBasedUnit`` with a null ``Name`` even though the
  schema marks it mandatory (IfcOpenShell does not enforce this at
  parse time). Bonsai already treats this as a real, previously-hit
  defect class for ``ifcopenshell.util.unit`` (see PR fixing #8885);
  this covers the same class of bug in ``bim/import_ifc.py``'s own
  direct ``unit.Name`` reads.

- ``update_linked_aggregates``: ``IfcRoot.Name`` is genuinely optional,
  so a member of a legacy "BBIM_Linked_Aggregate" group with no Name
  crashed every subsequent load of that file."""

import logging
import os
import tempfile

import bpy
import ifcopenshell
import ifcopenshell.api.group
import ifcopenshell.api.root

import bonsai.bim.import_ifc as import_ifc
import bonsai.tool as tool
from test.bim.bootstrap import NewFile

NAMELESS_LENGTH_UNIT_IFC = """ISO-10303-21;
HEADER;
FILE_DESCRIPTION((''),'2;1');
FILE_NAME('','',(''),(''),'','','');
FILE_SCHEMA(('IFC4'));
ENDSEC;
DATA;
#1=IFCPROJECT('0AntSXen9$3gN_yzeBBRAn',$,'My Project',$,$,$,$,(#5),#4);
#4=IFCUNITASSIGNMENT((#2));
#2=IFCCONVERSIONBASEDUNIT($,.LENGTHUNIT.,$,#3);
#3=IFCMEASUREWITHUNIT(IFCLENGTHMEASURE(0.0254),#6);
#6=IFCSIUNIT($,.LENGTHUNIT.,$,.METRE.);
#5=IFCGEOMETRICREPRESENTATIONCONTEXT($,'Model',3,1.0E-5,#7,$);
#7=IFCAXIS2PLACEMENT3D(#8,$,$);
#8=IFCCARTESIANPOINT((0.,0.,0.));
ENDSEC;
END-ISO-10303-21;
"""


class TestSetUnitsNamelessUnit(NewFile):
    def test_run(self):
        path = os.path.join(tempfile.mkdtemp(), "nameless_unit.ifc")
        with open(path, "w") as f:
            f.write(NAMELESS_LENGTH_UNIT_IFC)

        ifc = ifcopenshell.open(path)
        unit = ifc.by_type("IfcConversionBasedUnit")[0]
        assert unit.Name is None

        settings = import_ifc.IfcImportSettings.factory(bpy.context, path, logging.getLogger("ImportIFC"))
        importer = import_ifc.IfcImporter(settings)
        importer.file = ifc

        # Must not raise AttributeError on the None .Name.
        importer.set_units()


class TestUpdateLinkedAggregatesNamelessMember(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file(schema="IFC4")
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject", name="P")
        group = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcGroup", name="BBIM_Linked_Aggregate")
        wall = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall", name=None)
        assert wall.Name is None
        ifcopenshell.api.group.assign_group(ifc, products=[wall], group=group)

        settings = import_ifc.IfcImportSettings.factory(bpy.context, "", logging.getLogger("ImportIFC"))
        importer = import_ifc.IfcImporter(settings)
        importer.file = ifc

        # Must not raise AttributeError on the None .Name.
        importer.update_linked_aggregates()
