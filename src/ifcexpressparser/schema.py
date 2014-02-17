###############################################################################
#                                                                             #
# This file is part of IfcOpenShell.                                          #
#                                                                             #
# IfcOpenShell is free software: you can redistribute it and/or modify        #
# it under the terms of the Lesser GNU General Public License as published by #
# the Free Software Foundation, either version 3.0 of the License, or         #
# (at your option) any later version.                                         #
#                                                                             #
# IfcOpenShell is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                #
# Lesser GNU General Public License for more details.                         #
#                                                                             #
# You should have received a copy of the Lesser GNU General Public License    #
# along with this program. If not, see <http://www.gnu.org/licenses/>.        #
#                                                                             #
###############################################################################

import nodes
import collections

class Schema:
    def is_enumeration(self, v):
        return v in self.enumerations
    def is_select(self, v):
        return v in self.selects
    def is_simpletype(self, v):
        return v in self.simpletypes
    def is_type(self, v):
        return v in self.types
    def is_entity(self, v):
        return v in self.entities
    def __init__(self, parsetree):
        self.name = parsetree[1]

        sort = lambda d: collections.OrderedDict(sorted(d.items()))

        self.types = sort({t.name:t for t in parsetree if isinstance(t, nodes.TypeDeclaration)})
        self.entities = sort({t.name:t for t in parsetree if isinstance(t, nodes.EntityDeclaration)})

        of_type = lambda *types: sort({a: b.type.type for a,b in self.types.items() if any(isinstance(b.type.type, ty) for ty in types)})

        self.enumerations = of_type(nodes.EnumerationType)
        self.selects = of_type(nodes.SelectType)
        self.simpletypes = of_type(str, nodes.AggregationType)
