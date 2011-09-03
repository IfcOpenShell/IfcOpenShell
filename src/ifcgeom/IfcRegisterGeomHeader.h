#include "IfcRegisterUndef.h"
#define CLASS(T,V) bool convert(const T::ptr L, V& r);
#define SHAPE(T) CLASS(T,TopoDS_Shape)
#define WIRE(T) CLASS(T,TopoDS_Wire)
#define FACE(T) CLASS(T,TopoDS_Face)
#define CURVE(T) CLASS(T,Handle(Geom_Curve))
#include "IfcRegisterDef.h"

#include "IfcRegister.h"