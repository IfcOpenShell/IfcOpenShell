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

import bonsai.core.debug as subject
from test.core.bootstrap import debug


class TestParseExpress:
    def test_run(self, debug):
        debug.load_express("filename").should_be_called().will_return("schema")
        debug.add_schema_identifier("schema").should_be_called()
        subject.parse_express(debug, "filename")


class TestPurgeHdf5Cache:
    def test_run(self, debug):
        debug.purge_hdf5_cache().should_be_called()
        subject.purge_hdf5_cache(debug)
