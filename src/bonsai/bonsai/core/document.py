# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import ifcopenshell
    import bonsai.tool as tool


def load_project_documents(document: tool.Document) -> None:
    document.clear_document_tree()
    document.import_project_documents()
    document.enable_editing_ui()


def load_document(document_tool: tool.Document, document: ifcopenshell.entity_instance) -> None:
    document_tool.clear_document_tree()
    document_tool.expand_document(document)
    document_tool.import_project_documents()
    document_tool.disable_editing_document()


def disable_document_editing_ui(document: tool.Document) -> None:
    document.disable_editing_ui()
    document.disable_editing_document()


def enable_editing_document(document_tool: tool.Document, document: ifcopenshell.entity_instance) -> None:
    document_tool.set_active_document(document)
    document_tool.enable_document_editing()
    document_tool.import_document_attributes(document)


def disable_editing_document(document: tool.Document) -> None:
    document.clear_active_document()
    document.disable_document_editing()
    document.clear_document_attributes()


def add_information(ifc: tool.Ifc, document_tool: tool.Document, parent=None) -> ifcopenshell.entity_instance:
    document_tool.clear_document_tree()

    if parent is None:
        parent = document_tool.get_default_parent_for_information(ifc)

    information = ifc.run("document.add_information", parent=parent)
    ifc.run("document.add_reference", information=information)

    if document_tool.is_document_information(parent):
        document_tool.expand_document(parent)

    document_tool.import_project_documents()
    return information


def add_reference(ifc: tool.Ifc, document: tool.Document) -> None:
    parent = document.get_selected_document_information(ifc)

    if parent:
        reference = ifc.run("document.add_reference", information=parent)
        reference.Location = ""
        document.expand_document(parent)

    document.import_project_documents()


def edit_document(ifc: tool.Ifc, document_tool: tool.Document, document: ifcopenshell.entity_instance) -> None:
    attributes = document_tool.export_document_attributes()
    if document_tool.is_document_information(document):
        ifc.run("document.edit_information", information=document, attributes=attributes)
    else:
        ifc.run("document.edit_reference", reference=document, attributes=attributes)
    document_tool.disable_editing_document()
    document_tool.clear_document_tree()
    document_tool.import_project_documents()


def remove_document(ifc: tool.Ifc, document_tool: tool.Document, document: ifcopenshell.entity_instance) -> None:
    document_tool.clear_document_tree()
    if document_tool.is_document_information(document):
        ifc.run("document.remove_information", information=document)
    else:
        ifc.run("document.remove_reference", reference=document)
    document_tool.import_project_documents()


def assign_document(
    ifc: tool.Ifc, product: ifcopenshell.entity_instance, document: ifcopenshell.entity_instance
) -> None:
    ifc.run("document.assign_document", products=[product], document=document)


def unassign_document(
    ifc: tool.Ifc, product: ifcopenshell.entity_instance, document: ifcopenshell.entity_instance
) -> None:
    ifc.run("document.unassign_document", products=[product], document=document)
