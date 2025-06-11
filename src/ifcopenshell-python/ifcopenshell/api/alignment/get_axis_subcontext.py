# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2025 Thomas Krijnen <thomas@aecgeeks.com>
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

import ifcopenshell
import ifcopenshell.util.representation
import ifcopenshell.api.context
from ifcopenshell import entity_instance


def get_axis_subcontext(file: ifcopenshell.file) -> entity_instance:
    """
    Returns the IfcGeometricRepresentationSubContext for Model, Axis, MODEL_VIEW. If one does not exist, it is created.
    """
    axis_geom_subcontext = ifcopenshell.util.representation.get_context(file, "Model", "Axis", "MODEL_VIEW")
    if axis_geom_subcontext == None:
        geometric_representation_context = ifcopenshell.api.context.add_context(file, context_type="Model")
        axis_geom_subcontext = ifcopenshell.api.context.add_context(
            file,
            context_type="Model",
            context_identifier="Axis",
            target_view="MODEL_VIEW",
            parent=geometric_representation_context,
        )

    return axis_geom_subcontext
