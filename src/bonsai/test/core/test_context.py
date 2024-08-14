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

import bonsai.core.context as subject
from test.core.bootstrap import ifc, context


class TestAddContext:
    def test_adding_a_context(self, ifc):
        ifc.run(
            "context.add_context", context_type="Model", context_identifier=None, target_view=None, parent=None
        ).should_be_called().will_return("context")
        assert (
            subject.add_context(ifc, context_type="Model", context_identifier=None, target_view=None, parent=None)
            == "context"
        )

    def test_adding_a_subcontext(self, ifc):
        ifc.run(
            "context.add_context",
            context_type="Model",
            context_identifier="Body",
            target_view="MODEL_VIEW",
            parent="parent",
        ).should_be_called().will_return("subcontext")
        assert (
            subject.add_context(
                ifc, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent="parent"
            )
            == "subcontext"
        )


class TestRemoveContext:
    def test_removing_a_context(self, ifc):
        ifc.run("context.remove_context", context="context").should_be_called()
        subject.remove_context(ifc, context="context")


class TestEnableEditingContext:
    def test_run(self, context):
        context.set_context("context").should_be_called()
        context.import_attributes().should_be_called()
        subject.enable_editing_context(context, context="context")


class TestDisableEditingContext:
    def test_run(self, context):
        context.clear_context().should_be_called()
        subject.disable_editing_context(context)


class TestEditContext:
    def test_run(self, ifc, context):
        context.get_context().should_be_called().will_return("context")
        context.export_attributes().should_be_called().will_return("attributes")
        ifc.run("context.edit_context", context="context", attributes="attributes").should_be_called()
        context.clear_context().should_be_called()
        subject.edit_context(ifc, context)
