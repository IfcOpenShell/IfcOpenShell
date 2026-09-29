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

#ifndef IFCOPENSHELL_OPENCASCADE_BVH_TREE_H
#define IFCOPENSHELL_OPENCASCADE_BVH_TREE_H

#include "../../../ifcparse/file.h"

#include "../../../ifcgeom/element.h"
#include "../../../ifcgeom/iterator.h"
#include "../../../ifcgeom/tree.h"
#include "../../kernel_registry.h"
#include "../../../ifcparse/exception.h"
#include "clash_utils.h"

#include <Bnd_Box.hxx>
#include <Bnd_OBB.hxx>
#include <Precision.hxx>
#include <Standard_Macro.hxx>
#include <Standard_Version.hxx>
#include <TopoDS_Shape.hxx>

#include <BVH_BinaryTree.hxx>
#include <BVH_Box.hxx>
#include <BVH_BoxSet.hxx>
#include <BVH_LinearBuilder.hxx>
#include <BVH_Tree.hxx>
#include <BVH_Triangulation.hxx>
#include <BVH_Types.hxx>

#include <boost/functional/hash.hpp>

#include <algorithm>
#include <array>
#include <cmath>
#include <iterator>
#include <limits>
#include <map>
#include <memory>
#include <mutex>
#include <set>
#include <stack>
#include <thread>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

namespace ifcopenshell::geom {
	namespace impl {

		// Clashing is keyed by the product instances the triangulated elements
		// were added with, so anything else can not be looked up.
		inline void check_products(const std::vector<express::base>& instances) {
			for (const auto& instance : instances) {
				if (!instance || !instance.declaration().is("IfcProduct")) {
					throw ifcopenshell::exception("All instances should be of type IfcProduct");
				}
			}
		}

		// Intersection, collision and clearance implementation based on triangle
		// BVHs built from triangulated elements. All state is keyed directly by
		// the express::base product instances the elements were added with.
		class bvh_tree : public ifcopenshell::geom::tree {
		public:
			std::string backend_id() const override {
				return "opencascade.trianglebvh";
			}

			// The iterator overload of the base class is not hidden by the members below.
			using ifcopenshell::geom::tree::add_file;

			void add_file(ifcopenshell::file& file, const ifcopenshell::geom::settings& settings) override {
				auto settings_ = settings;
				settings_.get<ifcopenshell::geom::settings::IteratorOutput>().value = ifcopenshell::geom::settings::TRIANGULATED;
				settings_.get<ifcopenshell::geom::settings::UseWorldCoords>().value = true;

				ifcopenshell::geom::iterator iterator(ifcopenshell::geom::kernels::construct(&file, "opencascade", settings_), settings_, &file, {}, 1);
				add_file(iterator);
			}

			void add_element(ifcopenshell::geom::element* element) override {
				auto* triangulation = dynamic_cast<ifcopenshell::geom::triangulation_element*>(element);
				if (!triangulation) {
					throw ifcopenshell::exception("Tree backend '" + backend_id() + "' requires triangulated elements");
				}
				add_triangulation_element(triangulation);
			}

			std::vector<clash> clash_intersection_many(
					const std::vector<express::base>& set_a, const std::vector<express::base>& set_b,
					double tolerance = 0.002, bool check_all = true
				) const override {
				check_products(set_a);
				check_products(set_b);

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

				std::map<express::base, std::set<express::base>> tested_pairs;

				for (const auto& pair : bvh_clashes) {
					const int bvh_a_i = pair.first;
					const std::vector<int>& bvh_b_is = pair.second;
					for (int i=bvh_a->BegPrimitive(bvh_a_i); i<=bvh_a->EndPrimitive(bvh_a_i); ++i) {
						const express::base& t_a = set_a[box_set_a->Element(i)];
						for (const auto& bvh_b_i : bvh_b_is) {
							for (int j=bvh_b->BegPrimitive(bvh_b_i); j<=bvh_b->EndPrimitive(bvh_b_i); ++j) {
								const express::base& t_b = set_b[box_set_b->Element(j)];
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
					const std::vector<express::base>& set_a, const std::vector<express::base>& set_b, bool allow_touching = false
				) const override {
				check_products(set_a);
				check_products(set_b);

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

				std::map<express::base, std::set<express::base>> tested_pairs;

				for (const auto& pair : bvh_clashes) {
					const int bvh_a_i = pair.first;
					const std::vector<int>& bvh_b_is = pair.second;
					for (int i=bvh_a->BegPrimitive(bvh_a_i); i<=bvh_a->EndPrimitive(bvh_a_i); ++i) {
						const express::base& t_a = set_a[box_set_a->Element(i)];
						for (const auto& bvh_b_i : bvh_b_is) {
							for (int j=bvh_b->BegPrimitive(bvh_b_i); j<=bvh_b->EndPrimitive(bvh_b_i); ++j) {
								const express::base& t_b = set_b[box_set_b->Element(j)];
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
					const std::vector<express::base>& set_a, const std::vector<express::base>& set_b,
					double clearance = 0.05, bool check_all = false
				) const override {
				check_products(set_a);
				check_products(set_b);

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

				std::map<express::base, std::set<express::base>> tested_pairs;

				for (const auto& pair : bvh_clashes) {
					const int bvh_a_i = pair.first;
					const std::vector<int>& bvh_b_is = pair.second;
					for (int i=bvh_a->BegPrimitive(bvh_a_i); i<=bvh_a->EndPrimitive(bvh_a_i); ++i) {
						const express::base& t_a = set_a[box_set_a->Element(i)];
						for (const auto& bvh_b_i : bvh_b_is) {
							for (int j=bvh_b->BegPrimitive(bvh_b_i); j<=bvh_b->EndPrimitive(bvh_b_i); ++j) {
								const express::base& t_b = set_b[box_set_b->Element(j)];
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

		protected:
			struct clash_task {
				express::base a, b;
			};

			mutable long long tri_count_ = 0;

			std::map<express::base, Bnd_Box> aabbs_;
			std::map<express::base, Bnd_OBB> obbs_;
			std::map<express::base, double> max_protrusions_;
			std::map<express::base, opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>>> bvhs_;
			std::unordered_map<express::base, bool> is_manifold_;
			std::unordered_map<express::base, std::vector<std::array<int, 3>>> tris_;
			std::unordered_map<express::base, std::vector<gp_Pnt>> verts_;
			std::unordered_map<express::base, std::vector<gp_Vec>> normals_;

			bool is_point_in_shape(
					const gp_Pnt& v,
					const opencascade::handle<BVH_Tree<double, 3, BVH_BinaryTree>>& bvh,
					const std::vector<std::array<int, 3>>& tris,
					const std::vector<gp_Pnt>& verts,
					// In the case of "touching" rays, let's check again!
					bool should_check_again = false
					) const {
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

				while ( ! stack.empty()) {
					int i = stack.top();
					stack.pop();

					BVH_TreeBase<Standard_Real, 3>::BVH_VecNt min_point = bvh->MinPoint(i);
					BVH_TreeBase<Standard_Real, 3>::BVH_VecNt max_point = bvh->MaxPoint(i);

					box box;
					// + 1e-5 for tolerance
					box.corners[0][0] = static_cast<float>(min_point[0] - 1e-5);
					box.corners[0][1] = static_cast<float>(min_point[1] - 1e-5);
					box.corners[0][2] = static_cast<float>(min_point[2] - 1e-5);
					box.corners[1][0] = static_cast<float>(max_point[0] + 1e-5);
					box.corners[1][1] = static_cast<float>(max_point[1] + 1e-5);
					box.corners[1][2] = static_cast<float>(max_point[2] + 1e-5);

					if ( ! is_intersect_ray_box(&v_ray, &box)) {
						continue;
					}
					if (bvh->IsOuter(i)) {
						// Do ray triangle check.
						for (int j=bvh->BegPrimitive(i); j<=bvh->EndPrimitive(i); ++j) {
							const std::array<int, 3>& tri = tris[j];

							gp_Vec ta(verts[tri[0]].XYZ());
							gp_Vec tb(verts[tri[1]].XYZ());
							gp_Vec tc(verts[tri[2]].XYZ());

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

				std::array<double, 3> min_int{};
				std::array<double, 3> max_int{};

				ray_vector.Normalize();

				ray v_ray;
				v_ray.origin[0] = static_cast<float>(ray_origin.X());
				v_ray.origin[1] = static_cast<float>(ray_origin.Y());
				v_ray.origin[2] = static_cast<float>(ray_origin.Z());

				v_ray.dir[0] = static_cast<float>(ray_vector.X());
				v_ray.dir[1] = static_cast<float>(ray_vector.Y());
				v_ray.dir[2] = static_cast<float>(ray_vector.Z());
				v_ray.dir_inv[0] = static_cast<float>(1.0 / ray_vector.X());
				v_ray.dir_inv[1] = static_cast<float>(1.0 / ray_vector.Y());
				v_ray.dir_inv[2] = static_cast<float>(1.0 / ray_vector.Z());

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
					box.corners[0][0] = static_cast<float>(min_point[0] - 1e-5);
					box.corners[0][1] = static_cast<float>(min_point[1] - 1e-5);
					box.corners[0][2] = static_cast<float>(min_point[2] - 1e-5);
					box.corners[1][0] = static_cast<float>(max_point[0] + 1e-5);
					box.corners[1][1] = static_cast<float>(max_point[1] + 1e-5);
					box.corners[1][2] = static_cast<float>(max_point[2] + 1e-5);

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

			clash test_intersection(const express::base& tA, const express::base& tB, double tolerance, bool check_all = true) const {
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
				std::array<double, 3> protrusion_point{};
				std::array<double, 3> surface_point{};

				double pierce = -std::numeric_limits<double>::infinity();
				std::array<double, 3> pierce_point1{};
				std::array<double, 3> pierce_point2{};

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
						std::array<double, 3> v_protrusion_point{};
						std::array<double, 3> v_surface_point{};

						// Check for protrusions.
						for (const auto& bvh_b_i : bvh_b_is) {
							for (int j=bvh_b->BegPrimitive(bvh_b_i); j<=bvh_b->EndPrimitive(bvh_b_i); ++j) {
								const std::array<int, 3>& tri_b = tris_b[j];
								const gp_Vec& normal_b = normals_b[j];

								tri_count_++;

								// We're penetrating _into_ a shape, so don't
								// compare distances to faces with roughly the
								// same normal as the penetration.
								if (normal_a.Dot(normal_b) >= 0.9f) {
									continue;
								}

								gp_Vec ta(verts_b[tri_b[0]].XYZ());
								gp_Vec tb(verts_b[tri_b[1]].XYZ());
								gp_Vec tc(verts_b[tri_b[2]].XYZ());

								for (const auto& v : points_in_b) {
									gp_Vec ray_origin(v.XYZ());

									// Do (cheaper) line check.
									double at, au, av;
									if (intersectRayTriangle(ray_origin, normal_b, ta, tb, tc, at, au, av, false)) {
										double current_v_protrusion = at;

										if (current_v_protrusion < v_protrusion) {
											double aw = 1.0f - au - av; // Barycentric coordinate for ta
											gp_Vec point_on_b = aw * ta + au * tb + av * tc; // Intersection point
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

			clash test_collision(const express::base& tA, const express::base& tB, bool allow_touching) const {
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
								const std::array<int, 3>& tri_b = tris_b[j];
								const gp_Pnt& v1_b_pnt = verts_b[tri_b[0]];
								const gp_Pnt& v2_b_pnt = verts_b[tri_b[1]];
								const gp_Pnt& v3_b_pnt = verts_b[tri_b[2]];
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

			clash test_clearance(const express::base& tA, const express::base& tB, double clearance, bool check_all) const {
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
				std::array<double, 3> clearance_point1{};
				std::array<double, 3> clearance_point2{};

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
								const std::array<int, 3>& tri_b = tris_b[j];
								const gp_Pnt& v1_b_pnt = verts_b[tri_b[0]];
								const gp_Pnt& v2_b_pnt = verts_b[tri_b[1]];
								const gp_Pnt& v3_b_pnt = verts_b[tri_b[2]];

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

			std::unique_ptr<BVH_BoxSet<double, 3>> build_box_set(const std::vector<express::base>& elements) const {
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

			void add_triangulation_element(ifcopenshell::geom::triangulation_element* elem) {

				Bnd_Box aabb;
				Bnd_OBB obb;

				{
					auto& m = elem->transformation().data()->ccomponents();
					auto& vs = elem->geometry().verts();
					auto& fs = elem->geometry().faces();

					if (vs.empty() || fs.empty()) {
						return;
					}

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

					gp_Ax3 ax3;
					gp_Trsf trsf2;

					for (size_t attempt = 0; attempt < 2; ++attempt) {

						if (candidates.empty() || attempt == 1) {
							{
								gp_XYZ ref(0, 0, 1);
								candidates.push_back({std::abs(Z.Dot(ref)), ref});
							}
							{
								gp_XYZ ref(1, 0, 0);
								candidates.push_back({std::abs(Z.Dot(ref)), ref});
							}
						}

						auto X = std::min_element(candidates.begin(), candidates.end(), [](auto& p1, auto& p2) { return p1.first < p2.first; })->second;

						{
							try {
								ax3 = gp_Ax3(gp::Origin(), Z, X);
								trsf2.SetTransformation(gp::XOY(), ax3);
							} catch (Standard_ConstructionError&) {
								// Try again, likely we have all identical normals in candidates so
								// we cannot find a suitable candidate and need the two default axes
								continue;
							}
						}
					}

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

				const express::base t = elem->product();
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
				const auto builder = new BVH_LinearBuilder<double, 3>(BVH_Constants_LeafNodeSizeDefault, BVH_Constants_MaxTreeDepth);
				BVH_Triangulation<double, 3> triangulation(builder);

				for (size_t i = 0; i < elem_verts.size(); i += 3) {
#if OCC_VERSION_HEX >= 0x80000
					triangulation.Vertices.Append(BVH_Vec3d(elem_verts[i], elem_verts[i + 1], elem_verts[i + 2]));
#else
					triangulation.Vertices.push_back(BVH_Vec3d(elem_verts[i], elem_verts[i + 1], elem_verts[i + 2]));
#endif
					verts.push_back(gp_Pnt(elem_verts[i], elem_verts[i + 1], elem_verts[i + 2]));
				}

				for (size_t i = 0; i < elem_faces.size(); i += 3) {
					const auto& v1_pnt = verts[elem_faces[i]];
					const auto& v2_pnt = verts[elem_faces[i + 1]];
					const auto& v3_pnt = verts[elem_faces[i + 2]];
					gp_Vec dir1(v1_pnt, v2_pnt);
					gp_Vec dir2(v1_pnt, v3_pnt);
					gp_Vec cross_product = dir1.Crossed(dir2);
					if (cross_product.Magnitude() > ::Precision::Confusion()) {
#if OCC_VERSION_HEX >= 0x80000
						triangulation.Elements.Append(BVH_Vec4i(
#else
						triangulation.Elements.push_back(BVH_Vec4i(
#endif
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
				is_manifold_[t] = ifcopenshell::geom::tree::is_manifold(elem_faces);
				tris_[t] = std::move(tris);
				verts_[t] = std::move(verts);
				normals_[t] = std::move(normals);
				aabbs_[t] = aabb;
				obbs_[t] = obb;
				max_protrusions_[t] = std::min(std::min(obb.XHSize(), obb.YHSize()), obb.ZHSize()) * 2;
			}

		private:
			template <typename T>
			void apply_matrix_to_flat_verts(const std::vector<T>& flat_list, const ifcopenshell::geom::taxonomy::matrix4::ptr& matrix, std::vector<T>& result) {
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
		};
	}

}

#endif
