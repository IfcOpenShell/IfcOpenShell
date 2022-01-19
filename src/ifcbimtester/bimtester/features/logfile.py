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

import json


def create_logfile(thelogfile, ifcbasename):

    logfile = open(thelogfile, "w")
    logfile.write("BIMTester log file\n")
    logfile.write("------------------\n\n")
    logfile.write("ifc base file name: {}\n".format(ifcbasename))
    logfile.close()


def append_logfile(thecontext, step):

    # step attributes (also these set by user) scope is the scenario
    # https://behave.readthedocs.io/en/latest/thecontext_attributes.html
    print("Step '{}' failed".format(step.name))

    # log file
    logfile = open(thecontext.thelogfile, "a")
    logfile.write("\n\nStep '{}' failed\n".format(step.name))
    if hasattr(thecontext, "falseelems"):
        logfile.write("{}\n".format(json.dumps(thecontext.falseelems, indent=4)))
        if hasattr(thecontext, "falseprops"):
            logfile.write("{}\n".format(json.dumps(thecontext.falseprops, indent=4)))
    logfile.close()
