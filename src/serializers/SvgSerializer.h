/********************************************************************************
 *                                                                              *
 * Copyright 2015 IfcOpenShell and ROOT B.V.                                    *
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

#ifdef IFOPSH_WITH_OPENCASCADE

#ifndef SVGSERIALIZER_H
#define SVGSERIALIZER_H

#include "../ifcgeom/GeometrySerializer.h"
#include "../ifcgeom/kernels/opencascade/base_utils.h"
#include "../serializers/serializers_api.h"
#include "../serializers/util.h"

#include "../ifcparse/utils.h"

#include <HLRBRep_Algo.hxx>
#include <HLRBRep_HLRToShape.hxx>
#include <HLRBRep_PolyAlgo.hxx>
#include <HLRAlgo_Projector.hxx>
#include <gp_Pln.hxx>
#include <Bnd_Box.hxx>
#include <Standard_Version.hxx>
#include <BRep_Builder.hxx>
#include <HLRBRep_PolyHLRToShape.hxx>
#include <BRepTopAdaptor_FClass2d.hxx>
#include <Geom_Plane.hxx>
#include <BRepBndLib.hxx>
#include <BRepMesh_IncrementalMesh.hxx>
#include <TopExp_Explorer.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Face.hxx>
#include <TopoDS_Edge.hxx>
#include <TopoDS_Vertex.hxx>
#include <BRepGProp_Face.hxx>
#include <BRepGProp.hxx>
#include <GProp_GProps.hxx>
#include <BRepAlgoAPI_Common.hxx>
#include <BRepBuilderAPI_MakeEdge.hxx>
#include <Precision.hxx>
#include <gp_Vec.hxx>
#include <NCollection_DataMap.hxx>
#include <TopTools_ShapeMapHasher.hxx>

#if OCC_VERSION_HEX >= 0x70300
#include <Bnd_OBB.hxx>
#endif

#include <sstream>
#include <string>
#include <limits>
#include <array>
#include <tuple>
#include <map>
#include <iterator>
#include <algorithm>

typedef std::pair<const IfcUtil::IfcBaseEntity*, std::string> drawing_key;

struct storey_sorter {
	bool operator()(const drawing_key& ad, const drawing_key& bd) const {
		if (ad.first == nullptr && bd.first != nullptr) {
			return false;
		} else if (bd.first == nullptr && ad.first != nullptr) {
			return true;
		} else if (ad.first == nullptr && bd.first == nullptr) {
			return std::less<std::string>()(ad.second, bd.second);
		}

		auto a = ad.first;
		auto b = bd.first;

		const bool a_is_storey = a->declaration().is("IfcBuildingStorey");
		const bool b_is_storey = b->declaration().is("IfcBuildingStorey");
		if (a_is_storey && b_is_storey) {
			boost::optional<double> a_elev, b_elev;
			try {
				a_elev = static_cast<double>(a->get("Elevation"));
				b_elev = static_cast<double>(b->get("Elevation"));
			} catch (...) {};
			if (a_elev && b_elev) {
				if (std::equal_to<double>()(*a_elev, *b_elev)) {
					return std::less<unsigned int>()(a->id(), b->id());
				} else {
					return std::less<double>()(*a_elev, *b_elev);
				}
			}

			boost::optional<std::string> a_name, b_name;
			try {
				a_name = static_cast<std::string>(a->get("Name"));
				b_name = static_cast<std::string>(b->get("Name"));
			} catch (...) {};
			if (a_name && b_name) {
				if (std::equal_to<std::string>()(*a_name, *b_name)) {
					return std::less<unsigned int>()(a->id(), b->id());
				} else {
					return std::less<std::string>()(*a_name, *b_name);
				}
			}
		}
		return std::less<const IfcUtil::IfcBaseEntity*>()(a, b);
	}
};

struct horizontal_plan {
	const IfcUtil::IfcBaseEntity* storey;
	double elevation, offset, next_elevation;
};

struct horizontal_plan_at_element {};

struct vertical_section {
	gp_Pln plane;
	std::string name;
	bool with_projection;
	boost::optional<double> scale;
	boost::optional<std::pair<double, double>> size;
};

typedef boost::variant<horizontal_plan, horizontal_plan_at_element, vertical_section> section_data;

// Cross-object "cross-coplanar" edge classification (issue #3742), v2: lets a layered
// product's material be resolved per candidate face instead of once for the whole
// product (see geometry_data::cross_coplanar_layer_projection below for why). Purely a
// geometric lookup table -- axis/origin/offsets are all in the same world/drawing frame
// geometry_data::compound_local ends up in once trsf is applied, so a face's centroid can
// be classified into a layer with a single dot product + binary search, no boolean split
// of any geometry required. materials.size() == cumulative_offsets.size() - 1.
struct layer_projection {
	gp_Dir axis;
	gp_Pnt origin;
	std::vector<double> cumulative_offsets;
	std::vector<const IfcUtil::IfcBaseInterface*> materials;
};

struct geometry_data {
	TopoDS_Shape compound_local;
	std::vector<boost::optional<std::vector<double>>> dash_arrays;
	gp_Trsf trsf;
	const IfcUtil::IfcBaseEntity* product;
	const IfcUtil::IfcBaseEntity* storey;
	double storey_elevation;
	std::string ifc_name, svg_name;
	// Cross-object "cross-coplanar" edge classification (issue #3742): one style/material
	// identity for the whole product (the underlying IFC entity a resolved style was derived
	// from, whether via IfcStyledItem or IfcMaterial -- see taxonomy::style::instance), used
	// as the "same style/material" comparison key in the cross-object pass. Deliberately
	// per-product, not per-face/per-layer: per-item shapes are transformed and concatenated
	// away by the time compound_local exists (IfcGeom::Representation::BRep::as_compound()),
	// so there's no cheap way to trace a specific face in compound_local back to a specific
	// original item/layer. A single representative style per product is simpler and correct
	// for the common case (single-material elements, or layered elements where the touching
	// layer is also the one that happens to resolve first); nullptr if the product has none.
	const IfcUtil::IfcBaseInterface* cross_coplanar_style_instance;
	// Same per-product simplification as cross_coplanar_style_instance above, but for the
	// product's resolved material (IfcMaterial, or the first layer of an
	// IfcMaterialLayerSet(Usage)) rather than its rendering style. Material takes priority over
	// style in the cross-object match (see find_cross_coplanar_matches()): style is a
	// presentation concept and two products can coincidentally share a style while being made of
	// different materials (or vice versa). nullptr if the product has no resolved material.
	const IfcUtil::IfcBaseInterface* cross_coplanar_material_instance;
	// v2: when the product has a 2+ layer IfcMaterialLayerSetUsage, this lets
	// find_cross_coplanar_matches() resolve a candidate face's *own* layer material
	// instead of falling back to cross_coplanar_material_instance's whole-product
	// approximation -- fixes false positives where two products share a first-resolved
	// layer material but differ in a different layer (e.g. both have a Corten 1 layer,
	// but one's other layer is Concrete 1 and the other's is Concrete 2: the Corten
	// boundary genuinely matches, the Concrete boundary must not). boost::none for
	// non-layered products or layer sets with fewer than 2 layers, where a single
	// per-product material is already unambiguous.
	boost::optional<layer_projection> cross_coplanar_layer_projection;
};

struct drawing_meta {
	gp_Pln pln_3d;
	std::array<std::array<double, 3>, 3> matrix_3;
};

enum subtract_before_project {
	ON_SLABS_AT_FLOORPLANS,
	ON_SLABS_AND_WALLS,
	ALWAYS
};

typedef boost::variant<
	boost::blank,
	Handle(HLRBRep_Algo),
	Handle(HLRBRep_PolyAlgo)
> hlr_brep_or_poly_t;

namespace {
	class hlr_writer {
		const TopoDS_Shape& shape_;

	public:
		typedef void result_type;

		hlr_writer(const TopoDS_Shape& shape) : shape_(shape)
		{}

		void operator()(boost::blank&) const {
			throw std::runtime_error("");
		}

		void operator()(opencascade::handle<HLRBRep_Algo>& algo) const {
			algo->Add(shape_);
		}

		void operator()(opencascade::handle<HLRBRep_PolyAlgo>& algo) const {
			BRepMesh_IncrementalMesh(shape_, 0.10);
			algo->Load(shape_);
		}
	};

	template <typename T>
	TopoDS_Compound occt_join(T t) {
		BRep_Builder B;
		TopoDS_Compound C;
		B.MakeCompound(C);
		if (!t.IsNull()) {
			TopoDS_Iterator it(t);
			for (; it.More(); it.Next()) {
				B.Add(C, it.Value());
			}
		}
		return C;
	}

	template <typename T, typename... Ts>
	TopoDS_Compound occt_join(T t, Ts... tss) {
		BRep_Builder B;
		TopoDS_Compound C;
		B.MakeCompound(C);
		if (!t.IsNull()) {
			TopoDS_Iterator it(t);
			for (; it.More(); it.Next()) {
				B.Add(C, it.Value());
			}
		}
		auto rest = occt_join(tss...);
		if (!rest.IsNull()) {
			TopoDS_Iterator it(rest);
			for (; it.More(); it.Next()) {
				B.Add(C, it.Value());
			}
		}
		return C;
	}

	// Cross-object "cross-coplanar" edge classification (issue #3742) needs a style and a
	// material identity alongside each product's shape -- see geometry_data::
	// cross_coplanar_style_instance and ::cross_coplanar_material_instance for why those
	// identities are per-product, not per-face. The trailing layer_projection (v2) is the
	// exception: when present, it lets find_cross_coplanar_matches() resolve a candidate
	// face's *own* material instead of relying on the whole-product one -- see
	// geometry_data::cross_coplanar_layer_projection. All three are nullptr/none wherever
	// cross-coplanar classification is off, a product resolved none, or (for the
	// projection) the product isn't layered; unused by anything else that reads this list.
	typedef std::list<std::tuple<const IfcUtil::IfcBaseEntity*, TopoDS_Shape, const IfcUtil::IfcBaseInterface*, const IfcUtil::IfcBaseInterface*, boost::optional<layer_projection>>> product_shape_list_t;

	class hlr_calc {
	private:
		const HLRAlgo_Projector& projector_;
		const product_shape_list_t* product_shapes_ = nullptr;
		// SVG edge classification (issue #3668): per-(product, class) edge-only sub-shapes,
		// classified pre-HLR on the original (real-face) topology. Queried via
		// VCompound(S)/OutLineVCompound(S), which correlate by the identity of the *original*
		// edges added to the algorithm -- not by the reconstructed output -- so this works even
		// though HLR's own output compounds carry no face topology at all. Empty class string
		// means "unclassified" (used for the two fallback cases below).
		const std::list<std::tuple<const IfcUtil::IfcBaseEntity*, std::string, TopoDS_Shape>>* classified_shapes_ = nullptr;

	public:
		typedef std::list<std::tuple<const IfcUtil::IfcBaseEntity*, std::string, TopoDS_Shape>> result_type;

		hlr_calc(const HLRAlgo_Projector& projector) : projector_(projector)
		{}

		void set_product_shape(const product_shape_list_t* product_shapes) {
			product_shapes_ = product_shapes;
		}

		void set_classified_shapes(const std::list<std::tuple<const IfcUtil::IfcBaseEntity*, std::string, TopoDS_Shape>>* classified_shapes) {
			classified_shapes_ = classified_shapes;
		}

		result_type operator()(boost::blank&) const {
			throw std::runtime_error("");
		}

		template <typename HlrToShapeT>
		result_type extract(HlrToShapeT& hlr_shapes) {
			result_type r;
			if (classified_shapes_ && !classified_shapes_->empty()) {
				for (auto& t : *classified_shapes_) {
					r.push_back({ std::get<0>(t), std::get<1>(t), occt_join(hlr_shapes.OutLineVCompound(std::get<2>(t)), hlr_shapes.VCompound(std::get<2>(t))) });
				}
			} else if (product_shapes_) {
				for (auto& p : *product_shapes_) {
					r.push_back({ std::get<0>(p), std::string(), occt_join(hlr_shapes.OutLineVCompound(std::get<1>(p)), hlr_shapes.VCompound(std::get<1>(p))) });
				}
			} else {
				r.push_back({ nullptr, std::string(), occt_join(hlr_shapes.OutLineVCompound(), hlr_shapes.VCompound()) });
			}
			return r;
		}

		result_type operator()(opencascade::handle<HLRBRep_Algo>& algo) {
			algo->Projector(projector_);
			algo->Update();
			algo->Hide();
			HLRBRep_HLRToShape hlr_shapes(algo);
			return extract(hlr_shapes);
		}

		result_type operator()(opencascade::handle<HLRBRep_PolyAlgo>& algo) {
			algo->Projector(projector_);
			algo->Update();
			HLRBRep_PolyHLRToShape hlr_shapes;
			hlr_shapes.Update(algo);
			return extract(hlr_shapes);
		}
	};

	// Cross-object "cross-coplanar" edge classification (issue #3742). Deliberately
	// self-contained, not sharing geometry primitives with classify_edge_from_faces() /
	// face_normal_from_planar_face() in SvgSerializer.cpp (a separate, already carefully-tuned
	// function for the single-object 5-class scheme) -- and it has to be self-contained here
	// regardless, since prefiltered_hlr::build() is defined inline in this header, compiled
	// before classify_edge_from_faces() is even declared later in the .cpp. Keeping this pass'
	// own small set of primitives independent also means a future change to the 5-class scheme
	// can't accidentally affect this one, or vice versa.
	//
	// The class name added here ("cross-coplanar") must stay in sync with
	// edge_style_class_name(edge_style_class::cross_coplanar) in SvgSerializer.cpp -- there's
	// no shared enum to keep them structurally linked, since edge_style_class also lives in
	// that later, separate anonymous namespace.
	namespace cross_coplanar {
		constexpr const char* const class_name = "cross-coplanar";

		bool face_normal(const TopoDS_Face& f, gp_Dir& out) {
			auto s = BRep_Tool::Surface(f);
			if (s->DynamicType() != STANDARD_TYPE(Geom_Plane)) {
				return false;
			}
			auto p = Handle(Geom_Plane)::DownCast(s);
			gp_Dir d = p->Axis().Direction();
			if (f.Orientation() == TopAbs_REVERSED) {
				d.Reverse();
			}
			out = d;
			return true;
		}

		// A straight edge's endpoints in 3D, plus its (unit) direction and length -- the atom
		// the edge-coincidence matching below works with. Curved edges (no Geom_Line) and
		// degenerate (near-zero-length) edges are skipped by edge_to_line_seg, consistent with
		// this whole feature only supporting planar/straight geometry (same simplification
		// classify_edge_from_faces() already makes for the single-object 5-class scheme).
		struct LineSeg {
			gp_Pnt p0, p1;
			gp_Dir dir;
			double length;
		};

		// Deliberately orientation-*independent*: p0/p1 always come from the edge's intrinsic
		// curve parametrization (u0, u1), never adjusted for e.Orientation(). v3's coverage
		// accumulation and sub-edge reconstruction store/retrieve per-edge t-values across two
		// different topological contexts for "the same" edge (once via a face's own boundary
		// traversal in accumulate_edge_coverage(), later via a flat classified-edges compound in
		// replace_matched_edges()) -- the same edge can carry different relative orientation in
		// each (e.g. a shared edge between two faces of one product, or the separate
		// single-object classification pass picking a different owning face than this one's own
		// traversal does). An orientation-dependent swap here would make a t-value computed in
		// one context mean the *opposite* end when reconstructed in the other -- exactly the bug
		// that produced a sub-edge mirrored within its own original edge's span. Every other use
		// of `dir` in this namespace (collinearity, perpendicular distance) already goes through
		// abs()/cross-product magnitude and is sign-independent, so this doesn't change any
		// matching decision, only guarantees a stable frame for split_edge_by_coverage()'s
		// absolute-point reconstruction.
		boost::optional<LineSeg> edge_to_line_seg(const TopoDS_Edge& e) {
			double u0, u1;
			auto crv = BRep_Tool::Curve(e, u0, u1);
			if (!crv || crv->DynamicType() != STANDARD_TYPE(Geom_Line)) {
				return boost::none;
			}
			gp_Pnt p0 = crv->Value(u0);
			gp_Pnt p1 = crv->Value(u1);
			if (p0.Distance(p1) < Precision::Confusion()) {
				return boost::none;
			}
			gp_Vec v(p0, p1);
			return LineSeg{ p0, p1, gp_Dir(v), v.Magnitude() };
		}

		std::vector<LineSeg> face_line_segs(const TopoDS_Face& f) {
			std::vector<LineSeg> out;
			for (TopExp_Explorer e(f, TopAbs_EDGE); e.More(); e.Next()) {
				auto seg = edge_to_line_seg(TopoDS::Edge(e.Current()));
				if (seg) {
					out.push_back(*seg);
				}
			}
			return out;
		}

		// Merge overlapping/touching-within-tolerance 1D intervals -- the same union logic the
		// Python arrangement approach used all session for 2D projected lines, here applied to
		// real 3D edge intervals instead.
		std::vector<std::pair<double, double>> ivs_union(std::vector<std::pair<double, double>> ivs, double tol) {
			std::sort(ivs.begin(), ivs.end());
			std::vector<std::pair<double, double>> merged;
			for (auto& iv : ivs) {
				if (!merged.empty() && iv.first <= merged.back().second + tol) {
					merged.back().second = std::max(merged.back().second, iv.second);
				} else {
					merged.push_back(iv);
				}
			}
			return merged;
		}

		// Resolves the material at a specific 3D point for a (possibly layered) product: a
		// single dot product against `proj`'s axis/origin plus a binary search into
		// cumulative_offsets, clamped to a valid layer index -- falls back to `product_level`
		// (the whole-product material/style identity) when the product isn't layered at all.
		// Deliberately point-based rather than face-based: a face's *centroid* is only a valid
		// stand-in for "this face's material" when the face doesn't itself span more than one
		// layer -- for a face that does (e.g. a slanted/sheared face crossing a layer boundary),
		// sampling different points along a candidate edge's own overlap with a neighbour is
		// what lets each sub-range be judged on its own true material instead of one, possibly
		// unrepresentative, sample for the whole face.
		const IfcUtil::IfcBaseInterface* resolve_material_at_point(
			const gp_Pnt& point, const boost::optional<layer_projection>& proj,
			const IfcUtil::IfcBaseInterface* product_level
		) {
			if (!proj) {
				return product_level;
			}
			double dist = gp_Vec(proj->origin, point).Dot(proj->axis);
			auto& offs = proj->cumulative_offsets;
			size_t idx = std::upper_bound(offs.begin(), offs.end(), dist) - offs.begin();
			idx = std::min(std::max(idx, size_t(1)), proj->materials.size());
			return proj->materials[idx - 1];
		}

		// Projects every *internal* layer boundary of `proj` (excluding the product's own
		// overall start/end, which aren't a material transition) onto `seg`'s own t-axis --
		// i.e. for each boundary plane at proj->origin + offset*proj->axis, solves for the t
		// where seg's line crosses it. If `seg` is (near-)perpendicular to proj->axis, the line
		// never crosses a layer boundary at all (it's confined to a single layer already, the
		// common case for e.g. a horizontal edge on a vertically-layered slab) -- returns empty
		// in that case, which is exactly what lets the per-sub-interval logic degenerate to a
		// single-piece, whole-interval check when a layer split genuinely isn't relevant.
		std::vector<double> layer_boundary_ts(const LineSeg& seg, const layer_projection& proj) {
			std::vector<double> ts;
			double denom = seg.dir.Dot(proj.axis);
			if (std::abs(denom) < 1.e-9) {
				return ts;
			}
			double base = gp_Vec(proj.origin, seg.p0).Dot(proj.axis);
			for (size_t i = 1; i + 1 < proj.cumulative_offsets.size(); ++i) {
				ts.push_back((proj.cumulative_offsets[i] - base) / denom);
			}
			return ts;
		}

		// v3: raw covered intervals accumulated per original edge, across every qualifying
		// neighbour face pair the double loop in find_cross_coplanar_matches() finds -- keyed
		// by shape identity (TShape + Location), the same map/hasher pairing already used for
		// shape-identity bookkeeping in kernels/opencascade/{wire_utils,sweep_utils}.cpp. An
		// edge can legitimately be touched by more than one neighbour on different sub-ranges
		// (e.g. two separate adjacent slabs on either side of a wall's own length), so the
		// union of ALL contributions has to be known before any full-vs-partial-vs-none
		// decision is made -- deferred to split_edge_by_coverage() below, once the whole double
		// loop has finished.
		typedef NCollection_DataMap<TopoDS_Shape, std::vector<std::pair<double, double>>, TopTools_ShapeMapHasher> edge_coverage_map_t;

		// For each edge of `face` with a valid LineSeg, appends its raw covered sub-intervals
		// (against `other_segs`, the boundary edges of an already-confirmed-coplanar face of a
		// *different* product) into `coverage` -- accumulation only, no full/partial decision
		// here (see edge_coverage_map_t above for why that's deferred). This is a direct
		// edge-to-edge coincidence test -- not a face-area-overlap test (the previous, wrong
		// v1 approach: two side-by-side, non-overlapping faces sharing a boundary, or a void's
		// inner wire coincident with a plug's outer wire, both have *zero* area in common by
		// construction, even though the shared edge is exactly the "duplicate boundary" this
		// feature exists to find).
		//
		// `proj_this`/`material_this`/`style_this` describe `face`'s own product; `proj_other`/
		// `material_other`/`style_other` describe the neighbour `other_segs` came from. When
		// either is layered, a raw geometric interval isn't necessarily one material throughout
		// -- a face that itself spans more than one layer (e.g. a slanted face crossing a layer
		// boundary) would otherwise have its whole overlap judged by one, possibly
		// unrepresentative, sample. Instead each raw interval is split at every layer boundary
		// either side contributes (layer_boundary_ts()), and each resulting sub-range is
		// independently verified at its own midpoint before being accepted -- a sub-range where
		// materials genuinely agree (e.g. both Corten) is kept even if a neighbouring sub-range
		// of the *same* edge disagrees (e.g. Concrete 1 vs Concrete 2), and vice versa. When
		// neither side is layered this degenerates to exactly the old whole-interval behaviour
		// (no boundaries found, one pass through the loop below).
		void accumulate_edge_coverage(
			const TopoDS_Face& face, const std::vector<LineSeg>& other_segs, double tol,
			const boost::optional<layer_projection>& proj_this, const IfcUtil::IfcBaseInterface* material_this, const IfcUtil::IfcBaseInterface* style_this,
			const boost::optional<layer_projection>& proj_other, const IfcUtil::IfcBaseInterface* material_other, const IfcUtil::IfcBaseInterface* style_other,
			edge_coverage_map_t& coverage
		) {
			for (TopExp_Explorer eexp(face, TopAbs_EDGE); eexp.More(); eexp.Next()) {
				const TopoDS_Edge& e = TopoDS::Edge(eexp.Current());
				auto seg = edge_to_line_seg(e);
				if (!seg) {
					continue;
				}
				std::vector<std::pair<double, double>> covered;
				for (auto& other : other_segs) {
					if (std::abs(seg->dir.Dot(other.dir)) <= 1.0 - 3.8e-5) {
						continue;
					}
					gp_Vec to_other(seg->p0, other.p0);
					double perp_dist = to_other.Crossed(gp_Vec(seg->dir)).Magnitude();
					if (perp_dist >= tol) {
						continue;
					}
					double t0 = gp_Vec(seg->p0, other.p0).Dot(gp_Vec(seg->dir));
					double t1 = gp_Vec(seg->p0, other.p1).Dot(gp_Vec(seg->dir));
					double lo = std::min(t0, t1), hi = std::max(t0, t1);

					if (!proj_this && !proj_other) {
						covered.push_back({ lo, hi });
						continue;
					}

					std::vector<double> boundaries;
					if (proj_this) {
						auto bs = layer_boundary_ts(*seg, *proj_this);
						boundaries.insert(boundaries.end(), bs.begin(), bs.end());
					}
					if (proj_other) {
						auto bs = layer_boundary_ts(*seg, *proj_other);
						boundaries.insert(boundaries.end(), bs.begin(), bs.end());
					}
					std::vector<double> cuts;
					for (double b : boundaries) {
						if (b > lo && b < hi) {
							cuts.push_back(b);
						}
					}
					std::sort(cuts.begin(), cuts.end());

					double cursor = lo;
					for (size_t i = 0; i <= cuts.size(); ++i) {
						double piece_end = (i < cuts.size()) ? cuts[i] : hi;
						if (piece_end <= cursor) {
							continue;
						}
						double t_mid = 0.5 * (cursor + piece_end);
						gp_Pnt mid = seg->p0.Translated(gp_Vec(seg->dir) * t_mid);
						const auto* mat_this = resolve_material_at_point(mid, proj_this, material_this);
						const auto* mat_other = resolve_material_at_point(mid, proj_other, material_other);
						bool ok;
						if (mat_this || mat_other) {
							ok = mat_this && mat_other && mat_this == mat_other;
						} else {
							ok = style_this && style_other && style_this == style_other;
						}
						if (ok) {
							covered.push_back({ cursor, piece_end });
						}
						cursor = piece_end;
					}
				}
				if (covered.empty()) {
					continue;
				}
				auto* existing = coverage.ChangeSeek(e);
				if (existing) {
					existing->insert(existing->end(), covered.begin(), covered.end());
				} else {
					coverage.Bind(e, covered);
				}
			}
		}

		struct edge_split_result {
			std::vector<TopoDS_Edge> covered;
			std::vector<TopoDS_Edge> remainder;
			// True only when covered/remainder contain newly-constructed TopoDS_Edge objects
			// (the genuine partial-split path below) -- false when either vector just holds the
			// original, unmodified `e` (the full-coverage fast path, or the "nothing survived
			// noise filtering" fallback). Callers need this to know which edges are brand new
			// geometry that was never part of what build() feeds to the HLR algorithm, and so
			// must be separately injected into the owning product's items_ shape for HLRBRep_
			// HLRToShape::VCompound()/OutLineVCompound() to correlate them at all (see the
			// injection step in find_cross_coplanar_matches()).
			bool is_new_geometry = false;
		};

		// Unions `raw_intervals` (every contribution accumulate_edge_coverage() ever recorded
		// for `e`) and walks `e`'s own [0, length] range against that union to produce
		// alternating covered/uncovered sub-ranges -- v3's actual sub-edge split. Full coverage
		// keeps the fast path of moving the *whole*, unmodified edge (avoids introducing a
		// floating-point seam at an edge's own original endpoints for the common full-duplicate
		// case, and is byte-identical to pre-v3 behaviour). Only genuine partial coverage
		// constructs new, trimmed TopoDS_Edge objects (via BRepBuilderAPI_MakeEdge on two
		// points derived from `seg`'s own p0/dir -- no new geometric machinery). Sub-ranges
		// shorter than Precision::Confusion() are dropped rather than turned into degenerate
		// zero-length edges.
		edge_split_result split_edge_by_coverage(
			const TopoDS_Edge& e, const LineSeg& seg,
			const std::vector<std::pair<double, double>>& raw_intervals, double tol
		) {
			edge_split_result result;
			auto merged = ivs_union(raw_intervals, tol);

			for (auto& iv : merged) {
				if (iv.first <= tol && iv.second >= seg.length - tol) {
					result.covered.push_back(e);
					return result;
				}
			}

			// Clamp every merged interval to this edge's own [0, length] range -- a raw interval
			// can extend well past this edge's own endpoint (e.g. a much longer neighbour edge
			// collinear with a short one), leaving only a razor-thin sliver actually inside
			// [0, length]. A clamped sub-interval shorter than the matching tolerance itself is
			// noise (e.g. two edges only touching at a shared corner vertex) -- not a genuine
			// partial duplicate -- and is dropped rather than fragmenting the edge over it; it's
			// the *clamped* width that matters here, not the raw interval's own (pre-clamp)
			// width. If nothing genuinely covered survives, treat the whole edge as untouched,
			// same as if accumulate_edge_coverage() had never recorded anything for it at all.
			std::vector<std::pair<double, double>> clamped;
			for (auto& iv : merged) {
				double a = std::max(iv.first, 0.0);
				double b = std::min(iv.second, seg.length);
				if (b - a >= tol) {
					clamped.push_back({ a, b });
				}
			}
			if (clamped.empty()) {
				result.remainder.push_back(e);
				return result;
			}

			auto make_subedge = [&](double a, double b) -> boost::optional<TopoDS_Edge> {
				if (b - a < Precision::Confusion()) {
					return boost::none;
				}
				gp_Pnt pa = seg.p0.Translated(gp_Vec(seg.dir) * a);
				gp_Pnt pb = seg.p0.Translated(gp_Vec(seg.dir) * b);
				BRepBuilderAPI_MakeEdge mk(pa, pb);
				if (!mk.IsDone()) {
					return boost::none;
				}
				return mk.Edge();
			};

			result.is_new_geometry = true;

			double cursor = 0.0;
			for (auto& iv : clamped) {
				double a = iv.first;
				double b = iv.second;
				if (b <= cursor) {
					continue;
				}
				if (a > cursor) {
					if (auto sub = make_subedge(cursor, a)) {
						result.remainder.push_back(*sub);
					}
				}
				if (auto sub = make_subedge(std::max(a, cursor), b)) {
					result.covered.push_back(*sub);
				}
				cursor = std::max(cursor, b);
			}
			if (cursor < seg.length) {
				if (auto sub = make_subedge(cursor, seg.length)) {
					result.remainder.push_back(*sub);
				}
			}
			return result;
		}

		// Replaces `from` (one of a product's original 5-class buckets) with a new compound:
		// edges with no entry in `coverage` are kept unchanged; edges that split_edge_by_coverage()
		// finds fully covered are dropped entirely (as in pre-v3 behaviour -- they're already
		// committed to one of the original classes by the per-product classification pass that
		// runs before find_cross_coplanar_matches(), so without this an edge would end up
		// listed under two classes at once and get drawn twice); partially-covered edges are
		// *replaced* by their uncovered remainder sub-edge(s) -- same class, only the geometry
		// shrinks. Every covered sub-edge (whole or trimmed) is also appended to
		// `cross_coplanar_out`, so the cross-coplanar bucket and this replacement are always
		// built from exactly the same split decision. Whenever split_edge_by_coverage() reports
		// genuinely new geometry, every resulting piece (both covered and remainder) is *also*
		// appended to `new_geometry_out` -- these are edges build() never fed to the HLR
		// algorithm, so the caller has to inject them into the owning product's items_ shape
		// before build()'s algo->Add() loop runs, or HLRBRep_HLRToShape::VCompound()/
		// OutLineVCompound() (which correlate by original-input-edge identity, not by shape
		// content) will silently return nothing for them. `from`'s edges and `coverage`'s keys
		// are the same, non-moved, non-transformed original edges (both ultimately sourced from
		// the same per-product compound_to_hlr, never copied), so plain shape identity (TShape +
		// Location, via TopTools_ShapeMapHasher) is a safe, exact way to find the overlap.
		TopoDS_Compound replace_matched_edges(
			const TopoDS_Shape& from, edge_coverage_map_t& coverage, double tol,
			BRep_Builder& builder, TopoDS_Compound& cross_coplanar_out, TopoDS_Compound& new_geometry_out
		) {
			TopoDS_Compound result;
			builder.MakeCompound(result);
			for (TopExp_Explorer exp(from, TopAbs_EDGE); exp.More(); exp.Next()) {
				const TopoDS_Edge& e = TopoDS::Edge(exp.Current());
				auto* raw = coverage.ChangeSeek(e);
				if (!raw) {
					builder.Add(result, e);
					continue;
				}
				auto seg = edge_to_line_seg(e);
				if (!seg) {
					// Shouldn't happen -- coverage is only ever populated for edges that already
					// had a valid LineSeg -- but keep the edge rather than silently drop it.
					builder.Add(result, e);
					continue;
				}
				auto split = split_edge_by_coverage(e, *seg, *raw, tol);
				for (auto& c : split.covered) {
					builder.Add(cross_coplanar_out, c);
					if (split.is_new_geometry) {
						builder.Add(new_geometry_out, c);
					}
				}
				for (auto& r : split.remainder) {
					builder.Add(result, r);
					if (split.is_new_geometry) {
						builder.Add(new_geometry_out, r);
					}
				}
			}
			return result;
		}
	}

	class prefiltered_hlr {

		class face_info {
		private:
			gp_XYZ dxyz, xdir, ydir;

		public:
			TopoDS_Shape* item;
			TopoDS_Face face;
			bool is_convex;
			// @note copying the BRepTopAdaptor_FClass2d didn't work so it's a pointer
			BRepTopAdaptor_FClass2d* fclass;

			face_info(TopoDS_Shape* it, const TopoDS_Face& fa)
				: item(it)
				, face(fa)
				, fclass(nullptr)
			{
				TopExp_Explorer exp(face, TopAbs_WIRE);
				is_convex = exp.More() && IfcGeom::util::is_convex(TopoDS::Wire(exp.Current()), 1.e-5) && ([&exp]() {exp.Next(); return true; })() && !exp.More();

				auto surf = BRep_Tool::Surface(fa);
				if (surf->DynamicType() != STANDARD_TYPE(Geom_Plane)) {
					throw std::runtime_error("Not implemented");
				}

				auto pln = Handle(Geom_Plane)::DownCast(surf);

				dxyz = pln->Position().Location().XYZ();
				xdir = pln->Position().XDirection().XYZ();
				ydir = pln->Position().YDirection().XYZ();
			}

			~face_info() {
				delete fclass;
			}

			void project(const gp_Pnt& xyz, gp_Pnt2d& uv) {
				const gp_Vec d = xyz.XYZ() - dxyz;
				uv.SetX(d.Dot(xdir));
				uv.SetY(d.Dot(ydir));
			}

			void interp(const gp_Pnt2d& a, const gp_Pnt2d& b, double d, gp_Pnt2d& out) {
				out.SetCoord(a.X() + (b.X() - a.X()) * d, a.Y() + (b.Y() - a.Y()) * d);
			}

			bool contains(const gp_Pnt& bottomleft, const gp_Pnt& topright) {
				gp_Pnt2d a, b;
				project(bottomleft, a);
				project(topright, b);
				return contains(a, b);
			}

			bool contains(const gp_Pnt2d& bottomleft, const gp_Pnt2d& topright) {
				if (!fclass) {
					fclass = new BRepTopAdaptor_FClass2d(face, 1.e-5);
				}
				// @todo unify with the 2d boolean algo 
				gp_Pnt2d bottomright(topright.X(), bottomleft.Y());
				gp_Pnt2d topleft(bottomleft.X(), topright.Y());
				std::array<gp_Pnt2d const*, 4> loop{ {
					&bottomleft,
					&bottomright,
					&topright,
					&topleft
				} };

				if (is_convex) {
					for (int i = 0; i < 4; ++i) {
						if (fclass->Perform(*loop[i]) == TopAbs_OUT) {
							return false;
						}
					}
				} else {
					gp_Pnt2d tmp;
					// 0,1,2,3 -> interp over bounding box edges (i%4, (i+1)%4)
					// 4,5 -> interp over bounding box diagonals (i%4, (i+2)%4)
					// @todo use boolean_utils.h points_on_planar_face_generator?
					// ... or skip faces with inner bounds all together ?
					// ... ?
					for (int i = 0; i < 6; ++i) {
						// @todo proper edge intersection
						for (int j = 0; j < 16; ++j) {
							const gp_Pnt2d& a = *loop[i % 4];
							const gp_Pnt2d& b = *loop[(i + (i >= 4 ? 2 : 1)) % 4];
							interp(a, b, j / 16.0, tmp);
							if (fclass->Perform(tmp) == TopAbs_OUT) {
								return false;
							}
						}
					}
				}

				return true;
			}
		};

		hlr_brep_or_poly_t engine_;
		bool use_prefiltering_;
		bool use_hlr_poly_;
		bool segment_projection_;
		gp_Ax1 view_direction_;
		HLRAlgo_Projector projector_;
		// Cross-object "cross-coplanar" edge classification (issue #3742): both flags are
		// needed here, not just the cross-coplanar one -- see the gating comment in build().
		bool use_edge_classification_;
		bool use_cross_coplanar_classification_;
		double cross_coplanar_tolerance_;
		bool render_cross_coplanar_edges_;

		std::multimap<double, face_info> large_ortho_faces_;
		product_shape_list_t items_;
		// SVG edge classification (issue #3668): see add_classified_edges().
		std::list<std::tuple<const IfcUtil::IfcBaseEntity*, std::string, TopoDS_Shape>> classified_items_;

		Logger& logger_;

	public:

		prefiltered_hlr(Logger& logger, bool use_prefiltering, bool use_hlr_poly, bool segment_projection, const gp_Pln& view_direction,
			bool use_edge_classification = false, bool use_cross_coplanar_classification = false, double cross_coplanar_tolerance = 1.e-4,
			bool render_cross_coplanar_edges = false)
			: logger_(logger)
			, use_prefiltering_(use_prefiltering)
			, use_hlr_poly_(use_hlr_poly)
			, segment_projection_(segment_projection)
			// @nb negative z in accordance with occt projector convention (and opengl)
			, view_direction_(view_direction.Axis())
			, use_edge_classification_(use_edge_classification)
			, use_cross_coplanar_classification_(use_cross_coplanar_classification)
			, cross_coplanar_tolerance_(cross_coplanar_tolerance)
			, render_cross_coplanar_edges_(render_cross_coplanar_edges)
		{
			if (use_hlr_poly_) {
				engine_ = new HLRBRep_PolyAlgo;
			} else {
				engine_ = new HLRBRep_Algo;
			}

			gp_Trsf trsf;
			trsf.SetTransformation(view_direction.Position());
			projector_ = HLRAlgo_Projector(trsf, false, 1.);
		}

		// SVG edge classification (issue #3668): register an edge-only sub-shape of `product`'s
		// original (pre-HLR, real-face) geometry under a given class name (e.g. "outline",
		// "sharp"). The full shape must still be added via add() as usual for correct occlusion;
		// this only affects which *class* each edge's visible portion is later extracted as, via
		// HLRBRep_HLRToShape::VCompound(S)/OutLineVCompound(S) in hlr_calc, which correlate by the
		// identity of the original edges within S.
		void add_classified_edges(const IfcUtil::IfcBaseEntity* product, const std::string& cls, const TopoDS_Shape& edges) {
			classified_items_.push_back({ product, cls, edges });
		}

		bool is_obscured_(TopoDS_Shape* sit) {
			const TopoDS_Shape& s = *sit;

			double min_d = std::numeric_limits<double>::infinity();

			TopExp_Explorer exp(s, TopAbs_VERTEX);
			for (; exp.More(); exp.Next()) {
				const auto& v = TopoDS::Vertex(exp.Current());
				auto pnt = BRep_Tool::Pnt(v);
				auto d = -(pnt.XYZ() - view_direction_.Location().XYZ()).Dot(view_direction_.Direction().XYZ());
				if (d < min_d) {
					min_d = d;
				}
			}

			Bnd_Box box;
			BRepBndLib::AddClose(s, box);

			if (box.IsVoid()) {
				// false or true, it doesn't really matter, just don't
				// proceed because asking for a corner of a void box
				// throws an exception.
				return false;
			}

			auto lower = large_ortho_faces_.lower_bound(0.);
			auto upper = large_ortho_faces_.upper_bound(min_d);

			for (auto it = lower; it != upper; ++it) {
				if (it->second.item == sit) {
					continue;
				}

				if (it->second.contains(box.CornerMin(), box.CornerMax())) {
					return true;
				}
			}

			return false;
		}
		
		void add(const TopoDS_Shape& s, const IfcUtil::IfcBaseEntity* product, const IfcUtil::IfcBaseInterface* cross_coplanar_style_instance = nullptr, const IfcUtil::IfcBaseInterface* cross_coplanar_material_instance = nullptr, const boost::optional<layer_projection>& cross_coplanar_layer_projection = boost::none) {
			if (!use_prefiltering_) {
				items_.insert(items_.end(), {product, s, cross_coplanar_style_instance, cross_coplanar_material_instance, cross_coplanar_layer_projection});
				return;
			}

			TopoDS_Compound C;
			BRep_Builder BB;
			BB.MakeCompound(C);

			gp_Pnt P;
			gp_Vec V;
			gp_Dir D;

			if (IfcGeom::util::is_manifold(s)) {
				size_t n_faces_included = 0, n_total = 0;
				{
					TopExp_Explorer exp(s, TopAbs_FACE);
					for (; exp.More(); exp.Next(), n_total++) {
						const auto& face = TopoDS::Face(exp.Current());
						if (BRep_Tool::Surface(face)->DynamicType() == STANDARD_TYPE(Geom_Plane)) {
							BRepGProp_Face prop(face);

							prop.Normal(0., 0., P, V);
							if (V.SquareMagnitude() > 1.e-9) {
								D = V;
								// keep only front-facing
								if (D.Dot(view_direction_.Direction()) > 1.e-3) {
									BB.Add(C, face);
									n_faces_included++;
								}
							}
						} else {
							BB.Add(C, face);
							n_faces_included++;
						}
					}
				}

				logger_.Notice("SER", 34, "Included " + std::to_string(n_faces_included) + " faces out of " + std::to_string(n_total) + " after prefiltering");

				auto it = items_.insert(items_.end(), { product, C, cross_coplanar_style_instance, cross_coplanar_material_instance, cross_coplanar_layer_projection });

				{
					TopExp_Explorer exp(C, TopAbs_FACE);
					for (; exp.More(); exp.Next()) {
						const auto& face = TopoDS::Face(exp.Current());
						if (BRep_Tool::Surface(face)->DynamicType() == STANDARD_TYPE(Geom_Plane)) {
							
							// find large faces orthogonal to view dir
							BRepGProp_Face prop(face);
							prop.Normal(0., 0., P, V);
							D = V;

							if (D.Dot(view_direction_.Direction()) > (1. - 1.e-3)) {
								if (IfcGeom::util::face_area(face) > 2.) {
									// arbitrary vertex, is ok because orthogonal to view dir
									TopExp_Explorer expv(face, TopAbs_VERTEX);
									if (expv.More()) {
										const auto& v = TopoDS::Vertex(expv.Current());
										auto pnt = BRep_Tool::Pnt(v);

										auto d = -(pnt.XYZ() - view_direction_.Location().XYZ()).Dot(view_direction_.Direction().XYZ());

										if (d > 1.e-5) {
											large_ortho_faces_.insert({ d, face_info(&std::get<1>(*it), face) });
										}
									}
								}
							}
						}
					}
				}
			} else {
				items_.insert(items_.end(), { product, s, cross_coplanar_style_instance, cross_coplanar_material_instance, cross_coplanar_layer_projection });
			}
		}

		// Cross-object "cross-coplanar" edge classification (issue #3742). Runs once, over
		// every item added to this drawing/storey so far (items_ is already complete by the
		// time build() is called -- see the comment on this call site). Only takes effect
		// when both use_edge_classification_ and use_cross_coplanar_classification_ are set;
		// otherwise a no-op, so this feature is fully inert unless explicitly enabled twice
		// over (matching its ConversionSettings description).
		void find_cross_coplanar_matches() {
			if (!use_edge_classification_ || !use_cross_coplanar_classification_) {
				return;
			}

			// Per-product accumulated edge coverage (v3: raw intervals, not whole edges -- see
			// cross_coplanar::edge_coverage_map_t) -- more than one neighbour can each
			// contribute coverage to the same product's edges, so this has to be fully
			// accumulated across the whole double loop below before any full/partial/none
			// split decision is made (the post-loop pass, mirroring how per-product edges were
			// already deferred to a post-loop pass pre-v3).
			BRep_Builder builder;
			std::map<const IfcUtil::IfcBaseEntity*, cross_coplanar::edge_coverage_map_t> per_product_coverage;
			auto get_coverage = [&](const IfcUtil::IfcBaseEntity* product) -> cross_coplanar::edge_coverage_map_t& {
				return per_product_coverage[product];
			};

			for (auto ii = items_.begin(); ii != items_.end(); ++ii) {
				for (auto jj = std::next(ii); jj != items_.end(); ++jj) {
					const auto* product_i = std::get<0>(*ii);
					const TopoDS_Shape& shape_i = std::get<1>(*ii);
					const auto* style_i = std::get<2>(*ii);
					const auto* material_i = std::get<3>(*ii);
					const auto* product_j = std::get<0>(*jj);
					const TopoDS_Shape& shape_j = std::get<1>(*jj);
					const auto* style_j = std::get<2>(*jj);
					const auto* material_j = std::get<3>(*jj);
					const auto& proj_i = std::get<4>(*ii);
					const auto& proj_j = std::get<4>(*jj);

					// v2: when either product is layered, the whole-product material/style is
					// only an approximation (see geometry_data::cross_coplanar_layer_projection)
					// -- defer the real decision to the per-face-pair resolution below instead
					// of rejecting the pair outright here. Otherwise (the common, non-layered
					// case) this is the same product-level gate as before: material takes
					// priority over style as the "same substance" identity -- if either side
					// resolved a material, both must be present and equal (style is not
					// consulted at all in that case, even if it happens to also match: two
					// products can share a rendering style while being genuinely different
					// materials). Style is only the comparison when *neither* side has a
					// resolved material.
					if (!proj_i && !proj_j) {
						if (material_i || material_j) {
							if (!material_i || !material_j || material_i != material_j) {
								continue;
							}
						} else if (!style_i || !style_j || style_i != style_j) {
							continue;
						}
					}

					Bnd_Box box_i, box_j;
					BRepBndLib::AddClose(shape_i, box_i);
					BRepBndLib::AddClose(shape_j, box_j);
					if (box_i.IsVoid() || box_j.IsVoid()) {
						continue;
					}
					box_i.Enlarge(cross_coplanar_tolerance_);
					if (box_i.IsOut(box_j)) {
						continue;
					}

					for (TopExp_Explorer fi(shape_i, TopAbs_FACE); fi.More(); fi.Next()) {
						const TopoDS_Face& face_i = TopoDS::Face(fi.Current());
						gp_Dir n_i;
						if (!cross_coplanar::face_normal(face_i, n_i)) {
							continue;
						}
						TopExp_Explorer vexp_i(face_i, TopAbs_VERTEX);
						if (!vexp_i.More()) {
							continue;
						}
						gp_Pnt sample_i = BRep_Tool::Pnt(TopoDS::Vertex(vexp_i.Current()));

						for (TopExp_Explorer fj(shape_j, TopAbs_FACE); fj.More(); fj.Next()) {
							const TopoDS_Face& face_j = TopoDS::Face(fj.Current());
							gp_Dir n_j;
							if (!cross_coplanar::face_normal(face_j, n_j)) {
								continue;
							}
							// Normal-parallel test (same tolerance convention as
							// classify_edge_from_faces()'s own near-exact-parallel check).
							if (std::abs(n_i.Dot(n_j)) <= 1.0 - 3.8e-5) {
								continue;
							}
							// Plane-coincidence: perpendicular distance from a point on
							// face_j to face_i's plane.
							TopExp_Explorer vexp_j(face_j, TopAbs_VERTEX);
							if (!vexp_j.More()) {
								continue;
							}
							gp_Pnt sample_j = BRep_Tool::Pnt(TopoDS::Vertex(vexp_j.Current()));
							double plane_dist = std::abs(gp_Vec(sample_i, sample_j).Dot(n_i));
							if (plane_dist >= cross_coplanar_tolerance_) {
								continue;
							}

							// Material/style resolution when either product is layered has moved
							// to a per-*sub-interval* check inside accumulate_edge_coverage()
							// below -- a face-level (centroid-based) verdict here would wrongly
							// gate the *whole* face pair on one sample, when a face that itself
							// spans more than one layer needs each overlapping sub-range judged
							// on its own actual material (see accumulate_edge_coverage()'s own
							// comment). The product-level gate above already handled the common,
							// non-layered case; nothing further to check here before proceeding.

							// Edge-to-edge coincidence, not face-area overlap: two adjacent,
							// non-overlapping faces (side-by-side slabs, a void's inner wire
							// against a plug's outer wire) share a boundary edge but have zero
							// area in common by construction -- BRepAlgoAPI_Common would (and
							// used to) wrongly reject exactly the cases this feature exists to
							// find. face_line_segs() walks all wires of a face (including inner
							// ones), so void/hole boundaries are covered too.
							auto segs_i = cross_coplanar::face_line_segs(face_i);
							auto segs_j = cross_coplanar::face_line_segs(face_j);
							cross_coplanar::accumulate_edge_coverage(
								face_i, segs_j, cross_coplanar_tolerance_,
								proj_i, material_i, style_i, proj_j, material_j, style_j,
								get_coverage(product_i));
							cross_coplanar::accumulate_edge_coverage(
								face_j, segs_i, cross_coplanar_tolerance_,
								proj_j, material_j, style_j, proj_i, material_i, style_i,
								get_coverage(product_j));
						}
					}
				}
			}

			for (auto& kv : per_product_coverage) {
				const IfcUtil::IfcBaseEntity* product = kv.first;
				cross_coplanar::edge_coverage_map_t& coverage = kv.second;

				// v3: split_edge_by_coverage() (inside replace_matched_edges()) now decides,
				// per edge, whether coverage is none (kept untouched), full (moved to
				// new_edges whole, same fast path as pre-v3), or partial (replaced by its
				// uncovered remainder here, with the covered sub-edge appended to new_edges) --
				// always against the *union* of every neighbour's contribution to that edge,
				// accumulated across the whole double loop above. Always applied regardless of
				// render_cross_coplanar_edges_ (that flag only controls whether new_edges is
				// *also* re-added below for visibility, not whether a duplicate -- whole or
				// partial -- is hidden from its original class).
				TopoDS_Compound new_edges;
				builder.MakeCompound(new_edges);
				// v3: any genuinely new (trimmed) sub-edges split_edge_by_coverage() constructs
				// are collected here -- they were never part of what this product's shape gave
				// to the HLR algorithm, so they have to be injected into items_ below before
				// build()'s algo->Add() loop runs, or HLRBRep_HLRToShape's VCompound()/
				// OutLineVCompound() (which correlate by original-input-edge identity) would
				// silently return nothing for them and they'd never reach the rendered output.
				TopoDS_Compound new_geometry;
				builder.MakeCompound(new_geometry);
				for (auto& entry : classified_items_) {
					if (std::get<0>(entry) != product) {
						continue;
					}
					std::get<2>(entry) = cross_coplanar::replace_matched_edges(
						std::get<2>(entry), coverage, cross_coplanar_tolerance_, builder, new_edges, new_geometry);
				}

				if (render_cross_coplanar_edges_) {
					add_classified_edges(product, cross_coplanar::class_name, new_edges);
				}

				if (TopExp_Explorer(new_geometry, TopAbs_EDGE).More()) {
					for (auto& item : items_) {
						if (std::get<0>(item) != product) {
							continue;
						}
						TopoDS_Compound merged;
						builder.MakeCompound(merged);
						builder.Add(merged, std::get<1>(item));
						builder.Add(merged, new_geometry);
						std::get<1>(item) = merged;
					}
				}
			}
		}

		std::list<std::tuple<const IfcUtil::IfcBaseEntity*, std::string, TopoDS_Shape>> build() {
			find_cross_coplanar_matches();

			size_t n_included = 0;
			for (auto it = items_.begin(); it != items_.end(); ++it) {
				if (!use_prefiltering_ || !is_obscured_(&std::get<1>(*it))) {
					hlr_writer vis(std::get<1>(*it));
					boost::apply_visitor(vis, engine_);
					n_included++;
				}
			}
			if (use_prefiltering_) {
				logger_.Notice("SER", 35, "Included " + std::to_string(n_included) + " elements out of " + std::to_string(items_.size()) + " after prefiltering");
			}

			hlr_calc vis(projector_);
			if (segment_projection_) {
				vis.set_product_shape(&items_);
			}
			vis.set_classified_shapes(&classified_items_);
			return boost::apply_visitor(vis, engine_);
		}
	};
}

typedef prefiltered_hlr hlr_t;

class SERIALIZERS_API SvgSerializer : public WriteOnlyGeometrySerializer {
public:
	typedef std::pair<std::string, std::vector<util::string_buffer> > path_object;
	typedef std::vector< boost::shared_ptr<util::string_buffer::float_item> > float_item_list;
	enum storey_height_display_types {
		SH_NONE, SH_FULL, SH_LEFT
	};
protected:
	stream_or_filename svg_file;
	double xmin, ymin, xmax, ymax;
	boost::optional<std::vector<section_data>> section_data_;
	boost::optional<std::vector<section_data>> deferred_section_data_;
	boost::optional<double> scale_, calculated_scale_, center_x_, center_y_;
	boost::optional<double> storey_height_line_length_;
	boost::optional<std::pair<double, double>> size_, offset_2d_;
	boost::optional<std::string> space_name_transform_;

#if OCC_VERSION_HEX >= 0x70300	
	boost::optional<Bnd_OBB> view_box_3d_;
#endif
	

	bool with_section_heights_from_storey_, print_space_names_, print_space_areas_;
	storey_height_display_types storey_height_display_;
	bool draw_door_arcs_, is_floor_plan_;
	bool auto_section_, auto_elevation_;
	bool use_namespace_, use_hlr_poly_, use_prefiltering_, segment_projection_, always_project_, polygonal_;
	bool emit_building_storeys_;
	bool no_css_;
	bool unify_inputs_;
	bool mirror_y_;
	bool mirror_x_;
	bool only_valid_ = false;

	int profile_threshold_;

	// SVG edge classification (issue #3668): see classify_edge_from_faces() in SvgSerializer.cpp.
	double svg_ridge_angle_min_deg_;
	double svg_valley_angle_min_deg_;
	bool svg_emit_flush_edges_;
	bool svg_use_edge_classification_;
	bool svg_render_crease_edges_;
	bool svg_render_sharp_edges_;

	// Cross-object "cross-coplanar" edge classification (issue #3742): see the cross-object
	// pass in prefiltered_hlr::build() in SvgSerializer.cpp.
	bool svg_use_cross_coplanar_classification_;
	bool svg_render_cross_coplanar_edges_;
	double svg_cross_coplanar_tolerance_;

	IfcParse::IfcFile* file;
	const IfcUtil::IfcBaseEntity* storey_;
	std::multimap<drawing_key, path_object, storey_sorter> paths;
	std::map<drawing_key, drawing_meta> drawing_metadata;
	std::map<const IfcUtil::IfcBaseEntity*, hlr_t> storey_hlr;

	float_item_list xcoords, ycoords, radii;
	size_t xcoords_begin, ycoords_begin, radii_begin;

	boost::optional<std::string> section_ref_, elevation_ref_, elevation_ref_guid_;
	
	std::list<geometry_data> element_buffer_;

	hlr_t* hlr;

	std::string namespace_prefix_;

	// Used for drawing the storey elevation heights
	// @todo maybe better to rely on a screen-space bounding box
	Bnd_Box bnd_;

	void draw_hlr(const gp_Pln& pln, const drawing_key& drawing_name);

	subtract_before_project subtraction_settings_;

public:
	SvgSerializer(const stream_or_filename& out_filename, const ifcopenshell::geometry::Settings& geometry_settings, const ifcopenshell::geometry::SerializerSettings& settings, Logger* logger = nullptr)
		: WriteOnlyGeometrySerializer(geometry_settings, settings, logger_or_root(logger))
		, svg_file(out_filename)
		, xmin(+std::numeric_limits<double>::infinity())
		, ymin(+std::numeric_limits<double>::infinity())
		, xmax(-std::numeric_limits<double>::infinity())
		, ymax(-std::numeric_limits<double>::infinity())
		, with_section_heights_from_storey_(false)
		, print_space_names_(false)
		, print_space_areas_(false)
		, storey_height_display_(SH_NONE)
		, draw_door_arcs_(false)
		, is_floor_plan_(true)
		, auto_section_(false)
		, auto_elevation_(false)
		, use_namespace_(false)
		, use_hlr_poly_(false)
		, use_prefiltering_(false)
		, segment_projection_(false)
		, always_project_(false)
		, polygonal_(false)
		, emit_building_storeys_(true)
		, no_css_(false)
		, mirror_y_(false)
		, mirror_x_(false)
		, unify_inputs_(false)
		, profile_threshold_(-1)
		, svg_ridge_angle_min_deg_(45.)
		, svg_valley_angle_min_deg_(12.)
		, svg_emit_flush_edges_(false)
		, svg_use_edge_classification_(false)
		, svg_render_crease_edges_(true)
		, svg_render_sharp_edges_(true)
		, svg_use_cross_coplanar_classification_(false)
		, svg_render_cross_coplanar_edges_(false)
		, svg_cross_coplanar_tolerance_(1.e-4)
		, file(0)
		, storey_(0)
		, xcoords_begin(0)
		, ycoords_begin(0)
		, radii_begin(0)
		, hlr(nullptr)
		, namespace_prefix_("data-")
		, subtraction_settings_(ON_SLABS_AT_FLOORPLANS)
	{
		// ready() only reads geometry_settings() (already valid at this point, since the base
		// WriteOnlyGeometrySerializer initializer above has run) and has no other side effects,
		// so it's safe to call here. This is needed because ready() is otherwise only invoked
		// explicitly by IfcConvert.cpp's CLI driver -- callers that construct this serializer
		// directly via the Python bindings (e.g. Bonsai's drawing generation, which never calls
		// a ready()-equivalent because it isn't exposed via SWIG) would otherwise silently keep
		// every settings::Svg* member at its hardcoded constructor default forever, regardless
		// of what ifcopenshell.geom.settings().set(...) was actually configured to.
		ready();
	}
    void addXCoordinate(const boost::shared_ptr<util::string_buffer::float_item>& fi) { xcoords.push_back(fi); }
    void addYCoordinate(const boost::shared_ptr<util::string_buffer::float_item>& fi) { ycoords.push_back(fi); }
    void addSizeComponent(const boost::shared_ptr<util::string_buffer::float_item>& fi) { radii.push_back(fi); }
    void growBoundingBox(double x, double y) { if (x < xmin) xmin = x; if (x > xmax) xmax = x; if (y < ymin) ymin = y; if (y > ymax) ymax = y; }
    void writeHeader();
	void doWriteHeader();
    bool ready();
    void write(const IfcGeom::TriangulationElement* /*o*/) {}
    void write(const IfcGeom::BRepElement* o);
    void write(path_object& p, const TopoDS_Shape& wire, boost::optional<std::vector<double>> dash_array=boost::none, boost::optional<std::string> css_class=boost::none);
	void write(const geometry_data& data);
    path_object& start_path(const gp_Pln& p, const IfcUtil::IfcBaseEntity* storey, const std::string& id);
	path_object& start_path(const gp_Pln& p, const std::string& drawing_name, const std::string& id);
	bool isTesselated() const { return false; }
    void finalize();
    void setUnitNameAndMagnitude(const std::string& /*name*/, float /*magnitude*/) {}
	void setFile(IfcParse::IfcFile* f);
    void setBoundingRectangle(double width, double height);
	void setSectionHeight(double h, const IfcUtil::IfcBaseEntity* storey = 0);
	void setSectionHeightsFromStoreys(double offset=1.2);
	void setPrintSpaceNames(bool b) { print_space_names_ = b; }
	void setPrintSpaceAreas(bool b) { print_space_areas_ = b; }
	void setDrawStoreyHeights(storey_height_display_types sh) { storey_height_display_ = sh; }
	void setDrawDoorArcs(bool b) { draw_door_arcs_ = b; }
	void setStoreyHeightLineLength(double d) { storey_height_line_length_ = d; }
	void setSpaceNameTransform(const std::string& v) { space_name_transform_ = v; }
	void addTextAnnotations(const drawing_key& k);

	std::array<std::array<double, 3>, 3> resize();
	void resetScale();

	void setSectionRef(const boost::optional<std::string>& s) { 
		section_ref_ = s; 
	}

	void setElevationRef(const boost::optional<std::string>& s) {
		elevation_ref_ = s; 
		elevation_ref_guid_ = boost::none;
	}

	void setElevationRefGuid(const boost::optional<std::string>& s) {
		elevation_ref_ = boost::none;
		elevation_ref_guid_ = s;
	}

	void setAutoSection(bool b) {
		auto_section_ = b;
	}

	void setAutoElevation(bool b) {
		auto_elevation_ = b;
	}

	void setUseNamespace(bool b) {
		use_namespace_ = b;
		namespace_prefix_ = use_namespace_ ? "ifc:" : "data-";
	}

	void setUseHlrPoly(bool b) {
		use_hlr_poly_ = b;
	}

	void setUsePrefiltering(bool b) {
		use_prefiltering_ = b;
	}

	bool getUsePrefiltering() const {
		return use_prefiltering_;
	}

	void setSegmentProjection(bool b) {
		segment_projection_ = b;
	}

	bool getSegmentProjection() const {
		return segment_projection_;
	}

	void setPolygonal(bool b) {
		polygonal_ = b;
	}

	void setAlwaysProject(bool b) {
		always_project_ = b;
	}

	void setWithoutStoreys(bool b) {
		emit_building_storeys_ = !b;
	}

	void setNoCSS(bool b) {
		no_css_ = b;
	}

	void setUnifyInputs(bool b) {
		unify_inputs_ = b;
	}

	bool getUnifyInputs() const {
		return unify_inputs_;
	}

	void setOnlyValid(bool b) {
		only_valid_ = b;
	}

	bool getOnlyValid(bool b) const {
		return only_valid_;
	}

	void setScale(double s) { scale_ = s; }
	void setDrawingCenter(double x, double y) {
		center_x_ = x; center_y_ = y;
	}
    std::string nameElement(const IfcUtil::IfcBaseEntity* storey, const IfcGeom::Element* elem);
	std::string nameElement(const IfcUtil::IfcBaseEntity* elem);
	std::string idElement(const IfcUtil::IfcBaseEntity* elem);
	std::string object_id(const IfcUtil::IfcBaseEntity* storey, const IfcGeom::Element* o) {
		if (storey) {
			return idElement(storey) + "-" + GeometrySerializer::object_id(o);
		} else {
			return GeometrySerializer::object_id(o);
		}
	}

	void addDrawing(const gp_Pnt& pos, const gp_Dir& dir, const gp_Dir& ref, const std::string& name, bool include_projection) {
		deferred_section_data_.emplace();
		deferred_section_data_->push_back(vertical_section{ gp_Pln(gp_Ax3(pos, dir, ref)), name, include_projection });
	}

	void setSubtractionSettings(subtract_before_project sbp) {
		subtraction_settings_ = sbp;
	}

	subtract_before_project getSubtractionSettings() const {
		return subtraction_settings_;
	}

	void setProfileThreshold(int i) {
		profile_threshold_ = i;
	}

	int getProfileThreshold() const {
		return profile_threshold_;
	}

	void setMirrorY(bool b) {
		mirror_y_ = b;
	}

	bool getMirrorY() const {
		return mirror_y_;
	}

	void setMirrorX(bool b) {
		mirror_x_ = b;
	}

	bool getMirrorX() const {
		return mirror_x_;
	}

protected:
	std::string writeMetadata(const drawing_meta& m);
};

#endif
#endif
