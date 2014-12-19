#include "IfcRegisterUndef.h"
#define CLASS(T,V) bool convert(const IfcSchema::T* L, V& r);
#define SHAPES(T) CLASS(T,IfcRepresentationShapeItems)
#define SHAPE(T) CLASS(T,TopoDS_Shape)
#define WIRE(T) CLASS(T,TopoDS_Wire)
#define FACE(T) CLASS(T,TopoDS_Shape)
#define CURVE(T) CLASS(T,Handle(Geom_Curve))
#include "IfcRegisterDef.h"

#include "IfcRegister.h"