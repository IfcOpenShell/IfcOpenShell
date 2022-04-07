# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.


def load_project_documents(document):
    document.clear_document_tree()
    document.import_project_documents()
    document.clear_breadcrumbs()
    document.enable_editing_ui()


def load_document(document_tool, document=None):
    document_tool.clear_document_tree()
    document_tool.import_subdocuments(document)
    document_tool.import_references(document)
    document_tool.disable_editing_document()
    document_tool.add_breadcrumb(document)


def load_parent_document(document):
    document.clear_document_tree()
    document.remove_latest_breadcrumb()
    parent = document.get_active_breadcrumb()
    if parent:
        document.import_subdocuments(parent)
        document.import_references(parent)
        document.disable_editing_document()
    else:
        document.import_project_documents()


def disable_document_editing_ui(document):
    document.disable_editing_ui()
    document.disable_editing_document()


def enable_editing_document(document_tool, document=None):
    document_tool.import_document_attributes(document)
    document_tool.set_active_document(document)


def disable_editing_document(document):
    document.disable_editing_document()


def add_information(ifc, document):
    document.clear_document_tree()
    parent = document.get_active_breadcrumb()
    information = ifc.run("document.add_information", parent=parent)
    ifc.run("document.add_reference", information=information)
    if parent:
        document.import_subdocuments(parent)
        document.import_references(parent)
    else:
        document.import_project_documents()


def add_reference(ifc, document):
    parent = document.get_active_breadcrumb()
    ifc.run("document.add_reference", information=parent)
    document.clear_document_tree()
    document.import_subdocuments(parent)
    document.import_references(parent)


def edit_document(ifc, document_tool, document=None):
    attributes = document_tool.export_document_attributes()
    if document_tool.is_document_information(document):
        ifc.run("document.edit_information", information=document, attributes=attributes)
    else:
        ifc.run("document.edit_reference", reference=document, attributes=attributes)
    document_tool.disable_editing_document()
    document_tool.clear_document_tree()
    parent = document_tool.get_active_breadcrumb()
    if parent:
        document_tool.import_subdocuments(parent)
        document_tool.import_references(parent)
    else:
        document_tool.import_project_documents()


def remove_document(ifc, document_tool, document=None):
    document_tool.clear_document_tree()
    if document_tool.is_document_information(document):
        ifc.run("document.remove_information", information=document)
    else:
        ifc.run("document.remove_reference", reference=document)
    parent = document_tool.get_active_breadcrumb()
    if parent:
        document_tool.import_subdocuments(parent)
        document_tool.import_references(parent)
    else:
        document_tool.import_project_documents()


def assign_document(ifc, product=None, document=None):
    ifc.run("document.assign_document", product=product, document=document)


def unassign_document(ifc, product=None, document=None):
    ifc.run("document.unassign_document", product=product, document=document)
