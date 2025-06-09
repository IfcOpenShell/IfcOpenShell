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

from __future__ import annotations
import bpy
import ifcopenshell
import ifcopenshell.api.pset_template
import ifcopenshell.util.attribute
import ifcopenshell.util.element
import bonsai.core.tool
import bonsai.tool as tool
from pathlib import Path
from typing import Literal, final, TYPE_CHECKING
from bonsai.bim.ifc import IfcStore

if TYPE_CHECKING:
    from bonsai.bim.module.pset_template.prop import BIMPsetTemplateProperties


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

    @classmethod
    def get_pset_template_props(cls) -> BIMPsetTemplateProperties:
        return bpy.context.scene.BIMPsetTemplateProperties

    @classmethod
    def enable_editing_pset_template(cls) -> None:
        props = cls.get_pset_template_props()
        props.active_pset_template_id = int(props.pset_templates)

        pset_template_file = IfcStore.pset_template_file
        assert pset_template_file
        template = pset_template_file.by_id(props.active_pset_template_id)
        props.active_pset_template.global_id = template.GlobalId
        props.active_pset_template.name = template.Name or ""
        props.active_pset_template.description = template.Description or ""
        props.active_pset_template.template_type = template.TemplateType
        props.active_pset_template.applicable_entity = template.ApplicableEntity or ""

        # Disable because of the intersecting enums in data.py.
        props.active_prop_template_id = 0

    @classmethod
    def enable_editing_prop_template(cls, prop_template: ifcopenshell.entity_instance) -> None:
        props = tool.PsetTemplate.get_pset_template_props()
        props.active_prop_template_id = prop_template.id()

        pset_template_file = IfcStore.pset_template_file
        assert pset_template_file
        template = pset_template_file.by_id(props.active_prop_template_id)
        props.active_prop_template.name = template.Name or ""
        props.active_prop_template.description = template.Description or ""
        props.active_prop_template.primary_measure_type = template.PrimaryMeasureType or "-"
        props.active_prop_template.template_type = template.TemplateType
        props.active_prop_template.enum_values.clear()

        if template.Enumerators:
            props.active_prop_template.enum_values.clear()
            data_type = props.active_prop_template.get_value_name()
            for e in template.Enumerators.EnumerationValues:
                new = props.active_prop_template.enum_values.add()
                setattr(new, data_type, e.wrappedValue)

        # Disable because of the intersecting enums in data.py.
        props.active_pset_template_id = 0

    PSET_TEMPLATE_LOCATION = Literal["Global Pset Template", "Project Pset Template"]

    @classmethod
    def get_pset_template_files(cls) -> list[tuple[Path, PSET_TEMPLATE_LOCATION]]:
        """
        :return: List of pset template files. Each template file is represented
            by a tuple of the filepath and pset template location source.
        """
        paths: list[tuple[Path, tool.PsetTemplate.PSET_TEMPLATE_LOCATION]] = []
        for f in tool.Blender.get_data_dir_paths("pset", "*.ifc"):
            paths.append((f, "Global Pset Template"))

        props = tool.Blender.get_bim_props()
        pset_dir = Path(tool.Ifc.resolve_uri(props.pset_dir))
        if pset_dir.is_dir():
            for path in Path(pset_dir).glob("*.ifc"):
                paths.append((path, "Project Pset Template"))
        return paths
