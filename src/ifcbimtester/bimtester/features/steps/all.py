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

use_step_matcher("parse")
from bimtester.features.steps.aggregation import en

use_step_matcher("parse")
from bimtester.features.steps.application import en

use_step_matcher("parse")
from bimtester.features.steps.attributes_eleclasses import de, en

use_step_matcher("parse")
from bimtester.features.steps.attributes_psets import en, de

use_step_matcher("parse")
from bimtester.features.steps.attributes_qsets import en

use_step_matcher("parse")
from bimtester.features.steps.classification import en

use_step_matcher("parse")
from bimtester.features.steps.element_classes import en

use_step_matcher("parse")
from bimtester.features.steps.geocoding import en

use_step_matcher("parse")
from bimtester.features.steps.geolocation import en

use_step_matcher("parse")
from bimtester.features.steps.geometric_detail import de, en

use_step_matcher("parse")
from bimtester.features.steps.model_federation import en

use_step_matcher("parse")
from bimtester.features.steps.project_setup import de, en, fr, it, nl

use_step_matcher("parse")
from bimtester.features.steps.spatial_structure import en
