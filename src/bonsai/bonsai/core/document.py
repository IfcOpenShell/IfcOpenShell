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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import ifcopenshell

    import bonsai.tool as tool


def load_project_documents(document: tool.Document) -> None:
    document.clear_document_tree()
    document.import_project_documents()
    document.enable_editing_ui()


def disable_document_editing_ui(document: tool.Document) -> None:
    document.disable_editing_ui()
    document.disable_editing_document()


def disable_object_document_editing_ui(document: tool.Document) -> None:
    document.disable_object_editing_ui()


def enable_editing_document(document: tool.Document, ifc_document: ifcopenshell.entity_instance) -> None:
    document.set_active_document(ifc_document)
    document.import_document_attributes(ifc_document)


def disable_editing_document(document: tool.Document) -> None:
    document.clear_active_document()
    document.clear_document_attributes()


def add_information(ifc: tool.Ifc, document: tool.Document, parent=None) -> ifcopenshell.entity_instance:
    document.clear_document_tree()

    if parent is None:
        parent = document.get_default_parent_for_information()

    information = ifc.run("document.add_information", parent=parent)
    ifc.run("document.add_reference", information=information)

    if document.is_document_information(parent):
        document.expand_document(parent)

    document.import_project_documents()
    return information


def add_reference(ifc: tool.Ifc, document: tool.Document) -> None:
    parent = document.get_selected_document_information()

    if parent:
        reference = ifc.run("document.add_reference", information=parent)
        reference.Location = ""
        document.expand_document(parent)

    document.import_project_documents()


def edit_document(ifc: tool.Ifc, document: tool.Document, ifc_document: ifcopenshell.entity_instance) -> None:
    attributes = document.export_document_attributes()
    if document.is_document_information(ifc_document):
        ifc.run("document.edit_information", information=ifc_document, attributes=attributes)
    else:
        ifc.run("document.edit_reference", reference=ifc_document, attributes=attributes)
    document.disable_editing_document()
    document.clear_document_tree()
    document.import_project_documents()


def remove_document(ifc: tool.Ifc, document: tool.Document, ifc_document: ifcopenshell.entity_instance) -> None:
    document.clear_document_tree()
    if document.is_document_information(ifc_document):
        ifc.run("document.remove_information", information=ifc_document)
    else:
        ifc.run("document.remove_reference", reference=ifc_document)
    document.import_project_documents()


def assign_document(
    ifc: tool.Ifc, product: ifcopenshell.entity_instance, ifc_document: ifcopenshell.entity_instance
) -> None:
    ifc.run("document.assign_document", products=[product], document=ifc_document)


def unassign_document(
    ifc: tool.Ifc, product: ifcopenshell.entity_instance, ifc_document: ifcopenshell.entity_instance
) -> None:
    ifc.run("document.unassign_document", products=[product], document=ifc_document)
