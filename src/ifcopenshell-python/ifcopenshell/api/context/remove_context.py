# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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


class Usecase:
    def __init__(self, file, context=None):
        """Removes an IfcGeometricRepresentationContext

        Any representation geometry that is assigned to the context is also
        removed. If a context is removed, then any subcontexts are also removed.

        :param context: The IfcGeometricRepresentationContext entity to remove
        :type context: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            model = ifcopenshell.api.run("context.add_context", model, context_type="Model")
            # Revit had a bug where they incorrectly called the body representation a "Facetation"
            body = ifcopenshell.api.run("context.add_context", model,
                context_type="Model", context_identifier="Facetation", target_view="MODEL_VIEW", parent=model
            )

            # Let's just get rid of it completely
            ifcopenshell.api.run("context.remove_context", model, context=body)
        """
        self.file = file
        self.settings = {"context": context}

    def execute(self):
        for subcontext in self.settings["context"].HasSubContexts:
            ifcopenshell.api.run("context.remove_context", self.file, context=subcontext)

        if getattr(self.settings["context"], "ParentContext", None):
            new = self.settings["context"].ParentContext
            for inverse in self.file.get_inverse(self.settings["context"]):
                if inverse.is_a("IfcCoordinateOperation"):
                    inverse.SourceCRS = inverse.TargetCRS
                    ifcopenshell.util.element.remove_deep(self.file, inverse)
                else:
                    ifcopenshell.util.element.replace_attribute(inverse, self.settings["context"], new)
            self.file.remove(self.settings["context"])
        else:
            representations_in_context = self.settings["context"].RepresentationsInContext
            self.file.remove(self.settings["context"])
            for element in representations_in_context:
                ifcopenshell.api.run("geometry.remove_representation", self.file, representation=element)
