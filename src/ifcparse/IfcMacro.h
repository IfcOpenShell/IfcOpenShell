/********************************************************************************
 *                                                                              *
 * This file is part of IfcOpenShell.                                           *
 *                                                                              *
 * IfcOpenShell is free software: you can redistribute it and/or modify         *
 * it under the terms of the Lesser GNU General Public License as published by  *
 * the Free Software Foundation, either version 3.0 of the License, or          *
 * (at your option) any later version.                                          *
 *                                                                              *
 * IfcOpenShell is distributed in the hope that it will be useful,              *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
 * Lesser GNU General Public License for more details.                          *
 *                                                                              *
 * You should have received a copy of the Lesser GNU General Public License     *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.         *
 *                                                                              *
 ********************************************************************************/

/********************************************************************************
 *                                                                              *
 * Macro definitions that expand the schema definition in IfcSchema.h into      *
 * C++ code.                                                                    *
 *                                                                              *
 ********************************************************************************/

#undef IFC_CLASS
#undef IFC_SHAPE_CLASS
#undef IFC_FACE_CLASS
#undef IFC_SKIP_CLASS
#undef IFC_WIRE_CLASS
#undef IFC_CURVE_CLASS
#undef IFC_HELPER_CLASS
#undef IFC_RENDER_CLASS
#undef IFC_END_CLASS
#undef IFC_REF
#undef IFC_REFS
#undef IFC_FLT
#undef IFC_FLT_SUB
#undef IFC_INT
#undef IFC_STR
#undef IFC_BOOL

#ifdef IFC_PARSE_HEADER
#define IFC_CLASS(N,T) class N : public IfcParse::Entity { public:
#define IFC_SHAPE_CLASS(N) IFC_CLASS(N,"")
#define IFC_FACE_CLASS(N) IFC_CLASS(N,"")
#define IFC_WIRE_CLASS(N) IFC_CLASS(N,"")
#define IFC_CURVE_CLASS(N) IFC_CLASS(N,"")
#define IFC_HELPER_CLASS(N) IFC_CLASS(N,"")
#define IFC_RENDER_CLASS(N) IFC_CLASS(N,"")
#define IFC_END_CLASS };
#define IFC_REF(C,N,I) IfcEntity N();
#define IFC_REFS(C,N,I) IfcEntities N();
#define IFC_FLT(C,N,I) float N();
#define IFC_FLT_SUB(C,N,I,J) float N();
#define IFC_INT(C,N,I) int N();
#define IFC_STR(C,N,I) std::string N();
#define IFC_BOOL(C,N,I) bool N();
#endif

#ifdef IFC_PARSE_SOURCE
#define IFC_REF(C,N,I) IfcEntity C::N() { return *(*this)[I]; }
#define IFC_REFS(C,N,I) IfcEntities C::N() { return *(*this)[I]; }
#define IFC_FLT(C,N,I) float C::N() { return *(*this)[I]; }
#define IFC_FLT_SUB(C,N,I,J) float C::N() { return *(*(*this)[I])[J]; }
#define IFC_INT(C,N,I) int C::N() { return *(*this)[I]; }
#define IFC_STR(C,N,I) std::string C::N() { return *(*this)[I]; }
#define IFC_BOOL(C,N,I) bool C::N() { return *(*this)[I]; }
#endif

#ifdef IFC_PARSE_ENUM
#define IFC_SHAPE_CLASS(N) Ifc##N,
#define IFC_WIRE_CLASS(N) Ifc##N,
#define IFC_CURVE_CLASS(N) Ifc##N,
#define IFC_FACE_CLASS(N) Ifc##N,
#define IFC_CLASS(N,T) Ifc##N,
#define IFC_HELPER_CLASS(N) Ifc##N,
#define IFC_RENDER_CLASS(N) Ifc##N,
#endif

#ifdef IFC_PARSE_STR_ENUM
#define IFC_SHAPE_CLASS(N) if ( strcasecmp(a.c_str()+3,#N) == 0 ) { return IfcSchema::Enum::Ifc##N; }
#define IFC_FACE_CLASS(N) IFC_SHAPE_CLASS(N)
#define IFC_WIRE_CLASS(N) IFC_SHAPE_CLASS(N)
#define IFC_CURVE_CLASS(N) IFC_SHAPE_CLASS(N)
#define IFC_HELPER_CLASS(N) IFC_SHAPE_CLASS(N)
#define IFC_CLASS(N,T) IFC_SHAPE_CLASS(N)
#define IFC_RENDER_CLASS(N) IFC_SHAPE_CLASS(N)
#define IFC_SKIP_CLASS(N) if ( strcasecmp(a.c_str()+3,#N) == 0 ) { return IfcSchema::Enum::IfcDontCare; }
#endif

#ifdef IFC_PARSE_ENUM_STR
#define IFC_SHAPE_CLASS(N) if ( t == IfcSchema::Enum::Ifc##N ) return "Ifc" #N;
#define IFC_FACE_CLASS(N) IFC_SHAPE_CLASS(N)
#define IFC_WIRE_CLASS(N) IFC_SHAPE_CLASS(N)
#define IFC_CURVE_CLASS(N) IFC_SHAPE_CLASS(N)
#define IFC_HELPER_CLASS(N) IFC_SHAPE_CLASS(N)
#define IFC_RENDER_CLASS(N) IFC_SHAPE_CLASS(N)
#define IFC_CLASS(N,T) IFC_SHAPE_CLASS(N)
#endif

#ifdef IFC_PARSE_RENDER
#define IFC_RENDER_CLASS(N) if ( t == IfcSchema::Enum::Ifc##N ) return true;
#endif

#ifdef IFC_GEOM_HEADER
#define IFC_SHAPE_CLASS(N) bool convert(IfcSchema::N* Ifc##N,TopoDS_Shape& result);
#define IFC_FACE_CLASS(N) bool convert(IfcSchema::N* Ifc##N,TopoDS_Face& result);
#define IFC_WIRE_CLASS(N) bool convert(IfcSchema::N* Ifc##N,TopoDS_Wire& result);
#define IFC_CURVE_CLASS(N) bool convert(IfcSchema::N* Ifc##N,Handle(Geom_Curve)& result);
#define IFC_CLASS(N,T) bool convert(IfcSchema::N* Ifc##N,T& result);
#endif

#ifdef IFC_SHAPE_SRC
#define IFC_SHAPE_CLASS(N) else if ( L->type == IfcSchema::Enum::Ifc##N ) { IfcSchema::N* x = (IfcSchema::N*) L.get(); try { r = IfcGeom::convert(x,result); } catch(IfcParse::IfcException& e) { std::cout << "[Error] " << e.what() << std::endl;} catch(StdFail_NotDone&) { std::cout << "[Error] Unknown modelling error" << std::endl; }  }
#endif

#ifdef IFC_WIRE_SRC
#define IFC_WIRE_CLASS(N) else if ( L->type == IfcSchema::Enum::Ifc##N ) { IfcSchema::N* x = (IfcSchema::N*) L.get(); r = IfcGeom::convert(x,result); }
#endif

#ifdef IFC_FACE_SRC
#define IFC_FACE_CLASS(N) else if ( L->type == IfcSchema::Enum::Ifc##N ) { IfcSchema::N* x = (IfcSchema::N*) L.get(); r = IfcGeom::convert(x,result); }
#define IFC_WIRE_CLASS(N) else if ( L->type == IfcSchema::Enum::Ifc##N ) { IfcSchema::N* x = (IfcSchema::N*) L.get(); TopoDS_Wire wire; if ( ! IfcGeom::convert(x,wire) ) r = false; r = IfcGeom::convert_wire_to_face(wire,result); }
#endif

#ifdef IFC_CURVE_SRC
#define IFC_CURVE_CLASS(N) if ( L->type == IfcSchema::Enum::Ifc##N ) { IfcSchema::N* x = (IfcSchema::N*) L.get(); return IfcGeom::convert(x,result); }
#endif

#ifdef IFC_GEOM_CACHE
#define IFC_CLASS(N,T) std::map<int,T*> N;
#endif

#ifdef IFC_GEOM_CACHE_PURGE
#define IFC_CLASS(N,T) for(std::map<int,T*>::const_iterator it = N.begin(); it != N.end(); it ++ ) delete it->second; N.clear();
#endif

#ifndef IFC_CLASS
#define IFC_CLASS(N,T)
#endif
#ifndef IFC_SHAPE_CLASS
#define IFC_SHAPE_CLASS(N)
#endif
#ifndef IFC_FACE_CLASS
#define IFC_FACE_CLASS(N)
#endif
#ifndef IFC_SKIP_CLASS
#define IFC_SKIP_CLASS(N)
#endif
#ifndef IFC_WIRE_CLASS
#define IFC_WIRE_CLASS(N)
#endif
#ifndef IFC_CURVE_CLASS
#define IFC_CURVE_CLASS(N)
#endif
#ifndef IFC_HELPER_CLASS
#define IFC_HELPER_CLASS(N)
#endif
#ifndef IFC_RENDER_CLASS
#define IFC_RENDER_CLASS(N)
#endif
#ifndef IFC_END_CLASS
#define IFC_END_CLASS
#endif
#ifndef IFC_REF
#define IFC_REF(C,N,I)
#endif
#ifndef IFC_REFS
#define IFC_REFS(C,N,I)
#endif
#ifndef IFC_FLT
#define IFC_FLT(C,N,I)
#endif
#ifndef IFC_FLT_SUB
#define IFC_FLT_SUB(C,N,I,J)
#endif
#ifndef IFC_INT
#define IFC_INT(C,N,I)
#endif
#ifndef IFC_STR
#define IFC_STR(C,N,I)
#endif
#ifndef IFC_BOOL
#define IFC_BOOL(C,N,I)
#endif