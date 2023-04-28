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


class Usecase:
    def __init__(self, file, context, attributes):
        """Edits the attributes of an IfcGeometricRepresentationContext

        For more information about the attributes and data types of an
        IfcGeometricRepresentationContext, consult the IFC documentation.

        :param context: The IfcGeometricRepresentationContext entity you want to edit
        :type context: ifcopenshell.entity_instance.entity_instance
        :param attributes: a dictionary of attribute names and values.
        :type attributes: dict, optional
        :return: None
        :rtype: None

        Example:

        .. code:: python

            model = ifcopenshell.api.run("context.add_context", model, context_type="Model")
            # Revit had a bug where they incorrectly called the body representation a "Facetation"
            body = ifcopenshell.api.run("context.add_context", model,
                context_type="Model", context_identifier="Facetation", target_view="MODEL_VIEW", parent=model
            )

            # Let's fix it!
            ifcopenshell.api.run("context.edit_context", model,
                context=body, attributes={"ContextIdentifier": "Body"})
        """
        self.file = file
        self.settings = {"context": context, "attributes": attributes or {}}

    def execute(self):
        for name, value in self.settings["attributes"].items():
            setattr(self.settings["context"], name, value)
