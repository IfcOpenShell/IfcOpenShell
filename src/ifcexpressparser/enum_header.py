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

import templates

class EnumHeader:
    def __init__(self, mapping):
        selectable_simple_types = sorted(set(sum([b.values for a,b in mapping.schema.selects.items()], [])) & set(mapping.schema.types.keys()))
        enumerable_types = selectable_simple_types + [name for name, type in mapping.schema.entities.items()]
        
        self.str = templates.enum_header % {
            'schema_name_upper' : mapping.schema.name.upper(),
            'schema_name'       : mapping.schema.name.capitalize(),
            'types'             : ', '.join(enumerable_types)
        }
        
        self.schema_name = mapping.schema.name.capitalize()
    def __repr__(self):
        return self.str
    def emit(self):
        f = open('%senum.h'%self.schema_name, 'w', encoding='utf-8')
        f.write(str(self))
        f.close()
