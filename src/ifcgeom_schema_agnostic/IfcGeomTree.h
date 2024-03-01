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
#include "../ifcgeom_schema_agnostic/base_utils.h"
#include "../ifcgeom_schema_agnostic/clash_utils.h"
#include "../ifcgeom_schema_agnostic/bvh_utils.h"

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

#include <vector>
#include <future>
#include <mutex>
#include <unordered_map>
#include <unordered_set>
#include <BRepExtrema_TriangleSet.hxx>
#include <BRepLProp_SLProps.hxx>
#include <BVH_BinaryTree.hxx>
#include <BVH_Box.hxx>
#include <BVH_BoxSet.hxx>
#include <BVH_LinearBuilder.hxx>
#include <BVH_Tree.hxx>
#include <BVH_Triangulation.hxx>
#include <BVH_Types.hxx>
#include <Bnd_OBB.hxx>
#include <GeomAPI_ProjectPointOnSurf.hxx>
#include <Geom_Plane.hxx>
#include <IntTools_FaceFace.hxx>
#include <STEPConstruct_PointHasher.hxx>

#include "H5Cpp.h"


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

	struct clash {
        int clash_type; // 0 = protrusion, 1 = pierce, 2 = collision, 3 = clearance
		IfcUtil::IfcBaseClass* a;
		IfcUtil::IfcBaseClass* b;
		double distance;
		std::array<double, 3> p1;
		std::array<double, 3> p2;
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

            template <typename Fn>
            bool process_bvh_intersections(const T& tA, const T& tB, Fn&& f) {
                // Collide BVH trees of shape A vs B
                opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>> bvh_a = bvhs_.find(tA)->second;
                opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>> bvh_b = bvhs_.find(tB)->second;

                std::unordered_map<int, std::vector<int>> bvh_clashes = clash_bvh(bvh_a, bvh_b);
                if (bvh_clashes.empty()) {
                    return { -1, tA, tB, 0, {0, 0, 0}, {0, 0, 0} };
                }

                const std::vector<std::array<int, 3>>& tris_a = tris_.find(tA)->second;
                const std::vector<std::array<int, 3>>& tris_b = tris_.find(tB)->second;
                const std::vector<gp_Pnt>& verts_a = verts_.find(tA)->second;
                const std::vector<gp_Pnt>& verts_b = verts_.find(tB)->second;
                const std::vector<gp_Vec>& normals_a = normals_.find(tA)->second;
                const std::vector<gp_Vec>& normals_b = normals_.find(tB)->second;

                for (const auto& pair : bvh_clashes) {
                    const int bvh_a_i = pair.first;
                    const std::vector<int>& bvh_b_is = pair.second;

                    for (int i = bvh_a->BegPrimitive(bvh_a_i); i <= bvh_a->EndPrimitive(bvh_a_i); ++i) {
                        const std::array<int, 3>& tri = tris_a[i];

                        f(bvh_a, bvh_b, tris_a, tris_b, verts_a, verts_b, normals_a, normals_b, i, tri, bvh_b_is);
                    }
                }
            }

            clash test_intersection_2(const T& tA, const T& tB, double tolerance, bool check_all = true) {
                auto obb_b = obbs_.find(tB)->second;
                obb_b.Enlarge(-tolerance);

                // ~10% faster?
                std::unordered_set<int> points_in_b_cache;
                std::unordered_set<int> points_not_in_b_cache;

                double protrusion = -std::numeric_limits<double>::infinity();
                std::array<double, 3> protrusion_point;
                std::array<double, 3> surface_point;

                double pierce = -std::numeric_limits<double>::infinity();
                std::array<double, 3> pierce_point1;
                std::array<double, 3> pierce_point2;

                // No need to search beyond the distance of the max protrusion.
                const double max_protrusion = max_protrusions_.find(tB)->second;

                process_bvh_intersections(tA, tB, [
                    &obb_b,
                    &points_in_b_cache, 
                    &points_not_in_b_cache,
                    &protrusion,
                    &protrusion_point,
                    &surface_point,
                    &pierce,
                    &pierce_point1,
                    &pierce_point2,
                    &max_protrusion
                ](
                    opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>> bvh_a,
                    opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>> bvh_b,
                    const std::vector<std::array<int, 3>>& tris_a,
                    const std::vector<std::array<int, 3>>& tris_b,
                    const std::vector<gp_Pnt>& verts_a,
                    const std::vector<gp_Pnt>& verts_b,
                    const std::vector<gp_Vec>& normals_a,
                    const std::vector<gp_Vec>& normals_b,
                    int i,
                    const std::array<int, 3>& tri,
                    const std::vector<int>& bvh_b_is
                ) {
                    std::vector<gp_Pnt> points_in_b;

                    for (int v_id : tri) {
                        if (points_not_in_b_cache.find(v_id) != points_not_in_b_cache.end()) {
                            continue;
                        }

                        const gp_Pnt& v = verts_a[v_id];

                        if (points_in_b_cache.find(v_id) != points_in_b_cache.end()) {
                            points_in_b.push_back(v);
                            continue;
                        }

                        if (obb_b.IsOut(v)) {
                            points_not_in_b_cache.insert(v_id);
                            continue;
                        }

                        if (IfcGeom::util::is_point_in_shape(v, bvh_b, tris_b, verts_b)
                            && IfcGeom::util::is_point_in_shape(v, bvh_b, tris_b, verts_b, true)) {
                            points_in_b.push_back(v);
                            points_in_b_cache.insert(v_id);
                        } else {
                            points_not_in_b_cache.insert(v_id);
                        }
                    }

                    // If there are no points in b, this may be a "piercing" triangle.
                    if (points_in_b.empty()) {
                        gp_Vec v1_a_vec(verts_a[tri[0]].XYZ());
                        gp_Vec v2_a_vec(verts_a[tri[1]].XYZ());
                        gp_Vec v3_a_vec(verts_a[tri[2]].XYZ());

                        // Protrusions take priority over piercings. We only check for piercings if:
                        //  - This is a piercing triangle (e.g. no points in b)
                        //  - No protrusion was already found
                        //  - We haven't yet found a piercing at the max protrusion limit
                        if (protrusion == -std::numeric_limits<double>::infinity() && pierce != max_protrusion) {
                            std::array<
                                std::tuple<double, std::array<double, 3>, std::array<double, 3>>, 3
                            > pierce_results = {
                                IfcGeom::util::pierce_shape(v1_a_vec, v2_a_vec, bvh_b, tris_b, verts_b, normals_b),
                                IfcGeom::util::pierce_shape(v1_a_vec, v3_a_vec, bvh_b, tris_b, verts_b, normals_b),
                                IfcGeom::util::pierce_shape(v2_a_vec, v3_a_vec, bvh_b, tris_b, verts_b, normals_b)
                            };

                            for (const auto& pr : pierce_results) {
                                auto& p_dist = std::get<0>(pr);
                                auto& p_min = std::get<1>(pr);
                                auto& p_max = std::get<2>(pr);
                                if (p_dist > tolerance && p_dist > pierce) {
                                    // Piercings are capped at max_protrusion for intuitive results
                                    pierce = std::min(p_dist, max_protrusion);
                                    pierce_point1 = p_min;
                                    pierce_point2 = p_max;
                                    if (!check_all) {
                                        return { 1, tA, tB, pierce, pierce_point1, pierce_point2 };
                                    }
                                }
                            }
                        }

                        // Since there were no points in b, we don't need to check for protrusions.
                        continue;
                    }

                    const gp_Vec& normal_a = normals_a[i];
                    double v_protrusion = std::numeric_limits<double>::infinity();
                    std::array<double, 3> v_protrusion_point;
                    std::array<double, 3> v_surface_point;

                    // Check for protrusions.
                    for (const auto& bvh_b_i : bvh_b_is) {
                        for (int j = bvh_b->BegPrimitive(bvh_b_i); j <= bvh_b->EndPrimitive(bvh_b_i); ++j) {
                            const std::array<int, 3>& tri = tris_b[j];
                            const gp_Vec& normal_b = normals_b[j];

                            tri_count_++;

                            // We're penetrating _into_ a shape, so don't
                            // compare distances to faces with roughly the
                            // same normal as the penetration.
                            if (normal_a.Dot(normal_b) >= 0.9f) {
                                continue;
                            }

                            gp_Vec ta(verts_b[tri[0]].XYZ());
                            gp_Vec tb(verts_b[tri[1]].XYZ());
                            gp_Vec tc(verts_b[tri[2]].XYZ());

                            for (const auto& v : points_in_b) {
                                gp_Vec ray_origin(v.XYZ());

                                /*
                                std::cout << "POINT IN B " << v.X() << " " << v.Y() << " " << v.Z() << std::endl;
                                std::cout << "dir-> " << normal_b.X() << " " << normal_b.Y() << " " << normal_b.Z() << std::endl;
                                std::cout << "->tri " << v1_b[0] << " " << v1_b[1] << " " << v1_b[2] << std::endl;
                                std::cout << "->tri " << v2_b[0] << " " << v2_b[1] << " " << v2_b[2] << std::endl;
                                std::cout << "->tri " << v3_b[0] << " " << v3_b[1] << " " << v3_b[2] << std::endl;
                                */

                                // Do (cheaper) line check.
                                double at, au, av;
                                if (intersectRayTriangle(ray_origin, normal_b, ta, tb, tc, at, au, av, false)) {
                                    double current_v_protrusion = at;

                                    // std::cout << "We got a current protrusion " << current_v_protrusion << std::endl;
                                    if (current_v_protrusion < v_protrusion) {
                                        double aw = 1.0f - au - av; // Barycentric coordinate for ta
                                        gp_Vec point_on_b = aw * ta + au * tb + av * tc; // Intersection point
                                        // std::cout << "New v_protrusion winner of " << current_v_protrusion << std::endl;
                                        v_protrusion = current_v_protrusion;
                                        v_protrusion_point = { v.X(), v.Y(), v.Z() };
                                        v_surface_point = { point_on_b.X(), point_on_b.Y(), point_on_b.Z() };

                                        if (!check_all && v_protrusion > tolerance) {
                                            return { 0, tA, tB, v_protrusion, v_protrusion_point, v_surface_point };
                                        }
                                    }
                                }
                            }
                        }
                    }

                    if (v_protrusion != std::numeric_limits<double>::infinity()) {
                        if (v_protrusion > protrusion) {
                            // std::cout << "New actual protrusion winner of " << v_protrusion << std::endl;
                            protrusion = v_protrusion;
                            protrusion_point = v_protrusion_point;
                            surface_point = v_surface_point;
                            if (protrusion > (max_protrusion - 1e-3)) {
                                return { 0, tA, tB, protrusion, protrusion_point, surface_point };
                            }
                        }
                    }
                });
            }

			clash test_intersection(const T& tA, const T& tB, double tolerance, bool check_all = true) const {
                // If there are verts of A inside shape B (protrusion):
                //  1. For each vert, find the shortest distance to the closest face
                //  2. Find the innermost vert (i.e. the vert that has the longest distance)
                // Otherwise (piercing):
                //  1. Intersect each edge with shape B
                //  2. Find the longest distance between intersections

                auto obb_b = obbs_.find(tB)->second;
                obb_b.Enlarge(-tolerance);

                // No need to search beyond the distance of the max protrusion.
                const double max_protrusion = max_protrusions_.find(tB)->second;

                // Collide BVH trees of shape A vs B
                opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>> bvh_a = bvhs_.find(tA)->second;
                opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>> bvh_b = bvhs_.find(tB)->second;

                std::unordered_map<int, std::vector<int>> bvh_clashes = clash_bvh(bvh_a, bvh_b, max_protrusion);
                if (bvh_clashes.empty()) {
                    return {-1, tA, tB, 0, {0, 0, 0}, {0, 0, 0}};
                }

                const std::vector<std::array<int, 3>>& tris_a = tris_.find(tA)->second;
                const std::vector<std::array<int, 3>>& tris_b = tris_.find(tB)->second;
                const std::vector<gp_Pnt>& verts_a = verts_.find(tA)->second;
                const std::vector<gp_Pnt>& verts_b = verts_.find(tB)->second;
                const std::vector<gp_Vec>& normals_a = normals_.find(tA)->second;
                const std::vector<gp_Vec>& normals_b = normals_.find(tB)->second;

                // ~10% faster?
                std::unordered_set<int> points_in_b_cache;
                std::unordered_set<int> points_not_in_b_cache;

                double protrusion = -std::numeric_limits<double>::infinity();
                std::array<double, 3> protrusion_point;
                std::array<double, 3> surface_point;

                double pierce = -std::numeric_limits<double>::infinity();
                std::array<double, 3> pierce_point1;
                std::array<double, 3> pierce_point2;

                for (const auto& pair : bvh_clashes) {
                    const int bvh_a_i = pair.first;
                    const std::vector<int>& bvh_b_is = pair.second;

                    for (int i=bvh_a->BegPrimitive(bvh_a_i); i<=bvh_a->EndPrimitive(bvh_a_i); ++i) {
                        const std::array<int, 3>& tri = tris_a[i];
                        std::vector<gp_Pnt> points_in_b;

                        for (int v_id : tri) {
                            if (points_not_in_b_cache.find(v_id) != points_not_in_b_cache.end()) {
                                continue;
                            }

                            const gp_Pnt& v = verts_a[v_id];

                            if (points_in_b_cache.find(v_id) != points_in_b_cache.end()) {
                                points_in_b.push_back(v);
                                continue;
                            }

                            if (obb_b.IsOut(v)) {
                                points_not_in_b_cache.insert(v_id);
                                continue;
                            }

                            if (is_point_in_shape(v, bvh_b, tris_b, verts_b)
                                    && is_point_in_shape(v, bvh_b, tris_b, verts_b, true)) {
                                points_in_b.push_back(v);
                                points_in_b_cache.insert(v_id);
                            } else {
                                points_not_in_b_cache.insert(v_id);
                            }
                        }

                        // If there are no points in b, this may be a "piercing" triangle.
                        if (points_in_b.empty()) {
                            gp_Vec v1_a_vec(verts_a[tri[0]].XYZ());
                            gp_Vec v2_a_vec(verts_a[tri[1]].XYZ());
                            gp_Vec v3_a_vec(verts_a[tri[2]].XYZ());

                            // Protrusions take priority over piercings. We only check for piercings if:
                            //  - This is a piercing triangle (e.g. no points in b)
                            //  - No protrusion was already found
                            //  - We haven't yet found a piercing at the max protrusion limit
                            if (protrusion == -std::numeric_limits<double>::infinity() && pierce != max_protrusion) {
                                std::array<
                                    std::tuple<double, std::array<double, 3>, std::array<double, 3>>, 3
                                > pierce_results = {
                                    pierce_shape(v1_a_vec, v2_a_vec, bvh_b, tris_b, verts_b, normals_b),
                                    pierce_shape(v1_a_vec, v3_a_vec, bvh_b, tris_b, verts_b, normals_b),
                                    pierce_shape(v2_a_vec, v3_a_vec, bvh_b, tris_b, verts_b, normals_b)
                                };

                                for (const auto& pr : pierce_results) {
                                    auto& p_dist = std::get<0>(pr);
                                    auto& p_min = std::get<1>(pr);
                                    auto& p_max = std::get<2>(pr);
                                    if (p_dist > tolerance && p_dist > pierce) {
                                        // Piercings are capped at max_protrusion for intuitive results
                                        pierce = std::min(p_dist, max_protrusion);
                                        pierce_point1 = p_min;
                                        pierce_point2 = p_max;
                                        if ( ! check_all) {
                                            return {1, tA, tB, pierce, pierce_point1, pierce_point2};
                                        }
                                    }
                                }
                            }

                            // Since there were no points in b, we don't need to check for protrusions.
                            continue;
                        }

                        const gp_Vec& normal_a = normals_a[i];
                        double v_protrusion = std::numeric_limits<double>::infinity();
                        std::array<double, 3> v_protrusion_point;
                        std::array<double, 3> v_surface_point;

                        // Check for protrusions.
                        for (const auto& bvh_b_i : bvh_b_is) {
                            for (int j=bvh_b->BegPrimitive(bvh_b_i); j<=bvh_b->EndPrimitive(bvh_b_i); ++j) {
                                const std::array<int, 3>& tri = tris_b[j];
                                const gp_Vec& normal_b = normals_b[j];

                                tri_count_++;

                                // We're penetrating _into_ a shape, so don't
                                // compare distances to faces with roughly the
                                // same normal as the penetration.
                                if (normal_a.Dot(normal_b) >= 0.9f) {
                                    continue;
                                }

                                gp_Vec ta(verts_b[tri[0]].XYZ());
                                gp_Vec tb(verts_b[tri[1]].XYZ());
                                gp_Vec tc(verts_b[tri[2]].XYZ());

                                for (const auto& v : points_in_b) {
                                    gp_Vec ray_origin(v.XYZ());

                                    /*
                                    std::cout << "POINT IN B " << v.X() << " " << v.Y() << " " << v.Z() << std::endl;
                                    std::cout << "dir-> " << normal_b.X() << " " << normal_b.Y() << " " << normal_b.Z() << std::endl;
                                    std::cout << "->tri " << v1_b[0] << " " << v1_b[1] << " " << v1_b[2] << std::endl;
                                    std::cout << "->tri " << v2_b[0] << " " << v2_b[1] << " " << v2_b[2] << std::endl;
                                    std::cout << "->tri " << v3_b[0] << " " << v3_b[1] << " " << v3_b[2] << std::endl;
                                    */

                                    // Do (cheaper) line check.
                                    double at, au, av;
                                    if (intersectRayTriangle(ray_origin, normal_b, ta, tb, tc, at, au, av, false)) {
                                        double current_v_protrusion = at;

                                        // std::cout << "We got a current protrusion " << current_v_protrusion << std::endl;
                                        if (current_v_protrusion < v_protrusion) {
                                            double aw = 1.0f - au - av; // Barycentric coordinate for ta
                                            gp_Vec point_on_b = aw * ta + au * tb + av * tc; // Intersection point
                                            // std::cout << "New v_protrusion winner of " << current_v_protrusion << std::endl;
                                            v_protrusion = current_v_protrusion;
                                            v_protrusion_point = {v.X(), v.Y(), v.Z()};
                                            v_surface_point = {point_on_b.X(), point_on_b.Y(), point_on_b.Z()};

                                            if ( ! check_all && v_protrusion > tolerance) {
                                                return {0, tA, tB, v_protrusion, v_protrusion_point, v_surface_point};
                                            }
                                        }
                                    }
                                }
                            }
                        }

                        if (v_protrusion != std::numeric_limits<double>::infinity()) {
                            if (v_protrusion > protrusion) {
                                // std::cout << "New actual protrusion winner of " << v_protrusion << std::endl;
                                protrusion = v_protrusion;
                                protrusion_point = v_protrusion_point;
                                surface_point = v_surface_point;
                                if (protrusion > (max_protrusion - 1e-3)) {
                                    return {0, tA, tB, protrusion, protrusion_point, surface_point};
                                }
                            }
                        }
                    }
                }

                if (protrusion > tolerance) {
                    return {0, tA, tB, protrusion, protrusion_point, surface_point};
                }

                if (pierce > tolerance) {
                    return {1, tA, tB, pierce, pierce_point1, pierce_point2};
                }

                return {-1, tA, tB, 0, {0, 0, 0}, {0, 0, 0}};
            }

			clash test_collision(const T& tA, const T& tB, bool allow_touching) const {
                // Collide BVH trees of shape A vs B
                opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>> bvh_a = bvhs_.find(tA)->second;
                opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>> bvh_b = bvhs_.find(tB)->second;

                std::unordered_map<int, std::vector<int>> bvh_clashes = clash_bvh(bvh_a, bvh_b);
                if (bvh_clashes.empty()) {
                    return {-1, tA, tB, 0, {0, 0, 0}, {0, 0, 0}};
                }

                const std::vector<std::array<int, 3>>& tris_a = tris_.find(tA)->second;
                const std::vector<std::array<int, 3>>& tris_b = tris_.find(tB)->second;
                const std::vector<gp_Pnt>& verts_a = verts_.find(tA)->second;
                const std::vector<gp_Pnt>& verts_b = verts_.find(tB)->second;
                const std::vector<gp_Vec>& normals_a = normals_.find(tA)->second;
                const std::vector<gp_Vec>& normals_b = normals_.find(tB)->second;

                for (const auto& pair : bvh_clashes) {
                    const int bvh_a_i = pair.first;
                    const std::vector<int>& bvh_b_is = pair.second;

                    for (int i=bvh_a->BegPrimitive(bvh_a_i); i<=bvh_a->EndPrimitive(bvh_a_i); ++i) {
                        const std::array<int, 3>& tri = tris_a[i];
                        const gp_Pnt& v1_a_pnt = verts_a[tri[0]];
                        const gp_Pnt& v2_a_pnt = verts_a[tri[1]];
                        const gp_Pnt& v3_a_pnt = verts_a[tri[2]];
                        const gp_Vec& normal_a = normals_a[i];

                        const gp_Vec v1_a_vec(v1_a_pnt.XYZ());
                        const gp_Vec v2_a_vec(v2_a_pnt.XYZ());
                        const gp_Vec v3_a_vec(v3_a_pnt.XYZ());

                        for (const auto& bvh_b_i : bvh_b_is) {
                            for (int j=bvh_b->BegPrimitive(bvh_b_i); j<=bvh_b->EndPrimitive(bvh_b_i); ++j) {
                                const std::array<int, 3>& tri = tris_b[j];
                                const gp_Pnt& v1_b_pnt = verts_b[tri[0]];
                                const gp_Pnt& v2_b_pnt = verts_b[tri[1]];
                                const gp_Pnt& v3_b_pnt = verts_b[tri[2]];
                                const gp_Vec& normal_b = normals_b[j];

                                tri_count_++;

                                const gp_Vec v1_b_vec(v1_b_pnt.XYZ());
                                const gp_Vec v2_b_vec(v2_b_pnt.XYZ());
                                const gp_Vec v3_b_vec(v3_b_pnt.XYZ());

                                // Allow a deviation of 0.25 degrees in coplanarity check
                                if (std::abs(normal_a.Dot(normal_b)) >= 0.99999f) {
                                    continue;
                                }

                                gp_Vec int1, int2;
                                if (trianglesIntersect(v1_a_vec, v2_a_vec, v3_a_vec, v1_b_vec, v2_b_vec, v3_b_vec, int1, int2, ! allow_touching)) {
                                    if (allow_touching) {
                                        return {2, tA, tB, 0, {int1.X(), int1.Y(), int1.Z()}, {int2.X(), int2.Y(), int2.Z()}};
                                    }

                                    // A non-touching collision is defined as two triangles that:
                                    //  1. Are not coplanar
                                    //  2. The point of intersection is not along the edge of triangle A.
                                    //  3. The point of intersection is not a vertex of triangle B.

                                    if (
                                        ! is_point_on_line(int1, v1_a_vec, v2_a_vec)
                                        && ! is_point_on_line(int1, v1_a_vec, v3_a_vec)
                                        && ! is_point_on_line(int1, v2_a_vec, v3_a_vec)
                                    ) {
                                        if (
                                            (v1_b_vec - int1).Magnitude() > 1e-4
                                            && (v2_b_vec - int1).Magnitude() > 1e-4
                                            && (v3_b_vec - int1).Magnitude() > 1e-4
                                        ) {
                                            return {2, tA, tB, 0, {int1.X(), int1.Y(), int1.Z()}, {int2.X(), int2.Y(), int2.Z()}};
                                        }
                                    }

                                    if (
                                        ! is_point_on_line(int1, v1_b_vec, v2_b_vec)
                                        && ! is_point_on_line(int1, v1_b_vec, v3_b_vec)
                                        && ! is_point_on_line(int1, v2_b_vec, v3_b_vec)
                                    ) {
                                        if (
                                            (v1_a_vec - int1).Magnitude() > 1e-4
                                            && (v2_a_vec - int1).Magnitude() > 1e-4
                                            && (v3_a_vec - int1).Magnitude() > 1e-4
                                        ) {
                                            return {2, tA, tB, 0, {int1.X(), int1.Y(), int1.Z()}, {int2.X(), int2.Y(), int2.Z()}};
                                        }
                                    }

                                    if (
                                        ! is_point_on_line(int2, v1_a_vec, v2_a_vec)
                                        && ! is_point_on_line(int2, v1_a_vec, v3_a_vec)
                                        && ! is_point_on_line(int2, v2_a_vec, v3_a_vec)
                                    ) {
                                        if (
                                            (v1_b_vec - int2).Magnitude() > 1e-4
                                            && (v2_b_vec - int2).Magnitude() > 1e-4
                                            && (v3_b_vec - int2).Magnitude() > 1e-4
                                        ) {
                                            return {2, tA, tB, 0, {int2.X(), int2.Y(), int2.Z()}, {int1.X(), int1.Y(), int1.Z()}};
                                        }
                                    }

                                    if (
                                        ! is_point_on_line(int2, v1_b_vec, v2_b_vec)
                                        && ! is_point_on_line(int2, v1_b_vec, v3_b_vec)
                                        && ! is_point_on_line(int2, v2_b_vec, v3_b_vec)
                                    ) {
                                        if (
                                            (v1_a_vec - int2).Magnitude() > 1e-4
                                            && (v2_a_vec - int2).Magnitude() > 1e-4
                                            && (v3_a_vec - int2).Magnitude() > 1e-4
                                        ) {
                                            return {2, tA, tB, 0, {int2.X(), int2.Y(), int2.Z()}, {int1.X(), int1.Y(), int1.Z()}};
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                return {-1, tA, tB, 0, {0, 0, 0}, {0, 0, 0}};
            }

			clash test_clearance(const T& tA, const T& tB, double clearance, bool check_all) const {
                // Collide BVH trees of shape A vs B
                opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>> bvh_a = bvhs_.find(tA)->second;
                opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>> bvh_b = bvhs_.find(tB)->second;

                std::unordered_map<int, std::vector<int>> bvh_clashes = clash_bvh(bvh_a, bvh_b, clearance);
                if (bvh_clashes.empty()) {
                    return {-1, tA, tB, 0, {0, 0, 0}, {0, 0, 0}};
                }

                const std::vector<std::array<int, 3>>& tris_a = tris_.find(tA)->second;
                const std::vector<std::array<int, 3>>& tris_b = tris_.find(tB)->second;
                const std::vector<gp_Pnt>& verts_a = verts_.find(tA)->second;
                const std::vector<gp_Pnt>& verts_b = verts_.find(tB)->second;

                double min_clearance = std::numeric_limits<double>::infinity();
                std::array<double, 3> clearance_point1;
                std::array<double, 3> clearance_point2;

                for (const auto& pair : bvh_clashes) {
                    const int bvh_a_i = pair.first;
                    const std::vector<int>& bvh_b_is = pair.second;

                    for (int i=bvh_a->BegPrimitive(bvh_a_i); i<=bvh_a->EndPrimitive(bvh_a_i); ++i) {
                        const std::array<int, 3>& tri = tris_a[i];
                        const gp_Pnt& v1_a_pnt = verts_a[tri[0]];
                        const gp_Pnt& v2_a_pnt = verts_a[tri[1]];
                        const gp_Pnt& v3_a_pnt = verts_a[tri[2]];

                        const gp_Vec v1_a_vec(v1_a_pnt.XYZ());
                        const gp_Vec v2_a_vec(v2_a_pnt.XYZ());
                        const gp_Vec v3_a_vec(v3_a_pnt.XYZ());

                        const std::array<gp_Vec, 3> p = {v1_a_vec, v2_a_vec, v3_a_vec};

                        for (const auto& bvh_b_i : bvh_b_is) {
                            for (int j=bvh_b->BegPrimitive(bvh_b_i); j<=bvh_b->EndPrimitive(bvh_b_i); ++j) {
                                const std::array<int, 3>& tri = tris_b[j];
                                const gp_Pnt& v1_b_pnt = verts_b[tri[0]];
                                const gp_Pnt& v2_b_pnt = verts_b[tri[1]];
                                const gp_Pnt& v3_b_pnt = verts_b[tri[2]];

                                tri_count_++;

                                const gp_Vec v1_b_vec(v1_b_pnt.XYZ());
                                const gp_Vec v2_b_vec(v2_b_pnt.XYZ());
                                const gp_Vec v3_b_vec(v3_b_pnt.XYZ());

                                const std::array<gp_Vec, 3> q = {v1_b_vec, v2_b_vec, v3_b_vec};

                                gp_Vec cp;
                                gp_Vec cq;

                                // https://stackoverflow.com/questions/53602907/algorithm-to-find-minimum-distance-between-two-triangles
                                distanceTriangleTriangleSquared(cp, cq, p, q);

                                double distance = (cq - cp).Magnitude();
                                if (distance < clearance && distance < min_clearance) {
                                    min_clearance = distance;
                                    clearance_point1 = {cp.X(), cp.Y(), cp.Z()};
                                    clearance_point2 = {cq.X(), cq.Y(), cq.Z()};
                                    if ( ! check_all || min_clearance < 1e-4) {
                                        return {3, tA, tB, min_clearance, clearance_point1, clearance_point2};
                                    }
                                }
                            }
                        }
                    }
                }

                if (min_clearance < clearance) {
                    return {3, tA, tB, min_clearance, clearance_point1, clearance_point2};

                }

                return {-1, tA, tB, 0, {0, 0, 0}, {0, 0, 0}};
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

		protected:

			// @todo this is ugly, embed this in the return type
			mutable std::vector<double> distances_;
			mutable std::vector<double> protrusion_distances_;
            mutable long long tri_count_ = 0;

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

			void add_triangulation(const T& t, const TopoDS_Shape& s) {
                // Note that the original add function is also used elsewhere (e.g. boolean_utils.cpp)
                // We don't want to randomly add triangulated voids in our
                // tree, so for now this is a separate function.

				Bnd_Box b;
				BRepBndLib::AddClose(s, b);
                aabbs_[t] = b;

                Bnd_OBB obb;
                // If IsOptimal = True it doubles the execution time.
                BRepBndLib::AddOBB(s, obb, true, false, false);
                obbs_[t] = obb;

                max_protrusions_[t] = std::min(std::min(obb.XHSize(), obb.YHSize()), obb.ZHSize()) * 2;

                int original_tris_index = 0;
                std::vector<std::array<int, 3>> original_tris;
                std::vector<gp_Pnt> verts;
                std::vector<gp_Vec> original_normals;

                // Attempt to copy exactly what BRepExtrema_TriangleSet is doing under the hood.
                const auto builder = new BVH_LinearBuilder<Standard_Real, 3> (BVH_Constants_LeafNodeSizeDefault, BVH_Constants_MaxTreeDepth);
                BVH_Triangulation<Standard_Real, 3> triangulation(builder);

                BRepExtrema_ShapeList shape_list;
                std::vector<bool> is_reversed;
                TopExp_Explorer exp_f;
                for (exp_f.Init(s, TopAbs_FACE); exp_f.More(); exp_f.Next()) {
                    shape_list.Append(TopoDS::Face(exp_f.Current()));

                    TopoDS_Face f = TopoDS::Face(exp_f.Current());
                    is_reversed.push_back(f.Orientation() == TopAbs_REVERSED);
                }

                // Standard_Boolean BRepExtrema_TriangleSet::Init (const BRepExtrema_ShapeList& theShapes)
                Standard_Boolean isOK = Standard_True;
                for (Standard_Integer aShapeIdx = 0; aShapeIdx < shape_list.Size() && isOK; ++aShapeIdx)
                {
                    if (shape_list (aShapeIdx).ShapeType() == TopAbs_FACE) {
                        // isOK = initFace (TopoDS::Face (shape_list(aShapeIdx)), aShapeIdx);
                        // Standard_Boolean BRepExtrema_TriangleSet::initFace (const TopoDS_Face& theFace, const Standard_Integer theIndex)

                        TopoDS_Face theFace = TopoDS::Face (shape_list(aShapeIdx));
                        Standard_Integer theIndex = aShapeIdx;
                        TopLoc_Location aLocation;

                        bool is_reversed = theFace.Orientation() == TopAbs_REVERSED;

                        Handle(Poly_Triangulation) aTriangulation = BRep_Tool::Triangulation (theFace, aLocation);
                        if (aTriangulation.IsNull())
                        {
                            isOK = false;
                        }

                        const Standard_Integer aVertOffset = static_cast<Standard_Integer> (verts.size()) - 1;

                        // initNodes (aTriangulation->MapNodeArray()->ChangeArray1(), aLocation.Transformation(), theIndex);
                        // void BRepExtrema_TriangleSet::initNodes (const TColgp_Array1OfPnt& theNodes, const gp_Trsf& theTrsf, const Standard_Integer theIndex)
                        TColgp_Array1OfPnt theNodes = aTriangulation->MapNodeArray()->ChangeArray1();
                        gp_Trsf theTrsf = aLocation.Transformation();

                        for (Standard_Integer aVertIdx = 1; aVertIdx <= theNodes.Size(); ++aVertIdx)
                        {
                            gp_Pnt aVertex = theNodes.Value (aVertIdx);
                            aVertex.Transform (theTrsf);
                            triangulation.Vertices.push_back (BVH_Vec3d (aVertex.X(), aVertex.Y(), aVertex.Z()));
                            verts.push_back(aVertex);
                            // myShapeIdxOfVtxVec.Append (theIndex);
                        }

                        // myNumVtxInShapeVec.SetValue (theIndex, theNodes.Size());

                        for (Standard_Integer aTriIdx = 1; aTriIdx <= aTriangulation->NbTriangles(); ++aTriIdx)
                        {
                            Standard_Integer aVertex1;
                            Standard_Integer aVertex2;
                            Standard_Integer aVertex3;

                            if (is_reversed) {
                                aTriangulation->Triangle (aTriIdx).Get (aVertex3, aVertex2, aVertex1);
                            } else {
                                aTriangulation->Triangle (aTriIdx).Get (aVertex1, aVertex2, aVertex3);
                            }

                            const auto& v1_pnt = verts[aVertex1 + aVertOffset];
                            const auto& v2_pnt = verts[aVertex2 + aVertOffset];
                            const auto& v3_pnt = verts[aVertex3 + aVertOffset];
                            gp_Vec dir1(v1_pnt, v2_pnt);
                            gp_Vec dir2(v1_pnt, v3_pnt);
                            gp_Vec cross_product = dir1.Crossed(dir2);
                            if (cross_product.Magnitude() > Precision::Confusion()) {
                                triangulation.Elements.push_back (BVH_Vec4i (
                                    aVertex1 + aVertOffset,
                                    aVertex2 + aVertOffset,
                                    aVertex3 + aVertOffset,
                                    original_tris_index));
                                    //theIndex));
                                original_tris_index++;
                                original_tris.push_back({
                                    aVertex1 + aVertOffset,
                                    aVertex2 + aVertOffset,
                                    aVertex3 + aVertOffset
                                });
                                original_normals.push_back(cross_product.Normalized());
                            }
                        }

                        // myNumTrgInShapeVec.SetValue (theIndex, aTriangulation->NbTriangles());

                        isOK = true;
                    } else if (shape_list (aShapeIdx).ShapeType() == TopAbs_EDGE) {
                        // isOK = initEdge (TopoDS::Edge (shape_list(aShapeIdx)), aShapeIdx);
                        // Should never occur, we don't pass in edges.
                    }
                }

                triangulation.MarkDirty();
                const auto bvh = triangulation.BVH();

                // After BVH is constructed, triangles are reordered
                std::vector<std::array<int, 3>> tris(triangulation.Size());
                std::vector<gp_Vec> normals(triangulation.Size());

                for (int i=0; i<triangulation.Size(); ++i) {
                    const auto& el = triangulation.Elements[i];
                    tris[i] = original_tris[el[3]];
                    normals[i] = original_normals[el[3]];
                }

                bvhs_[t] = bvh;
                is_manifold_[t] = IfcGeom::util::is_manifold(s);
                tris_[t] = std::move(tris);
                verts_[t] = std::move(verts);
                normals_[t] = std::move(normals);
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

            std::unique_ptr<BVH_BoxSet<double, 3>> build_box_set(const std::vector<T>& elements) const {
                double x, y, z, X, Y, Z;
                std::unique_ptr<BVH_BoxSet<double, 3>> box_set = std::make_unique<BVH_BoxSet<double, 3>>();
                for (int i=0; i<elements.size(); ++i) {
                    auto it = aabbs_.find(elements[i]);
                    if (it == aabbs_.end()) {
                        continue;
                    }
                    const auto& aabb = it->second;
                    aabb.Get(x, y, z, X, Y, Z);
                    const BVH_Box<Standard_Real, 3>::BVH_VecNt min(x, y, z);
                    const BVH_Box<Standard_Real, 3>::BVH_VecNt max(X, Y, Z);
                    BVH_Box<Standard_Real, 3> bvh_box(min, max);
                    box_set->Add(i, bvh_box);
                }
                return box_set;
            }

            struct clash_task {
                T a, b;
            };

            std::vector<std::vector<clash_task>> allocate_tasks_to_threads(
                    std::vector<clash_task>& task_queue) const {
                int num_threads = std::thread::hardware_concurrency();
                std::vector<std::vector<clash_task>> threaded_tasks(num_threads);

                size_t tasks_per_thread = task_queue.size() / num_threads;
                for (int i = 0; i < num_threads; ++i) {
                    auto startIter = std::next(task_queue.begin(), i * tasks_per_thread);
                    auto endIter = (i == num_threads - 1) ? task_queue.end() : std::next(startIter, tasks_per_thread);
                    threaded_tasks[i] = std::vector<clash_task>(startIter, endIter);
                }
                return threaded_tasks;
            }

            std::vector<clash> clash_intersection_many(
                    const std::vector<T>& set_a, const std::vector<T>& set_b,
                    double tolerance = 0.002, bool check_all = true
                ) const {
                std::vector<clash_task> task_queue;
                std::vector<clash> results;

                std::unique_ptr<BVH_BoxSet<double, 3>> box_set_a = build_box_set(set_a);
                std::unique_ptr<BVH_BoxSet<double, 3>> box_set_b = build_box_set(set_b);

                const opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>>& bvh_a = box_set_a->BVH();
                const opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>>& bvh_b = box_set_b->BVH();

                std::unordered_map<int, std::vector<int>> bvh_clashes = clash_bvh(bvh_a, bvh_b, 0.0);

                if (bvh_clashes.empty()) {
                    return results;
                }

                std::map<T, std::set<T>> tested_pairs;

                for (const auto& pair : bvh_clashes) {
                    const int bvh_a_i = pair.first;
                    const std::vector<int>& bvh_b_is = pair.second;
                    for (int i=bvh_a->BegPrimitive(bvh_a_i); i<=bvh_a->EndPrimitive(bvh_a_i); ++i) {
                        const T& t_a = set_a[box_set_a->Element(i)];
                        for (const auto& bvh_b_i : bvh_b_is) {
                            for (int j=bvh_b->BegPrimitive(bvh_b_i); j<=bvh_b->EndPrimitive(bvh_b_i); ++j) {
                                const T& t_b = set_b[box_set_b->Element(j)];
                                if (t_a == t_b) {
                                    continue;
                                }

                                if (tested_pairs[t_a].insert(t_b).second) {
                                    tested_pairs[t_b].insert(t_a).second;
                                } else {
                                    continue;
                                }

                                task_queue.emplace_back(clash_task{t_a, t_b});
                            }
                        }
                    }
                }

                std::vector<std::vector<clash_task>> threaded_tasks = allocate_tasks_to_threads(task_queue);

                std::vector<std::thread> threads;
                std::mutex results_mutex;

                for (auto& tasks : threaded_tasks) {
                    threads.emplace_back([this, &tasks, &results, &results_mutex, tolerance, check_all] {
                        std::vector<clash> thread_results;
                        for (auto& task : tasks) {
                            const auto& obb_a = obbs_.find(task.a)->second;
                            auto obb_b = obbs_.find(task.b)->second;
                            obb_b.Enlarge(-tolerance);
                            if (obb_a.IsOut(obb_b)) {
                                continue;
                            }

                            bool has_clash = false;
                            bool is_manifold = false;
                            clash result;

                            if (is_manifold_.find(task.b)->second) {
                                is_manifold = true;
                                clash intersection = test_intersection(task.a, task.b, tolerance, check_all);
                                if (intersection.clash_type != -1) {
                                    has_clash = true;
                                    result = intersection;
                                    if ( ! check_all) {
                                        thread_results.push_back(result);
                                        continue;
                                    }
                                }
                            }

                            if (is_manifold_.find(task.a)->second) {
                                is_manifold = true;
                                clash intersection = test_intersection(task.b, task.a, tolerance, check_all);
                                if (intersection.clash_type != -1) {
                                    // Replace the clash result if any of these criteria apply:
                                    // - We don't have a clash yet
                                    // - Our previous clash is piercing, and our new one is a protrusion
                                    // - We have the same clash type, but our clash is more severe
                                    if (
                                        ! has_clash
                                        || (result.clash_type == 1 && intersection.clash_type == 0)
                                        || (
                                               result.clash_type == intersection.clash_type
                                               && intersection.distance > result.distance
                                           )
                                    ) {
                                        has_clash = true;
                                        result = intersection;
                                    }
                                }
                            }

                            if ( ! is_manifold) {
                                clash collision = test_collision(task.a, task.b, false);
                                if (collision.clash_type != -1) {
                                    has_clash = true;
                                    result = collision;
                                }
                            }

                            if (has_clash) {
                                thread_results.push_back(result);
                            }
                        }
                        {
                            std::lock_guard<std::mutex> lock(results_mutex);
                            results.insert(results.end(), thread_results.begin(), thread_results.end());
                        }
                    });
                }

                for (auto& thread : threads) {
                    if (thread.joinable()) {
                        thread.join();
                    }
                }

                return results;
            }

            std::vector<clash> clash_collision_many(
                    const std::vector<T>& set_a, const std::vector<T>& set_b, bool allow_touching = false
                ) const {
                std::vector<clash_task> task_queue;
                std::vector<clash> results;

                std::unique_ptr<BVH_BoxSet<double, 3>> box_set_a = build_box_set(set_a);
                std::unique_ptr<BVH_BoxSet<double, 3>> box_set_b = build_box_set(set_b);

                const opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>>& bvh_a = box_set_a->BVH();
                const opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>>& bvh_b = box_set_b->BVH();

                std::unordered_map<int, std::vector<int>> bvh_clashes = clash_bvh(bvh_a, bvh_b, 0.0);

                if (bvh_clashes.empty()) {
                    return results;
                }

                std::map<T, std::set<T>> tested_pairs;

                for (const auto& pair : bvh_clashes) {
                    const int bvh_a_i = pair.first;
                    const std::vector<int>& bvh_b_is = pair.second;
                    for (int i=bvh_a->BegPrimitive(bvh_a_i); i<=bvh_a->EndPrimitive(bvh_a_i); ++i) {
                        const T& t_a = set_a[box_set_a->Element(i)];
                        for (const auto& bvh_b_i : bvh_b_is) {
                            for (int j=bvh_b->BegPrimitive(bvh_b_i); j<=bvh_b->EndPrimitive(bvh_b_i); ++j) {
                                const T& t_b = set_b[box_set_b->Element(j)];
                                if (t_a == t_b) {
                                    continue;
                                }

                                if (tested_pairs[t_a].insert(t_b).second) {
                                    tested_pairs[t_b].insert(t_a).second;
                                } else {
                                    continue;
                                }

                                task_queue.emplace_back(clash_task{t_a, t_b});
                            }
                        }
                    }
                }

                std::vector<std::vector<clash_task>> threaded_tasks = allocate_tasks_to_threads(task_queue);

                std::vector<std::thread> threads;
                std::mutex results_mutex;

                for (auto& tasks : threaded_tasks) {
                    threads.emplace_back([this, &tasks, &results, &results_mutex, allow_touching] {
                        std::vector<clash> thread_results;
                        for (auto& task : tasks) {
                            const auto& obb_a = obbs_.find(task.a)->second;
                            auto obb_b = obbs_.find(task.b)->second;
                            obb_b.Enlarge(-0.001);
                            if (obb_a.IsOut(obb_b)) {
                                continue;
                            }

                            clash result = test_collision(task.a, task.b, allow_touching);
                            if (result.clash_type != -1) {
                                thread_results.push_back(result);
                            }
                        }
                        {
                            std::lock_guard<std::mutex> lock(results_mutex);
                            results.insert(results.end(), thread_results.begin(), thread_results.end());
                        }
                    });
                }

                for (auto& thread : threads) {
                    if (thread.joinable()) {
                        thread.join();
                    }
                }

                return results;
            }

            std::vector<clash> clash_clearance_many(
                    const std::vector<T>& set_a, const std::vector<T>& set_b,
                    double clearance = 0.05, bool check_all = false
                ) const {
                std::vector<clash_task> task_queue;
                std::vector<clash> results;

                std::unique_ptr<BVH_BoxSet<double, 3>> box_set_a = build_box_set(set_a);
                std::unique_ptr<BVH_BoxSet<double, 3>> box_set_b = build_box_set(set_b);

                const opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>>& bvh_a = box_set_a->BVH();
                const opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>>& bvh_b = box_set_b->BVH();

                std::unordered_map<int, std::vector<int>> bvh_clashes = clash_bvh(bvh_a, bvh_b, clearance);

                if (bvh_clashes.empty()) {
                    return results;
                }

                std::map<T, std::set<T>> tested_pairs;

                for (const auto& pair : bvh_clashes) {
                    const int bvh_a_i = pair.first;
                    const std::vector<int>& bvh_b_is = pair.second;
                    for (int i=bvh_a->BegPrimitive(bvh_a_i); i<=bvh_a->EndPrimitive(bvh_a_i); ++i) {
                        const T& t_a = set_a[box_set_a->Element(i)];
                        for (const auto& bvh_b_i : bvh_b_is) {
                            for (int j=bvh_b->BegPrimitive(bvh_b_i); j<=bvh_b->EndPrimitive(bvh_b_i); ++j) {
                                const T& t_b = set_b[box_set_b->Element(j)];
                                if (t_a == t_b) {
                                    continue;
                                }

                                if (tested_pairs[t_a].insert(t_b).second) {
                                    tested_pairs[t_b].insert(t_a).second;
                                } else {
                                    continue;
                                }

                                task_queue.emplace_back(clash_task{t_a, t_b});
                            }
                        }
                    }
                }

                std::vector<std::vector<clash_task>> threaded_tasks = allocate_tasks_to_threads(task_queue);

                std::vector<std::thread> threads;
                std::mutex results_mutex;

                for (auto& tasks : threaded_tasks) {
                    threads.emplace_back([this, &tasks, &results, &results_mutex, clearance, check_all] {
                        std::vector<clash> thread_results;
                        for (auto& task : tasks) {
                            const auto& obb_a = obbs_.find(task.a)->second;
                            auto obb_b = obbs_.find(task.b)->second;
                            obb_b.Enlarge(clearance);
                            if (obb_a.IsOut(obb_b)) {
                                continue;
                            }

                            clash result = test_clearance(task.a, task.b, clearance, check_all);
                            if (result.clash_type != -1) {
                                thread_results.push_back(result);
                            }
                        }
                        {
                            std::lock_guard<std::mutex> lock(results_mutex);
                            results.insert(results.end(), thread_results.begin(), thread_results.end());
                        }
                    });
                }

                for (auto& thread : threads) {
                    if (thread.joinable()) {
                        thread.join();
                    }
                }

                return results;
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
            std::map<T, Bnd_Box> aabbs_;
            std::map<T, Bnd_OBB> obbs_; 
            std::map<T, double> max_protrusions_; 
            std::map<T, opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>>> bvhs_; 
            std::unordered_map<T, bool> is_manifold_;
            std::unordered_map<T, std::vector<std::array<int, 3>>> tris_;
            std::unordered_map<T, std::vector<gp_Pnt>> verts_;
            std::unordered_map<T, std::vector<gp_Vec>> normals_;

            // Temporary structures for H5
            std::vector<IfcGeom::TriangulationElement*> triangulation_elements_;
            std::map<IfcUtil::IfcBaseClass*, std::string> global_ids_;
            std::map<IfcUtil::IfcBaseClass*, std::string> names_;
            std::map<IfcUtil::IfcBaseClass*, std::vector<double>> placements_;
            std::map<std::string, std::vector<double>> local_verts_;
            std::map<std::string, std::vector<int>> local_faces_;
            std::map<std::string, std::vector<IfcGeom::Material>> local_materials_;
            std::map<std::string, std::vector<int>> local_material_ids_;
			
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

		void add_triangulation_element(IfcGeom::TriangulationElement* elem) {
            triangulation_elements_.push_back(elem);
            const auto& t = elem->product();
            const auto geometry_id = elem->geometry().id();
            placements_[t] = elem->transformation().matrix().data();
            names_[t] = elem->name();
            global_ids_[t] = elem->guid();

            if (local_verts_.find(geometry_id) != local_verts_.end()) {
                return;
            }

            local_verts_[geometry_id] = elem->geometry().verts();
            local_faces_[geometry_id] = elem->geometry().faces();
            local_materials_[geometry_id] = elem->geometry().materials();
            local_material_ids_[geometry_id] = elem->geometry().material_ids();
        }

		void add_element(IfcGeom::BRepElement* elem, bool should_triangulate=false) {
			if (!elem) {
				return;
			}
			auto compound = elem->geometry().as_compound();
			compound.Move(elem->transformation().data());
            if (should_triangulate) {
                add_triangulation(elem->product(), compound);
            } else {
                add(elem->product(), compound);
            }
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
					size_t index;
					if (sit == styles_.end()) {
						index = styles_.size();
						styles_.push_back(*adaptor);
					} else {
						index = std::distance(styles_.begin(), sit);
					}

					TopExp_Explorer exp(it.Value(), TopAbs_FACE);
					for (; exp.More(); exp.Next()) {
						face_styles_.Bind(exp.Current(), (int) index);
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
