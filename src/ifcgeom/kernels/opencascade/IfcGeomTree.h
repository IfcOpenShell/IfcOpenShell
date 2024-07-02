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

#include "../../../ifcparse/IfcFile.h"

#include "../../../ifcgeom/IfcGeomElement.h"
#include "../../../ifcgeom/Iterator.h"
#include "OpenCascadeConversionResult.h"
#include "base_utils.h"

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
#include <TopoDS_Face.hxx>
#include <TopoDS.hxx>

#include <vector>
#include <future>
#include <mutex>
#include <stack>
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
#include "clash_utils.h"

#ifdef WITH_HDF5
#include "H5Cpp.h"
#endif


namespace IfcGeom {

	struct ray_intersection_result {
		double distance;
		int style_index;
		const IfcUtil::IfcBaseEntity* instance;
		std::array<double, 3> position;
		std::array<double, 3> normal;
		double ray_distance;
		double dot_product;
	};

	struct clash {
        int clash_type; // 0 = protrusion, 1 = pierce, 2 = collision, 3 = clearance
		const IfcUtil::IfcBaseClass* a;
		const IfcUtil::IfcBaseClass* b;
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
                                if (std::abs(at) < 1e-4) {
                                    // The point is basically lying on a face so inside/outside is ambiguous.
                                    return false;
                                }
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
                if (crossProduct.Magnitude() > 1e-5) {
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
                if (crossProduct.Magnitude() > 1e-5) {
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
				auto shp = elem->geometry().as_compound();
				auto compound = ((ifcopenshell::geometry::OpenCascadeShape*)shp)->shape();
				const auto& m = elem->transformation().data()->ccomponents();
				gp_Trsf tr;
				tr.SetValues(
					m(0, 0), m(0, 1), m(0, 2), m(0, 3),
					m(1, 0), m(1, 1), m(1, 2), m(1, 3),
					m(2, 0), m(2, 1), m(2, 2), m(2, 3)
				);
				compound.Move(tr);
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
            std::map<const IfcUtil::IfcBaseClass*, std::string> global_ids_;
            std::map<const IfcUtil::IfcBaseClass*, std::string> names_;
            std::map<const IfcUtil::IfcBaseClass*, ifcopenshell::geometry::taxonomy::matrix4::ptr> placements_;
            std::map<std::string, std::vector<double>> local_verts_;
            std::map<std::string, std::vector<int>> local_faces_;
            std::map<std::string, std::vector<ifcopenshell::geometry::taxonomy::style::ptr>> local_materials_;
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

	class tree : public impl::tree<const IfcUtil::IfcBaseEntity*> {
	public:

		tree() {};

		tree(IfcParse::IfcFile& f) {
			add_file(f, ifcopenshell::geometry::Settings{});
		}

		tree(IfcParse::IfcFile& f, ifcopenshell::geometry::Settings settings) {
			add_file(f, settings);
		}

		tree(IfcGeom::Iterator& it) {
			add_file(it);
		}		

		void add_file(IfcParse::IfcFile& f, ifcopenshell::geometry::Settings settings) {
			ifcopenshell::geometry::Settings settings_ = settings;
			settings_.get<ifcopenshell::geometry::settings::IteratorOutput>().value = ifcopenshell::geometry::settings::NATIVE;
			settings_.get<ifcopenshell::geometry::settings::UseWorldCoords>().value = true;
			settings_.get<ifcopenshell::geometry::settings::ReorientShells>().value = true;

			IfcGeom::Iterator it(settings_, &f, {}, 1);

			add_file(it);
		}

		void add_file(IfcGeom::Iterator& it) {
			if (it.initialize()) {
				do {
					add_element(dynamic_cast<IfcGeom::BRepElement*>(it.get()));
				} while (it.next());
			}
		}

#ifdef WITH_HDF5
        void write_h5() {
            H5::H5File file("filename.h5", H5F_ACC_TRUNC);
            H5::Group shapes = file.createGroup("/shapes");

            std::set<std::string> processed_geometry_ids;
            std::vector<int> element_shape_ids;
            std::unordered_map<std::string, int> geometry_id_to_shape_id;
            int geometry_index = 0;

            std::vector<std::vector<float>> matrices;
            std::vector<std::array<float, 4>> colours;
            std::vector<std::string> names;
            std::vector<std::string> global_ids;

            const float tolerance = 0.01f; // Tolerance value for comparison

            for (const auto& elem : triangulation_elements_) {
                const auto geometry_id = elem->geometry().id();

                const auto& placement = placements_[elem->product()];
                {
                    decltype(matrices)::value_type m;
                    for (size_t i = 0; i < 16; ++i) {
                        m.push_back(static_cast<float>(placement->ccomponents().data()[i]));
                    }
                    matrices.push_back(m);
                }

                names.push_back(names_[elem->product()]);
                global_ids.push_back(global_ids_[elem->product()]);

                if (processed_geometry_ids.find(geometry_id) != processed_geometry_ids.end()) {
                    element_shape_ids.push_back(geometry_id_to_shape_id[geometry_id]);
                    continue;
                }

                processed_geometry_ids.insert(geometry_id);
                H5::Group group = shapes.createGroup(std::to_string(geometry_index));
                geometry_id_to_shape_id[geometry_id] = geometry_index;
                element_shape_ids.push_back(geometry_index);

                geometry_index++;

                const auto& faces = local_faces_[geometry_id];
                const auto& verts = local_verts_[geometry_id];
                const auto& materials = local_materials_[geometry_id];
                const auto& material_ids = local_material_ids_[geometry_id];

                std::vector<float> verts_float(verts.size());
                std::transform(verts.begin(), verts.end(), verts_float.begin(),
                   [](double val) { return static_cast<float>(val); });

                // Write faces
                size_t total_verts = verts.size() / 3;
                hsize_t faces_dims[1] = {faces.size()};
                H5::DataSpace faces_dataspace(1, faces_dims);
                H5::DSetCreatPropList faces_propList;
                faces_propList.setChunk(1, faces_dims);
                faces_propList.setDeflate(9);
                if (total_verts < (1 << 8)) {
                    H5::DataType dtype = H5::PredType::NATIVE_UINT8;
                    std::vector<uint8_t> faces_dtype(faces.begin(), faces.end());
                    H5::DataSet faces_dataset = group.createDataSet("faces", dtype, faces_dataspace, faces_propList);
                    faces_dataset.write(faces_dtype.data(), dtype);
                } else if (total_verts < (1 << 16)) {
                    H5::DataType dtype = H5::PredType::NATIVE_UINT16;
                    std::vector<uint16_t> faces_dtype(faces.begin(), faces.end());
                    H5::DataSet faces_dataset = group.createDataSet("faces", dtype, faces_dataspace, faces_propList);
                    faces_dataset.write(faces_dtype.data(), dtype);
                } else {
                    H5::DataType dtype = H5::PredType::NATIVE_UINT32;
                    H5::DataSet faces_dataset = group.createDataSet("faces", dtype, faces_dataspace, faces_propList);
                    faces_dataset.write(faces.data(), dtype);
                }

                // Write verts
                H5::DataType dtype = H5::PredType::NATIVE_FLOAT;
                hsize_t dims[1] = {verts.size()};
                H5::DataSpace dataspace(1, dims);
                H5::DSetCreatPropList propList;
                propList.setChunk(1, dims);
                propList.setDeflate(9);
                H5::DataSet dataset = group.createDataSet("verts", dtype, dataspace, propList);
                dataset.write(verts_float.data(), H5::PredType::NATIVE_FLOAT);

                // Write materials
                std::vector<uint8_t> material_keys;
                for (const auto& material : materials) {
                    float alpha = 1.0;
                    if (material->has_transparency() && material->transparency > 0) {
                        alpha = 1.0 - material->transparency;
                    }

                    int i = 0;
                    bool is_existing_colour = false;
                    for (const auto& colour : colours) {
                        if (std::abs(colour[0] - static_cast<float>(material->diffuse.ccomponents()[0])) < tolerance
                                && std::abs(colour[1] - static_cast<float>(material->diffuse.ccomponents()[1])) < tolerance
                                && std::abs(colour[2] - static_cast<float>(material->diffuse.ccomponents()[2])) < tolerance
                                && std::abs(colour[3] - alpha) < tolerance) {
                            is_existing_colour = true;
                            break;
                        }
                        i++;
                    }

                    if ( ! is_existing_colour) {
                        colours.push_back({
                            static_cast<float>(material->diffuse.ccomponents()[0]),
                            static_cast<float>(material->diffuse.ccomponents()[1]),
                            static_cast<float>(material->diffuse.ccomponents()[2]),
                            alpha});
                    }
                    material_keys.push_back(static_cast<decltype(material_keys)::value_type>(i));
                }

                size_t total_material_keys = material_keys.size();
                if (total_material_keys) {
                    hsize_t dims[1] = {material_keys.size()};
                    H5::DataSpace dataspace(1, dims);
                    H5::DSetCreatPropList propList;
                    propList.setChunk(1, dims);
                    propList.setDeflate(9);
                    H5::DataType dtype = H5::PredType::NATIVE_UINT8;
                    H5::DataSet dataset = group.createDataSet("materials", dtype, dataspace, propList);
                    dataset.write(material_keys.data(), dtype);
                }

                if (total_material_keys > 1) {
                    hsize_t dims[1] = {material_ids.size()};
                    H5::DataSpace dataspace(1, dims);
                    H5::DSetCreatPropList propList;
                    propList.setChunk(1, dims);
                    propList.setDeflate(9);
                    H5::DataType dtype = H5::PredType::NATIVE_UINT8;
                    H5::DataSet dataset = group.createDataSet("material_ids", dtype, dataspace, propList);
                    std::vector<uint8_t> data_dtype(material_ids.begin(), material_ids.end());
                    dataset.write(data_dtype.data(), dtype);
                }
            }

            // Write GlobalIds
            std::vector<uint8_t> uuids_array;
            for (const auto& id_str : global_ids) {
                for (size_t i = 0; i < id_str.length(); i += 2) {
                    uuids_array.push_back(std::stoi(id_str.substr(i, 2), 0, 16));
                }
            }

            hsize_t global_ids_dims[2] = {global_ids.size(), 16};  // 16 bytes per UUID
            H5::DataSpace global_ids_dataspace(2, global_ids_dims);
            H5::DataSet global_ids_dataset = file.createDataSet("element_global_ids", H5::PredType::NATIVE_UINT8, global_ids_dataspace);
            global_ids_dataset.write(uuids_array.data(), H5::PredType::NATIVE_UINT8);

            // Write names
            H5::StrType strType(H5::PredType::C_S1, H5T_VARIABLE);
            hsize_t names_dims[1] = {names.size()};
            H5::DataSpace names_dataspace(1, names_dims);
            H5::DataSet names_dataset = file.createDataSet("element_names", strType, names_dataspace);
            std::vector<const char*> cstr_names;
            for (const auto& name : names) {
                cstr_names.push_back(name.c_str());
            }
            names_dataset.write(&cstr_names[0], strType);

            // Write matrices
            std::vector<float> flat_matrices;
            for (const auto& matrix : matrices) {
                flat_matrices.insert(flat_matrices.end(), matrix.begin(), matrix.end());
            }
            hsize_t dims[2] = {matrices.size(), matrices[0].size()};
            H5::DataSpace dataspace(2, dims);
            H5::DSetCreatPropList propList;
            propList.setChunk(2, dims);
            propList.setDeflate(9);
            H5::DataSet dataset = file.createDataSet("element_matrices", H5::PredType::NATIVE_FLOAT, dataspace, propList);
            dataset.write(flat_matrices.data(), H5::PredType::NATIVE_FLOAT);

            // Write element_shape_ids
            hsize_t element_shape_ids_dims[1] = {element_shape_ids.size()};
            H5::DataSpace element_shape_ids_dataspace(1, element_shape_ids_dims);
            H5::DSetCreatPropList element_shape_ids_propList;
            element_shape_ids_propList.setChunk(1, element_shape_ids_dims);
            element_shape_ids_propList.setDeflate(9);
            if (geometry_index < (1 << 8)) {
                H5::DataType dtype = H5::PredType::NATIVE_UINT8;
                std::vector<uint8_t> element_shape_ids_dtype(element_shape_ids.begin(), element_shape_ids.end());
                H5::DataSet element_shape_ids_dataset = file.createDataSet("element_shape_ids", dtype, element_shape_ids_dataspace, element_shape_ids_propList);
                element_shape_ids_dataset.write(element_shape_ids_dtype.data(), dtype);
            } else if (geometry_index < (1 << 16)) {
                H5::DataType dtype = H5::PredType::NATIVE_UINT16;
                std::vector<uint16_t> element_shape_ids_dtype(element_shape_ids.begin(), element_shape_ids.end());
                H5::DataSet element_shape_ids_dataset = file.createDataSet("element_shape_ids", dtype, element_shape_ids_dataspace, element_shape_ids_propList);
                element_shape_ids_dataset.write(element_shape_ids_dtype.data(), dtype);
            } else if (geometry_index < (1UL << 32)) {
                H5::DataType dtype = H5::PredType::NATIVE_UINT32;
                std::vector<uint32_t> element_shape_ids_dtype(element_shape_ids.begin(), element_shape_ids.end());
                H5::DataSet element_shape_ids_dataset = file.createDataSet("element_shape_ids", dtype, element_shape_ids_dataspace, element_shape_ids_propList);
                element_shape_ids_dataset.write(element_shape_ids_dtype.data(), dtype);
            }

            // Write colours
            if (colours.size()) {
                std::vector<float> flat_colours;
                for (const auto& colour : colours) {
                    flat_colours.insert(flat_colours.end(), colour.begin(), colour.end());
                }
                hsize_t colours_dims[2] = {colours.size(), colours[0].size()};
                H5::DataSpace colours_dataspace(2, colours_dims);
                H5::DSetCreatPropList colours_propList;
                colours_propList.setChunk(2, colours_dims);
                colours_propList.setDeflate(9);
                H5::DataSet colours_dataset = file.createDataSet("materials", H5::PredType::NATIVE_FLOAT, colours_dataspace, colours_propList);
                colours_dataset.write(flat_colours.data(), H5::PredType::NATIVE_FLOAT);
            }
        }
#endif

        template <typename T>
        void apply_matrix_to_flat_verts(const std::vector<T>& flat_list, const ifcopenshell::geometry::taxonomy::matrix4::ptr& matrix, std::vector<T>& result) {
            Eigen::Vector3d vin;
            result.clear();
            result.reserve(flat_list.size());

            for (size_t i = 0; i < flat_list.size(); i += 3) {
                vin << 
                    flat_list[i],
                    flat_list[i + 1],
                    flat_list[i + 2];
                auto vout = matrix->ccomponents() * vin.homogeneous();
                result.push_back(vout(0));
                result.push_back(vout(1));
                result.push_back(vout(2));
            }
        }

        std::string uint8_to_b64(const std::vector<uint8_t>& uuids_array) {
            std::string hex_str;
            for (auto byte : uuids_array) {
                // Convert each byte to a two-digit hexadecimal string and append it to the result
                char hex[3]; // Two characters for the hex value and one for the null terminator
                snprintf(hex, sizeof(hex), "%02x", byte);
                hex_str.append(hex);
            }
            return hex_str;
        }

        static bool is_manifold(const std::vector<int>& fs) {
            // @nb this assumes geometry is processed with the WELD_VERTICES setting
            std::unordered_set<std::pair<size_t, size_t>, boost::hash<std::pair<size_t, size_t>>> dict;
            for (size_t i = 0; i < fs.size(); i += 3) {
                for (size_t j = 0; j < 3; ++j) {
                    auto k = (j + 1) % 3;
                    auto it = dict.find({ fs[i + j], fs[i + k] });
                    if (it != dict.end()) {
                        dict.erase(it);
                    } else {
                        dict.insert({ fs[i + k], fs[i + j] });
                    }
                }
            }
            return dict.empty();
        }

        void add_element(IfcGeom::TriangulationElement* elem) {

            Bnd_Box aabb;
            Bnd_OBB obb;

            {
                auto& m = elem->transformation().data()->ccomponents();
                auto& vs = elem->geometry().verts();
                auto& fs = elem->geometry().faces();

                gp_Trsf tr;
                tr.SetValues(
                    m(0, 0), m(0, 1), m(0, 2), m(0, 3),
                    m(1, 0), m(1, 1), m(1, 2), m(1, 3),
                    m(2, 0), m(2, 1), m(2, 2), m(2, 3)
                );

                std::vector<gp_Pnt> vs_transformed;
                vs_transformed.reserve(vs.size() / 3);
                for (size_t i = 0; i < vs.size(); i += 3) {
                    gp_Pnt p(vs[i + 0], vs[i + 1], vs[i + 2]);
                    vs_transformed.push_back(p.Transformed(tr));
                    aabb.Add(vs_transformed.back());
                }
            
                std::unordered_map<std::tuple<int, int, int>, std::vector<size_t>, boost::hash<std::tuple<int, int, int>>> quantized_normal_counts;

                std::vector<double> tri_areas;
                std::vector<gp_XYZ> tri_norms;
                for (size_t i = 0; i < fs.size(); i += 3) {
                    auto& p = vs_transformed[fs[i+0]];
                    auto& q = vs_transformed[fs[i+1]];
                    auto& r = vs_transformed[fs[i+2]];
                    auto cross = (q.XYZ() - p.XYZ()).Crossed(r.XYZ() - p.XYZ());
                    auto mag = cross.Modulus();
                    tri_areas.push_back(mag / 2.);
                    cross /= mag;
                    tri_norms.push_back(cross);
                    auto quantized = std::make_tuple(
                        static_cast<int>(cross.X() * 1000),
                        static_cast<int>(cross.Y() * 1000),
                        static_cast<int>(cross.Z() * 1000)
                    );
                    quantized_normal_counts[quantized].push_back(i / 3);
                }

                std::vector<std::pair<double, decltype(quantized_normal_counts)::const_iterator>> area_to_it;

                for (auto it = quantized_normal_counts.cbegin(); it != quantized_normal_counts.cend(); ++it) {
                    double area_sum = 0.;
                    for (auto& i : it->second) {
                        area_sum += tri_areas[i];
                    }
                    area_to_it.push_back({ area_sum, it });
                }

                std::sort(area_to_it.begin(), area_to_it.end(), [](auto& p1, auto& p2) { return p1.first < p2.first; });

                auto calc_average_norm = [&tri_norms](const std::vector<size_t>& idxs) {
                    gp_XYZ normal_sum;
                    for (auto& i : idxs) {
                        normal_sum.Add(tri_norms[i]);
                    }
                    normal_sum.Normalize();
                    return normal_sum;
                };

                auto Z = calc_average_norm(area_to_it.back().second->second);

                std::vector<std::pair<double, gp_XYZ>> candidates;

                size_t num_candidates = 0;
                for (auto it = ++area_to_it.rbegin(); it != area_to_it.rend() && num_candidates < 10; ++it, ++num_candidates) {
                    auto ref = calc_average_norm(it->second->second);
                    candidates.push_back({ std::abs(Z.Dot(ref)), ref });
                }

                if (candidates.empty()) {
                    {
                        gp_XYZ ref(0, 0, 1);
                        candidates.push_back({ std::abs(Z.Dot(ref)), ref });
                    }
                    {
                        gp_XYZ ref(1, 0, 0);
                        candidates.push_back({ std::abs(Z.Dot(ref)), ref });
                    }
                }

                auto X = std::min_element(candidates.begin(), candidates.end(), [](auto& p1, auto& p2) { return p1.first < p2.first; })->second;

                gp_Trsf trsf2;
                gp_Ax3 ax3(gp::Origin(), Z, X);
                trsf2.SetTransformation(gp::XOY(), ax3);

                Bnd_Box tmp;

                for (auto& p : vs_transformed) {
                    tmp.Add(p.Transformed(trsf2));
                }

                gp_Pnt cent = (tmp.CornerMax().XYZ() + tmp.CornerMin().XYZ()) / 2;
                auto halfsize = tmp.CornerMax().XYZ() - cent.XYZ();

                obb.SetXComponent(ax3.XDirection(), halfsize.X());
                obb.SetYComponent(ax3.YDirection(), halfsize.Y());
                obb.SetZComponent(ax3.Direction(), halfsize.Z());
                obb.SetCenter(cent.Transformed(trsf2.Inverted()));
            }
            
            const auto& t = elem->product();
            const auto& matrix = elem->transformation().data();
            const std::vector<double>& elem_verts_local = elem->geometry().verts();
            const std::vector<int>& elem_faces = elem->geometry().faces();
            std::vector<double> elem_verts;
            apply_matrix_to_flat_verts(elem_verts_local, matrix, elem_verts);

            int original_tris_index = 0;
            std::vector<std::array<int, 3>> original_tris;
            std::vector<gp_Pnt> verts;
            std::vector<gp_Vec> original_normals;

            // Attempt to copy exactly what BRepExtrema_TriangleSet is doing under the hood.
            const auto builder = new BVH_LinearBuilder<Standard_Real, 3>(BVH_Constants_LeafNodeSizeDefault, BVH_Constants_MaxTreeDepth);
            BVH_Triangulation<Standard_Real, 3> triangulation(builder);

            for (int i = 0; i < elem_verts.size(); i += 3) {
                triangulation.Vertices.push_back(BVH_Vec3d(elem_verts[i], elem_verts[i + 1], elem_verts[i + 2]));
                verts.push_back(gp_Pnt(elem_verts[i], elem_verts[i + 1], elem_verts[i + 2]));
            }

            for (int i = 0; i < elem_faces.size(); i += 3) {
                const auto& v1_pnt = verts[elem_faces[i]];
                const auto& v2_pnt = verts[elem_faces[i + 1]];
                const auto& v3_pnt = verts[elem_faces[i + 2]];
                gp_Vec dir1(v1_pnt, v2_pnt);
                gp_Vec dir2(v1_pnt, v3_pnt);
                gp_Vec cross_product = dir1.Crossed(dir2);
                if (cross_product.Magnitude() > Precision::Confusion()) {
                    triangulation.Elements.push_back(BVH_Vec4i(
                        elem_faces[i], elem_faces[i + 1], elem_faces[i + 2], original_tris_index
                    ));
                    original_tris_index++;
                    original_tris.push_back({
                        elem_faces[i], elem_faces[i + 1], elem_faces[i + 2]
                        });
                    original_normals.push_back(cross_product.Normalized());
                }
            }

            triangulation.MarkDirty();
            const auto bvh = triangulation.BVH();

            // After BVH is constructed, triangles are reordered
            std::vector<std::array<int, 3>> tris(triangulation.Size());
            std::vector<gp_Vec> normals(triangulation.Size());

            for (int i = 0; i < triangulation.Size(); ++i) {
                const auto& el = triangulation.Elements[i];
                tris[i] = original_tris[el[3]];
                normals[i] = original_normals[el[3]];
            }

            bvhs_[t] = bvh;
            is_manifold_[t] = is_manifold(elem_faces);
            tris_[t] = std::move(tris);
            verts_[t] = std::move(verts);
            normals_[t] = std::move(normals);
            aabbs_[t] = aabb;
            obbs_[t] = obb;
            max_protrusions_[t] = std::min(std::min(obb.XHSize(), obb.YHSize()), obb.ZHSize()) * 2;
        }
        
		void add_element(IfcGeom::BRepElement* elem) {
			if (!elem) {
				return;
			}

			auto compound_generic = elem->geometry().as_compound();
			auto compound = ((ifcopenshell::geometry::OpenCascadeShape*)compound_generic)->shape();
			
			const auto& m = elem->transformation().data()->ccomponents();
			gp_Trsf tr;
			tr.SetValues(
				m(0, 0), m(0, 1), m(0, 2), m(0, 3),
				m(1, 0), m(1, 1), m(1, 2), m(1, 3),
				m(2, 0), m(2, 1), m(2, 2), m(2, 3)
			);

			compound.Move(tr);
            add(elem->product(), compound);

			auto git = elem->geometry().begin();

			if (enable_face_styles_) {
				TopoDS_Iterator it(compound);
				for (; it.More(); it.Next(), ++git) {
					// Assumption is that the number of styles is small, so the linear lookup time is not significant.
					auto sit = std::find(styles_.begin(), styles_.end(), git->StylePtr());
					size_t index;
					if (sit == styles_.end()) {
						index = styles_.size();
						styles_.push_back(git->StylePtr());
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

		const std::vector<ifcopenshell::geometry::taxonomy::style::ptr>& styles() const {
			return styles_;
		}

	protected:
		typedef TopTools_DataMapOfShapeInteger face_style_map_t;

		face_style_map_t face_styles_;
		std::vector<ifcopenshell::geometry::taxonomy::style::ptr> styles_;
	};

}

#endif
