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
import operator
from collections import namedtuple, Iterable

shape_tuple = namedtuple('shape_tuple', ('data', 'geometry', 'styles'))

handle, main_loop, add_menu, add_function_to_menu = None, None, None, None

DEFAULT_STYLES = {
    "DEFAULT"            : (.7 , .7, .7     ),
    "IfcWall"            : (.8 , .8, .8     ),
    "IfcSite"            : (.75, .8, .65    ),
    "IfcSlab"            : (.4 , .4, .4     ),
    "IfcWallStandardCase": (.9 , .9, .9     ),
    "IfcWall"            : (.9 , .9, .9     ),
    "IfcWindow"          : (.75, .8, .75, .3),
    "IfcDoor"            : (.55, .3, .15    ),
    "IfcBeam"            : (.75, .7, .7     ),
    "IfcRailing"         : (.65, .6, .6     ),
    "IfcMember"          : (.65, .6, .6     ),
    "IfcPlate"           : (.8 , .8, .8     )
}

def initialize_display():
    import OCC.V3d
    import OCC.Display.SimpleGui
    
    global handle, main_loop, add_menu, add_function_to_menu
    handle, main_loop, add_menu, add_function_to_menu = OCC.Display.SimpleGui.init_display()

    def setup():
        viewer_handle = handle.GetViewer()
        viewer = viewer_handle.GetObject()
        
        def lights():
            viewer.InitActiveLights()
            while True:
                try: active_light = viewer.ActiveLight()
                except: break
                yield active_light
                viewer.NextActiveLights()
        
        lights = list(lights())
        for l in lights:
            viewer.DelLight(l)
            
        for dir in [(3,2,1), (-1,-2,-3)]:
            light = OCC.V3d.V3d_DirectionalLight(viewer_handle)
            light.SetDirection(*dir)
            viewer.SetLightOn(light.GetHandle())

    setup()
    return handle

def yield_subshapes(shape):
    import OCC.TopoDS
    
    it = OCC.TopoDS.TopoDS_Iterator(shape)
    while it.More():
        yield it.Value()
        it.Next()
    
def display_shape(shape, clr=None, viewer_handle=None):
    import OCC.gp
    import OCC.AIS
    import OCC.Quantity
    
    if viewer_handle is None: viewer_handle = handle

    if isinstance(shape, shape_tuple): 
        shape, representation = shape.geometry, shape
    else: representation = None
        
    material = OCC.Graphic3d.Graphic3d_MaterialAspect(OCC.Graphic3d.Graphic3d_NOM_PLASTER)
    material.SetDiffuse(1)
    
    if representation and not clr:
        if len(set(representation.styles)) == 1:
            clr = representation.styles[0]
            if min(clr) < 0. or max(clr) > 1.:
                clr = DEFAULT_STYLES.get(representation.data.type, DEFAULT_STYLES["DEFAULT"])
    
    if clr:
        ais = OCC.AIS.AIS_Shape(shape)
        ais.SetMaterial(material)
    
        if isinstance(clr, str):
            qclr = getattr(OCC.Quantity, "Quantity_NOC_%s" % clr.upper(), getattr(OCC.Quantity, "Quantity_NOC_%s1" % clr.upper(), None))
            if qclr is None:
                raise Exception("No color named '%s'" % clr.upper())
        elif isinstance(clr, Iterable):
            clr = tuple(clr)
            if len(clr) < 3 and len(clr) > 4:
                raise Exception("Need 3 or 4 colour components. Got '%r'." % clr)
            qclr = OCC.Quantity.Quantity_Color(clr[0], clr[1], clr[2], OCC.Quantity.Quantity_TOC_RGB)
        elif isinstance(clr, OCC.Quantity.Quantity_Color):
            qclr = clr
        else:
            raise Exception("Object of type %r cannot be used as a color." % type(clr))
        
        ais.SetColor(qclr)
        if isinstance(clr, tuple) and len(clr) == 4 and clr[3] < 1.:
            ais.SetTransparency(1. - clr[3])

    elif representation:
        default_style_applied = None
    
        ais = OCC.AIS.AIS_MultipleConnectedShape(shape)
    
        subshapes = list(yield_subshapes(shape))
        lens = len(representation.styles), len(subshapes)
        if lens[0] != lens[1]:
            import warnings
            warnings.warn("Unable to assign styles to subshapes. Encountered %d styles for %d shapes." % lens)
        else:
            for shp, stl in zip(subshapes, representation.styles):
                subshape = OCC.AIS.AIS_Shape(shp)
                if min(stl) < 0. or max(stl) > 1.:
                    default_style_applied = stl = DEFAULT_STYLES.get(representation.data.type, DEFAULT_STYLES["DEFAULT"])
                subshape.SetColor(OCC.Quantity.Quantity_Color(stl[0], stl[1], stl[2], OCC.Quantity.Quantity_TOC_RGB))
                subshape.SetMaterial(material)
                if len(stl) == 4 and stl[3] < 1.:
                    subshape.SetTransparency(1. - stl[3])
                ais.Connect(subshape.GetHandle())
                
        # For some reason it is necessary to set transparency here again
        # in order for transparency to be rendered on the subshape.
        applied_styles = representation.styles
        if default_style_applied:
            if len(default_style_applied) == 3: default_style_applied += (1.,)
            applied_styles += (default_style_applied,)
        
        if len(applied_styles):
            # The only way for this not to be true if is the entire shape is NULL
            min_transp = min(map(operator.itemgetter(3), applied_styles))
            if min_transp < 1.:
                ais.SetTransparency(1.)

    else:
        ais = OCC.AIS.AIS_Shape(shape)
        ais.SetMaterial(material)
        
        r = lambda: random.random() * 0.3 + 0.7
        clr = OCC.Quantity.Quantity_Color(r(), r(), r(), OCC.Quantity.Quantity_TOC_RGB)
        ais.SetColor(clr)
        
    ais_handle = ais.GetHandle()
    viewer_handle.Context.Display(ais_handle, False)
        
    return ais_handle


def set_shape_transparency(ais, t):
    handle.Context.SetTransparency(ais, t)


def get_bounding_box_center(bbox):
    import OCC.gp
    
    bbmin = [0.]*3; bbmax = [0.]*3
    bbmin[0], bbmin[1], bbmin[2], bbmax[0], bbmax[1], bbmax[2] = bbox.Get()
    return OCC.gp.gp_Pnt(*map(lambda xy: (xy[0]+xy[1])/2., zip(bbmin, bbmax)))

    
def serialize_shape(shape):
    import OCC.BRepTools
    
    shapes = OCC.BRepTools.BRepTools_ShapeSet()
    shapes.Add(shape)
    return shapes.WriteToString()
    
def create_shape_from_serialization(brep_object):
    import OCC.BRepTools
    
    brep_data, occ_shape, styles = None, None, ()
    
    is_product_shape = True
    try:
        brep_data = brep_object.geometry.brep_data
        styles = brep_object.geometry.surface_styles
    except: 
        try: 
            brep_data = brep_object.brep_data
            styles = brep_object.surface_styles
            is_product_shape = False
        except: pass
        
    styles = tuple(styles[i:i+4] for i in range(0, len(styles), 4))
        
    if not brep_data: return shape_tuple(brep_object, None, styles)
    
    try:
        ss = OCC.BRepTools.BRepTools_ShapeSet()
        ss.ReadFromString(brep_data)
        occ_shape = ss.Shape(ss.NbShapes())
    except: pass
    
    if is_product_shape:
        return shape_tuple(brep_object, occ_shape, styles)
    else:
        return occ_shape

