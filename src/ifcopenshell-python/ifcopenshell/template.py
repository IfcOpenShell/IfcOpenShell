# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Thomas Krijnen <thomas@aecgeeks.com>
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


import time
import uuid

from .file import file
from .guid import compress
from .ifcopenshell_wrapper import version
from typing import Optional


# A quick way to setup an 'empty' IFC file, taken from:
# http://academy.ifcopenshell.org/creating-a-simple-wall-with-property-set-and-quantity-information/
TEMPLATE = """ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('ViewDefinition [CoordinationView]'),'2;1');
FILE_NAME('%(filename)s','%(timestring)s',('%(creator)s'),('%(organization)s'),'%(application)s','%(application)s','');
FILE_SCHEMA(('%(schema_identifier)s'));
ENDSEC;
DATA;
#1=IFCPERSON($,$,'%(creator)s',$,$,$,$,$);
#2=IFCORGANIZATION($,'%(organization)s',$,$,$);
#3=IFCPERSONANDORGANIZATION(#1,#2,$);
#4=IFCAPPLICATION(#2,'%(application_version)s','%(application)s','');
#5=IFCOWNERHISTORY(#3,#4,$,.NOTDEFINED.,$,#3,#4,%(timestamp)s);
#6=IFCDIRECTION((1.,0.,0.));
#7=IFCDIRECTION((0.,0.,1.));
#8=IFCCARTESIANPOINT((0.,0.,0.));
#9=IFCAXIS2PLACEMENT3D(#8,#7,#6);
#10=IFCDIRECTION((0.,1.));
#11=IFCGEOMETRICREPRESENTATIONCONTEXT($,'Model',3,1.E-05,#9,#10);
#12=IFCDIMENSIONALEXPONENTS(0,0,0,0,0,0,0);
#13=IFCSIUNIT(*,.LENGTHUNIT.,$,.METRE.);
#14=IFCSIUNIT(*,.AREAUNIT.,$,.SQUARE_METRE.);
#15=IFCSIUNIT(*,.VOLUMEUNIT.,$,.CUBIC_METRE.);
#16=IFCSIUNIT(*,.PLANEANGLEUNIT.,$,.RADIAN.);
#17=IFCMEASUREWITHUNIT(IFCPLANEANGLEMEASURE(0.017453292519943295),#16);
#18=IFCCONVERSIONBASEDUNIT(#12,.PLANEANGLEUNIT.,'DEGREE',#17);
#19=IFCUNITASSIGNMENT((#13,#14,#15,#18));
#20=IFCPROJECT('%(project_globalid)s',#5,'%(project_name)s',$,$,$,$,(#11),#19);
ENDSEC;
END-ISO-10303-21;
"""

DEFAULTS = {
    "application": lambda d: "IfcOpenShell-%s" % version(),
    "application_version": lambda d: version(),
    "project_globalid": lambda d: compress(uuid.uuid4().hex),
    "schema_identifier": lambda d: "IFC4",
    "timestamp": lambda d: int(time.time()),
    "timestring": lambda d: time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(d.get("timestamp") or time.time())),
}


def create(
    filename: Optional[str] = None,
    timestring: Optional[str] = None,
    organization: Optional[str] = None,
    creator: Optional[str] = None,
    schema_identifier: Optional[str] = None,
    application_version: Optional[str] = None,
    timestamp: Optional[str] = None,
    application: Optional[str] = None,
    project_globalid: Optional[str] = None,
    project_name: Optional[str] = None,
) -> file:
    d = dict(locals())

    def _():
        for var, value in d.items():
            if value is None:
                yield var, DEFAULTS.get(var, lambda *args: "")(d)

    d.update(dict(_()))

    return file.from_string(TEMPLATE % d)
