# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.
# This file was generated with the assistance of an AI coding tool.

import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.root
import test.bootstrap


class TestAddTopologyRepresentation(test.bootstrap.IFC4):
    def setup_context(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        return ifcopenshell.api.context.add_context(
            self.file,
            context_type="Model",
            context_identifier="Reference",
            target_view="GRAPH_VIEW",
            parent=model,
        )

    def test_creates_topology_representation(self):
        context = self.setup_context()
        face = self.file.create_entity("IfcFaceSurface")
        rep = ifcopenshell.api.geometry.add_topology_representation(self.file, context=context, item=face)
        assert rep.is_a("IfcTopologyRepresentation")
        assert rep.ContextOfItems == context
        assert face in rep.Items

    def test_infers_face_representation_type(self):
        context = self.setup_context()
        face = self.file.create_entity("IfcFaceSurface")
        rep = ifcopenshell.api.geometry.add_topology_representation(self.file, context=context, item=face)
        assert rep.RepresentationType == "Face"

    def test_infers_edge_representation_type(self):
        context = self.setup_context()
        edge = self.file.create_entity("IfcEdge")
        rep = ifcopenshell.api.geometry.add_topology_representation(self.file, context=context, item=edge)
        assert rep.RepresentationType == "Edge"

    def test_defaults_representation_identifier_to_context_identifier(self):
        context = self.setup_context()
        face = self.file.create_entity("IfcFaceSurface")
        rep = ifcopenshell.api.geometry.add_topology_representation(self.file, context=context, item=face)
        assert rep.RepresentationIdentifier == context.ContextIdentifier

    def test_custom_representation_identifier(self):
        context = self.setup_context()
        face = self.file.create_entity("IfcFaceSurface")
        rep = ifcopenshell.api.geometry.add_topology_representation(
            self.file, context=context, item=face, representation_identifier="Body"
        )
        assert rep.RepresentationIdentifier == "Body"

    def test_custom_representation_type_overrides_inferred(self):
        context = self.setup_context()
        face = self.file.create_entity("IfcFaceSurface")
        rep = ifcopenshell.api.geometry.add_topology_representation(
            self.file, context=context, item=face, representation_type="Undefined"
        )
        assert rep.RepresentationType == "Undefined"


class TestAddTopologyRepresentationIFC2X3(test.bootstrap.IFC2X3, TestAddTopologyRepresentation):
    pass
