# BIMTester - OpenBIM Auditing Tool
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BIMTester.
#
# BIMTester is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BIMTester is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with BIMTester.  If not, see <http://www.gnu.org/licenses/>.

from collections import defaultdict


class TableModel:
    """This class represents a table of data"""

    def __init__(self, key_name=None, value_name=None):
        self.rows = defaultdict(list)
        self.key_name = key_name
        self.value_name = value_name

    def add_row(self, related, relating):
        self.rows[related].append(relating)

    def get_count(self):
        return len(self.rows)

    def get_count_distinct_values(self):
        return len(set(item for sublist in self.rows.values() for item in sublist))
