# IfcPatch - IFC patching utiliy
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcPatch.
#
# IfcPatch is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcPatch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcPatch.  If not, see <http://www.gnu.org/licenses/>.

import os
import logging
import ifcopenshell
from pathlib import Path
from typing import Union


class Patcher:
    def __init__(self, src: str, file: ifcopenshell.file, logger: logging.Logger, output_dir: Union[str, None] = None):
        """Split an IFC model into multiple models based on building storey

        The new IFC model names will be named after the storey name in the
        format of {i}-{name}.ifc, where {i} is an ascending number starting from
        0 and {name} is the name of the storey.

        :param output_dir: Specifies an output directory where the new IFC models will be saved.

        Example:

        .. code:: python

            ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "SplitByBuildingStorey", "arguments": ["C:/.../output_files"]})
        """
        self.src = src
        self.file = file
        self.logger = logger
        self.output_dir = output_dir

    def patch(self) -> None:
        import ifcopenshell
        import tempfile
        from shutil import copyfile

        if self.output_dir is None:
            output_dir = None
        else:
            output_dir = Path(self.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

        temp_file = None
        if not self.src:
            temp_file = tempfile.NamedTemporaryFile(suffix=".ifc", delete=False)
            self.src = temp_file.name
            self.file.write(self.src)

        storeys = self.file.by_type("IfcBuildingStorey")
        for i, storey in enumerate(storeys):
            filename = f"{i}-{storey.Name}.ifc"
            dest = filename if output_dir == None else output_dir / filename
            copyfile(self.src, dest)
            old_ifc: ifcopenshell.file = ifcopenshell.open(dest)
            new_ifc = ifcopenshell.file(schema=self.file.schema)

            if self.file.schema == "IFC2X3":
                elements = old_ifc.by_type("IfcProject") + old_ifc.by_type("IfcProduct")
            else:
                elements = old_ifc.by_type("IfcContext") + old_ifc.by_type("IfcProduct")

            inverse_elements: list[ifcopenshell.entity_instance] = []
            for element in elements:
                if element.is_a("IfcElement") and not self.is_in_storey(element, storey):
                    element.Representation = None
                    continue
                if element.is_a("IfcElement"):
                    styled_rep_items = [
                        i for i in old_ifc.traverse(element) if i.is_a("IfcRepresentationItem") and i.StyledByItem
                    ]
                    [new_ifc.add(i.StyledByItem[0]) for i in styled_rep_items]
                new_ifc.add(element)
                inverse_elements.extend(old_ifc.get_inverse(element))
            for inverse_element in inverse_elements:
                new_ifc.add(inverse_element)
            for element in new_ifc.by_type("IfcElement"):
                if not self.is_in_storey(element, storey):
                    new_ifc.remove(element)
            new_ifc.write(dest)

        if temp_file is not None:
            temp_file.close()
            os.unlink(temp_file.name)

    def is_in_storey(self, element: ifcopenshell.entity_instance, storey: ifcopenshell.entity_instance) -> bool:
        return (
            (contained_in_structure := element.ContainedInStructure)
            and (relating_structure := contained_in_structure[0].RelatingStructure).is_a("IfcBuildingStorey")
            and relating_structure.GlobalId == storey.GlobalId
        )
