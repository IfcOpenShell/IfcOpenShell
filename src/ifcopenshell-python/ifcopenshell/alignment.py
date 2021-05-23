from dataclasses import dataclass

import numpy

import ifcopenshell                             
import ifcopenshell.geom                            
import ifcopenshell.express
import ifcopenshell.transition_curve

# geometric primitives

# @notes
# - not sure if the separation of geometric primitives make sense
#   does it make handling the variety of distance expressions and
#   interpolation harder?

@dataclass
class line:
    start_point: numpy.ndarray
    direction_vector: numpy.ndarray
    
    def __call__(self, u):     
        return self.start_point + \
            self.direction_vector * u


@dataclass
class circle:
    radius: numpy.ndarray
    
    def __call__(self, u):        
        return numpy.array([
            self.radius * numpy.cos(u),
            self.radius * numpy.sin(u)
        ])

        
def place(matrix, func):
    """
    Higher order function for application of a 3x3 matrix
    to a 2D point. Assumes a functor such as line or circle.
    """
    def inner(*args):
        v = func(*args)
        # homogenize
        v = numpy.insert(v, v.shape[-1], 1, axis=-1)
        return (matrix @ v)[0:2]
    return inner


# mapping functions from IFC entities

def map_inst(inst):
    """
    Looks up one of the implementation functions below in the global namespace
    """
    return globals()[f"impl_{inst.is_a()}"](inst)


def impl_IfcLine(inst):
    return line(
        numpy.array(inst.Pnt.Coordinates),
        numpy.array(inst.Dir.Orientation.DirectionRatios) * inst.Dir.Magnitude
    )


def impl_IfcCircle(inst):
    return place(map_inst(inst.Position), circle(
        inst.Radius
    ))


def impl_IfcClothoid(inst):
    # @todo
    # place = map_inst(inst.Position)
    # ifcopenshell.transition_curve.TransitionCurve(
    #     StartPoint          = place.T[2]
    #     StartDirection      = numpy.arctan2(place.T[0][1], place.T[0][0]),
    #     SegmentLength       = 
    #     IsStartRadiusCCW    = 
    #     IsEndRadiusCCW      = 
    #     TransitionCurveType = 
    #     StartRadius         = 
    #     EndRadius           = 
    # )
    return lambda *args: numpy.array((0.,0.))


def impl_IfcAxis2Placement2D(inst):
    arr = numpy.eye(3)
    
    if inst is None:
        return arr
        
    arr.T[2, 0:2] = inst.Location.Coordinates
    
    if inst.RefDirection is None:
        return arr
        
    arr.T[0, 0:2] = inst.RefDirection.DirectionRatios
    arr.T[0, 0:2] /= numpy.linalg.norm(arr.T[0, 0:2])
    arr.T[1, 0:2] = -arr.T[0,1], arr.T[0,0]
    
    return arr
        

# conversion functions for semantic design parameters (not used atm)

def convert(inst):
    """
    Looks up one of the conversion functions below in the global namespace
    """
    yield from globals()[f"convert_{inst.is_a()}_{inst.PredefinedType}"](inst)
    

def convert_IfcAlignmentHorizontalSegment_LINE(data):
    xy = numpy.array(data.StartPoint.Coordinates)
    yield xy
    di = numpy.array([
        numpy.cos(data.StartDirection),
        numpy.sin(data.StartDirection)
    ])
    yield xy + di * data.SegmentLength
    
# Two approaches, either DesignParameters or Representation  

def interpret_linear_element_semantics(settings, crv):
    # traverse decomposition
    for rel in crv.IsNestedBy:
        for obj in rel.RelatedObjects:
            yield from interpret_linear_element_semantics(settings, obj)
            
    # lookup design parameters and dispatch to conversion function
    if crv.is_a("IfcAlignmentSegment"):
        dp = crv.DesignParameters
        yield from convert(dp)

    
def interpret_linear_element_geometry(settings, crv):
    for segment in crv.Representation.Representations[0].Items[0].Segments:
    
        print(segment)
        print(segment.ParentCurve)
        print()        
    
        func = place(
            map_inst(segment.Placement), 
            map_inst(segment.ParentCurve)
        )

        for u in numpy.linspace(
            segment.SegmentStart[0],
            segment.SegmentStart[0] + segment.SegmentLength[0],
            num=32
        ):
            yield func(u)
            
    
interpret_linear_element = interpret_linear_element_geometry
            
def create_shape(settings, elem):
    if elem.is_a("IfcLinearPositioningElement") or elem.is_a("IfcLinearElement"):
        return numpy.row_stack(list(interpret_linear_element(settings, elem)))
    else:
        return ifcopenshell.geom.create_shape(settings, elem)
        
    
def print_structure(alignment, indent=0):
    """
    Debugging function to print alignment decomposition
    """
    print(" " * indent, str(alignment)[0:100])          
    for rel in alignment.IsNestedBy:                    
        for child in rel.RelatedObjects:        
            print_structure(child, indent+2)


if __name__ == "__main__":
    import sys
    from matplotlib import pyplot as plt
    
    s = ifcopenshell.express.parse("IFC4x3_RC3.exp")
    ifcopenshell.register_schema(s)
    f = ifcopenshell.open(sys.argv[1])
    print_structure(f.by_type("IfcAlignment")[0])

    al_hor = f.by_type("IfcAlignmentHorizontal")[0]
    xy = create_shape({}, al_hor)
    
    plt.plot(xy.T[0], xy.T[1])
    plt.savefig("horizontal_alignment.png")
