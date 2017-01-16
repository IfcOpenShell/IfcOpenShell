#include "CgalEntityMappingUndefine.h"
#define CLASS(T,V) bool convert(const IfcSchema::T* L, V& r);
#define SHAPES(T) CLASS(T,ConversionResults)
#define SHAPE(T) CLASS(T,cgal_shape_t)
#define WIRE(T) CLASS(T,cgal_wire_t)
#define FACE(T) CLASS(T,cgal_face_t)
#define CURVE(T) CLASS(T,cgal_curve_t)
#include "CgalEntityMappingDefine.h"

#include "CgalEntityMapping.h"