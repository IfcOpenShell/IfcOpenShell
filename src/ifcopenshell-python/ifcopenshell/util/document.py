# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Petru Conduraru <petru@bimvoice.com>
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

from __future__ import annotations

from typing import Optional

import ifcopenshell


def get_revision_history(
    document: ifcopenshell.entity_instance, _visited: Optional[set[int]] = None
) -> list[ifcopenshell.entity_instance]:
    """Gets the superseded revisions of a document, oldest edits last

    A document (typically an IfcDocumentInformation, such as a drawing
    sheet) may have older revisions attached to it as subdocuments via
    IfcDocumentInformationRelationship, where ``document`` is considered the
    latest version and its related documents are progressively older
    revisions. See ``ifcopenshell.api.document.add_information`` for how
    such a chain is created.

    :param document: The IfcDocumentInformation to get the revision history
        of. This is typically the current/latest revision.
    :return: A flattened list of older IfcDocumentInformation revisions,
        ordered from the most recent to the oldest. ``document`` itself is
        not included.

    Example:

    .. code:: python

        history = ifcopenshell.util.document.get_revision_history(sheet)
        for revision in history:
            print(revision.Revision, revision.Description)
    """
    if _visited is None:
        _visited = set()
    results: list[ifcopenshell.entity_instance] = []
    for rel in document.IsPointer or []:
        for child in rel.RelatedDocuments or []:
            if child.id() in _visited:
                continue
            _visited.add(child.id())
            results.append(child)
            results.extend(get_revision_history(child, _visited))
    return results
