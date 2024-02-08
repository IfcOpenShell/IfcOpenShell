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

#include <stack>
#include <unordered_map>
#include <unordered_set>
#include <BRepExtrema_TriangleSet.hxx>
#include <BRepLProp_SLProps.hxx>
#include <BVH_BinaryTree.hxx>
#include <BVH_Box.hxx>
#include <BVH_LinearBuilder.hxx>
#include <BVH_Tree.hxx>
#include <Bnd_OBB.hxx>
#include <GeomAPI_ProjectPointOnSurf.hxx>
#include <Geom_Plane.hxx>
#include <IntTools_FaceFace.hxx>
#include <STEPConstruct_PointHasher.hxx>
#include <boost/stacktrace.hpp>
#include "clash_utils.h"


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
            bool is_shape_manifold(const TopoDS_Shape& s) {
                TopExp_Explorer exp(s, TopAbs_SHELL);
                bool is_closed = false;
                while (exp.More()) {
                    is_closed = true;
                    TopoDS_Shell shell = TopoDS::Shell(exp.Current());
                    TopTools_IndexedDataMapOfShapeListOfShape edgeFaceMap;
                    TopExp::MapShapesAndAncestors(s, TopAbs_EDGE, TopAbs_FACE, edgeFaceMap);

                    for (int i = 1; i <= edgeFaceMap.Extent(); ++i) {
                        if (edgeFaceMap(i).Extent() < 2) {
                            // This edge is not shared by two faces, indicating a potential opening
                            return false;
                        }
                    }
                    exp.Next();
                }
                return is_closed;
            }

            bool is_point_in_shape(
                    const gp_Pnt& v,
                    const opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>>& bvh,
                    const std::vector<std::array<int, 3>>& tris,
                    const std::vector<gp_Pnt>& verts,
                    // In the case of "touching" rays, let's check again!
                    bool should_check_again = false
                    ) const {
                ray v_ray;
                v_ray.origin[0] = v.X();
                v_ray.origin[1] = v.Y();
                v_ray.origin[2] = v.Z();

                if (should_check_again) {
                    // The first check may be incorrect if it intersects
                    // exactly between triangles or on edges of triangles.
                    // A second check is used to "double check" the results.
                    // The second check is perpendicular because AEC objects
                    // are typically symmetrical along an axis, and goes down
                    // because there's typically less stuff down there.
                    v_ray.dir[0] = 0.0f;
                    v_ray.dir[1] = 0.0f;
                    v_ray.dir[2] = -1.0f;
                    v_ray.dir_inv[0] = INFINITY; // 1.0f/dir[0]
                    v_ray.dir_inv[1] = INFINITY; // 1.0f/dir[1]
                    v_ray.dir_inv[2] = -1.0f; // 1.0f/dir[2]
                } else {
                    v_ray.dir[0] = 1.0f;
                    v_ray.dir[1] = 0.0f;
                    v_ray.dir[2] = 0.0f;
                    v_ray.dir_inv[0] = 1.0f; // 1.0f/dir[0]
                    v_ray.dir_inv[1] = INFINITY; // 1.0f/dir[1]
                    v_ray.dir_inv[2] = INFINITY; // 1.0f/dir[2]
                }

                gp_Vec ray_origin(v.X(), v.Y(), v.Z());
                gp_Vec ray_vector(v_ray.dir[0], v_ray.dir[1], v_ray.dir[2]);

                int total_intersections = 0;

                std::stack<int> stack;
                stack.push(0);

                while ( ! stack.empty()) {
                    int i = stack.top();
                    stack.pop();

                    BVH_TreeBase<Standard_Real, 3>::BVH_VecNt min_point = bvh->MinPoint(i);
                    BVH_TreeBase<Standard_Real, 3>::BVH_VecNt max_point = bvh->MaxPoint(i);

                    box box;
                    // + 1e-5 for tolerance
                    box.corners[0][0] = min_point[0] - 1e-5;
                    box.corners[0][1] = min_point[1] - 1e-5;
                    box.corners[0][2] = min_point[2] - 1e-5;
                    box.corners[1][0] = max_point[0] + 1e-5;
                    box.corners[1][1] = max_point[1] + 1e-5;
                    box.corners[1][2] = max_point[2] + 1e-5;
                    /*
                    std::cout << "Ray " 
                        << v_ray.origin[0] << " "
                        << v_ray.origin[1] << " "
                        << v_ray.origin[2] << " "
                        << std::endl;
                    std::cout << "Box " 
                        << min_point[0] << " "
                        << min_point[1] << " "
                        << min_point[2] << " "
                        << max_point[0] << " "
                        << max_point[1] << " "
                        << max_point[2] << " "
                        << std::endl;
                    */

                    if ( ! is_intersect_ray_box(&v_ray, &box)) {
                        continue;
                    }
                    //std::cout << "Ray hits box" << std::endl;
                    if (bvh->IsOuter(i)) {
                        //std::cout << "Ray hits leaf" << std::endl;
                        // Do ray triangle check.
                        for (int j=bvh->BegPrimitive(i); j<=bvh->EndPrimitive(i); ++j) {
                            const std::array<int, 3>& tri = tris[j];

                            gp_Vec ta(verts[tri[0]].XYZ());
                            gp_Vec tb(verts[tri[1]].XYZ());
                            gp_Vec tc(verts[tri[2]].XYZ());

                            /*
                            std::cout << "ray origin " << ray_origin.X() << " " << ray_origin.Y() << " " << ray_origin.Z() << std::endl;
                            std::cout << "inside-tri " << ta.X() << " " << ta.Y() << " " << ta.Z() << std::endl;
                            std::cout << "inside-tri " << tb.X() << " " << tb.Y() << " " << tb.Z() << std::endl;
                            std::cout << "inside-tri " << tc.X() << " " << tc.Y() << " " << tc.Z() << std::endl;
                            */
                            double at, au, av;
                            if (intersectRayTriangle(ray_origin, ray_vector, ta, tb, tc, at, au, av, false)) {
                                // At is a signed intersection distance (positive is along +ray_vector)
                                if (at > -1e-5) {
                                    total_intersections++;
                                }
                            }
                        }
                    } else {
                        stack.push(bvh->Child<0>(i));
                        stack.push(bvh->Child<1>(i));
                    }
                }

                return total_intersections % 2 != 0;
            }

            std::tuple<
                double,
                std::array<double, 3>,
                std::array<double, 3>
                > pierce_shape(
                    const gp_Vec& e1,
                    const gp_Vec& e2,
                    const opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>>& bvh,
                    const std::vector<bool>& valid_tris,
                    const std::vector<std::array<int, 3>>& tris,
                    const std::vector<gp_Pnt>& verts,
                    const std::vector<gp_Vec>& normals
                    ) const {
                const gp_Vec& ray_origin = e1;
                gp_Vec ray_vector = e2 - e1;
                double edge_length = ray_vector.Magnitude();

                std::array<double, 3> min_int;
                std::array<double, 3> max_int;

                ray_vector.Normalize();

                ray v_ray;
                v_ray.origin[0] = ray_origin.X();
                v_ray.origin[1] = ray_origin.Y();
                v_ray.origin[2] = ray_origin.Z();

                v_ray.dir[0] = ray_vector.X();
                v_ray.dir[1] = ray_vector.Y();
                v_ray.dir[2] = ray_vector.Z();
                v_ray.dir_inv[0] = 1.0f / ray_vector.X();
                v_ray.dir_inv[1] = 1.0f / ray_vector.Y();
                v_ray.dir_inv[2] = 1.0f / ray_vector.Z();

                double min_distance = std::numeric_limits<double>::infinity();
                double max_distance = -std::numeric_limits<double>::infinity();

                std::stack<int> stack;
                stack.push(0);

                while ( ! stack.empty()) {
                    int i = stack.top();
                    stack.pop();

                    BVH_TreeBase<Standard_Real, 3>::BVH_VecNt min_point = bvh->MinPoint(i);
                    BVH_TreeBase<Standard_Real, 3>::BVH_VecNt max_point = bvh->MaxPoint(i);

                    box box;
                    // + 1e-5 for tolerance
                    box.corners[0][0] = min_point[0] - 1e-5;
                    box.corners[0][1] = min_point[1] - 1e-5;
                    box.corners[0][2] = min_point[2] - 1e-5;
                    box.corners[1][0] = max_point[0] + 1e-5;
                    box.corners[1][1] = max_point[1] + 1e-5;
                    box.corners[1][2] = max_point[2] + 1e-5;

                    if ( ! is_intersect_ray_box(&v_ray, &box)) {
                        continue;
                    }
                    if (bvh->IsOuter(i)) {
                        // Do ray triangle check.
                        for (int j=bvh->BegPrimitive(i); j<=bvh->EndPrimitive(i); ++j) {
                            if ( ! valid_tris[j]) {
                                continue;
                            }
                            const std::array<int, 3>& tri = tris[j];
                            const gp_Vec& normal = normals[j];

                            if (std::abs(normal.Dot(ray_vector)) < 1e-3) {
                                continue; // This ray is coplanar to the triangle
                            }

                            gp_Vec ta(verts[tri[0]].XYZ());
                            gp_Vec tb(verts[tri[1]].XYZ());
                            gp_Vec tc(verts[tri[2]].XYZ());

                            double at, au, av;
                            // Do box check first?
                            if (intersectRayTriangle(ray_origin, ray_vector, ta, tb, tc, at, au, av, false)) {
                                // At is a signed intersection distance (positive is along +ray_vector)
                                if (at > 0 && at < edge_length) {
                                    double aw = 1.0f - au - av; // Barycentric coordinate for ta
                                    gp_Vec int_vec = aw * ta + au * tb + av * tc; // Intersection point

                                    if (
                                        is_point_on_line(int_vec, ta, tb)
                                        || is_point_on_line(int_vec, ta, tc)
                                        || is_point_on_line(int_vec, tb, tc)
                                        || (ta - int_vec).Magnitude() < 1e-4
                                        || (tb - int_vec).Magnitude() < 1e-4
                                        || (tc - int_vec).Magnitude() < 1e-4
                                    ) {
                                        continue;
                                    }

                                    if (at < min_distance) {
                                        min_distance = at;
                                        min_int = {int_vec.X(), int_vec.Y(), int_vec.Z()};
                                    }
                                    if (at > max_distance) {
                                        max_distance = at;
                                        max_int = {int_vec.X(), int_vec.Y(), int_vec.Z()};
                                    }
                                }
                            }
                        }
                    } else {
                        stack.push(bvh->Child<0>(i));
                        stack.push(bvh->Child<1>(i));
                    }
                }

                if (min_distance == std::numeric_limits<double>::infinity()) {
                    return std::make_tuple(-1, min_int, max_int);
                }
                return std::make_tuple(max_distance - min_distance, min_int, max_int);
            }

            bool is_point_on_line(const gp_Pnt& point, const gp_Pnt& lineStart, const gp_Pnt& lineEnd) const {
                // Create vectors
                gp_Vec startToPoint(point.XYZ() - lineStart.XYZ());
                gp_Vec startToEnd(lineEnd.XYZ() - lineStart.XYZ());

                // Check if the point is on the line defined by start and end
                // by checking if the cross product is (near) zero vector, indicating collinearity.
                gp_Vec crossProduct = startToPoint.Crossed(startToEnd);
                if (crossProduct.Magnitude() > Precision::Confusion()) {
                    return false; // Not collinear, hence not on the line segment
                }
                return true; // The point is on the line segment
            }

            // Vec variant? This _Pnt and _Vec difference is annoying.
            bool is_point_on_line(const gp_Vec& point, const gp_Vec& lineStart, const gp_Vec& lineEnd) const {
                // Create vectors
                gp_Vec startToPoint = point - lineStart;
                gp_Vec startToEnd = lineEnd - lineStart;

                // Check if the point is on the line defined by start and end
                // by checking if the cross product is (near) zero vector, indicating collinearity.
                gp_Vec crossProduct = startToPoint.Crossed(startToEnd);
                if (crossProduct.Magnitude() > Precision::Confusion()) {
                    return false; // Not collinear, hence not on the line segment
                }
                return true; // The point is on the line segment
            }

            std::unordered_map<int, std::vector<int>> clash_bvh(
                opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>> bvh_a,
                opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>> bvh_b,
                double extend = 0.0
                    ) const {
                std::unordered_map<int, std::vector<int>> bvh_clashes;
                for (int i=0; i<bvh_a->Length(); ++i) {
                    if ( ! bvh_a->IsOuter(i)) {
                        continue;
                    }

                    BVH_TreeBase<Standard_Real, 3>::BVH_VecNt bvh_a_min = bvh_a->MinPoint(i);
                    BVH_TreeBase<Standard_Real, 3>::BVH_VecNt bvh_a_max = bvh_a->MaxPoint(i);
                    bvh_a_min[0] -= 1e-3;
                    bvh_a_min[1] -= 1e-3;
                    bvh_a_min[2] -= 1e-3;
                    bvh_a_max[0] += 1e-3;
                    bvh_a_max[1] += 1e-3;
                    bvh_a_max[2] += 1e-3;

                    BVH_Box<Standard_Real, 3> box_a(bvh_a_min, bvh_a_max);

                    std::stack<int> stack;
                    stack.push(0);

                    while ( ! stack.empty()) {
                        int j = stack.top();
                        stack.pop();

                        BVH_TreeBase<Standard_Real, 3>::BVH_VecNt bvh_b_min = bvh_b->MinPoint(j);
                        BVH_TreeBase<Standard_Real, 3>::BVH_VecNt bvh_b_max = bvh_b->MaxPoint(j);
                        bvh_b_min[0] -= extend + 1e-3;
                        bvh_b_min[1] -= extend + 1e-3;
                        bvh_b_min[2] -= extend + 1e-3;
                        bvh_b_max[0] += extend + 1e-3;
                        bvh_b_max[1] += extend + 1e-3;
                        bvh_b_max[2] += extend + 1e-3;

                        if (box_a.IsOut(bvh_b_min, bvh_b_max)) {
                            continue;
                        }
                        if (bvh_b->IsOuter(j)) {
                            if (bvh_clashes.find(i) != bvh_clashes.end()) {
                                bvh_clashes[i].push_back(j);
                            } else {
                                bvh_clashes[i] = {j};
                            }
                        } else {
                            stack.push(bvh_b->Child<0>(j));
                            stack.push(bvh_b->Child<1>(j));
                        }
                    }
                }
                return bvh_clashes;
            }

			bool test_intersection(const T& tA, const T& tB, double tolerance, bool check_all = true) const {
                // If there are verts of A inside shape B (protrusion):
                //  1. For each vert, find the shortest distance to the closest face
                //  2. Find the innermost vert (i.e. the vert that has the longest distance)
                // Otherwise (piercing):
                //  1. Intersect each edge with shape B
                //  2. Find the longest distance between intersections

                // OBB check
                const auto& obb_a = obbs_.find(tA)->second;
                auto obb_b = obbs_.find(tB)->second;
                obb_b.Enlarge(-tolerance);
                if (obb_a.IsOut(obb_b)) {
                    return false;
                }

                // No need to search beyond the distance of the max protrusion.
                const double max_protrusion = max_protrusions_.find(tB)->second;

                // Collide BVH trees of shape A vs B
                opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>> bvh_a = bvhs_.find(tA)->second;
                opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>> bvh_b = bvhs_.find(tB)->second;

                std::unordered_map<int, std::vector<int>> bvh_clashes = clash_bvh(bvh_a, bvh_b, max_protrusion);
                if (bvh_clashes.empty()) {
                    return false;
                }

                const std::vector<bool>& valid_tris_a = valid_tris_.find(tA)->second;
                const std::vector<bool>& valid_tris_b = valid_tris_.find(tB)->second;
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
                        if ( ! valid_tris_a[i]) {
                            continue;
                        }

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
                                    pierce_shape(v1_a_vec, v2_a_vec, bvh_b, valid_tris_b, tris_b, verts_b, normals_b),
                                    pierce_shape(v1_a_vec, v3_a_vec, bvh_b, valid_tris_b, tris_b, verts_b, normals_b),
                                    pierce_shape(v2_a_vec, v3_a_vec, bvh_b, valid_tris_b, tris_b, verts_b, normals_b)
                                };

                                for (const auto& [p_dist, p_min, p_max] : pierce_results) {
                                    if (p_dist > tolerance && p_dist > pierce) {
                                        // Piercings are capped at max_protrusion for intuitive results
                                        pierce = std::min(p_dist, max_protrusion);
                                        pierce_point1 = p_min;
                                        pierce_point2 = p_max;
                                        if ( ! check_all) {
                                            clash_types_.push_back(1);
                                            protrusion_distances_.push_back(pierce);
                                            protrusion_points_.push_back(pierce_point1);
                                            surface_points_.push_back(pierce_point2);
                                            return true;
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
                                if ( ! valid_tris_b[j]) {
                                    continue;
                                }

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
                                                clash_types_.push_back(0);
                                                protrusion_distances_.push_back(v_protrusion);
                                                protrusion_points_.push_back(v_protrusion_point);
                                                surface_points_.push_back(v_surface_point);
                                                return true;
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
                                    clash_types_.push_back(0);
                                    protrusion_distances_.push_back(protrusion);
                                    protrusion_points_.push_back(protrusion_point);
                                    surface_points_.push_back(surface_point);
                                    return true;
                                }
                            }
                        }
                    }
                }

                if (protrusion > tolerance) {
                    clash_types_.push_back(0);
                    protrusion_distances_.push_back(protrusion);
                    protrusion_points_.push_back(protrusion_point);
                    surface_points_.push_back(surface_point);
                    return true;
                }

                if (pierce > tolerance) {
                    // Don't like this inaccurate reuse of variables.
                    clash_types_.push_back(1);
                    protrusion_distances_.push_back(pierce);
                    protrusion_points_.push_back(pierce_point1);
                    surface_points_.push_back(pierce_point2);
                    return true;
                }

                return false;
            }

			bool test_collision(const T& tA, const T& tB, bool allow_touching) const {
                // OBB check
                auto obb_a = obbs_.find(tA)->second;
                auto obb_b = obbs_.find(tB)->second;
                obb_b.Enlarge(-0.001); // Within 1mm is touching
                if (obb_a.IsOut(obb_b)) {
                    return false;
                }

                // Collide BVH trees of shape A vs B
                opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>> bvh_a = bvhs_.find(tA)->second;
                opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>> bvh_b = bvhs_.find(tB)->second;

                std::unordered_map<int, std::vector<int>> bvh_clashes = clash_bvh(bvh_a, bvh_b);
                if (bvh_clashes.empty()) {
                    return false;
                }

                const std::vector<bool>& valid_tris_a = valid_tris_.find(tA)->second;
                const std::vector<bool>& valid_tris_b = valid_tris_.find(tB)->second;
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
                        if ( ! valid_tris_a[i]) {
                            continue;
                        }

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
                                if ( ! valid_tris_b[j]) {
                                    continue;
                                }

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
                                        clash_types_.push_back(2);
                                        protrusion_distances_.push_back(0);
                                        protrusion_points_.push_back({int1.X(), int1.Y(), int1.Z()});
                                        surface_points_.push_back({int2.X(), int2.Y(), int2.Z()});
                                        return true;
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
                                            clash_types_.push_back(2);
                                            protrusion_distances_.push_back(0);
                                            protrusion_points_.push_back({int1.X(), int1.Y(), int1.Z()});
                                            surface_points_.push_back({int2.X(), int2.Y(), int2.Z()});
                                            return true;
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
                                            clash_types_.push_back(2);
                                            protrusion_distances_.push_back(0);
                                            protrusion_points_.push_back({int1.X(), int1.Y(), int1.Z()});
                                            surface_points_.push_back({int2.X(), int2.Y(), int2.Z()});
                                            return true;
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
                                            clash_types_.push_back(2);
                                            protrusion_distances_.push_back(0);
                                            protrusion_points_.push_back({int2.X(), int2.Y(), int2.Z()});
                                            surface_points_.push_back({int1.X(), int1.Y(), int1.Z()});
                                            return true;
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
                                            clash_types_.push_back(2);
                                            protrusion_distances_.push_back(0);
                                            protrusion_points_.push_back({int2.X(), int2.Y(), int2.Z()});
                                            surface_points_.push_back({int1.X(), int1.Y(), int1.Z()});
                                            return true;
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                return false;
            }

			bool test_clearance(const T& tA, const T& tB, double clearance, bool check_all) const {
                // OBB check
                const auto& obb_a = obbs_.find(tA)->second;
                auto obb_b = obbs_.find(tB)->second;
                obb_b.Enlarge(clearance);
                if (obb_a.IsOut(obb_b)) {
                    return false;
                }

                // Collide BVH trees of shape A vs B
                opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>> bvh_a = bvhs_.find(tA)->second;
                opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>> bvh_b = bvhs_.find(tB)->second;

                std::unordered_map<int, std::vector<int>> bvh_clashes = clash_bvh(bvh_a, bvh_b, clearance);
                if (bvh_clashes.empty()) {
                    return false;
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
                                        protrusion_distances_.push_back(min_clearance);
                                        protrusion_points_.push_back(clearance_point1);
                                        surface_points_.push_back(clearance_point2);
                                        return true;
                                    }
                                }
                            }
                        }
                    }
                }

                if (min_clearance < clearance) {
                    protrusion_distances_.push_back(min_clearance);
                    protrusion_points_.push_back(clearance_point1);
                    surface_points_.push_back(clearance_point2);
                    return true;
                }

                return false;
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
            // 0 = protrusion, 1 = pierce, 2 = collision, 3 = clearance
			mutable std::vector<int> clash_types_;
			mutable std::vector<double> protrusion_distances_;
			mutable std::vector<std::array<double, 3>> protrusion_points_;
			mutable std::vector<std::array<double, 3>> surface_points_;
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

			void add_triangulated(const T& t, const TopoDS_Shape& s) {
                // Note that the original add function is also used elsewhere (e.g. boolean_utils.cpp)
                // We don't want to randomly add triangulated voids in our
                // tree, so for now this is a separate function.
                // BRepMesh_IncrementalMesh(s, 1.e-3, false, 0.5);

				Bnd_Box b;
				BRepBndLib::AddClose(s, b);
				tree_.Add(t, b);
				shapes_[t] = s;

                Bnd_OBB obb;
                // If IsOptimal = True it doubles the execution time.
                BRepBndLib::AddOBB(s, obb, true, false, false);
                obbs_[t] = obb;

                max_protrusions_[t] = std::min(std::min(obb.XHSize(), obb.YHSize()), obb.ZHSize()) * 2;

                BRepExtrema_ShapeList shape_list;

                std::vector<bool> is_reversed;

                TopExp_Explorer exp_f;
                for (exp_f.Init(s, TopAbs_FACE); exp_f.More(); exp_f.Next()) {
                    shape_list.Append(exp_f.Current());

                    TopoDS_Face f = TopoDS::Face(exp_f.Current());
                    is_reversed.push_back(f.Orientation() == TopAbs_REVERSED);
                }

                BRepExtrema_TriangleSet triangle_set(shape_list);
                const opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>>& bvh = triangle_set.BVH();

                std::vector<bool> valid_tris(triangle_set.Size(), true);
                std::vector<std::array<int, 3>> tris(triangle_set.Size());
                std::vector<gp_Vec> normals(triangle_set.Size());

                const BVH_Array3d& vertices = triangle_set.GetVertices();
                std::vector<gp_Pnt> verts(vertices.size());
                int i = 0;
                for (const auto& v : vertices) {
                    verts[i] = gp_Pnt(v[0], v[1], v[2]);
                    i++;
                }

                for (int i=0; i<triangle_set.Size(); ++i) {
                    NCollection_Array1<int> indices;
                    triangle_set.GetVtxIndices(i, indices);
                    if (is_reversed[triangle_set.GetFaceID(i)]) {
                        std::swap(indices[0], indices[2]);
                    }

                    gp_Pnt& v1_pnt = verts[indices[0]];
                    gp_Pnt& v2_pnt = verts[indices[1]];
                    gp_Pnt& v3_pnt = verts[indices[2]];
                    gp_Vec dir1(v1_pnt, v2_pnt);
                    gp_Vec dir2(v1_pnt, v3_pnt);
                    gp_Vec cross_product = dir1.Crossed(dir2);
                    if (cross_product.Magnitude() > Precision::Confusion()) {
                        normals[i] = cross_product.Normalized();
                        tris[i] = {indices[0], indices[1], indices[2]};
                    } else {
                        valid_tris[i] = false;
                    }
                }

                // Debug
                /*
                std::cout << "DEBUGG:" << std::endl;
                for (int i=0; i<triangle_set.Size(); ++i) {
                    BVH_Vec3d v1, v2, v3;
                    triangle_set.GetVertices(i, v1, v2, v3);
                    int face_id = triangle_set.GetFaceID(i);
                    std::cout << "Triangle in triangle set:" << std::endl;
                    std::cout << v1[0] << " " << v1[1] << " " << v1[2] << std::endl;
                    if (faces[face_id].Orientation() == TopAbs_REVERSED) {
                        std::cout << v3[0] << " " << v3[1] << " " << v3[2] << std::endl;
                        std::cout << v2[0] << " " << v2[1] << " " << v2[2] << std::endl;
                    } else {
                        std::cout << v2[0] << " " << v2[1] << " " << v2[2] << std::endl;
                        std::cout << v3[0] << " " << v3[1] << " " << v3[2] << std::endl;
                    }
                }
                */

                bvhs_[t] = bvh;
                is_manifold_[t] = is_shape_manifold(s);
                tris_[t] = std::move(tris);
                verts_[t] = std::move(verts);
                normals_[t] = std::move(normals);
                valid_tris_[t] = std::move(valid_tris);
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

			std::vector<T> clash_intersection(const T& t, double tolerance = 0.002, bool check_all = true) const {
				clash_types_.clear();
				protrusion_distances_.clear();
				protrusion_points_.clear();
				surface_points_.clear();

				std::vector<T> ts = select_box(t, true, 1e-5);
				if (ts.empty()) {
					return ts;
				}

				std::vector<T> ts_filtered;
				ts_filtered.reserve(ts.size());

				typename std::vector<T>::const_iterator it = ts.begin();
				for (it = ts.begin(); it != ts.end(); ++it) {
                    if (t == *it) {
                        continue; // Don't clash against itself.
                    }

                    if (is_manifold_.find(*it)->second) {
                        if (test_intersection(t, *it, tolerance, check_all)) {
                            ts_filtered.push_back(*it);
                        }
                    } else {
                        if (test_collision(t, *it, false)) {
                            ts_filtered.push_back(*it);
                        }
                    }
				}
                std::cout << "Tri count " << tri_count_ << std::endl;

				return ts_filtered;
			}


			std::vector<T> clash_collision(const T& t, bool allow_touching = false) const {
				protrusion_points_.clear();

				std::vector<T> ts = select_box(t, true, 1e-5);
				if (ts.empty()) {
					return ts;
				}

				std::vector<T> ts_filtered;
				ts_filtered.reserve(ts.size());

				typename std::vector<T>::const_iterator it = ts.begin();
				for (it = ts.begin(); it != ts.end(); ++it) {
                    if (t == *it) {
                        continue; // Don't clash against itself.
                    }

					if (test_collision(t, *it, allow_touching)) {
						ts_filtered.push_back(*it);
					}
				}
                std::cout << "Tri count " << tri_count_ << std::endl;

				return ts_filtered;
            }

			std::vector<T> clash_clearance(const T& t, double clearance, bool check_all) const {
				protrusion_distances_.clear();
				protrusion_points_.clear();
				surface_points_.clear();

				std::vector<T> ts = select_box(t, true, clearance);
				if (ts.empty()) {
					return ts;
				}

				std::vector<T> ts_filtered;
				ts_filtered.reserve(ts.size());

				typename std::vector<T>::const_iterator it = ts.begin();
				for (it = ts.begin(); it != ts.end(); ++it) {
                    if (t == *it) {
                        continue; // Don't clash against itself.
                    }

					if (test_clearance(t, *it, clearance, check_all)) {
						ts_filtered.push_back(*it);
					}
				}
                std::cout << "Tri count " << tri_count_ << std::endl;

				return ts_filtered;
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
            std::map<T, Bnd_OBB> obbs_; 
            std::map<T, double> max_protrusions_; 
            std::map<T, opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>>> bvhs_; 
            std::unordered_map<T, bool> is_manifold_;
            std::unordered_map<T, std::vector<bool>> valid_tris_;
            std::unordered_map<T, std::vector<std::array<int, 3>>> tris_;
            std::unordered_map<T, std::vector<gp_Pnt>> verts_;
            std::unordered_map<T, std::vector<gp_Vec>> normals_;
			
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

		void add_element(IfcGeom::BRepElement* elem, bool should_triangulate=false) {
			if (!elem) {
				return;
			}
			auto compound = elem->geometry().as_compound();
			compound.Move(elem->transformation().data());
            if (should_triangulate) {
                add_triangulated(elem->product(), compound);
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

		const std::vector<int>& clash_types() const {
			return clash_types_;
		}

		const std::vector<double>& protrusion_distances() const {
			return protrusion_distances_;
		}

		const std::vector<std::array<double, 3>>& protrusion_points() const {
			return protrusion_points_;
		}

		const std::vector<std::array<double, 3>>& surface_points() const {
			return surface_points_;
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
