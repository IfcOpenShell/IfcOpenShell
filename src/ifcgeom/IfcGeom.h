﻿/********************************************************************************
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
#include <array>

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
#include <gp_Quaternion.hxx>
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

#include "../ifcparse/macros.h"
#include "../ifcparse/IfcParse.h"
#include "../ifcparse/IfcBaseClass.h"

#include "../ifcgeom/IfcGeomElement.h" 
#include "../ifcgeom/IfcGeomRepresentation.h" 
#include "../ifcgeom/IfcRepresentationShapeItem.h"
#include "../ifcgeom/IfcGeomShapeType.h"

#include "../ifcgeom_schema_agnostic/Kernel.h"

#include "ifc_geom_api.h"

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

#define INCLUDE_PARENT_DIR(x) STRINGIFY(../ifcparse/x.h)
#include INCLUDE_PARENT_DIR(IfcSchema)
#undef INCLUDE_PARENT_DIR
#define INCLUDE_PARENT_DIR(x) STRINGIFY(../ifcparse/x-definitions.h)
#include INCLUDE_PARENT_DIR(IfcSchema)

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

class IFC_GEOM_API MAKE_TYPE_NAME(Kernel) : public IfcGeom::Kernel {
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

	double deflection_tolerance;
	double max_faces_to_orient;
	double ifc_length_unit;
	double ifc_planeangle_unit;
	double modelling_precision;
	double dimensionality;
	double layerset_first;
	gp_Vec offset = gp_Vec{0.0, 0.0, 0.0};
	gp_Quaternion rotation = gp_Quaternion{};
	gp_Trsf offset_and_rotation = gp_Trsf();

#ifndef NO_CACHE
	MAKE_TYPE_NAME(Cache) cache;
#endif

	std::map<int, SurfaceStyle> style_cache;

	const SurfaceStyle* internalize_surface_style(const std::pair<IfcUtil::IfcBaseClass*, IfcUtil::IfcBaseClass*>& shading_style);

	 // For stopping PlacementRelTo recursion in convert(const IfcSchema::IfcObjectPlacement* l, gp_Trsf& trsf)
	const IfcParse::declaration* placement_rel_to;

	faceset_helper* faceset_helper_;

public:
	MAKE_TYPE_NAME(Kernel)()
		: IfcGeom::Kernel(0)
		, deflection_tolerance(0.001)
		, max_faces_to_orient(-1.0)
		, ifc_length_unit(1.0)
		, ifc_planeangle_unit(-1.0)
		, modelling_precision(0.00001)
		, dimensionality(1.)
		, placement_rel_to(nullptr)
		, faceset_helper_(nullptr)
	{}

	MAKE_TYPE_NAME(Kernel)(const MAKE_TYPE_NAME(Kernel)& other)
		: IfcGeom::Kernel(0)
		, deflection_tolerance(other.deflection_tolerance)
		, max_faces_to_orient(other.max_faces_to_orient)
		, ifc_length_unit(other.ifc_length_unit)
		, ifc_planeangle_unit(other.ifc_planeangle_unit)
		, modelling_precision(other.modelling_precision)
		, dimensionality(other.dimensionality)
		, placement_rel_to(other.placement_rel_to)
		// @nb faceset_helper_ always initialized to 0
		, faceset_helper_(nullptr)
		, offset(other.offset)
		, rotation(other.rotation)
		, offset_and_rotation(other.offset_and_rotation)
	{
	}

	MAKE_TYPE_NAME(Kernel)& operator=(const MAKE_TYPE_NAME(Kernel)& other) {
		deflection_tolerance = other.deflection_tolerance;
		max_faces_to_orient = other.max_faces_to_orient;
		ifc_length_unit = other.ifc_length_unit;
		ifc_planeangle_unit = other.ifc_planeangle_unit;
		modelling_precision = other.modelling_precision;
		dimensionality = other.dimensionality;
		placement_rel_to = other.placement_rel_to;
		offset = other.offset;
		rotation = other.rotation;
		offset_and_rotation = other.offset_and_rotation;
		return *this;
	}

	void set_offset(const std::array<double, 3>& offset);
	void set_rotation(const std::array<double, 4>& rotation);

	bool convert_wire_to_face(const TopoDS_Wire& wire, TopoDS_Face& face);
	bool convert_wire_to_faces(const TopoDS_Wire& wire, TopoDS_Compound& face);
	bool convert_curve_to_wire(const Handle(Geom_Curve)& curve, TopoDS_Wire& wire);
	bool convert_shapes(const IfcUtil::IfcBaseClass* L, IfcRepresentationShapeItems& result);
	IfcGeom::ShapeType shape_type(const IfcUtil::IfcBaseClass* L);
	bool convert_shape(const IfcUtil::IfcBaseClass* L, TopoDS_Shape& result);
	bool flatten_shape_list(const IfcGeom::IfcRepresentationShapeItems& shapes, TopoDS_Shape& result, bool fuse);
	bool convert_wire(const IfcUtil::IfcBaseClass* L, TopoDS_Wire& result);
	bool convert_curve(const IfcUtil::IfcBaseClass* L, Handle(Geom_Curve)& result);
	bool convert_face(const IfcUtil::IfcBaseClass* L, TopoDS_Shape& result);
	bool convert_openings(const IfcSchema::IfcProduct* entity, const IfcSchema::IfcRelVoidsElement::list::ptr& openings, const IfcRepresentationShapeItems& entity_shapes, const gp_Trsf& entity_trsf, IfcRepresentationShapeItems& cut_shapes);
	bool convert_openings_fast(const IfcSchema::IfcProduct* entity, const IfcSchema::IfcRelVoidsElement::list::ptr& openings, const IfcRepresentationShapeItems& entity_shapes, const gp_Trsf& entity_trsf, IfcRepresentationShapeItems& cut_shapes);
	void assert_closed_wire(TopoDS_Wire& wire);

	bool convert_layerset(const IfcSchema::IfcProduct*, std::vector<Handle_Geom_Surface>&, std::vector<const SurfaceStyle*>&, std::vector<double>&);
	bool apply_layerset(const IfcRepresentationShapeItems&, const std::vector<Handle_Geom_Surface>&, const std::vector<const SurfaceStyle*>&, IfcRepresentationShapeItems&);
	bool apply_folded_layerset(const IfcRepresentationShapeItems&, const std::vector< std::vector<Handle_Geom_Surface> >&, const std::vector<const SurfaceStyle*>&, IfcRepresentationShapeItems&);
	bool fold_layers(const IfcSchema::IfcWall*, const IfcRepresentationShapeItems&, const std::vector<Handle_Geom_Surface>&, const std::vector<double>&, std::vector< std::vector<Handle_Geom_Surface> >&);

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

	IfcSchema::IfcSurfaceStyleShading* get_surface_style(IfcSchema::IfcRepresentationItem* item);
	const IfcSchema::IfcRepresentationItem* find_item_carrying_style(const IfcSchema::IfcRepresentationItem* item);
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

	static TopoDS_Shape apply_transformation(const TopoDS_Shape&, const gp_Trsf&);
	static TopoDS_Shape apply_transformation(const TopoDS_Shape&, const gp_GTrsf&);
	
	bool is_identity_transform(IfcUtil::IfcBaseClass*);

	IfcSchema::IfcRelVoidsElement::list::ptr find_openings(IfcSchema::IfcProduct* product);

	IfcSchema::IfcRepresentation* find_representation(const IfcSchema::IfcProduct*, const std::string&);

	std::pair<std::string, double> initializeUnits(IfcSchema::IfcUnitAssignment*);

    template <typename P, typename PP>
    IfcGeom::BRepElement<P, PP>* create_brep_for_representation_and_product(
        const IteratorSettings&, IfcSchema::IfcRepresentation*, IfcSchema::IfcProduct*);

	template <typename P, typename PP>
    IfcGeom::BRepElement<P, PP>* create_brep_for_processed_representation(
        const IteratorSettings&, IfcSchema::IfcRepresentation*, IfcSchema::IfcProduct*, IfcGeom::BRepElement<P, PP>*);

	const IfcSchema::IfcMaterial* get_single_material_association(const IfcSchema::IfcProduct*);
	IfcSchema::IfcRepresentation* representation_mapped_to(const IfcSchema::IfcRepresentation* representation);
	IfcSchema::IfcProduct::list::ptr products_represented_by(const IfcSchema::IfcRepresentation*);
	const SurfaceStyle* get_style(const IfcSchema::IfcRepresentationItem*);
	const SurfaceStyle* get_style(const IfcSchema::IfcMaterial*);
	
	template <typename T> std::pair<IfcSchema::IfcSurfaceStyle*, T*> _get_surface_style(const IfcSchema::IfcStyledItem* si) {
		std::vector<IfcSchema::IfcPresentationStyle*> prs_styles;

#ifdef SCHEMA_HAS_IfcStyleAssignmentSelect
		IfcEntityList::ptr style_assignments = si->Styles();
		for (IfcEntityList::it kt = style_assignments->begin(); kt != style_assignments->end(); ++kt) {
			
			// Using IfcPresentationStyleAssignment is deprecated, use the direct assignment of a subtype of IfcPresentationStyle instead.
			auto style_k = (*kt)->as<IfcSchema::IfcPresentationStyle>();
			if (style_k) {
				prs_styles.push_back(style_k);
				continue;
			}

			if (!(*kt)->declaration().is(IfcSchema::IfcPresentationStyleAssignment::Class())) {
				continue;
			}

			IfcSchema::IfcPresentationStyleAssignment* style_assignment = (IfcSchema::IfcPresentationStyleAssignment*) *kt;

			Logger::Warning("Deprecated usage of", style_assignment);
#else
		IfcSchema::IfcPresentationStyleAssignment::list::ptr style_assignments = si->Styles();
		for (IfcSchema::IfcPresentationStyleAssignment::list::it kt = style_assignments->begin(); kt != style_assignments->end(); ++kt) {
			IfcSchema::IfcPresentationStyleAssignment* style_assignment = *kt;
#endif

			// Only in case of 2x3 or old style IfcPresentationStyleAssignment

			IfcEntityList::ptr styles = style_assignment->Styles();

			for (IfcEntityList::it lt = styles->begin(); lt != styles->end(); ++lt) {
				auto style_l = (*lt)->as<IfcSchema::IfcPresentationStyle>();
				if (style_l) {
					prs_styles.push_back(style_l);
				}
			}
		}
		
		for (auto& style : prs_styles) {
			if (style->declaration().is(IfcSchema::IfcSurfaceStyle::Class())) {
				IfcSchema::IfcSurfaceStyle* surface_style = (IfcSchema::IfcSurfaceStyle*) style;
				if (surface_style->Side() != IfcSchema::IfcSurfaceSide::IfcSurfaceSide_NEGATIVE) {
					IfcEntityList::ptr styles_elements = surface_style->Styles();
					for (IfcEntityList::it mt = styles_elements->begin(); mt != styles_elements->end(); ++mt) {
						if ((*mt)->declaration().is(T::Class())) {
							return std::make_pair(surface_style, (T*) *mt);
						}
					}
				}
			}
		}

		return std::make_pair<IfcSchema::IfcSurfaceStyle*, T*>(0,0);
	}

	template <typename T> std::pair<IfcSchema::IfcSurfaceStyle*, T*> get_surface_style(const IfcSchema::IfcRepresentationItem* representation_item) {
  		// For certain representation items, most notably boolean operands,
		// a style definition might reside on one of its operands.
		representation_item = find_item_carrying_style(representation_item);

		if (representation_item->as<IfcSchema::IfcStyledItem>()) {
			return _get_surface_style<T>(representation_item->as<IfcSchema::IfcStyledItem>());
		}
		IfcSchema::IfcStyledItem::list::ptr styled_items = representation_item->StyledByItem();
		if (styled_items->size()) {
			// StyledByItem is a SET [0:1] OF IfcStyledItem, so we return after the first IfcStyledItem:
			return _get_surface_style<T>(*styled_items->begin());
		}
		return std::make_pair<IfcSchema::IfcSurfaceStyle*, T*>(0,0);
	}

	void purge_cache() { 
		// Rather hack-ish, but a stopgap solution to keep memory under control
		// for large files. SurfaceStyles need to be kept at all costs, as they
		// are read later on when serializing Collada files.
#ifndef NO_CACHE
		cache = MAKE_TYPE_NAME(Cache)();
#endif
	}

	void set_conversion_placement_rel_to(const IfcParse::declaration* type);

#include "IfcRegisterGeomHeader.h"

	virtual void setValue(GeomValue var, double value);
	virtual double getValue(GeomValue var) const;

	virtual IfcGeom::BRepElement<double>* convert(
		const IteratorSettings& settings, IfcUtil::IfcBaseClass* representation,
		IfcUtil::IfcBaseClass* product)
	{
		return create_brep_for_representation_and_product<double, double>(settings, (IfcSchema::IfcRepresentation*) representation, (IfcSchema::IfcProduct*) product);
	}

	virtual IfcRepresentationShapeItems convert(IfcUtil::IfcBaseClass* item) {
		IfcRepresentationShapeItems items;
		bool success = convert_shapes(item, items);
		if (!success) {
			throw IfcParse::IfcException("Failed to process representation item");
		}
		return items;
	}

	virtual bool convert_placement(IfcUtil::IfcBaseClass* item, gp_Trsf& trsf) {
		if (item->as<IfcSchema::IfcObjectPlacement>()) {
			return convert(item->as<IfcSchema::IfcObjectPlacement>(), trsf);
		} else {
			return false;
		}
	}

};

IfcUtil::IfcBaseClass* MAKE_TYPE_NAME(tesselate_)(const TopoDS_Shape& shape, double deflection);
IfcUtil::IfcBaseClass* MAKE_TYPE_NAME(serialise_)(const TopoDS_Shape& shape, bool advanced);

}
#endif
