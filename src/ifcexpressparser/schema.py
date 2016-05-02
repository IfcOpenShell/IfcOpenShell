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
import platform
import collections

if tuple(map(int, platform.python_version_tuple())) < (2, 7):
    import ordereddict
    collections.OrderedDict = ordereddict.OrderedDict
    
# According to ISO 10303-11 7.1.2: Letters: "... The case of 
# letters is significant only within explicit string literals."
class OrderedCaseInsensitiveDict(collections.OrderedDict):
    class KeyObject(str):
        def __eq__(self, other):
            return self.lower() == other.lower()
        def __hash__(self):
            return hash(self.lower())
            
    def __init__(self, *args, **kwargs):
        collections.OrderedDict.__init__(self)
        for key, value in collections.OrderedDict(*args, **kwargs).items():
            self[OrderedCaseInsensitiveDict.KeyObject(key)] = value
    def __setitem__(self, key, value):
        return collections.OrderedDict.__setitem__(self, OrderedCaseInsensitiveDict.KeyObject(key), value)
    def __getitem__(self, key):
        return collections.OrderedDict.__getitem__(self, OrderedCaseInsensitiveDict.KeyObject(key))
    def get(self, key, *args, **kwargs):
        return collections.OrderedDict.get(self, OrderedCaseInsensitiveDict.KeyObject(key), *args, **kwargs)
    def __contains__(self, key):
        return collections.OrderedDict.__contains__(self, OrderedCaseInsensitiveDict.KeyObject(key))

class Schema:
    def is_enumeration(self, v):
        return str(v) in self.enumerations
    def is_select(self, v):
        return str(v) in self.selects
    def is_simpletype(self, v):
        return str(v) in self.simpletypes
    def is_type(self, v):
        return str(v) in self.types
    def is_entity(self, v):
        return str(v) in self.entities
    def __init__(self, parsetree):
        self.name = parsetree[1]

        sort = lambda d: OrderedCaseInsensitiveDict(sorted(d))

        self.types = sort([(t.name,t) for t in parsetree if isinstance(t, nodes.TypeDeclaration)])
        self.entities = sort([(t.name,t) for t in parsetree if isinstance(t, nodes.EntityDeclaration)])

        of_type = lambda *types: sort([(a, b.type.type) for a,b in self.types.items() if any(isinstance(b.type.type, ty) for ty in types)])

        self.enumerations = of_type(nodes.EnumerationType)
        self.selects = of_type(nodes.SelectType)
        self.simpletypes = of_type(str, nodes.AggregationType, nodes.BinaryType, nodes.StringType)
