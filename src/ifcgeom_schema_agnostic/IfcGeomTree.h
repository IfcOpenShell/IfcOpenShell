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

#ifndef IFCGEOMTREE_H
#define IFCGEOMTREE_H

#include "../ifcparse/IfcFile.h"

#include "../ifcgeom_schema_agnostic/IfcGeomElement.h"
#include "../ifcgeom_schema_agnostic/IfcGeomIterator.h"
#include "../ifcgeom_schema_agnostic/IfcGeomMaterial.h"
#include "../ifcgeom_schema_agnostic/Kernel.h"

#include <NCollection_UBTree.hxx>
#include <BRepBndLib.hxx>
#include <Bnd_Box.hxx>
#include <BRep_Builder.hxx>
#include <BRepAlgoAPI_Common.hxx>
#include <BRepAlgoAPI_Cut.hxx>
#include <BRepExtrema_DistShapeShape.hxx>
#include <BRepClass3d_SolidClassifier.hxx>
#include <TopTools_DataMapOfShapeInteger.hxx>
#include <BRepBuilderAPI_MakeEdge.hxx>
#include <BRepExtrema_ExtPF.hxx>

namespace IfcGeom {

	struct ray_intersection_result {
		double distance;
		int style_index;
		IfcUtil::IfcBaseEntity* instance;
		std::array<double, 3> position;
		std::array<double, 3> normal;
		double ray_distance;
		double dot_product;
	};

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
		template <typename T>
		class tree {

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
					if (IfcGeom::Kernel::count(A, TopAbs_SHELL) == 0 ||
						IfcGeom::Kernel::count(B, TopAbs_SHELL) == 0)
					{
						return false;
					}

					if (completely_within) {
						BRepAlgoAPI_Cut cut(B, A);
						if (cut.IsDone()) {
							if (IfcGeom::Kernel::count(cut.Shape(), TopAbs_SHELL) == 0) {
								return true;
							}
						}
					} else {
						BRepAlgoAPI_Common common(A, B);
						if (common.IsDone()) {
							if (IfcGeom::Kernel::count(common.Shape(), TopAbs_SHELL) > 0) {
								return true;
							}
						}
					}
				}
				return false;
			}

		protected:

			// @todo this is ugly, embed this in the return type
			mutable std::vector<double> distances_;
			mutable std::vector<double> protrusion_distances_;

		public:

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
				typename map_t::const_iterator it = shapes_.find(t);
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

			std::vector<T> select(const IfcGeom::BRepElement* elem, bool completely_within = false, double extend = -1.e-5) const {
				auto compound = elem->geometry().as_compound();
				compound.Move(elem->transformation().data());
				return select(compound, completely_within, extend);
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
					B.MakeVertex(v, p, Precision::Confusion());
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
			typedef NCollection_UBTree<T, Bnd_Box> tree_t;
			typedef std::map<T, TopoDS_Shape> map_t;

			tree_t tree_;
			map_t shapes_;
			
			bool enable_face_styles_ = false;

			class selector : public tree_t::Selector
			{
			public:
				selector(const Bnd_Box& b)
					: tree_t::Selector()
					, bounds_(b)
				{}

				Standard_Boolean Reject(const Bnd_Box& b) const {
					return bounds_.IsOut(b);
				}

				Standard_Boolean Accept(const T& o) {
					results_.push_back(o);
					return Standard_True;
				}

				const std::vector<T>& results() const {
					return results_;
				}

			private:
				std::vector<T> results_;
				const Bnd_Box& bounds_;
			};

		};
	}

	class tree : public impl::tree<IfcUtil::IfcBaseEntity*> {
	public:

		tree() {};

		tree(IfcParse::IfcFile& f) {
			add_file(f, IfcGeom::IteratorSettings());
		}

		tree(IfcParse::IfcFile& f, const IfcGeom::IteratorSettings& settings) {
			add_file(f, settings);
		}

		tree(IfcGeom::Iterator& it) {
			add_file(it);
		}		

		void add_file(IfcParse::IfcFile& f, const IfcGeom::IteratorSettings& settings) {
			IfcGeom::IteratorSettings settings_ = settings;
			settings_.set(IfcGeom::IteratorSettings::DISABLE_TRIANGULATION, true);
			settings_.set(IfcGeom::IteratorSettings::USE_WORLD_COORDS, true);
			settings_.set(IfcGeom::IteratorSettings::SEW_SHELLS, true);

			IfcGeom::Iterator it(settings_, &f);

			add_file(it);
		}

		void add_file(IfcGeom::Iterator& it) {
			if (it.initialize()) {
				do {
					add_element(dynamic_cast<IfcGeom::BRepElement*>(it.get()));
				} while (it.next());
			}
		}

		void add_element(IfcGeom::BRepElement* elem) {
			if (!elem) {
				return;
			}
			auto compound = elem->geometry().as_compound();
			compound.Move(elem->transformation().data());
			add(elem->product(), compound);
			auto git = elem->geometry().begin();

			if (enable_face_styles_) {
				TopoDS_Iterator it(compound);
				for (; it.More(); it.Next(), ++git) {
					std::unique_ptr<IfcGeom::Material> adaptor;					
					if (git->hasStyle()) {
						adaptor.reset(new Material(git->StylePtr()));
					} else {
						adaptor.reset(new Material(IfcGeom::get_default_style(elem->type())));
					}
					
					// Assumption is that the number of styles is small, so the linear lookup time is not significant.
					auto sit = std::find(styles_.begin(), styles_.end(), *adaptor);
					int index;
					if (sit == styles_.end()) {
						index = styles_.size();
						styles_.push_back(*adaptor);
					} else {
						index = std::distance(styles_.begin(), sit);
					}

					TopExp_Explorer exp(it.Value(), TopAbs_FACE);
					for (; exp.More(); exp.Next()) {
						face_styles_.Bind(exp.Current(), index);
					}
				}
			}
		}

		const std::vector<double>& distances() const {
			return distances_;
		}

		const std::vector<double>& protrusion_distances() const {
			return protrusion_distances_;
		}

		std::vector<IfcGeom::ray_intersection_result> select_ray(const gp_Pnt& p0, const gp_Dir& d, double length = 1000.) const {
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
					ordered.insert({ u,	{ u, sidx, c,
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
		}

		bool enable_face_styles() const {
			return enable_face_styles_;
		}

		void enable_face_styles(bool b) {
			enable_face_styles_ = b;
		}

		const std::vector<IfcGeom::Material>& styles() const {
			return styles_;
		}

	protected:
		typedef TopTools_DataMapOfShapeInteger face_style_map_t;

		face_style_map_t face_styles_;
		std::vector<IfcGeom::Material> styles_;
	};

}

#endif
