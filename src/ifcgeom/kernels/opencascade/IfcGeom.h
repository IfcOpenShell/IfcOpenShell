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

#ifndef IFCGEOM_H
#define IFCGEOM_H

#include <cmath>

static const double ALMOST_ZERO = 1.e-9;

template <typename T>
inline static bool ALMOST_THE_SAME(const T& a, const T& b, double tolerance=ALMOST_ZERO) {
	return fabs(a-b) < tolerance; 
}

#include <gp_Pnt.hxx>
#include <gp_Vec.hxx>
#include <gp_Mat.hxx>
#include <gp_Mat2d.hxx>
#include <gp_GTrsf.hxx>
#include <gp_GTrsf2d.hxx>
#include <gp_Trsf.hxx>
#include <gp_Trsf2d.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Wire.hxx>
#include <TopoDS_Face.hxx>
#include <Geom_Curve.hxx>
#include <gp_Pln.hxx>
#include <TColgp_SequenceOfPnt.hxx>
#include <TopTools_ListOfShape.hxx>
#include <BOPAlgo_Operation.hxx>
#include <BRep_Builder.hxx>
#include <BRepBuilderAPI_MakeEdge.hxx>

#include "../../../ifcparse/macros.h"
#include "../../../ifcparse/IfcParse.h"
#include "../../../ifcparse/IfcBaseClass.h"

#include "../../../ifcgeom/kernel_agnostic/AbstractKernel.h" 

#include "../../../ifcgeom/schema_agnostic/IfcGeomElement.h" 
#include "../../../ifcgeom/schema_agnostic/IfcGeomRepresentation.h" 
#include "../../../ifcgeom/schema_agnostic/ConversionResult.h"
#include "../../../ifcgeom/kernels/opencascade/IfcGeomShapeType.h"

#include "../../../ifcgeom/schema_agnostic/Kernel.h"
#include "../../../ifcgeom/schema_agnostic/opencascade/OpenCascadeConversionResult.h"

#include "../../../ifcgeom/schema_agnostic/ifc_geom_api.h"

// Define this in case you want to conserve memory usage at all cost. This has been
// benchmarked extensively: https://github.com/IfcOpenShell/IfcOpenShell/pull/47
// #define NO_CACHE

#ifdef NO_CACHE

#define IN_CACHE(T,E,t,e)
#define CACHE(T,E,e)

#else

#define IN_CACHE(T,E,t,e) std::map<int,t>::const_iterator it = cache.T.find(E->data().id());\
if ( it != cache.T.end() ) { e = it->second; return true; }
#define CACHE(T,E,e) cache.T[E->data().id()] = e;

#endif

#define INCLUDE_SCHEMA(x) STRINGIFY(../../../ifcparse/x.h)
#include INCLUDE_SCHEMA(IfcSchema)
#undef INCLUDE_SCHEMA
#define INCLUDE_SCHEMA(x) STRINGIFY(../../../ifcparse/x-definitions.h)
#include INCLUDE_SCHEMA(IfcSchema)
#undef INCLUDE_SCHEMA

namespace IfcGeom {
	class IFC_GEOM_API geometry_exception : public std::exception {
	protected:
		std::string message;
	public:
		geometry_exception(const std::string& m)
			: message(m) {}
		virtual ~geometry_exception() throw () {}
		virtual const char* what() const throw() {
			return message.c_str();
		}
	};

	class IFC_GEOM_API too_many_faces_exception : public geometry_exception {
	public:
		too_many_faces_exception()
			: geometry_exception("Too many faces for operation") {}
	};

class IFC_GEOM_API MAKE_TYPE_NAME(Cache) {
public:
#include "IfcRegisterCreateCache.h"
	std::map<int, TopoDS_Shape> Shape;
};

class IFC_GEOM_API MAKE_TYPE_NAME(Kernel) : public IfcGeom::MAKE_TYPE_NAME(AbstractKernel) {
private:

	/*
	faceset_helper traverses the forward instance references of IfcConnectedFaceSet and then provides a mapping
	M of (IfcCartesianPoint, IfcCartesianPoint) -> TopoDS_Edge, where M(a, b) is a partner of M(b, a), ie share
	the same underlying edge but with orientation reversed. This then later speeds op the process of creating a
	manifold Shell / Solid from this set of faces. Only IfcPolyLoop instances are used. Points within the tolerance
	threshiold are merged, so consider points a, b, c, distance(a, b) < eps then M(a, b) = Null, M(a, b) = M(a, c).
	*/
	class faceset_helper {
	private:
		MAKE_TYPE_NAME(Kernel)* kernel_;
		std::set<const IfcSchema::IfcPolyLoop*> duplicates_;
		std::map<int, int> vertex_mapping_;
		std::map<std::pair<int, int>, TopoDS_Edge> edges_;
		double eps_;
		bool non_manifold_;

		template <typename Fn>
		void loop_(IfcSchema::IfcCartesianPoint::list::ptr& ps, const Fn& callback) {
			if (ps->size() < 3) {
				return;
			}

			auto a = *(ps->end() - 1);
			auto A = a->data().id();
			for (auto& b : *ps) {
				auto B = b->data().id();
				auto C = vertex_mapping_[A], D = vertex_mapping_[B];
				bool fwd = C < D;
				if (!fwd) {
					std::swap(C, D);
				}
				if (C != D) {
					callback(C, D, fwd);
					A = B;
				}
			}
		}
	public:
		faceset_helper(MAKE_TYPE_NAME(Kernel)* kernel, const IfcSchema::IfcConnectedFaceSet* l);

		~faceset_helper();

		bool non_manifold() const { return non_manifold_; }
		bool& non_manifold() { return non_manifold_; }

		bool edge(const IfcSchema::IfcCartesianPoint* a, const IfcSchema::IfcCartesianPoint* b, TopoDS_Edge& e) {
			int A = vertex_mapping_[a->data().id()];
			int B = vertex_mapping_[b->data().id()];
			if (A == B) {
				return false;
			}

			return edge(A, B, e);
		}

		bool edge(int A, int B, TopoDS_Edge& e) {
			auto it = edges_.find({A, B});
			if (it == edges_.end()) {
				return false;
			}
			e = it->second;
			return true;
		}

		bool wire(const IfcSchema::IfcPolyLoop* loop, TopoDS_Wire& wire) {
			if (duplicates_.find(loop) != duplicates_.end()) {
				return false;
			}
			BRep_Builder builder;
			builder.MakeWire(wire);
			int count = 0;
			auto ps = loop->Polygon();
			loop_(ps, [this, &builder, &wire, &count](int A, int B, bool fwd) {
				TopoDS_Edge e;
				if (edge(A, B, e)) {
					if (!fwd) {
						e.Reverse();
					}
					builder.Add(wire, e);
					count += 1;
				}
			});
			if (count >= 3) {
				wire.Closed(true);

				TopTools_ListOfShape results;
				if (kernel_->wire_intersections(wire, results)) {
					Logger::Warning("Self-intersections with " + boost::lexical_cast<std::string>(results.Extent()) + " cycles detected", loop);
					kernel_->select_largest(results, wire);
					non_manifold_ = true;
				}

				return true;
			} else {
				return false;
			}
		}

		double epsilon() const {
			return eps_;
		}
	};	

#ifndef NO_CACHE
	MAKE_TYPE_NAME(Cache) cache;
#endif

	faceset_helper* faceset_helper_;

public:
	MAKE_TYPE_NAME(Kernel)()
		: IfcGeom::MAKE_TYPE_NAME(AbstractKernel)("opencascade")
		, faceset_helper_(nullptr)
	{}

	MAKE_TYPE_NAME(Kernel)(const MAKE_TYPE_NAME(Kernel)& other) 
		: IfcGeom::MAKE_TYPE_NAME(AbstractKernel)("opencascade") 
	{
		*this = other;
	}

	MAKE_TYPE_NAME(Kernel)& operator=(const MAKE_TYPE_NAME(Kernel)& other) {
		setValue(GV_DEFLECTION_TOLERANCE,     other.getValue(GV_DEFLECTION_TOLERANCE));
		setValue(GV_MAX_FACES_TO_ORIENT,      other.getValue(GV_MAX_FACES_TO_ORIENT));
		setValue(GV_LENGTH_UNIT,              other.getValue(GV_LENGTH_UNIT));
		setValue(GV_PLANEANGLE_UNIT,          other.getValue(GV_PLANEANGLE_UNIT));
		setValue(GV_PRECISION,                other.getValue(GV_PRECISION));
		setValue(GV_DIMENSIONALITY,           other.getValue(GV_DIMENSIONALITY));
		setValue(GV_DEFLECTION_TOLERANCE,     other.getValue(GV_DEFLECTION_TOLERANCE));
		return *this;
	}

	bool convert_wire_to_face(const TopoDS_Wire& wire, TopoDS_Face& face);
	bool convert_curve_to_wire(const Handle(Geom_Curve)& curve, TopoDS_Wire& wire);
	bool convert_shapes(const IfcUtil::IfcBaseClass* L, ConversionResults& result);
	IfcGeom::ShapeType shape_type(const IfcUtil::IfcBaseClass* L);
	bool convert_shape(const IfcUtil::IfcBaseClass* L, TopoDS_Shape& result);
	bool flatten_shape_list(const IfcGeom::ConversionResults& shapes, TopoDS_Shape& result, bool fuse);
	bool convert_wire(const IfcUtil::IfcBaseClass* L, TopoDS_Wire& result);
	bool convert_curve(const IfcUtil::IfcBaseClass* L, Handle(Geom_Curve)& result);
	bool convert_face(const IfcUtil::IfcBaseClass* L, TopoDS_Shape& result);
	bool convert_openings(const IfcSchema::IfcProduct* entity, const IfcSchema::IfcRelVoidsElement::list::ptr& openings, const ConversionResults& entity_shapes, const ConversionResultPlacement* entity_trsf, ConversionResults& cut_shapes);
	void assert_closed_wire(TopoDS_Wire& wire);

	bool convert_layerset(const IfcSchema::IfcProduct*, std::vector<Handle_Geom_Surface>&, std::vector<const SurfaceStyle*>&, std::vector<double>&);
	bool apply_layerset(const ConversionResults&, const std::vector<Handle_Geom_Surface>&, const std::vector<const SurfaceStyle*>&, ConversionResults&);
	bool apply_folded_layerset(const ConversionResults&, const std::vector< std::vector<Handle_Geom_Surface> >&, const std::vector<const SurfaceStyle*>&, ConversionResults&);
	bool fold_layers(const IfcSchema::IfcWall*, const ConversionResults&, const std::vector<Handle_Geom_Surface>&, const std::vector<double>&, std::vector< std::vector<Handle_Geom_Surface> >&);

	bool split_solid_by_surface(const TopoDS_Shape&, const Handle_Geom_Surface&, TopoDS_Shape&, TopoDS_Shape&);
	bool split_solid_by_shell(const TopoDS_Shape&, const TopoDS_Shape& s, TopoDS_Shape&, TopoDS_Shape&);

#if OCC_VERSION_HEX < 0x60900
	bool boolean_operation(const TopoDS_Shape&, const TopTools_ListOfShape&, BOPAlgo_Operation, TopoDS_Shape&);
	bool boolean_operation(const TopoDS_Shape&, const TopoDS_Shape&, BOPAlgo_Operation, TopoDS_Shape&);
#else
	bool boolean_operation(const TopoDS_Shape&, const TopTools_ListOfShape&, BOPAlgo_Operation, TopoDS_Shape&, double fuzziness = -1.);
	bool boolean_operation(const TopoDS_Shape&, const TopoDS_Shape&, BOPAlgo_Operation, TopoDS_Shape&, double fuzziness = -1.);
#endif

	bool fit_halfspace(const TopoDS_Shape& a, const TopoDS_Shape& b, TopoDS_Shape& box, double& height);

	const Handle_Geom_Curve intersect(const Handle_Geom_Surface&, const Handle_Geom_Surface&);
	const Handle_Geom_Curve intersect(const Handle_Geom_Surface&, const TopoDS_Face&);
	const Handle_Geom_Curve intersect(const TopoDS_Face&, const Handle_Geom_Surface&);
	bool intersect(const Handle_Geom_Curve&, const Handle_Geom_Surface&, gp_Pnt&);
	bool intersect(const Handle_Geom_Curve&, const TopoDS_Face&, gp_Pnt&);
	bool intersect(const Handle_Geom_Curve&, const TopoDS_Shape&, std::vector<gp_Pnt>&);
	bool intersect(const Handle_Geom_Surface&, const TopoDS_Shape&, std::vector< std::pair<Handle_Geom_Surface, Handle_Geom_Curve> >&);
	bool closest(const gp_Pnt&, const std::vector<gp_Pnt>&, gp_Pnt&);
	bool project(const Handle_Geom_Curve&, const gp_Pnt&, gp_Pnt& p, double& u, double& d);
	bool project(const Handle_Geom_Surface&, const TopoDS_Shape&, double& u1, double& v1, double& u2, double& v2, double widen=0.1);
	
	bool find_wall_end_points(const IfcSchema::IfcWall*, gp_Pnt& start, gp_Pnt& end);

	bool create_solid_from_compound(const TopoDS_Shape& compound, TopoDS_Shape& solid);
	bool create_solid_from_faces(const TopTools_ListOfShape& face_list, TopoDS_Shape& solid);
	bool is_compound(const TopoDS_Shape& shape);
	bool is_convex(const TopoDS_Wire& wire);
	TopoDS_Shape halfspace_from_plane(const gp_Pln& pln,const gp_Pnt& cent);
	gp_Pln plane_from_face(const TopoDS_Face& face);
	gp_Pnt point_above_plane(const gp_Pln& pln, bool agree=true);
	const TopoDS_Shape& ensure_fit_for_subtraction(const TopoDS_Shape& shape, TopoDS_Shape& solid);
	bool profile_helper(int numVerts, double* verts, int numFillets, int* filletIndices, double* filletRadii, gp_Trsf2d trsf, TopoDS_Shape& face); 
	void apply_tolerance(TopoDS_Shape& s, double t);
	bool fill_nonmanifold_wires_with_planar_faces(TopoDS_Shape& shape);
	void remove_duplicate_points_from_loop(TColgp_SequenceOfPnt& polygon, bool closed, double tol=-1.);
	void remove_collinear_points_from_loop(TColgp_SequenceOfPnt& polygon, bool closed, double tol=-1.);
	bool wire_to_sequence_of_point(const TopoDS_Wire&, TColgp_SequenceOfPnt&);
	void sequence_of_point_to_wire(const TColgp_SequenceOfPnt&, TopoDS_Wire&, bool closed);
	bool approximate_plane_through_wire(const TopoDS_Wire&, gp_Pln&, double eps=-1.);
	bool flatten_wire(TopoDS_Wire&);
	/// Triangulate the set of wires. The firstmost wire is assumed to be the outer wire.
	bool triangulate_wire(const std::vector<TopoDS_Wire>&, TopTools_ListOfShape&);
	bool wire_intersections(const TopoDS_Wire & wire, TopTools_ListOfShape & wires);
	void select_largest(const TopTools_ListOfShape& shapes, TopoDS_Shape& largest);

	static double shape_volume(const TopoDS_Shape& s);
	static double face_area(const TopoDS_Face& f);

	static TopoDS_Shape apply_transformation(const TopoDS_Shape&, const OpenCascadePlacement*);
	static TopoDS_Shape apply_transformation(const TopoDS_Shape&, const gp_Trsf&);
	static TopoDS_Shape apply_transformation(const TopoDS_Shape&, const gp_GTrsf&);
	
	virtual bool is_identity_transform(const IfcUtil::IfcBaseClass*);
	virtual bool apply_layerset(const IfcSchema::IfcProduct* product, IfcGeom::ConversionResults& shapes);
	virtual bool validate_quantities(const IfcSchema::IfcProduct* product, const IfcGeom::Representation::BRep& brep);

	IfcSchema::IfcRepresentation* find_representation(const IfcSchema::IfcProduct*, const std::string&);
	
	std::pair<std::string, double> initializeUnits(IfcSchema::IfcUnitAssignment*);

    void purge_cache() { 
		// Rather hack-ish, but a stopgap solution to keep memory under control
		// for large files. SurfaceStyles need to be kept at all costs, as they
		// are read later on when serializing Collada files.
#ifndef NO_CACHE
		cache = MAKE_TYPE_NAME(Cache)();
#endif
	}	

#include "IfcRegisterGeomHeader.h"

	virtual IfcGeom::NativeElement<double>* convert(
		const IteratorSettings& settings, IfcUtil::IfcBaseClass* representation,
		IfcUtil::IfcBaseClass* product)
	{
		return create_brep_for_representation_and_product<double, double>(settings, (IfcSchema::IfcRepresentation*) representation, (IfcSchema::IfcProduct*) product);
	}

	virtual ConversionResults convert(IfcUtil::IfcBaseClass* item) {
		ConversionResults items;
		bool success = convert_shapes(item, items);
		if (!success) {
			throw IfcParse::IfcException("Failed to process representation item");
		}
		return items;
	}

	virtual bool convert_placement(IfcUtil::IfcBaseClass* item, ConversionResultPlacement*& trsf) {
		if (item->as<IfcSchema::IfcObjectPlacement>()) {
			gp_Trsf occt_trsf;
			if (convert(item->as<IfcSchema::IfcObjectPlacement>(), occt_trsf)) {
				trsf = new OpenCascadePlacement(occt_trsf);
				return true;
			}
		}
		return false;
	}

};

IfcUtil::IfcBaseClass* MAKE_TYPE_NAME(tesselate_)(const TopoDS_Shape& shape, double deflection);
IfcUtil::IfcBaseClass* MAKE_TYPE_NAME(serialise_)(const TopoDS_Shape& shape, bool advanced);

}
#endif
