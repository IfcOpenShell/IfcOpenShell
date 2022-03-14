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


def load_information(document):
    document.import_information()
    document.enable_information_editing_ui()
    document.disable_editing_document()


def load_references(document):
    document.import_references()
    document.enable_reference_editing_ui()
    document.disable_editing_document()


def disable_document_editing_ui(document):
    document.disable_editing_ui()
    document.disable_editing_document()


def enable_editing_document(document_tool, document=None):
    document_tool.import_document_attributes(document)
    document_tool.set_active_document(document)


def disable_editing_document(document):
    document.disable_editing_document()


def add_information(ifc, document):
    result = ifc.run("document.add_information")
    document.import_information()
    document.import_document_attributes(result)
    document.set_active_document(result)


def add_reference(ifc, document):
    result = ifc.run("document.add_reference")
    document.import_references()
    document.import_document_attributes(result)
    document.set_active_document(result)


def edit_information(ifc, document, information=None):
    attributes = document.export_document_attributes()
    ifc.run("document.edit_information", information=information, attributes=attributes)
    document.disable_editing_document()
    document.import_information()


def edit_reference(ifc, document, reference=None):
    attributes = document.export_document_attributes()
    ifc.run("document.edit_reference", reference=reference, attributes=attributes)
    document.disable_editing_document()
    document.import_references()


def remove_document(ifc, document_tool, document=None):
    if document_tool.is_document_information(document):
        ifc.run("document.remove_document", document=document)
        document_tool.import_information()
    else:
        ifc.run("document.remove_document", document=document)
        document_tool.import_references()
    document_tool.disable_editing_document()


def enable_assigning_document(document, obj=None):
    document.import_references()
    document.enable_reference_editing_ui()
    document.disable_editing_document()
    document.enable_document_assignment_ui(obj)


def disable_assigning_document(document, obj=None):
    document.disable_document_assignment_ui(obj)


def assign_document(ifc, product=None, document=None):
    ifc.run("document.assign_document", product=product, document=document)


def unassign_document(ifc, product=None, document=None):
    ifc.run("document.unassign_document", product=product, document=document)
