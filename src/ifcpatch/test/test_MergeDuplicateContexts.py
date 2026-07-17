# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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


import ifcopenshell.guid

import ifcpatch
import test.bootstrap


class TestMergeDuplicateContexts(test.bootstrap.IFC4):
    def test_run(self):
        f = self.file
        project = f.by_type("IfcProject")
        project = project[0] if project else f.create_entity("IfcProject", GlobalId=ifcopenshell.guid.new())

        parent1 = f.createIfcGeometricRepresentationContext(ContextType="Model")
        parent2 = f.createIfcGeometricRepresentationContext(ContextType="Model")
        body1 = f.createIfcGeometricRepresentationSubContext(
            ContextType="Model", ContextIdentifier="Body", TargetView="MODEL_VIEW", ParentContext=parent1
        )
        body2 = f.createIfcGeometricRepresentationSubContext(
            ContextType="Model", ContextIdentifier="Body", TargetView="MODEL_VIEW", ParentContext=parent2
        )
        # A representation hangs off the duplicate subcontext; it must be
        # repointed onto the survivor, not orphaned.
        rep = f.createIfcShapeRepresentation(ContextOfItems=body2)
        # Both parents are listed on the project; the SET must not end up with
        # the survivor twice.
        project.RepresentationContexts = [parent1, parent2]

        output = ifcpatch.execute({"file": f, "recipe": "MergeDuplicateContexts", "arguments": []})

        # One Body subcontext and one Model parent context survive.
        bodies = [
            c
            for c in output.by_type("IfcGeometricRepresentationSubContext")
            if c.ContextIdentifier == "Body" and c.TargetView == "MODEL_VIEW"
        ]
        parents = output.by_type("IfcGeometricRepresentationContext", include_subtypes=False)
        assert len(bodies) == 1
        assert len(parents) == 1

        survivor_body = bodies[0]
        survivor_parent = parents[0]

        # The representation was repointed onto the surviving subcontext.
        assert rep.ContextOfItems == survivor_body
        # The surviving subcontext hangs off the surviving parent.
        assert survivor_body.ParentContext == survivor_parent
        # The project references the survivor exactly once (no SET duplicates).
        assert list(output.by_type("IfcProject")[0].RepresentationContexts) == [survivor_parent]

    def test_no_duplicates_is_a_noop(self):
        f = self.file
        parent = f.createIfcGeometricRepresentationContext(ContextType="Model")
        f.createIfcGeometricRepresentationSubContext(
            ContextType="Model", ContextIdentifier="Body", TargetView="MODEL_VIEW", ParentContext=parent
        )
        f.createIfcGeometricRepresentationSubContext(
            ContextType="Model", ContextIdentifier="Axis", TargetView="GRAPH_VIEW", ParentContext=parent
        )
        before = len(f.by_type("IfcGeometricRepresentationContext"))
        output = ifcpatch.execute({"file": f, "recipe": "MergeDuplicateContexts", "arguments": []})
        assert len(output.by_type("IfcGeometricRepresentationContext")) == before


class TestMergeDuplicateContextsIFC2X3(test.bootstrap.IFC2X3, TestMergeDuplicateContexts):
    pass
