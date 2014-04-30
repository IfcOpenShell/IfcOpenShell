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

###############################################################################
#                                                                             #
# The IfcOpenShell test suite downloads IFC files that are publicely          #
# available on the internet and uses Blender and IfcOpenShell to generate a   #
# render of the parsed file. For the script to run, Blender needs to be       #
# installed and added to PATH.                                                #
#                                                                             #
###############################################################################

import os
import sys
import shutil
import inspect
import subprocess
from zipfile import ZipFile
from urllib.request import urlretrieve

# Test whether Blender and IfcOpenShell are installed
if subprocess.call(['blender','-b','-P','bpy.py','TEST']) != 0:
    print("[Error] Failed to launch Blender")
    sys.exit(1)
else:
    print("[Notice] Found Blender and IfcOpenShell on system")

# Global variables for keeping track of test cases    
test_cases = []
failed = []

# Create the ouput directory
cwd = os.path.abspath(os.path.dirname(inspect.getfile(inspect.currentframe())))
os.chdir(cwd)
if not os.path.exists("output"): os.mkdir("output")
if not os.path.exists("input"): os.mkdir("input")

def extension(fn):
    return os.path.splitext(fn)[-1].lower()

# Class to download extract and convert IFC files    
class TestFile:
    def __init__(self,fn,store_as=None):
        global test_cases
        self.fn = fn
        self.store_as = store_as
        self.failed = []
        test_cases.append(self)
    def __call__(self):
        if self.fn.startswith("http://") or self.fn.startswith("ftp://"):
            fn = self.store_as if self.store_as else self.fn.split("/")[-1]
            if os.path.exists(os.path.join("input",fn)):
                print ("[Notice] Already downloaded:",fn)
            else:
                print ("[Notice] Downloading:",fn)
                urlretrieve(self.fn,os.path.join("input",fn))
            self.fn = fn
        if extension(self.fn) == '.zip':
            print ("[Notice] Extracting:",self.fn)
            zf = ZipFile(os.path.join("input",self.fn))
            self.fn = [n for n in zf.namelist() if extension(n) == '.ifc' and not n.startswith('__') and not n.startswith('.')]
            for fn in self.fn:
                if not os.path.exists(os.path.join("input",fn)): zf.extract(fn,"input")            
            zf.close()
        else: self.fn = [self.fn]
        for fn in self.fn:
            print ("[Notice] Rendering:",fn)
            succes = subprocess.call(['blender','-b','-P','bpy.py','render',os.path.join("input",fn)]) == 0
            if not succes: self.failed.append(fn)
        return len(self.failed) == 0
    def __str__(self): return "\n".join(self.failed) if len(self.failed) else ""
        
# Karlsruher Institut fuer Technologie
TestFile("http://iai-typo3.iai.fzk.de/www-extern-kit/fileadmin/download/download-vrsys/ADT-FZK-Haus-2005-2006.zip")
TestFile("http://iai-typo3.iai.fzk.de/www-extern-kit/fileadmin/download/download-vrsys/Nem-FZK-Haus-2x3.zip")
TestFile("http://iai-typo3.iai.fzk.de/www-extern-kit/fileadmin/download/download-vrsys/AC14-FZK-Haus.zip")
TestFile("http://iai-typo3.iai.fzk.de/www-extern-kit/fileadmin/download/download-vrsys/FZK-Haus-EliteCAD.zip")

TestFile("http://iai-typo3.iai.fzk.de/www-extern-kit/fileadmin/download/download-vrsys/FJK-Project-Final.zip")

TestFile("http://www.iai.fzk.de/www-extern-kit/fileadmin/download/download-vrsys/Bien-Zenker_Jasmin-Sun-AC14-V2-IFC.zip")

TestFile("http://www.iai.fzk.de/www-extern-kit/fileadmin/download/download-vrsys/ADT-Smiley-West-Project-14-10-2005.zip")
TestFile("http://www.iai.fzk.de/www-extern-kit/fileadmin/download/download-vrsys/Allplan-Smiley-West.zip")
TestFile("http://www.iai.fzk.de/www-extern-kit/fileadmin/download/download-vrsys/AC-11-Smiley-West-04-07-2007-IFC.zip")

TestFile("http://www.iai.fzk.de/www-extern-kit/fileadmin/download/download-vrsys/Allplan-2008-Institute-Var-2-IFC.zip")
TestFile("http://www.iai.fzk.de/www-extern-kit/fileadmin/download/download-vrsys/AC11-Institute-Var-2-IFC.zip")

TestFile("http://iai-typo3.iai.fzk.de/www-extern-kit/fileadmin/download/download-vrsys/PART02_Wilfer_200302_20070209_IFC.zip")
TestFile("http://iai-typo3.iai.fzk.de/www-extern-kit/fileadmin/download/download-vrsys/PART06_Kermi_200405_20070401_IFC.zip")

TestFile("http://iai-typo3.iai.fzk.de/www-extern-kit/fileadmin/download/download-vrsys/Ettenheim-GIS-05-11-2006_optimized.zip")

# Selvaag Gruppen
TestFile("ftp://ftp.dds.no/pub/ifc/Munkerud/Munkerud_hus6_BE.zip")

# Statsbygg 
TestFile("ftp://ftp.dds.no/pub/ifc/HiTOS/2x3_HiTOS_EL_new.zip")
TestFile("ftp://ftp.dds.no/pub/ifc/HiTOS/2x3_HiTOS_HVAC_new.zip")
TestFile("ftp://ftp.dds.no/pub/ifc/HiTOS/HITOS_Architectural_2006-10-25.zip")

# Nemetschek Vectorworks
TestFile("http://download2cf.nemetschek.net/www_misc/bim/DCR-LOD_100.zip")
TestFile("http://download2cf.nemetschek.net/www_misc/bim/DCR-LOD_200.zip")
# Rather large:
# TestFile("http://download2cf.nemetschek.net/www_misc/bim/DCR-LOD_300.zip")

# Data Design Systems
TestFile("ftp://ftp.dds.no/pub/ifc/BardNa/Dds_BardNa.zip")

# Common Building Information Model Files
TestFile("http://projects.buildingsmartalliance.org/files/?artifact_id=4278","2011-09-14-Duplex-IFC.zip")
TestFile("http://projects.buildingsmartalliance.org/files/?artifact_id=4284","2011-09-14-Office-IFC.zip")
# Rather large:
# TestFile("http://projects.buildingsmartalliance.org/files/?artifact_id=4289","2011-09-14-Clinic-IFC.zip")

# http://openifcmodel.cs.auckland.ac.nz IAI 
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/0912101-01wall_layers_number_1.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/0912101-02wall_opening_straight_ac_1.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/0912101-03wall_recess_ben_1.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/0912101-04wall_L-shape_all_1.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/0912102-01beam_profile_basic_rev_1.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/0912102-01beam_profile_para_ac_1.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/0912102-02brep_beams_opening_ben_1.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/0912102-02extruded_beam_open_tek_1.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/0912103-01col_profile_clip_ben_1.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/0912103-01columns_basic_all_1.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/0912103-02col_brep_opening_ben_1.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/0912103-02OpeningsInExtrudedColumns_rev_1.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/0912104-01slab_profile_basic_ac_1.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/0912104-03extruded_slab_openings_all_1.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/0912104-04slab_recess_tek_1.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/0912105-01doors_explicit_geom_all_1.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/0912105-02DoorOperationsPlacementInsideWall_rev_1.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/0912106-01window_brep_ac_1.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/0912106-02windows_placement_inside_wall_all_1.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/0912107-01stair_geometry_ben_1.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/0912108-01ramp_geometry_ben_2.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/0912108-01RampAsContainer_rev_1.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/0912109-01railing_brep_ac_1.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/0912109-01railing_extrusion_tek_1.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/09121010-01RoofWithGeometry_rev_1.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/09121010-02roof_with_openings_ben_1.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/09121011curtain_wall_basic_rev_1.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/09121012mem_profile_basic_tek_1.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/09121013plate_steel_exam_tek_1.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/09121014pile_basic_tek_1.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/09121015footing_ac_1.ifc")

# http://openifcmodel.cs.auckland.ac.nz NIST
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/171210AISC_Sculpture_brep.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/171210AISC_Sculpture_param.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/171210analysis_brep.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/171210analysis_param.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/171210Bentley1_brep.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/171210Bentley1_param.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/171210CADstudio_brep.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/171210cutouts_brep.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/171210DesignData1_brep.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/171210DesignData3_brep.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/171210PlayersTheater_param.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/171210profiles_brep.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/171210profilescp1_brep.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/171210sections_brep.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/171210threebeams_brep.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/171210TrainingStructure_brep.ifc")
TestFile("http://openifcmodel.cs.auckland.ac.nz/_models/171210eccentricity_physical.ifc")

# BIMserver 
TestFile("http://bimserver.googlecode.com/svn/trunk/TestData/data/06-03-01_windows_in_curved_wall_vw.ifc")
TestFile("http://bimserver.googlecode.com/svn/trunk/TestData/data/4351.ifc")
TestFile("http://bimserver.googlecode.com/svn/trunk/TestData/data/AC9R1-Haus-G-H-Ver2-2x3.ifc")
TestFile("http://bimserver.googlecode.com/svn/trunk/TestData/data/AC90R1-niedriha-V2-2x3.ifc")

# File courtesey of Jon Mirtschin / Geometry Gym  
TestFile("geometrygym_great_court_roof.ifc")

# File courtesey of Ryan Schultz / Opening Design / Studio Wikitecture  
TestFile("revit2012_janesville_restaurant.zip")

# Walls cut by IfcPolygonalBoundedHalfSpaces from Revit 2011
TestFile("revit2011_wall1.ifc")
TestFile("revit2011_wall2.ifc")

# Objects from Autocad Architecture 2010
TestFile("acad2010_walls.ifc")
TestFile("acad2010_objects.ifc")

# Various half space configuration to test cutting tolerances
TestFile("ifcopenshell_halfspaces.ifc")

# Several IfcPolygonalBoundedHalfSpaces cutting a single solid
TestFile("revit2014_multiple_bounded_halfspaces.ifc")

# Several parameterized profile extrusions generated by one
# of the examples from the IfcOpenShell repository
TestFile("IfcCShapeProfileDef.ifc")
TestFile("IfcCircleProfileDef.ifc")
TestFile("IfcEllipseProfileDef.ifc")
TestFile("IfcIShapeProfileDef.ifc")
TestFile("IfcLShapeProfileDef.ifc")
TestFile("IfcRectangleProfileDef.ifc")
TestFile("IfcTShapeProfileDef.ifc")
TestFile("IfcTrapeziumProfileDef.ifc")
TestFile("IfcUShapeProfileDef.ifc")
TestFile("IfcZShapeProfileDef.ifc")
TestFile("IfcReinforcingBar.ifc")

TestFile("advanced_brep.ifc")
TestFile("basic_shape_Brep.ifc")
TestFile("basic_shape_CSG.ifc")
TestFile("basic_shape_SurfaceModel.ifc")
TestFile("basic_shape_SweptSolid.ifc")
TestFile("basic_shape_Tessellation.ifc")
TestFile("building_element_configuration_wall.ifc")
TestFile("building_service_element_air-terminal-type.ifc")
TestFile("building_service_element_air-terminal.ifc")
TestFile("construction_scheduling_task.ifc")
TestFile("mapped_shape_multiple.ifc")
TestFile("mapped_shape_representation.ifc")
TestFile("mapped_shape_transformation.ifc")
TestFile("standard_case_element_beam.ifc")
TestFile("structural_analysis_curve.ifc")

for test in test_cases:
    succes = test()
    if not succes:
        failed.append(test)

if len(failed):        
    print("[Notice] Conversion failed for the following cases:")
    for test in failed:
        print (test)
else:
    print("[Notice] All cases succeeded")

