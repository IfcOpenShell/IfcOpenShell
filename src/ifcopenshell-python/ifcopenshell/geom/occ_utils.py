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

import random
from collections import namedtuple

import OCC.gp
import OCC.V3d
import OCC.Quantity
import OCC.BRepTools
import OCC.Display.SimpleGui

tuple = namedtuple('shape', ('data', 'geometry'))

handle, main_loop, add_menu, add_function_to_menu = None, None, None, None

def initialize_display():
    global handle, main_loop, add_menu, add_function_to_menu
    handle, main_loop, add_menu, add_function_to_menu = OCC.Display.SimpleGui.init_display()

    def setup():
        viewer_handle = handle.GetViewer()
        viewer = viewer_handle.GetObject()
        while True:
            viewer.InitActiveLights()
            try: active_light = viewer.ActiveLight()
            except: break
            viewer.DelLight(active_light)
            viewer.NextActiveLights()
        for dir in [(1,2,-3), (-2,-1,1)]:
            light = OCC.V3d.V3d_DirectionalLight(viewer_handle)
            light.SetDirection(*dir)
            viewer.SetLightOn(light.GetHandle())
    setup()
    return handle


def display_shape(shape, clr=None):
    if not clr: 
        r = lambda: random.random() * 0.3 + 0.7
        clr = OCC.Quantity.Quantity_Color(r(), r(), r(), OCC.Quantity.Quantity_TOC_RGB)
    return handle.DisplayShape(shape, color=clr, update=True)


def set_shape_transparency(ais, t):
    handle.Context.SetTransparency(ais, t)


def get_bounding_box_center(bbox):
    bbmin = [0.]*3; bbmax = [0.]*3
    bbmin[0], bbmin[1], bbmin[2], bbmax[0], bbmax[1], bbmax[2] = bbox.Get()
    return OCC.gp.gp_Pnt(*map(lambda xy: (xy[0]+xy[1])/2., zip(bbmin, bbmax)))


def create_shape_from_serialization(brep_object):
    brep_data, occ_shape = None, None
    
    is_product_shape = True
    try:
        brep_data = brep_object.geometry.brep_data
    except: 
        try: 
            brep_data = brep_object.brep_data
            is_product_shape = False
        except: pass
    if not brep_data: return tuple(brep_object, None)
    
    try:
        ss = OCC.BRepTools.BRepTools_ShapeSet()
        ss.ReadFromString(brep_data)
        occ_shape = ss.Shape(ss.NbShapes())
    except: pass
    
    if is_product_shape:
        return tuple(brep_object, occ_shape)
    else:
        return occ_shape

