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
from typing import Union


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
        if not context:
            return

        elements = ifcopenshell.util.selector.filter_elements(self.file, self.query)

        if not elements:
            return

        settings = ifcopenshell.geom.settings()
        settings.set("context-ids", [context.id()])

        # Iterator can handle only products, so we filter out everything else (IfcTypeProducts).
        products = []
        non_products = []
        for element in elements:
            if element.is_a("IfcProduct"):
                products.append(element)
            else:
                non_products.append(element)

        def store_geometry(
            element: ifcopenshell.entity_instance,
            shape: Union[ifcopenshell.geom.ShapeType, ifcopenshell.geom.ShapeElementType],
        ) -> None:
            geometry = getattr(shape, "geometry", shape)
            v = [[x.tolist() for x in ifcopenshell.util.shape.get_vertices(geometry)]]
            f = [ifcopenshell.util.shape.get_faces(geometry).tolist()]
            replacements[element] = (v, f)

        iterator = ifcopenshell.geom.iterator(settings, self.file, multiprocessing.cpu_count(), include=products)
        replacements = {}
        if iterator.initialize():
            for shape in iterator:
                element = self.file.by_guid(shape.guid)
                store_geometry(element, shape)

        for element in non_products:
            representation = ifcopenshell.util.representation.get_representation(element, context)
            if not representation:
                continue
            shape = ifcopenshell.geom.create_shape(settings, representation)
            store_geometry(element, shape)

        # Do the replacements outside the iterator to prevent messing up iterator state.
        for element, geometry in replacements.items():
            v, f = geometry
            if not v or not f:
                continue
            mesh = ifcopenshell.api.run(
                "geometry.add_mesh_representation",
                self.file,
                context=context,
                vertices=v,
                faces=f,
                force_faceted_brep=self.force_faceted_brep,
            )
            if element.is_a("IfcProduct"):
                representations = element.Representation.Representations
                representations = [r for r in representations if r.ContextOfItems != context]
                representations.append(mesh)
                element.Representation.Representations = representations
            else:  # IfcTypeProduct.
                rep_maps = element.RepresentationMaps
                for rep_map in rep_maps:
                    mapped_rep = rep_map.MappedRepresentation
                    if mapped_rep.ContextOfItems == context:
                        rep_map.MappedRepresentation = mesh
