# /// script
# [tool.ty.environment]
# root = ["."]
# ///
###############################################################################
#                                                                             #
# This file is part of IfcOpenShell.                                        #
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
#
import sys

from common import SCRIPT_DIR, run_streamed


def main() -> None:
    run_streamed(sys.executable, str(SCRIPT_DIR / "build-ifcopenshell.py"), "--target", "INSTALL", *sys.argv[1:])


if __name__ == "__main__":
    main()
