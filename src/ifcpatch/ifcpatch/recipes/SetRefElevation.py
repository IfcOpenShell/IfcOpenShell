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

import typing


class Patcher:
    def __init__(self, src, file, logger, elevation: typing.Union[str, float] = "0"):
        """Sets the reference elevation of all IfcSites

        To completely reference model coordinates, a reference elevation should
        be specified on the IfcSite. This is often omitted or not possible by
        proprietary BIM applications. This patch lets you set the reference
        elevation attribute explicitly.

        Note that this does not physically shift the Z coordinates of anything.
        The reference elevation is simply a numerical attribute.

        :param elevation: The elevation to set.
        :type elevation: typing.Union[str, float]

        Example:

        .. code:: python

            # All IfcSites will have their reference elevation set to 42.
            ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "SetRefElevation", "arguments": [42]})
        """
        self.src = src
        self.file = file
        self.logger = logger
        self.elevation = float(elevation)

    def patch(self):
        project = self.file.by_type("IfcProject")[0]
        sites = self.find_decomposed_ifc_class(project, "IfcSite")
        for site in sites:
            site.RefElevation = float(self.elevation)

    def find_decomposed_ifc_class(self, element, ifc_class):
        results = []
        rel_aggregates = element.IsDecomposedBy
        if not rel_aggregates:
            return results
        for rel_aggregate in rel_aggregates:
            for part in rel_aggregate.RelatedObjects:
                if part.is_a(ifc_class):
                    results.append(part)
                results.extend(self.find_decomposed_ifc_class(part, ifc_class))
        return results
