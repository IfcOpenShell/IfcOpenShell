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
import ifcopenshell.api
import ifcopenshell.util.classification
import bonsai.core.tool
import bonsai.tool as tool
from typing import Union, assert_never, TYPE_CHECKING

if TYPE_CHECKING:
    from bonsai.bim.module.classification.prop import BIMClassificationReferenceProperties, BIMClassificationProperties


class Classification(bonsai.core.tool.Classification):
    @classmethod
    def get_classification_props(cls) -> BIMClassificationProperties:
        assert (scene := bpy.context.scene)
        return scene.BIMClassificationProperties  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def get_classification_reference_props(cls) -> BIMClassificationReferenceProperties:
        assert (scene := bpy.context.scene)
        return scene.BIMClassificationReferenceProperties  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def get_location(cls, classification: ifcopenshell.entity_instance) -> Union[str, None]:
        schema = classification.file.schema
        if schema in ("IFC4", "IFC4X3"):
            return classification[5]
        elif schema == "IFC2X3":
            return None
        assert_never(schema)

    @classmethod
    def set_location(cls, classification: ifcopenshell.entity_instance, location: Union[str, None]) -> None:
        schema = classification.file.schema
        if schema in ("IFC4", "IFC4X3"):
            classification[5] = location
            return
        elif schema == "IFC2X3":
            return
        assert_never(schema)
