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
    
    try: brep_data = brep_object.geometry.brep_data
    except: pass    
    if not brep_data: return tuple(brep_object, None)
    
    try:
        ss = OCC.BRepTools.BRepTools_ShapeSet()
        ss.ReadFromString(brep_data)
        occ_shape = ss.Shape(ss.NbShapes())
    except: pass
    
    return tuple(brep_object, occ_shape)

