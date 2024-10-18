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
import ifcopenshell
import ifcopenshell.api.pset_template
import ifcopenshell.util.attribute
import ifcopenshell.util.element
import bonsai.core.tool
import bonsai.tool as tool
from typing import Union, Literal, Any, final
from typing_extensions import assert_never
from bonsai.bim.ifc import IfcStore


class PsetTemplate(bonsai.core.tool.PsetTemplate):
    class PsetTemplateOperator:
        """`tool.Ifc.Operator` but for pset template file."""

        @final
        def execute(self, context):
            IfcStore.begin_transaction(self)
            template_file = IfcStore.pset_template_file
            assert template_file
            self.template_file = template_file
            template_file.begin_transaction()
            result = self._execute(context)
            template_file.end_transaction()
            IfcStore.add_transaction_operation(self)
            IfcStore.end_transaction(self)
            bonsai.bim.handler.refresh_ui_data()
            return {"FINISHED"}

        def rollback(self, data):
            self.template_file.undo()

        def commit(self, data):
            self.template_file.redo()

        def _execute(self, context: bpy.types.Context) -> None:
            tool.Ifc.Operator._execute(self, context)

    @classmethod
    def add_pset_as_template(
        cls, pset: ifcopenshell.entity_instance, template_file: ifcopenshell.file
    ) -> ifcopenshell.entity_instance:
        # TODO: add tests.
        pset_template = ifcopenshell.api.pset_template.add_pset_template(template_file, pset.Name)
        for property in pset.HasProperties:
            ifcopenshell.api.pset_template.add_prop_template(
                template_file,
                pset_template,
                name=property.Name,
                description=property.Description,
                primary_measure_type=property.NominalValue.is_a(),
            )
        return pset_template
