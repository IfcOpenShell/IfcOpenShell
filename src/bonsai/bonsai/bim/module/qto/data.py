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


def refresh():
    QtoData.is_loaded = False


class QtoData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "has_cost_item": cls.has_cost_item(),
            "relating_cost_items": cls.relating_cost_items(),
        }

        cls.is_loaded = True

    @classmethod
    def has_cost_item(cls):
        return False if not cls.relating_cost_items() else True

    @classmethod
    def relating_cost_items(cls):
        obj = bpy.context.active_object
        if not obj:
            return
        element = tool.Ifc.get_entity(obj)
        if not element:
            return []

        results = []
        relating_cost_items = tool.Qto.get_related_cost_item_quantities(element)
        for relating_cost_item in relating_cost_items:
            results.append(
                {
                    "cost_item_id": relating_cost_item["cost_item_id"],
                    "cost_item_name": relating_cost_item["cost_item_name"],
                    "quantity_id": relating_cost_item["quantity_id"],
                    "quantity_name": relating_cost_item["quantity_name"],
                    "quantity_value": relating_cost_item["quantity_value"],
                    "quantity_type": relating_cost_item["quantity_type"],
                }
            )

        return results
