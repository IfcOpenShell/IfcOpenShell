// This file was generated with the assistance of an AI coding tool.

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

#ifndef IFCOPENSHELL_OPENCASCADE_UB_TREE_H
#define IFCOPENSHELL_OPENCASCADE_UB_TREE_H

#include "../../../ifcparse/file.h"

#include "../../../ifcgeom/element.h"
#include "../../../ifcgeom/iterator.h"
#include "../../../ifcgeom/tree.h"
#include "../../kernel_registry.h"
#include "../../../ifcparse/exception.h"
#include "opencascade_conversion_result.h"
#include "base_utils.h"

#include <NCollection_UBTree.hxx>
#include <BRepBndLib.hxx>
#include <Bnd_Box.hxx>
#include <BRep_Builder.hxx>
#include <BRepAlgoAPI_Common.hxx>
#include <BRepAlgoAPI_Cut.hxx>
#include <BRepExtrema_DistShapeShape.hxx>
#include <BRepClass3d_SolidClassifier.hxx>

#include <Standard_Macro.hxx>
#include <Standard_Version.hxx>
#include <TopoDS_Shape.hxx>
#include <Standard_Integer.hxx>
#include <TopTools_ShapeMapHasher.hxx>
#include <NCollection_DataMap.hxx>

#include <BRepBuilderAPI_MakeEdge.hxx>
#include <BRepExtrema_ExtPF.hxx>
#include <TopoDS_Face.hxx>
#include <TopoDS.hxx>

#include <algorithm>
#include <array>
#include <cmath>
#include <limits>
#include <map>
#include <type_traits>
#include <utility>
#include <vector>

namespace ifcopenshell::geom {
	namespace {

		// Approximates the distance `other` protrudes into `volume` by finding the
		// max face-vertex distance for every face, and taking the minimal value of
		// those. Note that this uses the internal `BRepExtrema_ExtPF` which only
		// returns solutions whose when the vertex projected onto the face is contained
		// within the face boundaries. In case of concave `volume` this is desirable.

		double max_distance_inside(const TopoDS_Shape& volume, const TopoDS_Shape& other) {
			TopExp_Explorer exp_v(volume.Reversed(), TopAbs_FACE);

			double min_face_vertex_distance = std::numeric_limits<double>::infinity();

			for (; exp_v.More(); exp_v.Next()) {
				const TopoDS_Face& f = TopoDS::Face(exp_v.Current());

				BRepExtrema_ExtPF epf;
				epf.Initialize(f, Extrema_ExtFlag_MIN);

				double face_vertex_distance = 0.;

				TopExp_Explorer exp_o(other, TopAbs_VERTEX);
				for (; exp_o.More(); exp_o.Next()) {
					const TopoDS_Vertex& v = TopoDS::Vertex(exp_o.Current());
					epf.Perform(v, f);
					if (epf.IsDone() && epf.NbExt() == 1) {
						double d = epf.SquareDistance(1);
						if (d > face_vertex_distance) {
							face_vertex_distance = d;
						}
					}
				}

				if (face_vertex_distance < min_face_vertex_distance) {
					min_face_vertex_distance = face_vertex_distance;
				}
			}

			if (min_face_vertex_distance == std::numeric_limits<double>::infinity()) {
				return -1.;
			} else {
				return std::sqrt(min_face_vertex_distance);
			}
		}
	}

	namespace impl {

		inline gp_Pnt make_point(const ifcopenshell::geom::tree_point& point) {
			return gp_Pnt(point[0], point[1], point[2]);
		}

		inline Bnd_Box make_box(const ifcopenshell::geom::tree_box& bounds) {
			Bnd_Box box;
			box.Add(make_point(bounds[0]));
			box.Add(make_point(bounds[1]));
			return box;
		}

		// Selection is keyed by the product instances the elements were added
		// with, so anything else can not be looked up.
		inline void check_product(const express::base& instance) {
			if (!instance || !instance.declaration().is("IfcProduct")) {
				throw ifcopenshell::exception("Instance should be an IfcProduct");
			}
		}

		template <typename T>
		std::vector<express::base> to_base_vector(const std::vector<T>& ts) {
			std::vector<express::base> result;
			result.reserve(ts.size());
			for (const auto& t : ts) {
				result.push_back(t);
			}
			return result;
		}

		// Selection implementation based on an NCollection_UBTree over bounding
		// boxes. The T-typed members are the interface consumed by the geometry
		// kernel, which instantiates this template with integer indices. When
		// instantiated with a type derived from express::base, the T-typed
		// select() and select_box() members also implement the corresponding
		// virtual methods of the abstract tree interface.
		template <typename T>
		class ub_tree : public ifcopenshell::geom::tree {
		public:
			std::string backend_id() const override {
				return "opencascade.brep";
			}

			// The iterator overload of the base class is not hidden by the members below.
			using ifcopenshell::geom::tree::add_file;

			void add_file(ifcopenshell::file& file, const ifcopenshell::geom::settings& settings) override {
				if constexpr (std::is_base_of_v<express::base, T>) {
					auto settings_ = settings;
					settings_.get<ifcopenshell::geom::settings::IteratorOutput>().value = ifcopenshell::geom::settings::NATIVE;
					settings_.get<ifcopenshell::geom::settings::UseWorldCoords>().value = true;
					settings_.get<ifcopenshell::geom::settings::ReorientShells>().value = true;

					ifcopenshell::geom::iterator iterator(ifcopenshell::geom::kernels::construct(&file, "opencascade", settings_), settings_, &file, {}, 1);
					add_file(iterator);
				} else {
					ifcopenshell::geom::tree::add_file(file, settings);
				}
			}

			void add_element(ifcopenshell::geom::element* element) override {
				if constexpr (std::is_base_of_v<express::base, T>) {
					auto* brep = dynamic_cast<ifcopenshell::geom::native_element*>(element);
					if (!brep) {
						throw ifcopenshell::exception("Tree backend '" + backend_id() + "' requires native brep elements");
					}

					TopoDS_Shape compound = transformed_compound(brep);
					add(brep->product(), compound);

					auto git = brep->geometry().begin();

					if (enable_face_styles_) {
						TopoDS_Iterator it(compound);
						for (; it.More(); it.Next(), ++git) {
							// Assumption is that the number of styles is small, so the linear lookup time is not significant.
							auto sit = std::find(styles_.begin(), styles_.end(), git->style_ptr());
							size_t index;
							if (sit == styles_.end()) {
								index = styles_.size();
								styles_.push_back(git->style_ptr());
							} else {
								index = std::distance(styles_.begin(), sit);
							}

							TopExp_Explorer exp(it.Value(), TopAbs_FACE);
							for (; exp.More(); exp.Next()) {
								face_styles_.Bind(exp.Current(), (int) index);
							}
						}
					}
				} else {
					ifcopenshell::geom::tree::add_element(element);
				}
			}

			std::vector<express::base> select_box(const ifcopenshell::geom::tree_point& point) const override {
				if constexpr (std::is_base_of_v<express::base, T>) {
					return to_base_vector(select_box(make_point(point)));
				} else {
					return ifcopenshell::geom::tree::select_box(point);
				}
			}

			std::vector<express::base> select_box(const ifcopenshell::geom::tree_box& bounds, bool completely_within = false) const override {
				if constexpr (std::is_base_of_v<express::base, T>) {
					return to_base_vector(select_box(make_box(bounds), completely_within));
				} else {
					return ifcopenshell::geom::tree::select_box(bounds, completely_within);
				}
			}

			std::vector<express::base> select(const ifcopenshell::geom::element* element, bool completely_within = false, double extend = -1.e-5) const override {
				if constexpr (std::is_base_of_v<express::base, T>) {
					auto* brep = dynamic_cast<const ifcopenshell::geom::native_element*>(element);
					if (!brep) {
						throw ifcopenshell::exception("Tree backend '" + backend_id() + "' requires native brep elements");
					}
					return to_base_vector(select(transformed_compound(brep), completely_within, extend));
				} else {
					return ifcopenshell::geom::tree::select(element, completely_within, extend);
				}
			}

			std::vector<express::base> select(const ifcopenshell::geom::tree_point& point, double extend = 0.0) const override {
				if constexpr (std::is_base_of_v<express::base, T>) {
					return to_base_vector(select(make_point(point), extend));
				} else {
					return ifcopenshell::geom::tree::select(point, extend);
				}
			}

			std::vector<ifcopenshell::geom::ray_intersection_result> select_ray(const ifcopenshell::geom::tree_point& origin, const ifcopenshell::geom::tree_point& direction, double length = 1000.) const override {
				if constexpr (std::is_base_of_v<express::base, T>) {
					gp_Pnt p0 = make_point(origin);
					gp_Dir d(direction[0], direction[1], direction[2]);

					gp_Pnt p1 = p0.XYZ() + d.XYZ() * length;
					auto E = BRepBuilderAPI_MakeEdge(p0, p1).Edge();
					Bnd_Box bb;
					bb.Add(p0);
					bb.Add(p1);
					auto candidates = select_box(bb);

					std::multimap<double, ray_intersection_result> ordered;

					for (auto& c : candidates) {
						BRepExtrema_DistShapeShape dss(E, shapes_.find(c)->second);
						for (int i = 1; i <= dss.NbSolution(); ++i) {
							if (dss.SupportTypeShape1(i) != BRepExtrema_IsOnEdge) {
								// @todo set to 0, is it on the first verteX?
								continue;
							}
							if (dss.SupportTypeShape2(i) != BRepExtrema_IsInFace) {
								continue;
							}
							double u, v, w;
							dss.ParOnEdgeS1(i, u);
							auto face = TopoDS::Face(dss.SupportOnShape2(i));
							int sidx = -1;
							if (enable_face_styles_) {
								sidx = face_styles_.Find(face);
							}
							dss.ParOnFaceS2(i, v, w);
							BRepGProp_Face prop(face);
							gp_Pnt P;
							gp_Vec V;
							prop.Normal(v, w, P, V);
							ordered.insert({ u,	{ u, sidx, c.template as<express::entity>(),
								{P.X(), P.Y(), P.Z()},
								{V.X(), V.Y(), V.Z()},
								d.XYZ().Dot(p0.XYZ() - P.XYZ()),
								V.Dot(d)
							} });
						}
					}

					std::vector<ray_intersection_result> result;
					for (auto& p : ordered) {
						result.push_back(p.second);
					}

					return result;
				} else {
					return ifcopenshell::geom::tree::select_ray(origin, direction, length);
				}
			}

			const std::vector<double>& distances() const override {
				return distances_;
			}

			const std::vector<double>& protrusion_distances() const override {
				return protrusion_distances_;
			}

			bool enable_face_styles() const override {
				return enable_face_styles_;
			}

			void enable_face_styles(bool enable) override {
				enable_face_styles_ = enable;
			}

			const std::vector<ifcopenshell::geom::taxonomy::style::ptr>& styles() const override {
				return styles_;
			}

			void add(const T& t, const Bnd_Box& b) {
				tree_.Add(t, b);
			}

			void add(const T& t, const TopoDS_Shape& s) {
				Bnd_Box b;
				BRepBndLib::AddClose(s, b);
				add(t, b);
				shapes_[t] = s;
			}

			std::vector<T> select_box(const T& t, bool completely_within = false, double extend=-1.e-5) const {
				if constexpr (std::is_base_of_v<express::base, T>) {
					check_product(t);
				}

				typename shape_map::const_iterator it = shapes_.find(t);
				if (it == shapes_.end()) {
					return std::vector<T>();
				}

				Bnd_Box b;
				BRepBndLib::AddClose(it->second, b);

				// Gap is assumed to be positive throughout the codebase,
				// but at least for IsOut() in the selector a negative
				// Gap should work as well.
				b.SetGap(b.GetGap() + extend);

				return select_box(b, completely_within);
			}

			std::vector<T> select_box(const gp_Pnt& p, double extend=0.0) const {
				Bnd_Box b;
				b.Add(p);
				b.SetGap(b.GetGap() + extend);
				return select_box(b);
			}

			std::vector<T> select_box(const Bnd_Box& b, bool completely_within = false) const {
				selector s(b);
				tree_.Select(s);
				if (completely_within) {
					std::vector<T> ts = s.results();
					std::vector<T> ts_filtered;
					ts_filtered.reserve(ts.size());
					typename std::vector<T>::const_iterator it = ts.begin();
					for (; it != ts.end(); ++it) {
						const TopoDS_Shape& shp = shapes_.find(*it)->second;
						Bnd_Box B;
						BRepBndLib::AddClose(shp, B);

						// BndBox::CornerMin() /-Max() introduced in OCCT 6.8
						double x1, y1, z1, x2, y2, z2;
						b.Get(x1, y1, z1, x2, y2, z2);
						double gap = B.GetGap();
						gp_Pnt p1(x1 - gap, y1 - gap, z1 - gap);
						gp_Pnt p2(x2 + gap, y2 + gap, z2 + gap);

						if (!b.IsOut(p1) && !b.IsOut(p2)) {
							ts_filtered.push_back(*it);
						}
					}
					return ts_filtered;
				} else {
					return s.results();
				}
			}

			std::vector<T> select(const T& t, bool completely_within = false, double extend = 0.0) const {
				if constexpr (std::is_base_of_v<express::base, T>) {
					check_product(t);
				}

				distances_.clear();
				protrusion_distances_.clear();

				std::vector<T> ts = select_box(t, completely_within, extend);
				if (ts.empty()) {
					return ts;
				}

				const TopoDS_Shape& A = shapes_.find(t)->second;

				std::vector<T> ts_filtered;
				ts_filtered.reserve(ts.size());

				typename std::vector<T>::const_iterator it = ts.begin();
				for (it = ts.begin(); it != ts.end(); ++it) {
					const TopoDS_Shape& B = shapes_.find(*it)->second;

					if (test(A, B, completely_within, extend)) {
						ts_filtered.push_back(*it);
					}
				}

				return ts_filtered;
			}

			std::vector<T> select(const TopoDS_Shape& s, bool completely_within = false, double extend = -1.e-5) const {
				distances_.clear();
				protrusion_distances_.clear();

				Bnd_Box bb;
				BRepBndLib::AddClose(s, bb);
				bb.SetGap(bb.GetGap() + extend);

				std::vector<T> ts = select_box(bb, completely_within);

				if (ts.empty()) {
					return ts;
				}

				std::vector<T> ts_filtered;
				ts_filtered.reserve(ts.size());

				typename std::vector<T>::const_iterator it = ts.begin();
				for (it = ts.begin(); it != ts.end(); ++it) {
					const TopoDS_Shape& B = shapes_.find(*it)->second;

					if (test(s, B, completely_within, extend)) {
						ts_filtered.push_back(*it);
					}
				}

				return ts_filtered;
			}

			std::vector<T> select(const gp_Pnt& p, double extend=0.0) const {
				distances_.clear();
				protrusion_distances_.clear();

				std::vector<T> ts = select_box(p, extend);
				if (ts.empty()) {
					return ts;
				}

				std::vector<T> ts_filtered;
				ts_filtered.reserve(ts.size());

				TopoDS_Vertex v;
				if (extend > 0.) {
					BRep_Builder B;
					B.MakeVertex(v, p, ::Precision::Confusion());
				}

				typename std::vector<T>::const_iterator it = ts.begin();
				for (it = ts.begin(); it != ts.end(); ++it) {
					const TopoDS_Shape& B = shapes_.find(*it)->second;
					if (extend > 0.0) {
						BRepExtrema_DistShapeShape dss(v, B);
						if (dss.Perform() && dss.NbSolution() >= 1 && dss.Value() <= extend) {
							distances_.push_back(dss.Value());
							protrusion_distances_.push_back(max_distance_inside(B, v));

							ts_filtered.push_back(*it);
						}
					} else {
						TopExp_Explorer exp(B, TopAbs_SOLID);
						for (; exp.More(); exp.Next()) {
							BRepClass3d_SolidClassifier cls(exp.Current(), p, 1e-5);
							if (cls.State() != TopAbs_OUT) {
								ts_filtered.push_back(*it);
								break;
							}
						}
					}
				}

				return ts_filtered;
			}

		protected:
			typedef NCollection_UBTree<T, Bnd_Box> spatial_tree;
			typedef std::map<T, TopoDS_Shape> shape_map;
			typedef NCollection_DataMap<TopoDS_Shape, int, TopTools_ShapeMapHasher> face_style_map;

			spatial_tree tree_;
			shape_map shapes_;

			// @todo this is ugly, embed this in the return type
			mutable std::vector<double> distances_;
			mutable std::vector<double> protrusion_distances_;

			bool enable_face_styles_ = false;

			face_style_map face_styles_;
			std::vector<ifcopenshell::geom::taxonomy::style::ptr> styles_;

			class selector : public spatial_tree::Selector
			{
			public:
				selector(const Bnd_Box& b)
					: spatial_tree::Selector()
					, bounds_(b)
				{}

				bool Reject(const Bnd_Box& b) const {
					return bounds_.IsOut(b);
				}

				bool Accept(const T& o) {
					results_.push_back(o);
                    return true;
				}

				const std::vector<T>& results() const {
					return results_;
				}

			private:
				std::vector<T> results_;
				const Bnd_Box& bounds_;
			};

		private:
			// The compound shape of a native element in world coordinates.
			TopoDS_Shape transformed_compound(const ifcopenshell::geom::native_element* elem) const {
				auto* compound_generic = static_cast<ifcopenshell::geom::open_cascade_shape*>(elem->geometry().as_compound());
				TopoDS_Shape compound(std::move(compound_generic->shape()));
				delete compound_generic;

				const auto& m = elem->transformation().data()->ccomponents();
				gp_Trsf tr;
				tr.SetValues(
					m(0, 0), m(0, 1), m(0, 2), m(0, 3),
					m(1, 0), m(1, 1), m(1, 2), m(1, 3),
					m(2, 0), m(2, 1), m(2, 2), m(2, 3)
				);
				compound.Move(tr);

				return compound;
			}

			bool test(const TopoDS_Shape& A, const TopoDS_Shape& B, bool completely_within, double extend) const {
				if (extend > 0.) {
					BRepExtrema_DistShapeShape dss(A, B);
					if (dss.Perform() && dss.NbSolution() >= 1) {
						if (dss.Value() <= extend) {
							distances_.push_back(dss.Value());
							protrusion_distances_.push_back(max_distance_inside(B, A));
						}
						return dss.Value() <= extend;
					}
				} else {
					if (util::count(A, TopAbs_SHELL) == 0 ||
						util::count(B, TopAbs_SHELL) == 0)
					{
						return false;
					}

					if (completely_within) {
						BRepAlgoAPI_Cut cut(B, A);
						if (cut.IsDone()) {
							if (util::count(cut.Shape(), TopAbs_SHELL) == 0) {
								return true;
							}
						}
					} else {
						BRepAlgoAPI_Common common(A, B);
						if (common.IsDone()) {
							if (util::count(common.Shape(), TopAbs_SHELL) > 0) {
								return true;
							}
						}
					}
				}
				return false;
			}
		};
	}

}

#endif
