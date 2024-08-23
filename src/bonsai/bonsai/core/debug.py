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


def parse_express(debug, filename):
    debug.add_schema_identifier(debug.load_express(filename))


def purge_hdf5_cache(debug):
    debug.purge_hdf5_cache()


def purge_unused_elements(ifc, debug, ifc_class):
    ifc_file = ifc.get()
    unused_elements = [i for i in ifc_file.by_type(ifc_class) if ifc_file.get_total_inverses(i) == 0]
    unused_elements_amount = len(unused_elements)
    debug.remove_unused_elements(unused_elements)
    return unused_elements_amount
