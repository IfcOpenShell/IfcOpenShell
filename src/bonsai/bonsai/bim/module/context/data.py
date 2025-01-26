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
import bonsai.tool as tool
import ifcopenshell
from typing import Any


def refresh():
    ContextData.is_loaded = False


class ContextData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"contexts": cls.get_contexts()}
        cls.is_loaded = True

    @classmethod
    def get_contexts(cls) -> list[dict[str, Any]]:
        results = []
        for context in tool.Ifc.get().by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            results.append(
                {
                    "id": context.id(),
                    "context_type": context.ContextType,
                    "subcontexts": cls.get_subcontexts(context),
                }
            )
        return results

    @classmethod
    def get_subcontexts(cls, context: ifcopenshell.entity_instance) -> list[dict[str, Any]]:
        results = []
        for subcontext in context.HasSubContexts:
            results.append(
                {
                    "id": subcontext.id(),
                    "context_type": subcontext.ContextType,
                    "context_identifier": subcontext.ContextIdentifier,
                    "target_view": subcontext.TargetView,
                }
            )
        return results
