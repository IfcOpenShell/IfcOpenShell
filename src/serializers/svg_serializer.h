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

#include "../ifcgeom/geometry_serializer.h"
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
#include <BRepGProp_Face.hxx>

#if OCC_VERSION_HEX >= 0x70300
#include <Bnd_OBB.hxx>
#endif

#include <sstream>
#include <string>
#include <limits>
#include <array>
#include <tuple>

typedef std::pair<express::base, std::string> drawing_key;

struct storey_sorter {
	bool operator()(const drawing_key& ad, const drawing_key& bd) const {
		if (!ad.first && bd.first) {
			return false;
		} else if (!bd.first && ad.first) {
			return true;
		} else if (!ad.first && !bd.first) {
			return std::less<std::string>()(ad.second, bd.second);
		}

		auto a = ad.first;
		auto b = bd.first;

		const bool a_is_storey = a.declaration().is("IfcBuildingStorey");
		const bool b_is_storey = b.declaration().is("IfcBuildingStorey");
		if (a_is_storey && b_is_storey) {
			std::optional<double> a_elev, b_elev;
			try {
				a_elev = static_cast<double>(a.as<express::entity>().get("Elevation"));
				b_elev = static_cast<double>(b.as<express::entity>().get("Elevation"));
			} catch (...) {};
			if (a_elev && b_elev) {
				if (std::equal_to<double>()(*a_elev, *b_elev)) {
					return std::less<unsigned int>()(a.id(), b.id());
				} else {
					return std::less<double>()(*a_elev, *b_elev);
				}
			}

			std::optional<std::string> a_name, b_name;
			try {
				a_name = static_cast<std::string>(a.as<express::entity>().get("Name"));
				b_name = static_cast<std::string>(b.as<express::entity>().get("Name"));
			} catch (...) {};
			if (a_name && b_name) {
				if (std::equal_to<std::string>()(*a_name, *b_name)) {
					return std::less<unsigned int>()(a.id(), b.id());
				} else {
					return std::less<std::string>()(*a_name, *b_name);
				}
			}
		}
		return std::less<express::base>()(a, b);
	}
};

struct horizontal_plan {
	express::base storey;
	double elevation, offset, next_elevation;
};

struct horizontal_plan_at_element {};

struct vertical_section {
	gp_Pln plane;
	std::string name;
	bool with_projection;
	std::optional<double> scale;
	std::optional<std::pair<double, double>> size;
};

typedef boost::variant<horizontal_plan, horizontal_plan_at_element, vertical_section> section_data;

struct geometry_data {
	TopoDS_Shape compound_local;
	std::vector<std::optional<std::vector<double>>> dash_arrays;
	gp_Trsf trsf;
	express::base product;
	express::base storey;
	double storey_elevation;
	std::string ifc_name, svg_name;
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

	class hlr_calc {
	private:
		const HLRAlgo_Projector& projector_;
		const std::list<std::pair<express::base, TopoDS_Shape>>* product_shapes_ = nullptr;
		// SVG edge classification (issue #3668): per-(product, class) edge-only sub-shapes,
		// classified pre-HLR on the original (real-face) topology. Empty class string means
		// "unclassified" (used for the two fallback cases below).
		const std::list<std::tuple<express::base, std::string, TopoDS_Shape>>* classified_shapes_ = nullptr;

	public:
		typedef std::list<std::tuple<express::base, std::string, TopoDS_Shape>> result_type;

		hlr_calc(const HLRAlgo_Projector& projector) : projector_(projector)
		{}

		void set_product_shape(const std::list<std::pair<express::base, TopoDS_Shape>>* product_shapes) {
			product_shapes_ = product_shapes;
		}

		void set_classified_shapes(const std::list<std::tuple<express::base, std::string, TopoDS_Shape>>* classified_shapes) {
			classified_shapes_ = classified_shapes;
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
					r.push_back({ p.first, std::string(), occt_join(hlr_shapes.OutLineVCompound(p.second), hlr_shapes.VCompound(p.second)) });
				}
			} else {
				r.push_back({ express::base{}, std::string(), occt_join(hlr_shapes.OutLineVCompound(), hlr_shapes.VCompound()) });
			}
			return r;
		}

		result_type operator()(boost::blank&) const {
			throw std::runtime_error("");
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
				is_convex = exp.More() && ifcopenshell::geom::util::is_convex(TopoDS::Wire(exp.Current()), 1.e-5) && ([&exp]() {exp.Next(); return true; })() && !exp.More();

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

		std::multimap<double, face_info> large_ortho_faces_;
		std::list<std::pair<express::base, TopoDS_Shape>> items_;
		// SVG edge classification (issue #3668): see add_classified_edges().
		std::list<std::tuple<express::base, std::string, TopoDS_Shape>> classified_items_;

		ifcopenshell::logger& logger_;

	public:

		prefiltered_hlr(ifcopenshell::logger& logger, bool use_prefiltering, bool use_hlr_poly, bool segment_projection, const gp_Pln& view_direction)
			: use_prefiltering_(use_prefiltering)
			, use_hlr_poly_(use_hlr_poly)
			, segment_projection_(segment_projection)
			// @nb negative z in accordance with occt projector convention (and opengl)
			, view_direction_(view_direction.Axis())
			, logger_(logger)
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
		// original (pre-HLR, real-face) geometry under a given class name. The full shape must
		// still be added via add() as usual for correct occlusion.
		void add_classified_edges(express::base product, const std::string& cls, const TopoDS_Shape& edges) {
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

		void add(const TopoDS_Shape& s, express::base product) {
			if (!use_prefiltering_) {
				items_.insert(items_.end(), {product, s});
				return;
			}

			TopoDS_Compound C;
			BRep_Builder BB;
			BB.MakeCompound(C);

			gp_Pnt P;
			gp_Vec V;
			gp_Dir D;

			if (ifcopenshell::geom::util::is_manifold(s)) {
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

				logger_.notice("SER", 34, "Included " + std::to_string(n_faces_included) + " faces out of " + std::to_string(n_total) + " after prefiltering");

				auto it = items_.insert(items_.end(), { product, C });

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
								if (ifcopenshell::geom::util::face_area(face) > 2.) {
									// arbitrary vertex, is ok because orthogonal to view dir
									TopExp_Explorer expv(face, TopAbs_VERTEX);
									if (expv.More()) {
										const auto& v = TopoDS::Vertex(expv.Current());
										auto pnt = BRep_Tool::Pnt(v);

										auto d = -(pnt.XYZ() - view_direction_.Location().XYZ()).Dot(view_direction_.Direction().XYZ());

										if (d > 1.e-5) {
											large_ortho_faces_.insert({ d, face_info(&it->second, face) });
										}
									}
								}
							}
						}
					}
				}
			} else {
				items_.insert(items_.end(), { product, s });
			}
		}

		std::list<std::tuple<express::base, std::string, TopoDS_Shape>> build() {
			size_t n_included = 0;
			for (auto it = items_.begin(); it != items_.end(); ++it) {
				if (!use_prefiltering_ || !is_obscured_(&it->second)) {
					hlr_writer vis(it->second);
					boost::apply_visitor(vis, engine_);
					n_included++;
				}
			}
			if (use_prefiltering_) {
				logger_.notice("SER", 35, "Included " + std::to_string(n_included) + " elements out of " + std::to_string(items_.size()) + " after prefiltering");
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

typedef prefiltered_hlr hlr_engine;

class SERIALIZERS_API svg_serializer : public ifcopenshell::geom::write_only_geometry_serializer {
public:
	typedef std::pair<std::string, std::vector<util::string_buffer> > path_object;
	typedef std::vector< std::shared_ptr<util::string_buffer::float_item> > float_item_list;
	enum storey_height_display_types {
		SH_NONE, SH_FULL, SH_LEFT
	};
protected:
	stream_or_filename svg_file;
	double xmin, ymin, xmax, ymax;
	std::optional<std::vector<section_data>> section_data_;
	std::optional<std::vector<section_data>> deferred_section_data_;
	std::optional<double> scale_, calculated_scale_, center_x_, center_y_;
	std::optional<double> storey_height_line_length_;
	std::optional<std::pair<double, double>> size_, offset_2d_;
	std::optional<std::string> space_name_transform_;

#if OCC_VERSION_HEX >= 0x70300
	std::optional<Bnd_OBB> view_box_3d_;
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

	// SVG edge classification (issue #3668): see classify_edge_from_faces() in svg_serializer.cpp.
	double svg_ridge_angle_min_deg_;
	double svg_valley_angle_min_deg_;
	bool svg_emit_flush_edges_;
	bool svg_use_edge_classification_;
	bool svg_render_crease_edges_;
	bool svg_render_sharp_edges_;

	ifcopenshell::file* file;
	express::base storey_;
	std::multimap<drawing_key, path_object, storey_sorter> paths;
	std::map<drawing_key, drawing_meta> drawing_metadata;
    std::map<express::base, hlr_engine> storey_hlr;

	float_item_list xcoords, ycoords, radii;
	size_t xcoords_begin, ycoords_begin, radii_begin;

	std::optional<std::string> section_ref_, elevation_ref_, elevation_ref_guid_;

	std::list<geometry_data> element_buffer_;

	hlr_engine* hlr;

	std::string namespace_prefix_;

	// Used for drawing the storey elevation heights
	// @todo maybe better to rely on a screen-space bounding box
	Bnd_Box bnd_;

	void draw_hlr(const gp_Pln& pln, const drawing_key& drawing_name);
	void apply_settings();

	subtract_before_project subtraction_settings_;

public:
	svg_serializer(const stream_or_filename& out_filename, const ifcopenshell::geom::settings& settings, ifcopenshell::logger* logger = nullptr)
		: ifcopenshell::geom::write_only_geometry_serializer(settings, logger)
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
		, unify_inputs_(false)
		, mirror_y_(false)
		, mirror_x_(false)
		, profile_threshold_(-1)
		, svg_ridge_angle_min_deg_(45.)
		, svg_valley_angle_min_deg_(12.)
		, svg_emit_flush_edges_(false)
		, svg_use_edge_classification_(false)
		, svg_render_crease_edges_(true)
		, svg_render_sharp_edges_(true)
		, file(0)
		, xcoords_begin(0)
		, ycoords_begin(0)
		, radii_begin(0)
		, hlr(nullptr)
		, namespace_prefix_("data-")
		, subtraction_settings_(ON_SLABS_AT_FLOORPLANS)
	{
		apply_settings();
	}
    void addXCoordinate(const std::shared_ptr<util::string_buffer::float_item>& fi) { xcoords.push_back(fi); }
    void addYCoordinate(const std::shared_ptr<util::string_buffer::float_item>& fi) { ycoords.push_back(fi); }
    void addSizeComponent(const std::shared_ptr<util::string_buffer::float_item>& fi) { radii.push_back(fi); }
    void growBoundingBox(double x, double y) { if (x < xmin) xmin = x; if (x > xmax) xmax = x; if (y < ymin) ymin = y; if (y > ymax) ymax = y; }
    void writeHeader();
	void doWriteHeader();
    bool ready();
    void write(const ifcopenshell::geom::triangulation_element* /*o*/) {}
    void write(const ifcopenshell::geom::native_element* o);
    void write(path_object& p, const TopoDS_Shape& wire, std::optional<std::vector<double>> dash_array=std::nullopt, std::optional<std::string> css_class=std::nullopt);
	void write(const geometry_data& data);
    path_object& start_path(const gp_Pln& p, const express::base& storey, const std::string& id);
	path_object& start_path(const gp_Pln& p, const std::string& drawing_name, const std::string& id);
	bool isTesselated() const { return false; }
    void finalize();
    void setUnitNameAndMagnitude(const std::string& /*name*/, float /*magnitude*/) {}
	void setFile(ifcopenshell::file& f);
    void setBoundingRectangle(double width, double height);
    void setSectionHeight(double h, express::base storey = express::base());
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

	void setSectionRef(const std::optional<std::string>& s) {
		section_ref_ = s;
	}

	void setElevationRef(const std::optional<std::string>& s) {
		elevation_ref_ = s;
		elevation_ref_guid_ = std::nullopt;
	}

	void setElevationRefGuid(const std::optional<std::string>& s) {
		elevation_ref_ = std::nullopt;
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

	bool getOnlyValid(bool) const {
		return only_valid_;
	}

	void setScale(double s) { scale_ = s; }
	void setDrawingCenter(double x, double y) {
		center_x_ = x; center_y_ = y;
	}
    std::string nameElement(express::base storey, const ifcopenshell::geom::element* elem);
	std::string nameElement(express::base elem);
	std::string idElement(express::base elem);
    std::string object_id(express::base storey, const ifcopenshell::geom::element* o) {
		if (storey) {
			return idElement(storey) + "-" + ifcopenshell::geom::geometry_serializer::object_id(o);
		} else {
			return ifcopenshell::geom::geometry_serializer::object_id(o);
		}
	}

	void addDrawing(const gp_Pnt& pos, const gp_Dir& dir, const gp_Dir& ref, const std::string& name, bool include_projection) {
		deferred_section_data_.emplace();
		deferred_section_data_->push_back(vertical_section{ gp_Pln(gp_Ax3(pos, dir, ref)), name, include_projection, std::nullopt, std::nullopt });
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
