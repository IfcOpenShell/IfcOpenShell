#ifndef BVH_UTILS_H
#define BVH_UTILS_H

#include <stack>
#include <unordered_map>

namespace IfcGeom {
namespace util {

template <typename T>
bool is_point_on_line(const T& point, const T& lineStart, const T& lineEnd) {
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

bool is_point_in_shape(
    const gp_Pnt& v,
    const opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>>& bvh,
    const std::vector<std::array<int, 3>>& tris,
    const std::vector<gp_Pnt>& verts,
    // In the case of "touching" rays, let's check again!
    bool should_check_again = false
) {
    ray v_ray;
    v_ray.origin[0] = static_cast<float>(v.X());
    v_ray.origin[1] = static_cast<float>(v.Y());
    v_ray.origin[2] = static_cast<float>(v.Z());

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

    while (!stack.empty()) {
        int i = stack.top();
        stack.pop();

        BVH_TreeBase<Standard_Real, 3>::BVH_VecNt min_point = bvh->MinPoint(i);
        BVH_TreeBase<Standard_Real, 3>::BVH_VecNt max_point = bvh->MaxPoint(i);

        box box;
        // + 1e-5 for tolerance
        box.corners[0][0] = static_cast<float>(min_point[0] - 1.e-5);
        box.corners[0][1] = static_cast<float>(min_point[1] - 1.e-5);
        box.corners[0][2] = static_cast<float>(min_point[2] - 1.e-5);
        box.corners[1][0] = static_cast<float>(max_point[0] + 1.e-5);
        box.corners[1][1] = static_cast<float>(max_point[1] + 1.e-5);
        box.corners[1][2] = static_cast<float>(max_point[2] + 1.e-5);
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

        if (!is_intersect_ray_box(&v_ray, &box)) {
            continue;
        }
        //std::cout << "Ray hits box" << std::endl;
        if (bvh->IsOuter(i)) {
            //std::cout << "Ray hits leaf" << std::endl;
            // Do ray triangle check.
            for (int j = bvh->BegPrimitive(i); j <= bvh->EndPrimitive(i); ++j) {
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
    const std::vector<std::array<int, 3>>& tris,
    const std::vector<gp_Pnt>& verts,
    const std::vector<gp_Vec>& normals
) {
    const gp_Vec& ray_origin = e1;
    gp_Vec ray_vector = e2 - e1;
    double edge_length = ray_vector.Magnitude();

    std::array<double, 3> min_int;
    std::array<double, 3> max_int;

    ray_vector.Normalize();

    ray v_ray;
    v_ray.origin[0] = static_cast<float>(ray_origin.X());
    v_ray.origin[1] = static_cast<float>(ray_origin.Y());
    v_ray.origin[2] = static_cast<float>(ray_origin.Z());

    v_ray.dir[0] = static_cast<float>(ray_vector.X());
    v_ray.dir[1] = static_cast<float>(ray_vector.Y());
    v_ray.dir[2] = static_cast<float>(ray_vector.Z());
    v_ray.dir_inv[0] = 1.0f / static_cast<float>(ray_vector.X());
    v_ray.dir_inv[1] = 1.0f / static_cast<float>(ray_vector.Y());
    v_ray.dir_inv[2] = 1.0f / static_cast<float>(ray_vector.Z());

    double min_distance = std::numeric_limits<double>::infinity();
    double max_distance = -std::numeric_limits<double>::infinity();

    std::stack<int> stack;
    stack.push(0);

    while (!stack.empty()) {
        int i = stack.top();
        stack.pop();

        BVH_TreeBase<Standard_Real, 3>::BVH_VecNt min_point = bvh->MinPoint(i);
        BVH_TreeBase<Standard_Real, 3>::BVH_VecNt max_point = bvh->MaxPoint(i);

        box box;
        // + 1e-5 for tolerance
        box.corners[0][0] = static_cast<float>(min_point[0] - 1.e-5);
        box.corners[0][1] = static_cast<float>(min_point[1] - 1.e-5);
        box.corners[0][2] = static_cast<float>(min_point[2] - 1.e-5);
        box.corners[1][0] = static_cast<float>(max_point[0] + 1.e-5);
        box.corners[1][1] = static_cast<float>(max_point[1] + 1.e-5);
        box.corners[1][2] = static_cast<float>(max_point[2] + 1.e-5);

        if (!is_intersect_ray_box(&v_ray, &box)) {
            continue;
        }
        if (bvh->IsOuter(i)) {
            // Do ray triangle check.
            for (int j = bvh->BegPrimitive(i); j <= bvh->EndPrimitive(i); ++j) {
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
                            min_int = { int_vec.X(), int_vec.Y(), int_vec.Z() };
                        }
                        if (at > max_distance) {
                            max_distance = at;
                            max_int = { int_vec.X(), int_vec.Y(), int_vec.Z() };
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

std::unordered_map<int, std::vector<int>> clash_bvh(
    opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>> bvh_a,
    opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>> bvh_b,
    double extend = 0.0
) {
    std::unordered_map<int, std::vector<int>> bvh_clashes;
    for (int i = 0; i < bvh_a->Length(); ++i) {
        if (!bvh_a->IsOuter(i)) {
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

        while (!stack.empty()) {
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
                    bvh_clashes[i] = { j };
                }
            } else {
                stack.push(bvh_b->Child<0>(j));
                stack.push(bvh_b->Child<1>(j));
            }
        }
    }
    return bvh_clashes;
}

}
}

#endif
