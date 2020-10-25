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

class Base(object):
    """
    A base class for all code generation classes. Currently only working around
    some python 2/3 incompatibilities in terms of unicode file handling.
    """
    def emit(self):
        import platform
        if tuple(map(int, platform.python_version_tuple())) < (2, 8):
            from io import open as unicode_open
            unicode_type = unicode
        else:
            unicode_open = open
            unicode_type = lambda x, *args, **kwargs: x
        f = unicode_open(self.file_name, 'w', encoding='utf-8')
        f.write(unicode_type(repr(self), encoding='utf-8', errors='ignore'))
        f.close()
