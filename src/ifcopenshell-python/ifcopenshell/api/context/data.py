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


class Data:
    is_loaded = False
    contexts = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.contexts = {}

    @classmethod
    def load(cls, file):
        if not file:
            return
        cls.contexts = {}
        for context in file.by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            subcontexts = {}
            for subcontext in context.HasSubContexts:
                subcontexts[int(subcontext.id())] = {
                    "ContextType": subcontext.ContextType,
                    "ContextIdentifier": subcontext.ContextIdentifier,
                    "TargetView": subcontext.TargetView,
                }
            cls.contexts[int(context.id())] = {"ContextType": context.ContextType, "HasSubContexts": subcontexts}
        cls.is_loaded = True
