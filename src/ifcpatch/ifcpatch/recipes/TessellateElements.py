# IfcPatch - IFC patching utiliy
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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

import ifcopenshell
import ifcopenshell.api
import ifcopenshell.geom
import ifcopenshell.util.selector
import ifcopenshell.util.shape
import ifcopenshell.util.representation
import multiprocessing
from logging import Logger


class Patcher:
    def __init__(
        self,
        src: str,
        file: ifcopenshell.file,
        logger: Logger,
        query: str = "IfcBeam",
        force_faceted_brep: bool = False,
    ):
        """Convert element body representations to tessellations or faceted breps

        Some software have bugs that result in incorrect geometry being
        imported for more complex representation types, such as CSGs. This
        patch converts elements matching your query into a tessellation (or
        faceted brep for IFC2X3) which is generally supported by all
        implementations. Note that styles and shape aspects are not preserved.

        See example bug: https://github.com/Autodesk/revit-ifc/issues/707

        :param query: Query string to filter out elements to convert, defaults to "IfcBeam"
        :type query: str
        :param force_faceted_brep: Force using IfcFacetedBreps instead of IfcPolygonalFaceSets,
            defaults to `False`
        :type force_faceted_brep: bool

        Example:

        .. code:: python

            ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "TessellateElements", "arguments": ["IfcBeam", False]})
        """
        self.src = src
        self.file = file
        self.logger = logger
        self.query = query
        self.force_faceted_brep = force_faceted_brep

    def patch(self):
        context = ifcopenshell.util.representation.get_context(self.file, "Model", "Body", "MODEL_VIEW")
        elements = ifcopenshell.util.selector.filter_elements(self.file, self.query)

        if not elements:
            return

        settings = ifcopenshell.geom.settings()
        settings.set(settings.STRICT_TOLERANCE, True)
        settings.set_context_ids([context.id()])
        iterator = ifcopenshell.geom.iterator(settings, self.file, multiprocessing.cpu_count(), include=elements)
        replacements = {}
        if iterator.initialize():
            while True:
                shape = iterator.get()
                element = self.file.by_guid(shape.guid)
                v = [[x.tolist() for x in ifcopenshell.util.shape.get_vertices(shape.geometry)]]
                f = [ifcopenshell.util.shape.get_faces(shape.geometry)]
                replacements[element] = (v, f)
                if not iterator.next():
                    break

        # Do the replacements outside the iterator to prevent messing up iterator state.
        for element, geometry in replacements.items():
            v, f = geometry
            mesh = ifcopenshell.api.run(
                "geometry.add_mesh_representation",
                self.file,
                context=context,
                vertices=v,
                faces=f,
                force_faceted_brep=self.force_faceted_brep,
            )
            representations = element.Representation.Representations
            representations = [r for r in representations if r.ContextOfItems != context]
            representations.append(mesh)
            element.Representation.Representations = representations
