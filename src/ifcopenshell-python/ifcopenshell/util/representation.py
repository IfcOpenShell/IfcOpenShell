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


def get_context(ifc_file, context, subcontext=None, target_view=None):
    if subcontext or target_view:
        elements = ifc_file.by_type("IfcGeometricRepresentationSubContext")
    else:
        elements = ifc_file.by_type("IfcGeometricRepresentationContext", include_subtypes=False)
    for element in elements:
        if context and element.ContextType != context:
            continue
        if subcontext and getattr(element, "ContextIdentifier") != subcontext:
            continue
        if target_view and getattr(element, "TargetView") != target_view:
            continue
        return element


def is_representation_of_context(representation, context, subcontext=None, target_view=None):
    if target_view is not None:
        return (
            representation.ContextOfItems.is_a("IfcGeometricRepresentationSubContext")
            and representation.ContextOfItems.TargetView == target_view
            and representation.ContextOfItems.ContextIdentifier == subcontext
            and representation.ContextOfItems.ContextType == context
        )
    elif subcontext is not None:
        return (
            representation.ContextOfItems.is_a("IfcGeometricRepresentationSubContext")
            and representation.ContextOfItems.ContextIdentifier == subcontext
            and representation.ContextOfItems.ContextType == context
        )
    elif representation.ContextOfItems.ContextType == context:
        return True


def get_representation(element, context, subcontext=None, target_view=None):
    if element.is_a("IfcProduct") and element.Representation:
        for r in element.Representation.Representations:
            if is_representation_of_context(r, context, subcontext, target_view):
                return r
    elif element.is_a("IfcTypeProduct") and element.RepresentationMaps:
        for r in element.RepresentationMaps:
            if is_representation_of_context(r.MappedRepresentation, context, subcontext, target_view):
                return r.MappedRepresentation
