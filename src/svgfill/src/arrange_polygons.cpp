// #define SVGFILL_DEBUG
// #define SVGFILL_MAIN

#ifndef SVGFILL_MAIN
#include "svgfill.h"
#endif

#include <CGAL/Exact_predicates_exact_constructions_kernel.h>
#include <CGAL/Boolean_set_operations_2.h>
#include <CGAL/Polygon_2.h>
#include <CGAL/Polygon_with_holes_2.h>
#include <CGAL/Partition_traits_2.h>
#include <CGAL/partition_2.h>
#include <CGAL/create_offset_polygons_2.h>
#include <CGAL/Polygon_triangulation_decomposition_2.h>
#include <CGAL/Gmpz.h>
#include <CGAL/Filtered_extended_homogeneous.h>
#include <CGAL/box_intersection_d.h>

#include <CGAL/AABB_tree.h>
#include <CGAL/AABB_traits.h>
#include <CGAL/AABB_segment_primitive.h>

#include <vector>
#include <iostream>

#include "graph_2d.h"

#if CGAL_VERSION_NR >= 1060000000
#define variant_get std::get_if
#define my_shared_ptr std::shared_ptr
#else
#define variant_get boost::get
#define my_shared_ptr boost::shared_ptr
#endif

typedef CGAL::Exact_predicates_exact_constructions_kernel K;
typedef CGAL::Polygon_2<K> Polygon_2;
typedef CGAL::Polygon_with_holes_2<K> Polygon_with_holes_2;
typedef K::Point_2 Point_2;
typedef K::Segment_2 Segment_2;
typedef std::vector<Polygon_2> Polygon_list;
typedef CGAL::Arr_segment_traits_2<K> Traits_2;
typedef typename Traits_2::Point_2 Arr_Point_2;
typedef typename Traits_2::X_monotone_curve_2 Arr_Segment_2;
typedef CGAL::Arrangement_2<Traits_2> Arrangement_2;

template <typename K>
using Triangle = std::array<CGAL::Point_2<K>, 3>;

template <typename K2>
Polygon_2 convert_polygon(const CGAL::Polygon_2<K2>& poly) {
    Polygon_2 exact_poly;
    typedef CGAL::Cartesian_converter<K2, K> Converter_Epick_to_Epeck;
    Converter_Epick_to_Epeck converter;
    for (auto vit = poly.vertices_begin(); vit != poly.vertices_end(); ++vit) {
        exact_poly.push_back(converter(*vit));  // Convert each vertex
    }
    return exact_poly;
}

template <typename P>
void remove_close_points(P& p, double eps = 1.e-2) {
    std::vector<CGAL::Point_2<typename P::Traits::Kernel>> ps;
    ps.reserve(p.size());
    auto I = p.begin();
    auto J = I + 1;
    for (;; ++J) {
        bool last = false;
        if (J == p.end()) {
            J = p.begin();
            last = true;
        }
        // std::cout << "d " << std::sqrt(CGAL::to_double(CGAL::squared_distance(*I, *J))) << std::endl;
        if (CGAL::squared_distance(*I, *J) > (eps * eps)) {
            ps.push_back(*J);
            I = J;
        }
        if (last) {
            break;
        }
    }
    if (ps.size() >= 2 && CGAL::squared_distance(ps.front(), ps.back()) <= eps * eps) {
        // Remove the last point if it is too close to the first point
        ps.pop_back();
    }
    if (ps.size() != p.size()) {
        // std::cerr << "Removed " << (p.size() - ps.size()) << " close points from polygon" << std::endl;
        p = P(ps.begin(), ps.end());
    }
}

std::vector<Polygon_2> create_and_convert_offset_polygon(double offset_distance, const Polygon_2& polygon_) {
    auto polygon = polygon_;
    if (!polygon.is_counterclockwise_oriented()) {
        polygon.reverse_orientation();
    }

    remove_close_points(polygon);

    // Create the offset polygons using Epick kernel
    // create_exterior_skeleton_and_offset_polygons_2()
    std::vector<my_shared_ptr<CGAL::Polygon_2<CGAL::Epick>>> offset_polygons;

    if (offset_distance >= 0.) {
        offset_polygons = CGAL::create_exterior_skeleton_and_offset_polygons_2(offset_distance, polygon);
        // erase the first outer frame
        offset_polygons.erase(offset_polygons.begin());
        offset_polygons.front()->reverse_orientation();
    } else {
        offset_polygons = CGAL::create_interior_skeleton_and_offset_polygons_2(-offset_distance, polygon);
    }

    // Convert each offset polygon back to the Epeck kernel
    std::vector<Polygon_2> exact_offset_polygons;
    for (auto& inexact_poly_ptr : offset_polygons) {
        remove_close_points(*inexact_poly_ptr);
        Polygon_2 exact_poly = convert_polygon(*inexact_poly_ptr);
        exact_offset_polygons.push_back(exact_poly);
    }

    return exact_offset_polygons;
}

template <typename T>
T take_first_if_single_item(const std::vector<T>& vec) {
    if (vec.size() == 0) {
		throw std::runtime_error("Expected at least one item");
    }
    if (true || vec.size() == 1) {
        return vec.front();
    }
    throw std::runtime_error("Expected a single item");
}

template <typename T>
boost::optional<T> maybe_take_first_if_single_item(const std::vector<T>& vec) {
    if (vec.size() == 0) {
        return boost::none;
    }
    if (true || vec.size() == 1) {
        return vec.front();
    }
}

template <typename T>
boost::optional<Polygon_2> subtract_retain_largest(const T& lhs, const T& rhs) {
    std::vector<Polygon_with_holes_2> result;
    boost::optional<Polygon_2> mp;

    CGAL::difference(lhs, rhs, std::back_inserter(result));

    std::sort(result.begin(), result.end(), [](const Polygon_with_holes_2& a, const Polygon_with_holes_2& b) {
        return a.outer_boundary().area() < b.outer_boundary().area();
    });

    if (result.size() > 0) {
        if (result.front().has_holes()) {
            return boost::none;
        }
        return result.front().outer_boundary();
    }

    return boost::none;
}

Polygon_2 circ_to_poly(typename Arrangement_2::Ccb_halfedge_const_circulator circ)
{
    Polygon_2 poly;
    auto curr = circ;
    do {
        poly.push_back(curr->source()->point());
    } while (++curr != circ);
    return poly;
}

Polygon_with_holes_2 circ_to_poly(typename Arrangement_2::Ccb_halfedge_const_circulator circ, typename Arrangement_2::Inner_ccb_const_iterator a, typename Arrangement_2::Inner_ccb_const_iterator b)
{
    Polygon_with_holes_2 poly(circ_to_poly(circ));
    for (auto it = a; it != b; ++it) {
        poly.add_hole(circ_to_poly(*it));
    }
    return poly;
}

Polygon_2 fuse_with_offset(const std::vector<Polygon_2>& polygons, double polygon_offset_distance) {
    // Find the outer perimeter using offset - union - negative offset
    std::vector<Polygon_2> offset_polygons;
    for (auto& r : polygons) {
        auto ps = create_and_convert_offset_polygon(polygon_offset_distance, r);
        for (auto& p : ps) {
            if (!p.is_simple()) {
                /*{
                    std::cerr << "[";
                    bool first = true;
                    for (auto& pp : r) {
                        if (!first) {
                            std::cerr << ",";
                        }
                        first = false;
                        std::cerr << "(" << pp.x() << "," << pp.y() << ")";
                    }
                    std::cerr << "]" << std::endl;
                }
                {
                    std::cerr << "[";
                    bool first = true;
                    for (auto& pp : p) {
                        if (!first) {
                            std::cerr << ",";
                        }
                        first = false;
                        std::cerr << "(" << pp.x() << "," << pp.y() << ")";
                    }
                    std::cerr << "]" << std::endl;
                }*/
                throw std::runtime_error("Complex polygon originated from offset");
            }
        }
        offset_polygons.insert(offset_polygons.end(), ps.begin(), ps.end());
    }

    // Perform Boolean union on the offset polygons
    std::vector<Polygon_with_holes_2> unioned_polygons;
    CGAL::join(offset_polygons.begin(), offset_polygons.end(), std::back_inserter(unioned_polygons));
    Polygon_2 fused_removed_close_points = unioned_polygons.front().outer_boundary();
    remove_close_points(unioned_polygons.front().outer_boundary(), polygon_offset_distance);

    // Apply negative offset to get the outer perimeter polygon
    auto inner_offset = create_and_convert_offset_polygon(
        // Slightly smaller inset distance for non-manifold situs?
        -polygon_offset_distance + 1.e-8,
        fused_removed_close_points);

    if (inner_offset.size() != 1) {
        throw std::runtime_error("Unexpected union outcome - num outer perimiters: " + std::to_string(inner_offset.size()));
    }

    return inner_offset.front();
}

double estimate_polygon_offset_distance(const std::vector<Polygon_2>& polygons) {
    double total_edge_length = 0.;
    size_t num_edges = 0;
    for (auto& p : polygons) {
        for (auto it = p.edges_begin(); it != p.edges_end(); ++it) {
            total_edge_length += std::sqrt(CGAL::to_double(CGAL::squared_distance(it->start(), it->end())));
            num_edges += 1;
        }
    }
    return total_edge_length / num_edges / 2;
}

void clean_polygon(Polygon_2& poly) {
    // Ensure counterclockwise orientation and remove duplicate last point if present also remove close points
    if (!poly.is_counterclockwise_oriented()) {
        poly.reverse_orientation();
    }
    std::vector<CGAL::Point_2<K>> ps(poly.begin(), poly.end());
    if (ps.front() == ps.back()) {
        ps.pop_back();
    }
    poly = Polygon_2(ps.begin(), ps.end());
    remove_close_points(poly);
}

void smooth_polygon(double factor, Polygon_2& poly) {
    auto ps = create_and_convert_offset_polygon(-factor, poly);
    if (ps.size() == 1) {
        auto r2 = ps.front();
        ps = create_and_convert_offset_polygon(+factor, r2);
        if (ps.size() == 1) {
            poly = ps.front();
        }
    }
}

template <typename K, typename OutIt>
void split_self_intersecting_polygon(const CGAL::Polygon_2<K>& poly, OutIt output_it) {
    if (poly.is_simple()) {
        *output_it++ = poly;
        return;
    }
    Arrangement_2 arr;
    for (auto it = poly.edges_begin(); it != poly.edges_end(); ++it) {
        CGAL::insert(arr, Segment_2(it->start(), it->end()));
    }
    for (auto it = arr.faces_begin(); it != arr.faces_end(); ++it) {
        if (it->is_unbounded()) {
            for (auto jt = it->inner_ccbs_begin(); jt != it->inner_ccbs_end(); ++jt) {
                auto inner = circ_to_poly(*jt);
                // reverse because it's an inner bound to the infinite outer facet
                inner.reverse_orientation();
                *output_it++ = inner;
            }
        }
    }
}

std::set<std::pair<size_t, size_t>>
find_overlaps(const std::vector<Polygon_2>& polygons) {
    typedef CGAL::Box_intersection_d::Box_with_handle_d<double, 2, size_t, CGAL::Box_intersection_d::ID_EXPLICIT> Box;
    std::vector<Box> boxes;

    std::vector<std::vector<CGAL::Triangle_2<K>>> input_triangulated;

    for (auto it = polygons.begin(); it != polygons.end(); ++it) {
        constexpr double offset = 1.e-3;
        auto b = it->bbox();
        boxes.emplace_back(
            CGAL::Bbox_2(b.xmin() - offset, b.ymin() - offset, b.xmax() + offset, b.ymax() + offset),
            std::distance(polygons.begin(), it));

        CGAL::Polygon_triangulation_decomposition_2<K> decompositor;
        std::vector<Polygon_2> temp;
        decompositor(*it, std::back_inserter(temp));
        input_triangulated.emplace_back();
        for (auto& pol : temp) {
            auto it = pol.vertices_circulator();
            const auto& p = *(it++);
            const auto& q = *(it++);
            const auto& r = *(it++);
            input_triangulated.back().emplace_back(p, q, r);
        }
    }

    std::set<std::pair<size_t, size_t>> overlaps;

    CGAL::box_self_intersection_d(boxes.begin(), boxes.end(), [&input_triangulated, &overlaps](const Box& a, const Box& b) {
        for (auto& t1 : input_triangulated[a.handle()]) {
            bool registered_overlap = false;
            for (auto& t2 : input_triangulated[b.handle()]) {
                if (CGAL::squared_distance(t1, t2) < (1.e-3 * 1.e-3)) {
                    overlaps.insert({(a.handle() < b.handle()) ? a.handle() : b.handle(),
                                     (a.handle() < b.handle()) ? b.handle() : a.handle()});
                    registered_overlap = true;
                    break;
                }
            }
            if (registered_overlap) {
                // no need to check other triangles
                break;
            }
        }
    });

    return overlaps;
}

class DebugWriter {
  public:
    DebugWriter(bool enabled, const std::string& filename_prefix)
        : enabled_(enabled) {
        if (enabled_) {
            obj.open(filename_prefix + ".obj");
            vi = 1;
            svg.open(filename_prefix + ".svg");
            svg << "<svg xmlns=\"http://www.w3.org/2000/svg\" version=\"1.1\" viewBox=\"-10 -10 200 200\">\n";
        }
    }
    ~DebugWriter() {
        if (enabled_) {
            svg << "</svg>\n";
            obj << std::flush;
            obj.close();
            svg.close();
        }
    }

    void write_polygon(const Polygon_2& polygon, const std::string& name) {
        if (enabled_) {
            write_polygon_to_obj_(obj, vi, true, polygon, name);
            write_polygon_to_svg_(svg, polygon, name);
            obj << std::flush;
        }
    }

    void write_segment(const Point_2& p, const Point_2& q, const std::string& name) {
        if (enabled_) {
            if (last_segment_name_ != name) {
                last_segment_name_ = name;
                obj << "o " << name << "\n";
            }
            obj << "v " << CGAL::to_double(p.x()) << " " << CGAL::to_double(p.y()) << " 0\n";
            obj << "v " << CGAL::to_double(q.x()) << " " << CGAL::to_double(q.y()) << " 0\n";
            obj << "l " << vi++;
            obj << " " << vi++ << "\n";

            svg << "<line class=\"" << name << "\" x1=\"" << CGAL::to_double(p.x()) << "\" y1=\"" << -CGAL::to_double(p.y()) << "\" x2=\"" << CGAL::to_double(q.x()) << "\" y2=\"" << -CGAL::to_double(q.y()) << "\" />";

            obj << std::flush;
        }
    }

    void write_polygon(const Polygon_with_holes_2& polygon, const std::string& name) {
        if (enabled_) {
            write_polygon(polygon.outer_boundary(), name);
            for (auto hit = polygon.holes_begin(); hit != polygon.holes_end(); ++hit) {
                write_polygon(*hit, name);
            }
        }
    }

    void write_polygons(const std::vector<Polygon_2>& polygons, const std::string& name) {
        if (enabled_) {
            size_t i = 0;
            for (auto& polygon : polygons) {
                write_polygon_to_obj_(obj, vi, true, polygon, name + "_" + std::to_string(i++));
                write_polygon_to_svg_(svg, polygon, name);
             }
            obj << std::flush;
        }
    }

    void write_polygons(const std::vector<Polygon_with_holes_2>& polygons, const std::string& name) {
        if (enabled_) {
            size_t i = 0;
            for (auto& polygon : polygons) {
                write_polygon_to_obj_(obj, vi, true, polygon.outer_boundary(), name + "_" + std::to_string(i));
                write_polygon_to_svg_(svg, polygon.outer_boundary(), name);
                for (auto hit = polygon.holes_begin(); hit != polygon.holes_end(); ++hit) {
                    write_polygon_to_obj_(obj, vi, true, *hit, name + "_" + std::to_string(i));
                    write_polygon_to_svg_(svg, *hit, name);
                }
            }
            obj << std::flush;
        }
    }

  private:
    std::ofstream obj;
    size_t vi;
    std::ofstream svg;
    bool enabled_;
    std::string last_segment_name_;
    
    void write_polygon_to_svg_(std::ostream& ofs, const Polygon_2& polygon, const std::string& class_name = "") {
        ofs << "<polygon class=\"" + class_name + "\" points=\"";
        for (auto vit = polygon.vertices_begin(); vit != polygon.vertices_end(); ++vit) {
            ofs << CGAL::to_double(vit->x()) << "," << -CGAL::to_double(vit->y()) << " ";
        }
        ofs << "\"/>\n";
    }

    void write_polygon_to_obj_(std::ofstream& ofs, size_t& vertex_index, bool as_line, const Polygon_2& polygon, const std::string& name) {
        ofs << "o " << name << "\n"; // Object name

        // Write vertices
        for (auto vit = polygon.vertices_begin(); vit != polygon.vertices_end(); ++vit) {
            ofs << "v " << CGAL::to_double(vit->x()) << " " << CGAL::to_double(vit->y()) << " 0\n";
        }

        if (as_line) {
            // Write line segments (edges)
            for (size_t j = 0; j < polygon.size(); ++j) {
                ofs << "l " << vertex_index + j << " " << vertex_index + (j + 1) % polygon.size() << "\n";
            }
        } else {
            ofs << "f";
            for (size_t j = 0; j < polygon.size(); ++j) {
                ofs << " " << vertex_index + j;
            }
            ofs << "\n";
        }

        vertex_index += polygon.size();
    }
};

void eliminate_overlaps(double OVERLAP_RESOLUTION_DISTANCE, std::vector<Polygon_2>& polygons) {
    // solve overlaps by means of subtraction
    // loop over overlaps and subtract the smaller polygon from the larger one

    std::set<size_t> eliminated_polies;

    /*
    std::map<size_t, size_t> overlap_counts;
    for (auto& p : overlaps) {
        overlap_counts[p.first]++;
        overlap_counts[p.second]++;
    }
    */

    auto overlaps = find_overlaps(polygons);

    for (const auto& edge : overlaps) {
        // Skip eliminated
        if (eliminated_polies.find(edge.first) != eliminated_polies.end() ||
            eliminated_polies.find(edge.second) != eliminated_polies.end()) {
            continue;
        }

        // Many overlaps indicate an aggregated polygon, skip them
        /*
        if (overlap_counts[edge.first] > 10 || overlap_counts[edge.second] > 10) {
            if (overlap_counts[edge.first] > 10) {
                eliminated_polies.insert(edge.first);
            }
            if (overlap_counts[edge.second] > 10) {
                eliminated_polies.insert(edge.second);
            }
            continue;
        }
        */

        // these are pointers now, because otherwise swap would not work?
        auto* poly1 = &polygons[edge.first];
        auto* poly2 = &polygons[edge.second];

        // @todo this is applied during overlap processing, maybe better after the boolean operation,
        // because they can be come small or narrow when overlaps are resolved

        // Populate eliminated_polies with small polygons
        // This can happen over time when modifications are made to the polygons to solve overlaps
        bool skip = false;
        if (poly1->area() < 1.e-2) {
            eliminated_polies.insert(edge.first);
            skip = true;
        }
        if (poly2->area() < 1.e-2) {
            eliminated_polies.insert(edge.second);
            skip = true;
        }
        // Small slivers are also just eliminated
        if (!maybe_take_first_if_single_item(create_and_convert_offset_polygon(-1.e-1, *poly1))) {
            eliminated_polies.insert(edge.first);
            skip = true;
        }
        if (!maybe_take_first_if_single_item(create_and_convert_offset_polygon(-1.e-1, *poly2))) {
            eliminated_polies.insert(edge.second);
            skip = true;
        }
        if (skip) {
            continue;
        }

        // Skip polygons that have a very high intersection over union
        // ratio, which indicates that they are very likely duplicates
        if (CGAL::do_intersect(*poly1, *poly2)) {
            std::vector<Polygon_with_holes_2> result;
            CGAL::intersection(*poly1, *poly2, std::back_inserter(result));
            typename K::FT intersection_area = 0;
            for (auto& r : result) {
                auto poly_area = r.outer_boundary().area();
                for (auto& h : r.holes()) {
                    poly_area -= h.area();
                }
                intersection_area += poly_area;
            }
            CGAL::Polygon_with_holes_2<K> poly12;
            CGAL::join(*poly1, *poly2, poly12);
            typename K::FT union_area = poly12.outer_boundary().area();
            for (auto& h : poly12.holes()) {
                union_area -= h.area();
            }
            if (union_area > 0 && intersection_area / union_area > 0.99) {
                // std::cerr << intersection_area / union_area << std::endl;
                eliminated_polies.insert(edge.first);
                continue;
            }
        }

        if (!(poly1->is_simple() && poly2->is_simple())) {
            continue;
        }

        {
            std::vector<Polygon_with_holes_2> result;

            boost::optional<Polygon_2> mp1, mp2, mp3, mp4;
            bool swap = false;

            swap = poly1->area() <= poly2->area();
            if (swap) {
                std::swap(poly1, poly2);
            }

            bool success = false;
            if ((mp1 = maybe_take_first_if_single_item(create_and_convert_offset_polygon(OVERLAP_RESOLUTION_DISTANCE, *poly2)))) {
                if ((mp2 = subtract_retain_largest(*poly1, *mp1))) {
                    if ((mp3 = maybe_take_first_if_single_item(create_and_convert_offset_polygon(OVERLAP_RESOLUTION_DISTANCE * 2, *mp2)))) {
                        if ((mp4 = subtract_retain_largest(*poly2, *mp3))) {
                            *poly1 = *mp2;
                            *poly2 = *mp4;
                            success = true;
                        }
                    }
                }
            }

            if (!success) {
                eliminated_polies.insert(swap ? edge.first : edge.second);
                continue;
            }
        }
    }

    // iterate over the eliminated polygons and remove them from the input polygons
    for (auto it = eliminated_polies.rbegin(); it != eliminated_polies.rend(); ++it) {
        polygons.erase(polygons.begin() + *it);
    }
}

class SegmentLookup {
  public:
    typedef std::vector<Polygon_2>::const_iterator PolygonIt;

    SegmentLookup(const std::vector<Polygon_2>& polygons)
        : polygons_ref_(polygons) 
    {
        // Unfortunately CGAL does not seem to have a ready to use aabb primitive for segments in 2D,
        // so we have to use 3D segments and aabb tree for 2D polygons.
        for (auto it = polygons.begin(); it != polygons.end(); ++it) {
            for (auto eit = it->edges_begin(); eit != it->edges_end(); ++eit) {
                CGAL::Segment_3<K> seg3d(
                    CGAL::Point_3<K>(eit->source().x(), eit->source().y(), 0),
                    CGAL::Point_3<K>(eit->target().x(), eit->target().y(), 0));
                all_segs.push_back(seg3d);
                seg_to_poly[&all_segs.back()] = it;
            }
        }
        tree_ = Tree(all_segs.begin(), all_segs.end());
        tree_.accelerate_distance_queries();
    }

    // This part is the most computationally expensive. Caching effectively halves the lookup time here, since every vertex on the subdivided corridor mesh has on average two outgoing edges.
    PolygonIt input_polygon_boundary(const Point_2& p, double tol = 1e-5) {
        auto it = input_polygon_boundary_cache_.find(p);
        if (it != input_polygon_boundary_cache_.end()) {
            return it->second;
        }

        // Find closest point & corresponding segment
        auto closest = tree_.closest_point_and_primitive(CGAL::Point_3<K>(p.x(), p.y(), 0));
        const auto& closest_pt = closest.first;
        auto seg_ptr = &*closest.second;

        double d = CGAL::to_double(CGAL::squared_distance(p, Point_2(closest_pt.x(), closest_pt.y())));

        PolygonIt res;
        if (d < (tol * tol)) {
            res = seg_to_poly.find(seg_ptr)->second;
        } else {
            res = polygons_ref_.end();
        }

        input_polygon_boundary_cache_[p] = res;
        return res;
    };

    std::pair<PolygonIt, CGAL::Point_2<K>> close_input_point(const CGAL::Point_2<K>& P) const {
        // @todo use tree
        CGAL::Point_2<K> closest;
        double closest_distance = std::numeric_limits<double>::infinity();
        auto input_it = polygons_ref_.end();

        // unfortunately some imprecision slept into the code so we can't
        // so we can't just use has_on_boundary() anymore
        for (auto it = polygons_ref_.begin(); it != polygons_ref_.end(); ++it) {
            for (auto& p : *it) {
                auto d = std::sqrt(CGAL::to_double(CGAL::squared_distance(P, p)));
                if (d < closest_distance) {
                    closest_distance = d;
                    closest = p;
                    input_it = it;
                }
            }
        }

        return std::make_pair(input_it, closest);
    };

    std::pair<PolygonIt, CGAL::Point_2<K>> project_input_point(const CGAL::Point_2<K>& P) const {
        // @todo use tree

        CGAL::Point_2<K> closest;
        typename K::FT closest_sq_distance = std::numeric_limits<double>::infinity();
        auto input_it = polygons_ref_.end();

        // unfortunately some imprecision slept into the code so we can't
        // so we can't just use has_on_boundary() anymore
        for (auto it = polygons_ref_.begin(); it != polygons_ref_.end(); ++it) {
            for (auto jt = it->edges_begin(); jt != it->edges_end(); ++jt) {
                auto Pp = jt->supporting_line().projection(P);
                auto d = CGAL::squared_distance(Pp, P);
                if (d < closest_sq_distance) {
                    closest_sq_distance = d;
                    closest = Pp;
                    input_it = it;
                }
            }
        }

        return std::make_pair(input_it, closest);
    };

private:
    using TreeTraits = CGAL::AABB_traits<K, CGAL::AABB_segment_primitive<K, std::list<CGAL::Segment_3<K>>::iterator>>;
    using Tree = CGAL::AABB_tree<TreeTraits>;

    const std::vector<Polygon_2>& polygons_ref_;
    std::list<CGAL::Segment_3<K>> all_segs;
    std::unordered_map<CGAL::Segment_3<K>*, PolygonIt> seg_to_poly;
    Tree tree_;

    std::map<Point_2, std::vector<Polygon_2>::const_iterator> input_polygon_boundary_cache_;
};

Polygon_2 subdivide_polygon(double max_distance, const Polygon_2 & p) {
    std::vector<Point_2> points;
    for (auto it = p.edges_begin(); it != p.edges_end(); ++it) {
        const auto& seg = *it;
        auto num_splits = (int)std::ceil(std::sqrt(CGAL::to_double(seg.squared_length())) / max_distance) - 1;
        points.push_back(seg.source());
        for (auto i = 0; i < num_splits; ++i) {
            auto d = (seg.target() - seg.source()) / (num_splits + 1) * (i + 1);
            points.push_back(seg.source() + d);
        }
    }
    return Polygon_2(points.begin(), points.end());
};

Polygon_with_holes_2 subdivide_polygon(double max_distance, const Polygon_with_holes_2& pwh) {
    Polygon_2 outer = subdivide_polygon(max_distance, pwh.outer_boundary());
    std::vector<Polygon_2> holes;
    for (auto hit = pwh.holes_begin(); hit != pwh.holes_end(); ++hit) {
        holes.push_back(subdivide_polygon(max_distance, *hit));
    }
    return Polygon_with_holes_2(outer, holes.begin(), holes.end());
};

std::tuple<
    std::map<Point_2, std::vector<Point_2>>, 
    std::map<Point_2, std::pair<Point_2, Point_2>>,
    std::map<std::pair<Point_2, Point_2>, std::vector<const CGAL::Polygon_2<K>*>>>
build_line_graph(const std::vector<Polygon_2>& input_polygons, SegmentLookup& segment_lookup, const std::vector<Polygon_2>& triangular_polygons) {
    // Build maps of triangle -> edge and edge -> triangle in order to do traversal on the 'corridor mesh'
    std::map<std::pair<Point_2, Point_2>, std::vector<const CGAL::Polygon_2<K>*>> segment_to_facet;
    std::map<std::pair<Point_2, Point_2>, std::vector<const CGAL::Polygon_2<K>*>> segment_to_input_facet;
    std::map<std::pair<Point_2, Point_2>, Point_2> segment_to_midpoint;
    std::map<Point_2, std::pair<Point_2, Point_2>> midpoint_to_segment;
    std::map<const CGAL::Polygon_2<K>*, std::vector<std::pair<Point_2, Point_2>>> facet_to_segment;

    for (auto& tri : triangular_polygons) {
        for (size_t i = 0; i < 3; ++i) {
            size_t j = (i + 1) % 3;
            auto& pi = tri.vertex(i);
            auto& pj = tri.vertex(j);
            const bool orientation = std::lexicographical_compare(pi.cartesian_begin(), pi.cartesian_end(), pj.cartesian_begin(), pj.cartesian_end());
            std::pair<Point_2, Point_2> seg(orientation ? pi : pj, orientation ? pj : pi);
            segment_to_facet[seg].push_back(&tri);
            facet_to_segment[&tri].push_back(seg);
        }
    }

    // @todo The smarter thing to do probably after creating the corridor mesh, register segments wrt to originating input polygon(s) and maintain that mapping when subdividing

    // Register midpoints on the edges within the 'corridor mesh' that span multiple input polygons
    for (auto& p : segment_to_facet) {
        auto center = CGAL::ORIGIN + (((p.first.first - CGAL::ORIGIN) + (p.first.second - CGAL::ORIGIN)) / 2);

        auto p1index = segment_lookup.input_polygon_boundary(p.first.first);
        auto p2index = segment_lookup.input_polygon_boundary(p.first.second);

        segment_to_input_facet[p.first].push_back(&*p1index);
        segment_to_input_facet[p.first].push_back(&*p2index);

        if (p1index != input_polygons.end() && p2index != input_polygons.end() && p1index != p2index) {
            segment_to_midpoint[p.first] = center;
            midpoint_to_segment[center] = p.first;
        }
    }

    // Observe corridor mesh topology to join edge midpoints into a network
    std::map<Point_2, std::vector<Point_2>> line_graph;
    for (auto& p : segment_to_midpoint) {
        for (auto& q : segment_to_facet[p.first]) {
            for (auto& r : facet_to_segment[q]) {
                if (p.first == r) {
                    continue;
                }
                decltype(segment_to_midpoint)::const_iterator it;
                if ((it = segment_to_midpoint.find(r)) != segment_to_midpoint.end()) {
                    line_graph[p.second].push_back(it->second);
                }
            }
        }
    }

    return {line_graph, midpoint_to_segment, segment_to_input_facet};
}

std::set<Triangle<K>> find_triangles(const std::map<Point_2, std::vector<Point_2>>& line_graph) {
    // Find triangles in this network often occuring at junctions in the corridor mesh
    std::set<Triangle<K>> triangles;
    std::function<void(std::vector<Point_2>&)> find_triangles_recursive;
    find_triangles_recursive = [&](std::vector<Point_2>& path) -> void {
        // If depth reaches 3, check for a triangle
        if (path.size() == 3) {
            // Check if we can complete the triangle by going from the current point back to the start
            const std::vector<Point_2>& neighbors_current = line_graph.at(path.back());
            if (std::find(neighbors_current.begin(), neighbors_current.end(), path.front()) != neighbors_current.end()) {
                // We found a triangle, add it to the set
                Triangle<K> triangle = {path[0], path[1], path[2]};
                std::sort(triangle.begin(), triangle.end());
                triangles.insert(triangle);
            }
            return;
        }

        // Otherwise, continue exploring neighbors
        const std::vector<Point_2>& neighbors = line_graph.at(path.back());
        for (const Point_2& neighbor : neighbors) {
            if (std::find(path.begin(), path.end(), neighbor) == path.end()) {
                path.push_back(neighbor);
                find_triangles_recursive(path);
                path.pop_back(); // Backtrack
            }
        }
    };

    for (auto& p : line_graph) {
        std::vector<Point_2> ps = {p.first};
        find_triangles_recursive(ps);
    }

    return triangles;
}

std::set<std::pair<Point_2, Point_2>> eliminate_triangles(const std::map<Point_2, std::vector<Point_2>>& line_graph) {
    auto triangles = find_triangles(line_graph);

    // @todo this currently uses a simple cartesian kernel for performance for support of sqrt, but
    // this should be possible to rewrite as ratios/slopes in the exact kernel as well
    using SK = CGAL::Simple_cartesian<double>;
    CGAL::Cartesian_converter<K, SK> C{};

    std::set<std::pair<Point_2, Point_2>> eliminated_segments;
    for (auto& t : triangles) {
        Triangle<SK> st;
        std::transform(t.begin(), t.end(), st.begin(), C);

        double global_min_abs_dot = std::numeric_limits<double>::infinity();
        size_t global_min_abs_dot_index;

        for (size_t i = 0; i < 3; ++i) {
            auto j = (i + 2) % 3;
            auto e0 = st[i] - st[j];
            e0 /= std::sqrt(e0.squared_length());

            double max_abs_dot = 0.;

            {
                auto& ni = line_graph.find(t[i])->second;
                for (auto& n : ni) {
                    if (std::find(t.begin(), t.end(), n) == t.end()) {
                        // not contained in triangle
                        auto sn = C(n);
                        auto en = sn - st[i];
                        en /= std::sqrt(en.squared_length());
                        auto dot = std::abs(en * e0);

                        if (dot > max_abs_dot) {
                            max_abs_dot = dot;
                        }
                    }
                }
            }

            {
                auto& nj = line_graph.find(t[j])->second;
                for (auto& n : nj) {
                    if (std::find(t.begin(), t.end(), n) == t.end()) {
                        // not contained in triangle
                        auto sn = C(n);
                        auto en = sn - st[j];
                        en /= std::sqrt(en.squared_length());
                        auto dot = std::abs(en * e0);

                        if (dot > max_abs_dot) {
                            max_abs_dot = dot;
                        }
                    }
                }
            }

            if (max_abs_dot < global_min_abs_dot) {
                global_min_abs_dot = max_abs_dot;
                global_min_abs_dot_index = i;
            }
        }

        {
            auto i = global_min_abs_dot_index;
            auto j = (i + 2) % 3;

            eliminated_segments.insert({t[i], t[j]});
            eliminated_segments.insert({t[j], t[i]});
        }
    }

    return eliminated_segments;
}

bool is_parallel_2degree_node(Graph2D<K>::vertex_const_iterator vit) {
    auto it = vit->second.begin();
    auto& P = *it++;
    auto& Q = *it++;
    auto e1 = P - vit->first;
    auto e2 = vit->first - Q;
    if (e1.squared_length() == 0 || e2.squared_length() == 0) {
        // @todo why does this happen?
        return false;
    }
    e1 /= std::sqrt(CGAL::to_double(e1.squared_length()));
    e2 /= std::sqrt(CGAL::to_double(e2.squared_length()));
    return std::abs(CGAL::to_double(e1 * e2)) > (1. - 1.e-5);
};


void eliminate_colinear_vertices(Graph2D<K>& G) {
    size_t n_vertices_removed = 0;
    for (auto vit = G.vertices_begin(); vit != G.vertices_end();) {
        if (vit->second.size() == 2) {
            if (is_parallel_2degree_node(vit)) {
                vit = G.eliminate_vertex(vit);
                ++n_vertices_removed;
            } else {
                ++vit;
            }
        } else {
            ++vit;
        }
    }
}

void edge_slide(Graph2D<K>& G) {
    std::list<CGAL::Segment_2<K>> edges_to_remove, edges_to_insert;

    for (auto vit = G.vertices_begin(); vit != G.vertices_end(); ++vit) {
        auto& selected = vit->first;

        if (vit->second.size() >= 3) {
            for (auto vjt = vit->second.begin(); vjt != vit->second.end(); ++vjt) {
                auto& neighbour = *vjt;
                bool processed_neighbour = false;

                if (G.find(neighbour)->second.size() == 2 && !is_parallel_2degree_node(G.find(neighbour))) {
                    auto vkt = G.find(neighbour)->second.begin();
                    if (selected == *vkt) {
                        vkt++;
                    }
                    auto& other = *vkt;

                    if ((other - neighbour).squared_length() < (neighbour - selected).squared_length()) {
                        continue;
                    }

                    auto incoming = CGAL::Ray_2<K>(other, neighbour - other);
                    boost::optional<CGAL::Segment_2<K>> closest_neighbouring_segment;
                    boost::optional<CGAL::Point_2<K>> closest_intersection_point;
                    K::FT sq_distance_along_ray = std::numeric_limits<double>::infinity();

                    for (auto vlt = vit->second.begin(); vlt != vit->second.end(); ++vlt) {
                        auto& other_neighbour = *vlt;
                        if (vlt != vjt) {
                            CGAL::Segment_2<K> neighbouring_segment(selected, other_neighbour);
                            auto x = CGAL::intersection(incoming, neighbouring_segment);
                            if (x) {
                                if (auto* xp = variant_get<CGAL::Point_2<K>>(&*x)) {
                                    auto dist = ((*xp) - other).squared_length();
                                    if (dist < sq_distance_along_ray) {
                                        closest_neighbouring_segment = neighbouring_segment;
                                        closest_intersection_point = *xp;
                                        sq_distance_along_ray = dist;
                                    }
                                }
                            }
                        }
                    }

                    if (closest_intersection_point && closest_neighbouring_segment) {
                        edges_to_remove.push_back(*closest_neighbouring_segment);
                        edges_to_remove.push_back({neighbour, selected});
                        edges_to_insert.push_back({closest_neighbouring_segment->source(), *closest_intersection_point});
                        edges_to_insert.push_back({closest_neighbouring_segment->target(), *closest_intersection_point});
                        edges_to_insert.push_back({neighbour, *closest_intersection_point});

                        processed_neighbour = true;
                    }
                }
                if (processed_neighbour) {
                    // Only one neigbour is processed because otherwise we obtain intersections
                    break;
                }
            }
        }
    }

    for (auto& s : edges_to_remove) {
        G.remove_edge(s.source(), s.target());
    }

    for (auto& s : edges_to_insert) {
        G.insert(s.source(), s.target());
    }
}

std::list<std::pair<Point_2, Point_2>> extend_end_vertices_based_on_input(
    const Graph2D<K>& G, 
    const std::map<Point_2, std::pair<Point_2, Point_2>>& midpoint_to_segment,
    const std::map<std::pair<Point_2, Point_2>, std::vector<const CGAL::Polygon_2<K>*>>& segment_to_input_facet,
    const Polygon_list& inner_offset,
    const SegmentLookup& segment_lookup
){
    std::list<std::pair<Point_2, Point_2>> constructed_segments;

    for (auto it = G.vertices_begin(); it != G.vertices_end(); ++it) {
        if (it->second.size() == 1) {
            auto& M = it->first;

            const std::pair<Point_2, Point_2>* q = nullptr;

            if (midpoint_to_segment.find(M) == midpoint_to_segment.end()) {
                typename K::FT min_sq_distance = std::numeric_limits<double>::infinity();
                for (auto& pa : midpoint_to_segment) {
                    if (CGAL::squared_distance(pa.first, M) < min_sq_distance) {
                        q = &pa.second;
                        min_sq_distance = CGAL::squared_distance(pa.first, M);
                    }
                }
            } else {
                q = &midpoint_to_segment.find(M)->second;
            }

            if (q == nullptr) {
                continue;
            }

            bool handled_as_graph_path = false;

            // distance from unioned - shoot ray?
            if (segment_to_input_facet.find(*q)->second.size() == 2) {
                for (auto& bnd : inner_offset) {
                    // if point M is contained in bnd interior:
                    if (bnd.has_on_bounded_side(M)) {
                        auto& incoming = *it->second.begin();
                        // create ray incoming -> M
                        CGAL::Ray_2<K> ray(incoming, M - incoming);
                        // intersect ray with boundary
                        boost::optional<CGAL::Segment_2<K>> closest_segment;
                        boost::optional<CGAL::Point_2<K>> closest_intersection_point;
                        K::FT sq_distance_along_ray = std::numeric_limits<double>::infinity();
                        for (auto jt = bnd.edges_begin(); jt != bnd.edges_end(); ++jt) {
                            const auto& seg = *jt;
                            auto x = CGAL::intersection(ray, seg);
                            if (x) {
                                if (auto* xp = variant_get<CGAL::Point_2<K>>(&*x)) {
                                    auto dist = ((*xp) - M).squared_length();
                                    if (dist < sq_distance_along_ray) {
                                        closest_segment = seg;
                                        closest_intersection_point = *xp;
                                        sq_distance_along_ray = dist;
                                    }
                                }
                            }
                        }

                        if (closest_intersection_point) {
                            Graph2D<K> GGG(bnd);
                            GGG.refine(*GGG.query(*closest_intersection_point, 0.01), *closest_intersection_point);

                            std::array<std::set<CGAL::Point_2<K>>, 2> input_points = {{{}, {}}};

                            size_t i = 0;
                            for (auto& fac : segment_to_input_facet.find(*q)->second) {
                                for (auto it = fac->vertices_begin(); it != fac->vertices_end(); ++it) {
                                    auto seg = GGG.query(*it, 0.01);
                                    if (seg) {
                                        if (seg->source() != *it && seg->target() != *it) {
                                            GGG.refine(*seg, *it);
                                        }
                                        input_points[i].insert(*it);
                                    }
                                }
                                i++;
                            }

                            auto a1 = GGG.shorted_path(*closest_intersection_point, input_points[0]);
                            auto a2 = GGG.shorted_path(*closest_intersection_point, input_points[1]);

                            if (!a1.empty() && !a2.empty()) {

                                if (M != *closest_intersection_point) {
                                    constructed_segments.push_front({M, *closest_intersection_point});
                                }
                                for (auto it = a1.begin(); it != a1.end() && std::next(it) != a1.end(); ++it) {
                                    constructed_segments.push_front({*it, *(std::next(it))});
                                }
                                for (auto it = a2.begin(); it != a2.end() && std::next(it) != a2.end(); ++it) {
                                    constructed_segments.push_front({*it, *(std::next(it))});
                                }

                                handled_as_graph_path = true;
                                break;
                            }
                        }
                    }
                }
            }

            if (!handled_as_graph_path) {
                // else we choose to map point to the midpoint of the found two close points.

                auto pq = segment_lookup.close_input_point(q->first);
                auto pr = segment_lookup.close_input_point(q->second);

                auto Q = pq.second;
                auto R = pr.second;

                if (Q == R) {
                    // this can happen in situations like this:
                    // where Q and R are co-located, because the point R' is further away
                    // in that case M + M-Q should gives is x that we then project onto the
                    // input boundary
                    //
                    //
                    // ┌───────┐
                    // │       │
                    // │       │
                    // │       │
                    // └───────o   <--Q,R
                    //
                    // ────────o   <--M
                    //
                    // ┌───────x───────────────o  <---R'
                    // │                       │
                    // │                       │
                    // │                       │
                    // │                       │
                    // └───────────────────────┘

                    // @todo is this projection actually necessary or is it already 'exact enough'?
                    R = segment_lookup.project_input_point(M + (M - Q)).second;
                }

                auto avg = CGAL::ORIGIN + ((Q - CGAL::ORIGIN) + (R - CGAL::ORIGIN)) / 2;

                constructed_segments.push_front({M, avg});
                constructed_segments.push_front({avg, Q});
                constructed_segments.push_front({avg, R});
            }
        }
    }

    return constructed_segments;
}

void fuse_corridor_halves_with_input(Arrangement_2& arr, Graph2D<K>& G, SegmentLookup& segment_lookup, const Polygon_list& input_polygons, DebugWriter& debug_output) {
    std::set<Arrangement_2::Halfedge_handle> edges_to_remove;

    for (auto it = arr.faces_begin(); it != arr.faces_end(); ++it) {
        if (it->is_unbounded()) {
            continue;
        }
        bool is_corridor = false;
        {
            auto curr = it->outer_ccb();
            do {
                auto& p = curr++->source()->point();
                if (G.find(p) != G.vertices_end()) {
                    is_corridor = true;
                    break;
                }
            } while (curr != it->outer_ccb());

            for (auto jt = it->inner_ccbs_begin(); jt != it->inner_ccbs_end(); ++jt) {
                curr = *jt;
                do {
                    auto& p = curr++->source()->point();
                    if (G.find(p) != G.vertices_end()) {
                        is_corridor = true;
                        break;
                    }
                } while (curr != *jt);
                if (is_corridor) {
                    break;
                }
            }
        }

        if (is_corridor) {
            auto curr = it->outer_ccb();
            do {
                auto& p = curr->source()->point();
                auto& q = curr->target()->point();
                auto center = CGAL::ORIGIN + (((p - CGAL::ORIGIN) + (q - CGAL::ORIGIN)) / 2);
                auto p1index = segment_lookup.input_polygon_boundary(center);
                const bool on_orig_bound = p1index != input_polygons.end();
                if (on_orig_bound) {
                    if (edges_to_remove.find(curr->twin()) != edges_to_remove.end()) {
                        // std::cerr << "Warning trying to delete edge twice" << std::endl;
                    } else {
                        edges_to_remove.insert(curr);
                    }
                }
                curr++;
            } while (curr != it->outer_ccb());

            for (auto jt = it->inner_ccbs_begin(); jt != it->inner_ccbs_end(); ++jt) {
                curr = *jt;
                do {
                    auto& p = curr->source()->point();
                    auto& q = curr->target()->point();
                    auto center = CGAL::ORIGIN + (((p - CGAL::ORIGIN) + (q - CGAL::ORIGIN)) / 2);
                    auto p1index = segment_lookup.input_polygon_boundary(center);
                    const bool on_orig_bound = p1index != input_polygons.end();
                    if (on_orig_bound) {
                        if (edges_to_remove.find(curr->twin()) != edges_to_remove.end()) {
                            // std::cerr << "Warning trying to delete edge twice" << std::endl;
                        } else {
                            edges_to_remove.insert(curr);
                        }
                    }
                    curr++;
                } while (curr != *jt);
                if (is_corridor) {
                    break;
                }
            }
        }
    }

    size_t remove_id = 0;
    for (auto& e : edges_to_remove) {
        debug_output.write_segment(e->source()->point(), e->target()->point(), "arr_remove_edge_" + std::to_string(remove_id++));
        CGAL::remove_edge(arr, e);
    }
}

class timer {
  public:
    class entry {
      public:
        entry(std::map<std::string, std::chrono::high_resolution_clock::time_point>::const_iterator start_it)
            : start_it(start_it) {}
        void stop() {
            auto end = std::chrono::high_resolution_clock::now();
            auto duration = std::chrono::duration<double, std::milli>(end - start_it->second).count();
            std::cerr << "Timing for " << start_it->first << ": " << duration << " ms" << std::endl;
        }

      private:
        std::map<std::string, std::chrono::high_resolution_clock::time_point>::const_iterator start_it;
    };

    entry start(const std::string& name) {
        return entry(timings_.insert({name, std::chrono::high_resolution_clock::now()}).first);
    }

  private:
    std::map<
        std::string,
        std::chrono::high_resolution_clock::time_point>
        timings_;
};

void arrange_cgal_polygons(const std::vector<Polygon_2>& input_polygons_, std::vector<Polygon_2>& output_polygons, double polygon_offset_distance = -1.) {
    static const double OVERLAP_RESOLUTION_DISTANCE = 1.e-2;
    // even larger amount of inset so that outer perimeter is safely within all input polygons even when overlap resolution is applied
    // no, `1.e-2 + 1.e-5` creates issues with the outer perimeter, are there other tolerances in play?
    static const double OUTER_PERIMITER_ADDITIONAL_INSET_AMOUNT = 1.e-5; 

#ifdef SVGFILL_DEBUG
    auto t = std::time(nullptr);
    auto tm = *std::localtime(&t);

    std::ostringstream oss;
    oss << std::put_time(&tm, "arrangement_%Y%m%d%H%M%S");
    auto now = oss.str();
    DebugWriter debug_output(true, now);
#else
    DebugWriter debug_output(false, "");
#endif

    timer timer;

    auto t0 = timer.start("input");

    debug_output.write_polygons(input_polygons_, "input");

    if (polygon_offset_distance < 0.) {
        polygon_offset_distance = estimate_polygon_offset_distance(input_polygons_);
    }   

    // Create copy to make mutable for cleaning
    auto input_polygons = input_polygons_;

    for (auto& polygon : input_polygons) {
        clean_polygon(polygon);
    }

    {
        decltype(input_polygons) split_polygons;
        for (auto& poly : input_polygons) {
            split_self_intersecting_polygon(poly, std::back_inserter(split_polygons));
        }
        std::swap(input_polygons, split_polygons);
    }

    t0.stop();
    t0 = timer.start("overlap elimination");

    eliminate_overlaps(OVERLAP_RESOLUTION_DISTANCE, input_polygons);

    t0.stop();

    // [NB Nov 6] we cannot do this anymore because it could revert the spacing between input polygons
    // that touch in the corner.
    // Now that overlaps/touches at corners are handled more locally only a small indent is produced
    // which would be undone by means of an inset+offset.
    // 
    // [NB Nov 10] this is actually still necessary though, but we apply a much smaller distance now
    // to keep the overlap eliminations in tact
    // 
    // Inset-offset to remove tiny details that may cause enourmous spikes in offsets
    for (auto& r : input_polygons) {
        smooth_polygon(-polygon_offset_distance / 10000., r);
    }

    debug_output.write_polygons(input_polygons, "processed_input");

    SegmentLookup segment_lookup(input_polygons);

    t0 = timer.start("outer perimeter");

    // Find the outer perimeter using offset - union - negative offset
    std::vector<Polygon_2> offset_polygons;
    for (auto& r : input_polygons) {
        auto R = r;
        if (!R.is_counterclockwise_oriented()) {
            R.reverse_orientation();
        }

        // Overlap removal can also result in close points causing problems when converted into non-exact nt
        remove_close_points(R);

        auto ps = create_and_convert_offset_polygon(polygon_offset_distance, R);
        for (auto& p : ps) {
            if (!p.is_simple()) {
                throw std::runtime_error("Complex polygon originated from offset");
            }
        }
        offset_polygons.insert(offset_polygons.end(), ps.begin(), ps.end());
    }

    debug_output.write_polygons(offset_polygons, "offset_input");

    // Perform Boolean union on the offset polygons
    std::vector<Polygon_with_holes_2> unioned_polygons;
    CGAL::join(offset_polygons.begin(), offset_polygons.end(), std::back_inserter(unioned_polygons));

    if (unioned_polygons.size() > 1) {
        // @todo this is currently one of the major limitations in the code that still can be eliminated
        // by grouping the input polygons by their perimiter polygon in unioned_polygons
        std::sort(unioned_polygons.begin(), unioned_polygons.end(), [](auto& p, auto& q) { return p.outer_boundary().area() > q.outer_boundary().area(); });
    }

    debug_output.write_polygon(unioned_polygons.front().outer_boundary(), "offset_joined");

    Polygon_2 fused_removed_close_points = unioned_polygons.front().outer_boundary();
    remove_close_points(fused_removed_close_points, 1.e-4);

    // Apply negative offset to get the outer perimeter polygon
    auto inner_offset = create_and_convert_offset_polygon(
        // Because polygon_offset is inexact, make sure our inset distance is slightly larger
        // std::nexttoward(-polygon_offset_distance, -std::numeric_limits<double>::infinity()),

        // 1.e-8 even was too little and still resulted in slivers of triangle around the perimeter  
        -polygon_offset_distance - OUTER_PERIMITER_ADDITIONAL_INSET_AMOUNT,
        fused_removed_close_points);

    debug_output.write_polygons(inner_offset, "outer_perimiter");

    t0.stop();
    t0 = timer.start("corridor creation");

    // Subtract original polygons from outer perimeter
    std::vector<Polygon_with_holes_2> difference_result, difference_result_subdivided;
    for (auto& i : inner_offset) {
        std::vector<Polygon_with_holes_2> working_copy;
        working_copy.emplace_back(i);

        for (auto& r : input_polygons) {
            std::vector<Polygon_with_holes_2> temp_working_copy;
            for (auto& wc : working_copy) {
                CGAL::difference(wc, r, std::back_inserter(temp_working_copy));
            }
            working_copy = temp_working_copy;
        }
        difference_result.insert(difference_result.end(), working_copy.begin(), working_copy.end());
    }

    t0.stop();
    t0 = timer.start("corridor triangulation");

    // subdivide difference_result to have better more detailed triangulation and therefore less-pronounced artefacts in midpoint network

    for (auto& pwh : difference_result) {
        difference_result_subdivided.push_back(subdivide_polygon(polygon_offset_distance / 8., pwh));
        // difference_result_subdivided.push_back(subdivide_polygon(polygon_offset_distance / 64., pwh));
    }

    debug_output.write_polygons(difference_result_subdivided, "corridor_subdivided");

    std::vector<CGAL::Polygon_2<K>> triangular_polygons;
    for (auto& pwh : difference_result_subdivided) {
        CGAL::Polygon_triangulation_decomposition_2<K> decompositor;
        decompositor(pwh, std::back_inserter(triangular_polygons));
    }

    t0.stop();

    /*
    * // @todo decide whether this is smart or not
    * // Would this not hurt topology too much?
    triangular_polygons.erase(std::remove_if(triangular_polygons.begin(), triangular_polygons.end(), [](const CGAL::Polygon_2<K>& p) {
        return CGAL::to_double(p.area()) < 1.e-8;
    }), triangular_polygons.end());
    */

    t0 = timer.start("center line");

    debug_output.write_polygons(triangular_polygons, "triangulated_corridor");

    auto [line_graph, midpoint_to_segment, segment_to_input_facet] = build_line_graph(input_polygons, segment_lookup, triangular_polygons);
    for (auto& p : line_graph) {
        for (auto& q : p.second) {
            debug_output.write_segment(p.first, q, "network_1");
        }
    }

    t0.stop();

    t0 = timer.start("center line cleaning");
    
    auto triangles = find_triangles(line_graph);

    // For every triangle found in the network we eliminate one edge to break the cycle
    // The edge we eliminate is the edge with the greatest angle with any of it's neighbours
    auto eliminated_segments = eliminate_triangles(line_graph);

    Graph2D<K> G2(line_graph);
    for (auto& e : eliminated_segments) {
        debug_output.write_segment(e.first, e.second, "eliminated");
        G2.remove_edge(e.first, e.second);
    }

    auto G = G2.weld_vertices();

    for (auto it = G.edges_begin(); it != G.edges_end(); ++it) {
        debug_output.write_segment(it->first, it->second, "network_2");
    }

    eliminate_colinear_vertices(G);

    edge_slide(G);

    for (auto it = G.edges_begin(); it != G.edges_end(); ++it) {
        debug_output.write_segment(it->first, it->second, "network_3");
    }

    t0.stop();

    t0 = timer.start("topology");

    auto segments = extend_end_vertices_based_on_input(G, midpoint_to_segment, segment_to_input_facet, inner_offset, segment_lookup);

    // Now plot the edges on an arrangement in order to find planar cycles
    // and merge the corridor-halves with their neighbouring input polygon
    Arrangement_2 arr;
    G.to_arrangement(arr);

    for (auto& pq : segments) {
        if (pq.first == pq.second) {
            continue;
        }
        CGAL::insert(arr, Segment_2(pq.first, pq.second));

        debug_output.write_segment(pq.first, pq.second, "extended_segments");
    }

    // Write input polygons to arrangement_2
    for (auto& poly : input_polygons) {
        for (size_t i = 0; i != poly.size(); ++i) {
            auto j = (i + 1) % poly.size();
            if (poly.vertex(i) == poly.vertex(j)) {
                continue;
            }
            CGAL::insert(arr, Segment_2(poly.vertex(i), poly.vertex(j)));
        }
    }

    // Just for the automatic numbering, create a full vector
    std::vector<Polygon_2> temp;
    for (auto it = arr.faces_begin(); it != arr.faces_end(); ++it) {
        if (it->is_unbounded()) {
            continue;
        }
        temp.push_back(circ_to_poly(it->outer_ccb()));
    }
    debug_output.write_polygons(temp, "arr_faces");


    /* {
        // debug, add outer bounds so that we can plot the face for any remaining edges
        auto poly = unioned_polygons.front().outer_boundary();
        for (size_t i = 0; i != poly.size(); ++i) {
            auto j = (i + 1) % poly.size();
            CGAL::insert(arr, Segment_2(poly.vertex(i), poly.vertex(j)));
        }
    } */

    // Now loop over the arrangement faces, when a face coincides with a point on the
    // corridor network we know it needs to be joined with an input polygon. In that
    // case the edges need to be eliminated that correspond to original geometry.

    fuse_corridor_halves_with_input(arr, G, segment_lookup, input_polygons, debug_output);

    t0.stop();

    for (auto it = arr.faces_begin(); it != arr.faces_end(); ++it) {
        if (it->is_unbounded()) {
            continue;
        }
        output_polygons.push_back(circ_to_poly(it->outer_ccb()));
    }

    debug_output.write_polygons(output_polygons, "arr_faces_merged");
}

#ifndef SVGFILL_MAIN

bool svgfill::arrange_polygons(const std::vector<svgfill::polygon_2>& polygons, std::vector<svgfill::polygon_2>& arranged)
{
    std::vector<Polygon_2> cgal_polygons, cgal_polygons_out;
    std::transform(polygons.begin(), polygons.end(), std::back_inserter(cgal_polygons), [](auto& poly) {
        Polygon_2 result;
        std::transform(poly.boundary.begin(), poly.boundary.end(), std::back_inserter(result), [](auto& p) {
            return Point_2(p[0], p[1]);
        });
        return result;
    });
    arrange_cgal_polygons(cgal_polygons, cgal_polygons_out);
    std::transform(cgal_polygons_out.begin(), cgal_polygons_out.end(), std::back_inserter(arranged), [](auto& poly) {
        svgfill::polygon_2 result;
        std::transform(poly.begin(), poly.end(), std::back_inserter(result.boundary), [](auto& pt) {
            return svgfill::point_2{
                CGAL::to_double(pt.cartesian(0)),
                CGAL::to_double(pt.cartesian(1)),
            };
        });
        return result;
    });
    return true;
}

#else

template <typename T>
Polygon_2 create_rectangle(T x_min, T y_min, T x_max, T y_max) {
    Polygon_2 rectangle;
    rectangle.push_back(Point_2(x_min, y_min));
    rectangle.push_back(Point_2(x_max, y_min));
    rectangle.push_back(Point_2(x_max, y_max));
    rectangle.push_back(Point_2(x_min, y_max));
    return rectangle;
}

#include <nlohmann/json.hpp>

int main(int argc, char** argv) {
    std::vector<Polygon_2> input_polygons, output;

    if (argc == 2) {
        using json = nlohmann::json;
        std::ifstream file(argv[1]);
        json jsonData;
        file >> jsonData;
        size_t i = 0;
        for (const auto& item : jsonData.items()) {
            std::cout << "i " << i << std::endl;
            i++;
            input_polygons.clear();
            const auto& polygonsData = item.value();
            for (const auto& polygonData : polygonsData) {
                input_polygons.emplace_back();
                for (const auto& pointData : polygonData) {
                    double x = pointData[0];
                    double y = pointData[1];
                    input_polygons.back().push_back(CGAL::Point_2<K>(x, y));
                }
            }
            arrange_cgal_polygons(input_polygons, output);
            break;
        }
        return 0;
    } else {
        Polygon_2 rect1 = create_rectangle<typename Polygon_2::FT>(0, 0, 2, 1);
        Polygon_2 rect2 = create_rectangle<typename Polygon_2::FT>(2.2, 0, 4, 1.1);
        Polygon_2 rect3 = create_rectangle<typename Polygon_2::FT>(0, 1.2, 2, 4);
        Polygon_2 rect4 = create_rectangle<typename Polygon_2::FT>(2.2, 1.2, 6, 4);
        Polygon_2 rect5 = create_rectangle<typename Polygon_2::FT>(4.2, 0, 6, 1.1);

        input_polygons = { rect1, rect2, rect3, rect4, rect5 };
    }
    arrange_cgal_polygons(input_polygons, output);

    return 0;
}

#endif
