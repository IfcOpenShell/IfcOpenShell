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
# This file was generated with the assistance of an AI coding tool.

import ifcopenshell
import ifcopenshell.api.system
import ifcopenshell.api.type

import bonsai.tool as tool
from bonsai.bim.module.model.mep import MEPGenerator
from test.bim.bootstrap import NewFile


class TestGetCompatibleFittingType(NewFile):
    def test_existing_fitting_with_no_port_at_its_origin_is_reused(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        segment_type = ifc.createIfcPipeSegmentType(PredefinedType="RIGIDSEGMENT")
        fitting_type = ifc.createIfcPipeFittingType(PredefinedType="TRANSITION")
        fitting = ifc.createIfcPipeFitting()
        ifcopenshell.api.type.assign_type(ifc, related_objects=[fitting], relating_type=fitting_type)
        segments = []
        segment_ports = []
        for x in (1.0, 2.0):
            segment = ifc.createIfcPipeSegment()
            ifcopenshell.api.type.assign_type(ifc, related_objects=[segment], relating_type=segment_type)
            segment_port = ifcopenshell.api.system.add_port(ifc, element=segment)
            fitting_port = ifcopenshell.api.system.add_port(ifc, element=fitting)
            fitting_port.ObjectPlacement = ifc.createIfcLocalPlacement(
                None, ifc.createIfcAxis2Placement3D(ifc.createIfcCartesianPoint((x, 0.0, 0.0)))
            )
            ifcopenshell.api.system.connect_port(ifc, port1=fitting_port, port2=segment_port)
            segments.append(segment)
            segment_ports.append(segment_port)
        result = MEPGenerator().get_compatible_fitting_type(segments, segment_ports, "TRANSITION")
        assert result["fitting_type"] == fitting_type
