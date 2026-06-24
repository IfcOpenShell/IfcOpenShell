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

#include "OpenCascadeKernel.h"
#include "base_utils.h"

#include <TopExp.hxx>
#include <BRepTools_WireExplorer.hxx>
#include <BRepBuilderAPI_MakeEdge.hxx>
#include <BRepBuilderAPI_MakePolygon.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>
#include <BRepOffsetAPI_ThruSections.hxx>
#include <BRepBuilderAPI_MakeSolid.hxx>
#include <BRepBuilderAPI_Transform.hxx>

using namespace ifcopenshell::geometry;
using namespace ifcopenshell::geometry::kernels;
using namespace IfcGeom;
using namespace IfcGeom::util;

// @todo duplicated
namespace {
template <typename T, typename Cmp = std::less<T>>
bool has_intersection(const std::set<T, Cmp>& A,
                      const std::set<T, Cmp>& B) {
    auto itA = A.begin();
    auto itB = B.begin();

    while (itA != A.end() && itB != B.end()) {
        if (Cmp()(*itA, *itB)) {
            ++itA;
        } else if (Cmp()(*itB, *itA)) {
            ++itB;
        } else {
            return true;
        }
    }
    return false;
}
}

bool OpenCascadeKernel::convert(const taxonomy::loft::ptr loft, TopoDS_Shape& result) {
	if (loft->children.size() < 2) {
		return false;
	}

	bool non_polygonal = false;
	for (auto& ch : loft->children) {
		if (ch->kind() == taxonomy::FACE) {
			const auto& f = std::static_pointer_cast<taxonomy::face>(ch);
			for (auto& w : f->children) {
				for (auto& e : w->children) {
					if (e->basis && e->basis->kind() != taxonomy::LINE) {
						non_polygonal = true;
						break;
					}
				}
				if (non_polygonal) {
					break;
				}
			}
			if (non_polygonal) {
				break;
			}
		}
	}

	if (non_polygonal) {
		if (loft->children.size() < 2) {
            Logger::Root().Error("GEO", 177, "Not enough sections to loft");
            return false;
        }

		std::vector<std::vector<TopoDS_Wire>> sections;
        sections.reserve(loft->children.size());

		TopoDS_Shape f0, f1;

        // Convert all children to vectors of wires
        for (const auto& child : loft->children) {
            TopoDS_Shape shape;
            if (!convert(std::static_pointer_cast<taxonomy::face>(child), shape)) {
                return false;
            }
            if (shape.ShapeType() != TopAbs_FACE) {
                return false;
            }
			// At least make sure to have outer wire consistent, but in reality
			// this is probably not a concern given how to build up these faces
            auto f = TopoDS::Face(shape);

			if (child == loft->children.front()) {
                f0 = f;
            } else if (child == loft->children.back()) {
				f1 = f;
            }

            auto outer = BRepTools::OuterWire(f);
            sections.emplace_back();
            sections.back().push_back(outer);
            for (TopoDS_Iterator it(f); it.More(); it.Next()) {
                if (outer != it.Value()) {
                    sections.back().push_back(TopoDS::Wire(it.Value()));
                }
            }
        }

		auto first_wire_count = sections.front().size();
        for (auto& section : sections) {
			if (section.size() != first_wire_count) {
				Logger::Root().Error("GEO", 178, "Inconsistent number of wires in sections");
				return false;
			}
        }

		BRep_Builder BB;
		TopoDS_Shell comp;
		BB.MakeShell(comp);

        for (size_t i = 0; i < first_wire_count; ++i) {
            // Rule=True uses linear interpolation.
            // This is critical for preventing twists in roads/railings.
            BRepOffsetAPI_ThruSections builder(false, true);
            for (auto& ws : sections) {
                builder.AddWire(ws[i]);
            }
            builder.Build();
			if (!builder.IsDone()) {
				return false;
			}
			for (TopExp_Explorer exp(builder.Shape(), TopAbs_FACE); exp.More(); exp.Next()) {
				BB.Add(comp, exp.Current());
			}
		}

		BB.Add(comp, f0.Reversed());
		BB.Add(comp, f1);

		result = BRepBuilderAPI_MakeSolid(comp).Solid();

		return true;
	}
	
	NCollection_List<TopoDS_Shape> faces;
	TopoDS_Compound comp;
	BRep_Builder BB;
	BB.MakeCompound(comp);

	std::vector<TopoDS_Shape> shps(loft->children.size());
    std::vector<std::vector<std::set<std::string>>> all_tags;

	// First convert all taxonomy items to TopoDS_Wire/Face
    for (auto it = loft->children.begin(); it < loft->children.end(); ++it) {
		auto i = std::distance(loft->children.begin(), it);
        if ((*it)->kind() == taxonomy::FACE) {
            if (!convert(std::static_pointer_cast<taxonomy::face>((*it)), shps[i])) {
                return false;
            }
        }
        if ((*it)->kind() == taxonomy::LOOP) {

			// @todo duplicated with infra_sweep_helper
			// I think make_loft() where should just return a shell instead, because
			// this faceted lofting does not depend on any functionality in the geometry library
			// and the branching with tags needs to be solved twice otherwise
			auto loop_to_points = [](const taxonomy::loop::ptr& loop, const boost::optional<std::vector<std::string>>& input_tags) -> std::pair<std::vector<taxonomy::point3::ptr>, std::vector<std::set<std::string>>> {
                std::vector<taxonomy::point3::ptr> points;
                std::vector<std::set<std::string>> tags;
                std::vector<std::string>::const_iterator tag_it;

                if (!loop->closed.get_value_or(false)) {
                    points = {boost::get<taxonomy::point3::ptr>(loop->children[0]->start)};
                    if (input_tags) {
                        tags = {{input_tags->front()}};
                        tag_it = ++input_tags->begin();
                    }
                }
                for (auto& e : loop->children) {
                    const auto& p1 = boost::get<taxonomy::point3::ptr>(e->start);
                    const auto& p2 = boost::get<taxonomy::point3::ptr>(e->end);
                    if (input_tags && p1->ccomponents() == p2->ccomponents()) {
                        tags.back().insert(*tag_it);
                        ++tag_it;
                    } else {
                        points.push_back(p2);
                        if (input_tags) {
                            tags.emplace_back();
                            tags.back().insert(*tag_it);
                            ++tag_it;
                        }
                    }
                }
                if (!input_tags) {
                    if (loop->closed.get_value_or(false)) {
                        // close polygon by referencing first point
                        points.push_back(points.front());
                    }
                }
                return {points, tags};
            };

			auto lp = std::static_pointer_cast<taxonomy::loop>(*it);
            TopoDS_Wire w;

			if (lp->tags) {
                auto [points, tags] = loop_to_points(lp, lp->tags);
                BRepBuilderAPI_MakePolygon mp;
                for (auto& p : points) {
                    const auto& xyz = p->ccomponents();
                    mp.Add(gp_Pnt(xyz(0), xyz(1), xyz(2)));
                }
                w = mp.Wire();

				if (lp->matrix && !lp->matrix->is_identity()) {
                    const auto& m = lp->matrix->ccomponents();
                    gp_Trsf tr;
                    tr.SetValues(
                        m(0, 0), m(0, 1), m(0, 2), m(0, 3), m(1, 0), m(1, 1), m(1, 2), m(1, 3), m(2, 0), m(2, 1), m(2, 2), m(2, 3));
                    w = TopoDS::Wire(BRepBuilderAPI_Transform(w, tr).Shape());
                }

				all_tags.push_back(tags);
			} else {
                if (!convert(std::static_pointer_cast<taxonomy::loop>((*it)), w)) {
                    return false;
                }
			}

            shps[i] = w;
        }
        if (shps[i].ShapeType() != TopAbs_FACE && shps[i].ShapeType() != TopAbs_WIRE) {
            return false;
        }
    }

	/*
	// With --dimensionality CURVES_SURFACES_AND_SOLIDS this will give the interpolated profiles as line geometry
	{
        for (auto& f : shps) {
			BB.Add(comp, f);
        }
	}
	result = comp;
    return true;
	*/

    if (shps.size() < 2) {
        Logger::Root().Error("GEO", 179, "Not enough sections to loft");
        return false;
    }

    if (shps[0].ShapeType() == TopAbs_FACE) {
        // When processing a sectioned *surface* there are no
        // begin and end caps that need to be added.
        BB.Add(comp, shps.front().Reversed());
        BB.Add(comp, shps.back());
    }

	// @todo this approach is
    // potentially incorrect as there is no guarantee that the wires for
    // subsequently placed profiles are traversed from an equivalent start vertex.
	for (auto it = shps.begin(); it < shps.end() - 1; ++it) {
        auto ii = std::distance(shps.begin(), it);
		auto jt = it + 1;
		std::array<std::vector<TopoDS_Shape>::const_iterator, 2> fa = { it, jt };
		std::vector<std::array<TopoDS_Wire, 2>> ws;
		ws.emplace_back();
		for (int i = 0; i < 2; ++i) {
            if (fa[i]->ShapeType() == TopAbs_FACE) {
                ws[0][i] = BRepTools::OuterWire(TopoDS::Face(*fa[i]));
				size_t j = 1;
                for (TopExp_Explorer exp(*fa[i], TopAbs_WIRE); exp.More(); exp.Next()) {
					if (exp.Current() != ws[0][i]) {
						while (ws.size() <= j) {
							ws.emplace_back();
						}
						ws[j++][i] = TopoDS::Wire(exp.Current());
					}
				}
			} else {
                ws[0][i] = TopoDS::Wire(*fa[i]);
			}
		}

		if (!all_tags.empty()) {
			// only open profiles have tags for now, so there is only one wire, no inner wires
            const auto& wp = ws[0];
            std::array<std::vector<gp_Pnt>, 2> profile_points;
            std::array<std::vector<std::vector<std::set<std::string>>>::const_iterator, 2> tag_pairs = {
                all_tags.begin() + std::distance(shps.begin(), it),
                all_tags.begin() + std::distance(shps.begin(), jt)};
            
			for (size_t i = 0; i < 2; ++i) {
                NCollection_IndexedDataMap<TopoDS_Shape, NCollection_List<TopoDS_Shape>, TopTools_ShapeMapHasher> ancestors;
				const auto& wire = wp[i];
                auto& result = profile_points[i];

				TopExp::MapShapesAndAncestors(
                    wire,
                    TopAbs_VERTEX,
                    TopAbs_EDGE,
                    ancestors);

                TopoDS_Vertex v0, vn, previous;
                TopExp::Vertices(wire, v0, vn);

				TopoDS_Vertex curr = v0;
                result.push_back(BRep_Tool::Pnt(curr));

				while (true) {
                    if (curr.IsSame(vn)) {
                        break;
                    }

                    const NCollection_List<TopoDS_Shape>& incidentEdges = ancestors.FindFromKey(curr);

                    for (NCollection_List<TopoDS_Shape>::Iterator it(incidentEdges); it.More(); it.Next()) {
                        const TopoDS_Edge& e = TopoDS::Edge(it.Value());
						
						TopoDS_Vertex ev0, ev1;
                        TopExp::Vertices(e, ev0, ev1);

						TopoDS_Vertex other_on_edge = curr.IsSame(ev0) ? ev1 : ev0;
                        if (other_on_edge.IsSame(previous)) {
                            continue;
                        } else {
                            previous = curr;
                            curr = other_on_edge;
                            result.push_back(BRep_Tool::Pnt(curr));
                            break;
						}
                    }
				}
            }

			auto a = profile_points[0].begin();
            auto b = profile_points[1].begin();
            auto c = tag_pairs[0]->begin();
            auto d = tag_pairs[1]->begin();

			if (!has_intersection(*c, *d)) {
                throw std::runtime_error("Starting vertices do not have corresponding tags");
			}

			auto emit_triangle = [&](const gp_Pnt& p1, const gp_Pnt& p2, const gp_Pnt& p3) {
                BB.Add(comp, BRepBuilderAPI_MakeFace(BRepBuilderAPI_MakePolygon(p1, p2, p3, true).Wire()).Face());
            };

			while (c != (tag_pairs[0]->end() - 1) && d != (tag_pairs[0]->end() - 1)) {
                if (c != (tag_pairs[0]->end() - 1) && has_intersection(*(c + 1), *d)) {
                    emit_triangle(*a, *(a + 1), *b);
                    ++a;
                    ++c;
                } else if (d != (tag_pairs[1]->end() - 1) && has_intersection(*c, *(d + 1))) {
                    emit_triangle(*a, *(b + 1), *b);
                    ++b;
                    ++d;
                } else if (c != (tag_pairs[0]->end() - 1) && d != (tag_pairs[1]->end() - 1) && has_intersection(*(c + 1), *(d + 1))) {
                    emit_triangle(*a, *(a + 1), *b);
                    emit_triangle(*(a + 1), *(b + 1), *b);
                    ++a;
                    ++b;
                    ++c;
                    ++d;
                } else {
                    throw std::runtime_error("Unable to construct surface");
				}				
			}

            continue;
        }		

		for (auto& wp : ws) {
			BRepTools_WireExplorer a(wp[0]);
			BRepTools_WireExplorer b(wp[1]);
			for (; a.More() && b.More(); a.Next(), b.Next()) {
				auto& e1 = a.Current();
				// auto e3 = TopoDS::Edge(b.Current().Reversed());
				auto& e3 = b.Current();

				// Documentation says unconnected edges are automatically connected, but this is not the case
				TopoDS_Vertex e1a, e1b, e3a, e3b;
				TopExp::Vertices(e1, e1a, e1b, true);
				TopExp::Vertices(e3, e3a, e3b, true);
				auto e2 = BRepBuilderAPI_MakeEdge(e1b, e3a).Edge();
				auto e4 = BRepBuilderAPI_MakeEdge(e3b, e1a).Edge();

				/*
				BRepFill_Filling fill;
				fill.Add(e1, GeomAbs_C0);
				fill.Add(e2, GeomAbs_C0);
				fill.Add(e3, GeomAbs_C0);
				fill.Add(e4, GeomAbs_C0);
				fill.Build();
				// faces.Append(fill.Face());
				BB.Add(comp, fill.Face());
				*/

				auto f = BRepBuilderAPI_MakeFace(BRepBuilderAPI_MakePolygon(e1a, e1b, e3b, true).Wire()).Face();
				BB.Add(comp, f);
				auto g = BRepBuilderAPI_MakeFace(BRepBuilderAPI_MakePolygon(e3b, e3a, e1a, true).Wire()).Face();
				BB.Add(comp, g);
			}
		}
	}

	// create_solid_from_faces(faces, result, settings_.get<settings::Precision>().get());
	result = comp;

	return true;
}

bool OpenCascadeKernel::convert_impl(const taxonomy::loft::ptr loft, IfcGeom::ConversionResults& results) {
    return handle_occt_exception([&]() -> bool {

	TopoDS_Shape shape;
	if (!convert(loft, shape)) {
		return false;
	}
	results.emplace_back(ConversionResult(
		loft->instance->as<IfcUtil::IfcBaseEntity>()->id(),
		loft->matrix,
		new OpenCascadeShape(shape),
		loft->surface_style
	));
	return true;

    });
}
