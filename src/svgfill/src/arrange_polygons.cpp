#define SVGFILL_DEBUG
// #define SVGFILL_MAIN

#ifndef SVGFILL_MAIN
#include "svgfill.h"
#endif

#include "../../ifcparse/IfcLogger.h"

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
typedef K::Vector_2 Vector_2;
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
    auto it = std::max_element(ps.begin(), ps.end(), [&](const auto& p, const auto& q) { return p.area() < q.area(); });
    if (it != ps.end()) {
        auto qs = create_and_convert_offset_polygon(+factor, *it);
        auto jt = std::max_element(qs.begin(), qs.end(), [&](const auto& p, const auto& q) { return p.area() < q.area(); });
        if (jt != qs.end()) {
            poly = *jt;
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
    DebugWriter() : enabled_(false) {}

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

    DebugWriter(const DebugWriter&) = delete;

    DebugWriter(DebugWriter&& other) noexcept
        : obj(std::move(other.obj)), vi(other.vi), svg(std::move(other.svg)), enabled_(other.enabled_), last_segment_name_(std::move(other.last_segment_name_))
    {
        other.enabled_ = false;
        other.vi = 1;
        other.last_segment_name_.clear();
    }

    DebugWriter& operator=(const DebugWriter&) = delete;
    
    DebugWriter& operator=(DebugWriter&& other) noexcept {
        if (this == &other) {
            return *this;
        }

        if (enabled_) {
            svg << "</svg>\n";
            obj << std::flush;
            obj.close();
            svg.close();
        }

        obj = std::move(other.obj);
        svg = std::move(other.svg);
        vi = other.vi;
        enabled_ = other.enabled_;
        last_segment_name_ = std::move(other.last_segment_name_);

        other.enabled_ = false;
        other.vi = 1;
        other.last_segment_name_.clear();

        return *this;
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

            svg << "<line class=\"" << name << "\" x1=\"" << CGAL::to_double(p.x()) << "\" y1=\"" << -CGAL::to_double(p.y()) << "\" x2=\"" << CGAL::to_double(q.x()) << "\" y2=\"" << -CGAL::to_double(q.y()) << "\" />\n";

            obj << std::flush;
        }
    }

    void write_point(const Point_2& p, const std::string& name) {
        if (enabled_) {
            obj << "o " << name << "\n";
            obj << "v " << CGAL::to_double(p.x()) << " " << CGAL::to_double(p.y()) << " 0\n";
            vi++;
            svg << "<circle class=\"" << name << "\" cx=\"" << CGAL::to_double(p.x()) << "\" cy=\"" << -CGAL::to_double(p.y()) << "\" r=\"0.5\" />\n";
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

    void write_polygons(const Arrangement_2& arr, const std::string& name) {
        if (enabled_) {
            // Just for the automatic numbering, create a full vector
            std::vector<Polygon_2> temp;
            for (auto it = arr.faces_begin(); it != arr.faces_end(); ++it) {
                if (it->is_unbounded()) {
                    continue;
                }
                temp.push_back(circ_to_poly(it->outer_ccb()));
            }
            write_polygons(temp, name);
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
        auto class_name_ = class_name;
        if (!polygon.is_simple()) {
            if (!class_name_.empty()) {
                class_name_ += " ";
            }
            class_name_ += "self_intersecting";
        }
        ofs << "<polygon class=\"" + class_name_ + "\" points=\"";
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

void eliminate_overlaps(DebugWriter& debug_writer, double OVERLAP_RESOLUTION_DISTANCE, std::vector<Polygon_2>& polygons) {
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

            bool is_ = edge == std::make_pair<size_t, size_t>(25, 27);

            bool success = false;
            if ((mp1 = maybe_take_first_if_single_item(create_and_convert_offset_polygon(OVERLAP_RESOLUTION_DISTANCE, *poly2)))) {
                if (is_) {
                    debug_writer.write_polygon(*mp1, "mp1");
                }
                smooth_polygon(OVERLAP_RESOLUTION_DISTANCE / 100., *mp1);
                if (is_) {
                    debug_writer.write_polygon(*mp1, "mp1b");
                }
                if ((mp2 = subtract_retain_largest(*poly1, *mp1))) {
                    if (is_) {
                        debug_writer.write_polygon(*mp2, "mp2");
                    }
                    smooth_polygon(OVERLAP_RESOLUTION_DISTANCE / 100., *mp2);
                    if (is_) {
                        debug_writer.write_polygon(*mp2, "mp2b");
                    }
                    if ((mp3 = maybe_take_first_if_single_item(create_and_convert_offset_polygon(OVERLAP_RESOLUTION_DISTANCE * 2, *mp2)))) {
                        if (is_) {
                            debug_writer.write_polygon(*mp3, "mp3");
                        }
                        smooth_polygon(OVERLAP_RESOLUTION_DISTANCE / 100., *mp3);
                        if (is_) {
                            debug_writer.write_polygon(*mp3, "mp3b");
                        }
                        if ((mp4 = subtract_retain_largest(*poly2, *mp3))) {
                            if (is_) {
                                debug_writer.write_polygon(*mp4, "mp4");
                            }
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

    std::vector<CGAL::Segment_2<K>> n_closest_input_segments(const Segment_2& e, size_t n = 2) const {
        auto mid = CGAL::ORIGIN + ((e.source() - CGAL::ORIGIN) + (e.target() - CGAL::ORIGIN)) / 2;

        std::vector<std::list<CGAL::Segment_3<K>>::iterator> cands;
        cands.reserve(64);

        auto mid3 = CGAL::Point_3<K>(mid.x(), mid.y(), 0);

        for (int i = -1; i <= 3; ++i) {
            cands.clear();
            double r = std::pow(10.0, i);
            auto midbb = mid3.bbox();
            CGAL::Bbox_3 box(midbb.xmin() - r, midbb.ymin() - r, -1.0, midbb.xmax() + r, midbb.ymax() + r, +1.0);
            tree_.all_intersected_primitives(box, std::back_inserter(cands));
            if (cands.size() >= n) {
                break;
            }
        }

        if (cands.empty()) {
            return {};
        }

        std::vector<std::pair<typename K::FT, CGAL::Segment_2<K>>> scored;
        scored.reserve(cands.size());
        for (auto it : cands) {
            const auto& s3 = *it;
            Segment_2 s2(Point_2(s3.source().x(), s3.source().y()), Point_2(s3.target().x(), s3.target().y()));
            scored.emplace_back(CGAL::squared_distance(mid, s2), s2);
        }

        std::sort(scored.begin(), scored.end(), [](auto& a, auto& b) { return a.first < b.first; });
        if (scored.size() > n) {
            scored.resize(n);
        }

        std::vector<CGAL::Segment_2<K>> out;
        out.reserve(scored.size());
        for (auto& p : scored) {
            out.push_back(p.second);
        }
        return out;
    }

    PolygonIt end() const {
        return polygons_ref_.end();
    }

private:
    using TreeTraits = CGAL::AABB_traits<K, CGAL::AABB_segment_primitive<K, std::list<CGAL::Segment_3<K>>::iterator>>;
    using Tree = CGAL::AABB_tree<TreeTraits>;

    const std::vector<Polygon_2>& polygons_ref_;
    std::list<CGAL::Segment_3<K>> all_segs;
    std::unordered_map<CGAL::Segment_3<K>*, PolygonIt> seg_to_poly;
    Tree tree_;

    std::map<Point_2, std::vector<Polygon_2>::const_iterator> input_polygon_boundary_cache_;
};

Polygon_2 subdivide_polygon_on_same_input(SegmentLookup& segment_lookup, double max_distance, const Polygon_2& p, std::map<Point_2, SegmentLookup::PolygonIt>& point_lookup) {
    std::vector<Point_2> points;
    for (auto it = p.edges_begin(); it != p.edges_end(); ++it) {
        auto source_poly = segment_lookup.input_polygon_boundary(it->source());
        auto target_poly = segment_lookup.input_polygon_boundary(it->target());
        const auto& seg = *it;
        points.push_back(seg.source());
        if (source_poly == target_poly && source_poly != segment_lookup.end()) {
            point_lookup.emplace(seg.source(), source_poly);
            point_lookup.emplace(seg.target(), source_poly);
            auto num_splits = (int)std::ceil(std::sqrt(CGAL::to_double(seg.squared_length())) / max_distance) - 1;
            for (auto i = 0; i < num_splits; ++i) {
                auto d = (seg.target() - seg.source()) / (num_splits + 1) * (i + 1);
                auto p = seg.source() + d;
                point_lookup.emplace(p, source_poly);
                points.push_back(p);
            }
        }
    }
    return Polygon_2(points.begin(), points.end());
};

Polygon_with_holes_2 subdivide_polygon_on_same_input(SegmentLookup& segment_lookup, double max_distance, const Polygon_with_holes_2& pwh, std::map<Point_2, SegmentLookup::PolygonIt>& point_lookup) {
    Polygon_2 outer = subdivide_polygon_on_same_input(segment_lookup, max_distance, pwh.outer_boundary(), point_lookup);
    std::vector<Polygon_2> holes;
    for (auto hit = pwh.holes_begin(); hit != pwh.holes_end(); ++hit) {
        holes.push_back(subdivide_polygon_on_same_input(segment_lookup, max_distance, *hit, point_lookup));
    }
    return Polygon_with_holes_2(outer, holes.begin(), holes.end());
};

std::tuple<
    std::map<Point_2, std::vector<Point_2>>, 
    std::map<Point_2, std::pair<Point_2, Point_2>>,
    std::map<std::pair<Point_2, Point_2>, std::vector<const CGAL::Polygon_2<K>*>>
>
build_line_graph(const std::vector<Polygon_2>& input_polygons, const std::map<Point_2, SegmentLookup::PolygonIt>& point_lookup, const std::vector<Polygon_2>& triangular_polygons)
{

    // Build maps of triangle -> edge and edge -> triangle in order to do traversal on the 'corridor mesh'
    std::map<std::pair<Point_2, Point_2>, std::vector<const CGAL::Polygon_2<K>*>> segment_to_facet;
    std::map<std::pair<Point_2, Point_2>, std::vector<const CGAL::Polygon_2<K>*>> segment_to_input_facet;
    std::map<std::pair<Point_2, Point_2>, Point_2> segment_to_midpoint;
    std::map<Point_2, std::pair<Point_2, Point_2>> midpoint_to_segment;
    std::map<const CGAL::Polygon_2<K>*, std::vector<std::pair<Point_2, Point_2>>> facet_to_segment;


    // std::map<Point_2, double> midpoint_to_edge_length;

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

        auto p1index = point_lookup.find(p.first.first);
        auto p2index = point_lookup.find(p.first.second);

        if (p1index == point_lookup.end() || p2index == point_lookup.end()) {
            continue;
        }

        segment_to_input_facet[p.first].push_back(&*p1index->second);
        segment_to_input_facet[p.first].push_back(&*p2index->second);

        if (p1index->second != input_polygons.end() && p2index->second != input_polygons.end() && p1index->second != p2index->second) {
            segment_to_midpoint[p.first] = center;
            midpoint_to_segment[center] = p.first;
            // midpoint_to_edge_length[center] = std::sqrt(CGAL::to_double(CGAL::squared_distance(p.first.first, p.first.second)));
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

    return {line_graph, midpoint_to_segment, segment_to_input_facet}; // } , midpoint_to_edge_length};
}

using DPoint = CGAL::Simple_cartesian<double>::Point_2;
using DDir = CGAL::Simple_cartesian<double>::Vector_2;
using DBox = std::array<DPoint, 2>;

struct CenterLineGraphData {
    std::vector<Point_2> points;
    std::vector<std::optional<std::pair<Point_2, Point_2>>> orig_segments;
    std::vector<DPoint> points_double;
    std::vector<std::pair<size_t, size_t>> edges;
    std::vector<std::vector<size_t>> incident_edges;
};

struct LineRun {
    Point_2 start_exact;
    Point_2 end_exact;
    DPoint start;
    DPoint end;
    DDir direction;
    double avg_width;
    double length;
    size_t vertex_count;
};

struct RunBoxRecord {
    size_t run_index;
    DPoint start;
    DPoint end;
    DDir direction;
    double width;
    double length;
    std::array<DPoint, 4> corners;
    DBox bbox;
};

struct MergedBoxRecord {
    DPoint start;
    DPoint end;
    DDir direction;
    DDir normal;
    double avg_width;
    double length;
    size_t member_count;
    std::vector<size_t> members;
    std::array<DPoint, 4> corners;
    DBox bbox;
    Point_2 exact_start;
    Point_2 exact_end;
};

struct BoxCluster {
    std::vector<size_t> members;
    MergedBoxRecord box;
};

struct SnapCandidate {
    size_t box_index;
    double box_distance;
    double line_distance;
    Point_2 projection;
};

DDir unit(const DDir& a) {
    auto n = std::sqrt(a.squared_length());
    if (n < 1.e-9) {
        return {0., 0.};
    }
    return a / n;
}

DDir perpendicular(const DDir& a) {
    return DDir(-a.y(), a.x());
}

DDir canonicalize_like(const DDir& a, const DDir& ref) {
    return (a * ref) < 0. ? -a : a;
}

DPoint to_double_point(const Point_2& p) {
    return {CGAL::to_double(p.x()), CGAL::to_double(p.y())};
}

Point_2 to_exact_point(const DPoint& p) {
    return Point_2(p.x(), p.y());
}

double point_line_distance(const DPoint& p, const DPoint& line_point, const DDir& line_dir) {
    auto u = unit(line_dir);
    auto delta = (p - line_point);
    if (u.squared_length() < 1.e-18) {
        return std::sqrt(delta.squared_length());
    }
    return std::abs(CGAL::determinant(u.x(), u.y(), delta.x(), delta.y()));
}

double angle_between_dirs_deg(const DDir& a, const DDir& b) {
    auto u = unit(a);
    auto v = unit(b);
    auto c = std::abs(u * v);
    if (c > 1.) {
        c = 1.;
    }
    return std::acos(c) * 180. / 3.14159265358979323846;
}

std::array<DPoint, 4> rectangle_corners(const DPoint& start, const DPoint& end, double width) {
    auto u = unit(end - start);
    if (u.squared_length() < 1.e-18) {
        u = {1., 0.};
    }
    auto n = perpendicular(u);
    auto ext = width;
    auto p0 = start - u * ext;
    auto p1 = end + u * ext;
    auto w = n * (width / 2.);
    return {p0 + w, p1 + w, p1 - w, p0 - w};
}

DBox aabb_from_points(const std::array<DPoint, 4>& corners) {
    DBox bbox{corners[0], corners[0]};
    for (auto& p : corners) {
        bbox[0] = {std::min(bbox[0].x(), p.x()), std::min(bbox[0].y(), p.y())};
        bbox[1] = {std::max(bbox[1].x(), p.x()), std::max(bbox[1].y(), p.y())};
    }
    return bbox;
}

bool aabb_overlap(const DBox& a, const DBox& b, double eps = 1.e-9) {
    return a[0].x() <= b[1].x() + eps &&
           a[1].x() + eps >= b[0].x() &&
           a[0].y() <= b[1].y() + eps &&
           a[1].y() + eps >= b[0].y();
}

std::pair<double, double> projected_interval_on_axis(const std::array<DPoint, 4>& points, const DDir& axis_u) {
    auto u = unit(axis_u);
    auto t0 = (points.front() - CGAL::ORIGIN) * u;
    auto interval = std::make_pair(t0, t0);
    for (auto& p : points) {
        auto t = (p - CGAL::ORIGIN) * u;
        interval.first = std::min(interval.first, t);
        interval.second = std::max(interval.second, t);
    }
    return interval;
}

bool intervals_overlap(const std::pair<double, double>& a, const std::pair<double, double>& b, double eps = 1.e-9) {
    return a.first <= b.second + eps && b.first <= a.second + eps;
}

bool obb_overlap(const std::array<DPoint, 4>& a, const std::array<DPoint, 4>& b, double eps = 1.e-9) {
    auto has_separating_axis = [&](const std::array<DPoint, 4>& points) {
        for (size_t i = 0; i < points.size(); ++i) {
            auto edge = points[(i + 1) % points.size()] - points[i];
            auto axis = unit(perpendicular(edge));
            if (axis.squared_length() < 1.e-18) {
                continue;
            }
            if (!intervals_overlap(projected_interval_on_axis(a, axis), projected_interval_on_axis(b, axis), eps)) {
                return true;
            }
        }
        return false;
    };

    return !has_separating_axis(a) && !has_separating_axis(b);
}

template <typename T, typename U>
bool obb_overlap(const T& a, const U& b, double eps = 1.e-9) {
    return obb_overlap(a.corners, b.corners, eps);
}

CenterLineGraphData make_center_line_graph_data(
    const std::map<Point_2, std::vector<Point_2>>& line_graph,
    const std::map<Point_2, std::pair<Point_2, Point_2>>& midpoint_to_segment)
{
    CenterLineGraphData graph;
    std::map<Point_2, size_t> point_to_index;

    auto ensure_point = [&](const Point_2& p) {
        auto it = point_to_index.find(p);
        if (it != point_to_index.end()) {
            return it->second;
        }
        auto i = graph.points.size();
        point_to_index[p] = i;
        graph.points.push_back(p);
        auto mit = midpoint_to_segment.find(p);
        if (mit == midpoint_to_segment.end()) {
            graph.orig_segments.emplace_back();
        } else {
            graph.orig_segments.emplace_back(mit->second);
        }
        graph.points_double.push_back(to_double_point(p));
        graph.incident_edges.emplace_back();
        return i;
    };

    for (auto& p : line_graph) {
        ensure_point(p.first);
        for (auto& q : p.second) {
            ensure_point(q);
        }
    }

    std::set<std::pair<size_t, size_t>> seen_edges;
    for (auto& p : line_graph) {
        auto i = ensure_point(p.first);
        for (auto& q : p.second) {
            auto j = ensure_point(q);
            if (i == j) {
                continue;
            }
            auto e = i < j ? std::make_pair(i, j) : std::make_pair(j, i);
            if (seen_edges.insert(e).second) {
                auto k = graph.edges.size();
                graph.edges.push_back(e);
                graph.incident_edges[e.first].push_back(k);
                graph.incident_edges[e.second].push_back(k);
            }
        }
    }

    return graph;
}

double segment_width(const CenterLineGraphData& graph, const std::pair<size_t, size_t>& edge) {
    auto s1 = graph.orig_segments[edge.first];
    auto s2 = graph.orig_segments[edge.second];
    if (!s1 || !s2) {
        throw std::runtime_error("!!!");
    }

    // A line segment between two points is expected to span a triangle, which means that one of the
    // segment points ought to be shared.
    Point_2 refpoint;
    if (s1->first == s2->first) {
        refpoint = s1->first;
    } else if (s1->second == s2->first) {
        refpoint = s1->second;
    } else if (s1->first == s2->second) {
        refpoint = s1->first;
    } else if (s1->second == s2->second) {
        refpoint = s1->second;
    } else {
        throw std::runtime_error("!!!!!");
    }

    auto p1 = graph.points_double[edge.first];
    auto p2 = graph.points_double[edge.second];
    auto v = p2 - p1;

    if (v.squared_length() < 1.e-9) {
        throw std::runtime_error("!!!!!!!");
    }

    v /= std::sqrt(v.squared_length());
    auto n = perpendicular(v);
    auto P = to_double_point(refpoint);
    auto l = CGAL::abs((P - p1) * n);

    return 2 * l;
}

bool edge_supports_same_line(
    const DPoint& seed_a,
    const DPoint& seed_b,
    const DPoint& test_a,
    const DPoint& test_b,
    double angle_tol_deg = 3.,
    double line_dist_tol = 0.15)
{
    auto d_seed = seed_b - seed_a;
    auto d_test = test_b - test_a;
    if (d_seed.squared_length() < 1.e-18 || d_test.squared_length() < 1.e-18) {
        return false;
    }
    if (angle_between_dirs_deg(d_seed, d_test) > angle_tol_deg) {
        return false;
    }
    return
        point_line_distance(test_a, seed_a, d_seed) <= line_dist_tol &&
        point_line_distance(test_b, seed_a, d_seed) <= line_dist_tol;
}

std::vector<LineRun> runs_from_graph(const CenterLineGraphData& graph, double angle_tol_deg = 3., double line_dist_tol = 0.15) {
    std::vector<bool> visited(graph.edges.size(), false);
    std::vector<LineRun> runs;

    for (size_t seed_ei = 0; seed_ei < graph.edges.size(); ++seed_ei) {
        if (visited[seed_ei]) {
            continue;
        }

        const auto& seed_edge = graph.edges[seed_ei];
        auto seed_a = graph.points_double[seed_edge.first];
        auto seed_b = graph.points_double[seed_edge.second];
        auto seed_dir = seed_b - seed_a;
        if (seed_dir.squared_length() < 1.e-18) {
            visited[seed_ei] = true;
            continue;
        }

        std::vector<size_t> queue = {seed_ei};
        std::set<size_t> component_edges;

        while (!queue.empty()) {
            auto ei = queue.back();
            queue.pop_back();
            if (!component_edges.insert(ei).second) {
                continue;
            }

            const auto& edge = graph.edges[ei];
            std::array<size_t, 2> vertices = {edge.first, edge.second};
            for (auto v : vertices) {
                for (auto ej : graph.incident_edges[v]) {
                    if (ej == ei || visited[ej] || component_edges.count(ej)) {
                        continue;
                    }
                    const auto& candidate = graph.edges[ej];
                    auto test_a = graph.points_double[candidate.first];
                    auto test_b = graph.points_double[candidate.second];
                    if (edge_supports_same_line(seed_a, seed_b, test_a, test_b, angle_tol_deg, line_dist_tol)) {
                        queue.push_back(ej);
                    }
                }
            }
        }

        for (auto ei : component_edges) {
            visited[ei] = true;
        }

        std::set<size_t> component_vertices;
        auto ref = unit(seed_dir);
        DDir direction_sum{0., 0.};
        double total_length = 0.;
        double weighted_width_sum = 0.;

        for (auto ei : component_edges) {
            const auto& edge = graph.edges[ei];
            component_vertices.insert(edge.first);
            component_vertices.insert(edge.second);

            auto d = graph.points_double[edge.second] - graph.points_double[edge.first];
            auto u = canonicalize_like(unit(d), ref);
            direction_sum = direction_sum + u;

            auto len = std::sqrt(d.squared_length());
            total_length += len;
            weighted_width_sum += len * segment_width(graph, edge);
            // std::cout << " l: " << len << " w: " << segment_width(graph, edge) << " p1: " << graph.points_double[edge.first] << " p2: " << graph.points_double[edge.second] << std::endl;
        }

        auto run_direction = direction_sum.squared_length() < 1.e-18 ? ref : unit(direction_sum);

        double min_t = std::numeric_limits<double>::infinity();
        double max_t = -std::numeric_limits<double>::infinity();
        size_t start_index = *component_vertices.begin();
        size_t end_index = start_index;
        for (auto vi : component_vertices) {
            auto t = (graph.points_double[vi] - CGAL::ORIGIN) * run_direction;
            if (t < min_t) {
                min_t = t;
                start_index = vi;
            }
            if (t > max_t) {
                max_t = t;
                end_index = vi;
            }
        }

        auto avg_width = total_length < 1.e-9 ? segment_width(graph, seed_edge) : weighted_width_sum / total_length;

        // std::cout << "avg_width: " << avg_width << std::endl;

        runs.push_back({
            graph.points[start_index],
            graph.points[end_index],
            graph.points_double[start_index],
            graph.points_double[end_index],
            run_direction,
            avg_width,
            std::sqrt((graph.points_double[end_index] - graph.points_double[start_index]).squared_length()),
            component_vertices.size()
        });
    }

    return runs;
}

std::vector<RunBoxRecord> build_run_box_records(const std::vector<LineRun>& runs) {
    std::vector<RunBoxRecord> records;
    records.reserve(runs.size());
    for (size_t i = 0; i < runs.size(); ++i) {
        auto corners = rectangle_corners(runs[i].start, runs[i].end, runs[i].avg_width);
        records.push_back({
            i,
            runs[i].start,
            runs[i].end,
            unit(runs[i].end - runs[i].start),
            runs[i].avg_width,
            runs[i].length,
            corners,
            aabb_from_points(corners)
        });
    }
    return records;
}

template <typename T>
std::pair<double, double> projected_interval_on_axis(const T& box, const DDir& axis_u) {
    auto u = unit(axis_u);
    auto ta = (box.start - CGAL::ORIGIN) * u;
    auto tb = (box.end - CGAL::ORIGIN) * u;
    return {std::min(ta, tb), std::max(ta, tb)};
}

double interval_overlap_length(const std::pair<double, double>& a, const std::pair<double, double>& b) {
    return std::max(0., std::min(a.second, b.second) - std::max(a.first, b.first));
}

template <typename T>
double boxes_overlap_along_merge_axis(const T& a, const T& b) {
    auto d1 = unit(a.end - a.start);
    auto d2 = unit(b.end - b.start);
    if (d1 * d2 < 0.) {
        d2 = {-d2.x(), -d2.y()};
    }
    auto merge_axis = unit(d1 + d2);
    if (merge_axis.squared_length() < 1.e-18) {
        merge_axis = d1;
    }

    auto i1 = projected_interval_on_axis(a, merge_axis);
    auto i2 = projected_interval_on_axis(b, merge_axis);
    auto overlap = interval_overlap_length(i1, i2);
    auto small_length = std::min(i1.second - i1.first, i2.second - i2.first);
    if (small_length < 1.e-9) {
        return false;
    }
    return overlap / small_length;
}

MergedBoxRecord merge_cluster_to_box(const std::vector<size_t>& member_indices, const std::vector<RunBoxRecord>& records) {
    auto ref = records[member_indices.front()].direction;
    DDir direction_sum{0., 0.};
    for (auto i : member_indices) {
        auto u = canonicalize_like(records[i].direction, ref);
        direction_sum = direction_sum + u * std::max(records[i].length, 1.e-9);
    }

    auto u = direction_sum.squared_length() < 1.e-18 ? ref : unit(direction_sum);
    auto n = perpendicular(u);

    double tmin = std::numeric_limits<double>::infinity();
    double tmax = -std::numeric_limits<double>::infinity();
    double smin = std::numeric_limits<double>::infinity();
    double smax = -std::numeric_limits<double>::infinity();

    for (auto i : member_indices) {
        for (auto& corner : records[i].corners) {
            auto t = (corner - CGAL::ORIGIN) * u;
            auto s = (corner - CGAL::ORIGIN) * n;
            tmin = std::min(tmin, t);
            tmax = std::max(tmax, t);
            smin = std::min(smin, s);
            smax = std::max(smax, s);
        }
    }

    auto width = smax - smin;
    auto sc = (smin + smax) / 2.;
    auto start = u * tmin + n * sc;
    auto end = u * tmax + n * sc;
    auto corners = rectangle_corners(CGAL::ORIGIN + start, CGAL::ORIGIN + end, width);

    MergedBoxRecord box{
        CGAL::ORIGIN + start,
        CGAL::ORIGIN + end,
        u,
        n,
        width,
        std::sqrt((end - start).squared_length()),
        member_indices.size(),
        member_indices,
        corners,
        aabb_from_points(corners),
        to_exact_point(CGAL::ORIGIN + start),
        to_exact_point(CGAL::ORIGIN + end)
    };
    return box;
}

std::pair<double, double> merge_score(const MergedBoxRecord& a, const MergedBoxRecord& b) {
    auto ang = angle_between_dirs_deg(a.direction, b.direction);
    auto center_a = ((a.start - CGAL::ORIGIN) + (a.end - CGAL::ORIGIN)) / 2.;
    auto center_b = ((b.start - CGAL::ORIGIN) + (b.end - CGAL::ORIGIN)) / 2.;
    return {ang, std::sqrt((center_b - center_a).squared_length())};
}

bool clusters_can_merge(const BoxCluster& a, const BoxCluster& b, double angle_tol_deg = 5., double axis_overlap_ratio_limit = 0.5) {
    auto min_width = a.box.avg_width < b.box.avg_width ? a.box.avg_width : b.box.avg_width;
    auto max_width = a.box.avg_width > b.box.avg_width ? a.box.avg_width : b.box.avg_width;
    if (min_width > 1.e-9) {
        if (max_width / min_width > 5) {
            return false;
        }
    }
    if (!aabb_overlap(a.box.bbox, b.box.bbox)) {
        return false;
    }
    if (!obb_overlap(a.box, b.box)) {
        return false;
    }
    if (angle_between_dirs_deg(a.box.direction, b.box.direction) > angle_tol_deg) {
        return false;
    }
    if (boxes_overlap_along_merge_axis(a.box, b.box) > axis_overlap_ratio_limit) {
        auto a_center = CGAL::ORIGIN + ((a.box.start - CGAL::ORIGIN) + (a.box.end - CGAL::ORIGIN)) / 2.;
        auto b_center = CGAL::ORIGIN + ((b.box.start - CGAL::ORIGIN) + (b.box.end - CGAL::ORIGIN)) / 2.;
        auto a_dir = a.box.direction;
        auto b_dir = b.box.direction;
        auto dist = a.box.length < b.box.length ? point_line_distance(a_center, b_center, b_dir) : point_line_distance(b_center, a_center, a_dir);
        auto ref = a.box.length < b.box.length ? a.box.avg_width : b.box.avg_width;
        return dist < (ref / 4.);
    }
    return true;
}

std::vector<MergedBoxRecord> merge_intersecting_parallel_boxes_iterative(const std::vector<LineRun>& runs) {
    auto records = build_run_box_records(runs);
    std::vector<BoxCluster> clusters;
    clusters.reserve(records.size());
    for (size_t i = 0; i < records.size(); ++i) {
        clusters.push_back({{i}, merge_cluster_to_box({i}, records)});
    }

    while (true) {
        std::optional<std::pair<size_t, size_t>> best_pair;
        std::pair<double, double> best_score;

        for (size_t i = 0; i < clusters.size(); ++i) {
            for (size_t j = i + 1; j < clusters.size(); ++j) {
                if (!clusters_can_merge(clusters[i], clusters[j])) {
                    continue;
                }
                auto score = merge_score(clusters[i].box, clusters[j].box);
                if (!best_pair || score < best_score) {
                    best_pair = std::make_pair(i, j);
                    best_score = score;
                }
            }
        }

        if (!best_pair) {
            break;
        }

        auto i = best_pair->first;
        auto j = best_pair->second;
        std::vector<size_t> members = clusters[i].members;
        members.insert(members.end(), clusters[j].members.begin(), clusters[j].members.end());
        auto merged = BoxCluster{members, merge_cluster_to_box(members, records)};
        // std::cout << "Result width: " << merged.box.avg_width << "; from " << clusters[i].box.avg_width << " & " << clusters[j].box.avg_width << std::endl;

        std::vector<BoxCluster> next_clusters;
        next_clusters.reserve(clusters.size() - 1);
        for (size_t k = 0; k < clusters.size(); ++k) {
            if (k != i && k != j) {
                next_clusters.push_back(std::move(clusters[k]));
            }
        }
        next_clusters.push_back(std::move(merged));
        clusters = std::move(next_clusters);
    }

    std::vector<MergedBoxRecord> merged_boxes;
    merged_boxes.reserve(clusters.size());
    for (auto& cluster : clusters) {
        merged_boxes.push_back(cluster.box);
    }
    return merged_boxes;
}

Point_2 project_point_to_line_exact(const Point_2& p, const MergedBoxRecord& box) {
    auto d = box.exact_end - box.exact_start;
    if (d.squared_length() == 0) {
        return box.exact_start;
    }
    auto t = ((p - box.exact_start) * d) / d.squared_length();
    return box.exact_start + d * t;
}

boost::optional<Point_2> intersect_infinite_lines_exact(const MergedBoxRecord& a, const MergedBoxRecord& b) {
    if (a.exact_start == a.exact_end || b.exact_start == b.exact_end) {
        return boost::none;
    }
    auto x = CGAL::intersection(CGAL::Line_2<K>(a.exact_start, a.exact_end), CGAL::Line_2<K>(b.exact_start, b.exact_end));
    if (!x) {
        return boost::none;
    }
    if (auto* xp = variant_get<Point_2>(&*x)) {
        return *xp;
    }
    return boost::none;
}

double point_to_oriented_box_distance(const DPoint& p, const MergedBoxRecord& box) {
    auto d = box.end - box.start;
    auto L = std::sqrt(d.squared_length());
    if (L < 1.e-9) {
        return std::sqrt((p - box.start).squared_length());
    }

    auto u = d / L;
    auto n = perpendicular(u);
    auto rel = p - box.start;
    auto t = rel * u;
    auto s = rel * n;

    auto tmin = -box.avg_width / 2.;
    auto tmax = L + box.avg_width / 2.;
    auto smin = -box.avg_width / 2.;
    auto smax = box.avg_width / 2.;

    double dt = 0.;
    if (t < tmin) {
        dt = tmin - t;
    } else if (t > tmax) {
        dt = t - tmax;
    }

    double ds = 0.;
    if (s < smin) {
        ds = smin - s;
    } else if (s > smax) {
        ds = s - smax;
    }

    return std::hypot(dt, ds);
}

std::map<Point_2, std::vector<Point_2>> snap_points_to_box_axes(
    DebugWriter& debug,
    const CenterLineGraphData& graph,
    const std::vector<MergedBoxRecord>& boxes,
    const K::FT& max_projection_distance,
    Logger& logger) {
    std::vector<Point_2> snapped_points(graph.points.size());

    for (size_t i = 0; i < graph.points.size(); ++i) {
        if (boxes.empty()) {
            snapped_points[i] = graph.points[i];
            continue;
        }

        std::vector<SnapCandidate> candidates;
        candidates.reserve(boxes.size());
        for (size_t j = 0; j < boxes.size(); ++j) {
            candidates.push_back({
                j,
                point_to_oriented_box_distance(graph.points_double[i], boxes[j]),
                point_line_distance(graph.points_double[i], boxes[j].start, boxes[j].direction),
                project_point_to_line_exact(graph.points[i], boxes[j])
            });
        }

        std::vector<SnapCandidate> containing;
        for (auto& candidate : candidates) {
            if (candidate.box_distance <= 1.e-9) {
                containing.push_back(candidate);
            }
        }

        auto less = [](const SnapCandidate& a, const SnapCandidate& b) {
            if (a.line_distance != b.line_distance) {
                return a.line_distance < b.line_distance;
            }
            return a.box_distance < b.box_distance;
        };

        if (containing.size() >= 2) {
            std::sort(containing.begin(), containing.end(), less);
            auto& c1 = containing[0];
            auto& c2 = containing[1];
            if (angle_between_dirs_deg(boxes[c1.box_index].direction, boxes[c2.box_index].direction) > 8.) {
                if (auto x = intersect_infinite_lines_exact(boxes[c1.box_index], boxes[c2.box_index])) {
                    auto seg = CGAL::Segment_2<K>(graph.points[i], *x);
                    bool intersects_with_other_box_axis = false;
                    for (size_t j = 0; j < boxes.size(); ++j) {
                        if (j == c1.box_index || j == c2.box_index) {
                            continue;
                        }
                        auto& box = boxes[j];
                        auto box_seg = CGAL::Segment_2<K>(box.exact_start, box.exact_end);
                        if (CGAL::do_intersect(seg, box_seg)) {
                            intersects_with_other_box_axis = true;
                            break;
                        }
                    }
                    if (!intersects_with_other_box_axis) {
                        snapped_points[i] = *x;
                        debug.write_segment(graph.points[i], *x, "snap_candidate_1");
                        continue;
                    }
                }
            }
            snapped_points[i] = (c1.projection - graph.points[i]).squared_length() < (c2.projection - graph.points[i]).squared_length() ? c1.projection : c2.projection;
            debug.write_segment(graph.points[i], snapped_points[i], "snap_candidate_2");
            continue;
        }

        if (containing.size() == 1) {
            snapped_points[i] = containing[0].projection;
            debug.write_segment(graph.points[i], containing[0].projection, "snap_candidate_3");
            continue;
        }

        auto best = *std::min_element(candidates.begin(), candidates.end(), [](const SnapCandidate& a, const SnapCandidate& b) {
            if (a.box_distance != b.box_distance) {
                return a.box_distance < b.box_distance;
            }
            return a.line_distance < b.line_distance;
        });

        if ((graph.points[i] - best.projection).squared_length() < (max_projection_distance * max_projection_distance)) {
            snapped_points[i] = best.projection;
            debug.write_segment(graph.points[i], best.projection, "snap_candidate_4");
        } else {
            snapped_points[i] = graph.points[i];
            std::ostringstream message;
            message << "Snapping distance exceeds maximum distance: "
                    << std::sqrt(CGAL::to_double((snapped_points[i] - best.projection).squared_length()))
                    << " > " << max_projection_distance;
            logger.Message(Logger::LOG_WARNING, "ARR", 1, message.str());
        }
    }

    std::map<Point_2, std::set<Point_2>> adjacency;
    for (auto& edge : graph.edges) {
        auto a = snapped_points[edge.first];
        auto b = snapped_points[edge.second];
        if (a == b) {
            continue;
        }
        adjacency[a].insert(b);
        adjacency[b].insert(a);
    }

    std::map<Point_2, std::vector<Point_2>> snapped_graph;
    for (auto& p : adjacency) {
        snapped_graph[p.first] = {p.second.begin(), p.second.end()};
    }
    return snapped_graph;
}

Graph2D<K> join_segment_runs(
    DebugWriter& debug,
    const std::map<Point_2, std::vector<Point_2>>& line_graph,
    const std::map<Point_2, std::pair<Point_2, Point_2>>& midpoint_to_segment,
    const K::FT& max_projection_distance,
    Logger& logger) {
    auto graph = make_center_line_graph_data(line_graph, midpoint_to_segment);
    auto runs = runs_from_graph(graph);
    runs.erase(std::remove_if(runs.begin(), runs.end(), [](const LineRun& run) {
        return run.vertex_count <= 5;
    }), runs.end());

    std::vector<Polygon_2> run_polygons;
    for (auto& r : runs) {
        auto ps = rectangle_corners(r.start, r.end, r.avg_width);
        std::array<Point_2, 4> exact_corners;
        std::transform(ps.begin(), ps.end(), exact_corners.begin(), [](const DPoint& p) {
            return to_exact_point(p);
        });
        run_polygons.emplace_back(exact_corners.begin(), exact_corners.end());
    }
    debug.write_polygons(run_polygons, "initial_runs");
    run_polygons.clear();

    auto boxes = merge_intersecting_parallel_boxes_iterative(runs);

    for (auto& r : boxes) {
        auto ps = rectangle_corners(r.start, r.end, r.avg_width);
        std::array<Point_2, 4> exact_corners;
        std::transform(ps.begin(), ps.end(), exact_corners.begin(), [](const DPoint& p) {
            return to_exact_point(p);
        });
        run_polygons.emplace_back(exact_corners.begin(), exact_corners.end());
    }
    debug.write_polygons(run_polygons, "merged_boxes");

    auto snapped_graph = snap_points_to_box_axes(debug, graph, boxes, max_projection_distance, logger);
    return Graph2D<K>(snapped_graph);
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

struct Ccw_radial_sort {
    Point_2 c;
    explicit Ccw_radial_sort(const Point_2& center) : c(center) {}

    bool operator()(const Point_2& a, const Point_2& b) const {
        const Vector_2 va = a - c;
        const Vector_2 vb = b - c;

        // Only left-turn is not sufficient because we should not wrap around,
        // but rather start from e.g positive x-axis and then sort CCW.
        // Therefore top-half plane always comes before bottom-half plane.
        const bool ua = va.y() == 0 ? va.x() > 0 : va.y() > 0;
        const bool ub = vb.y() == 0 ? vb.x() > 0 : vb.y() > 0;
        if (ua != ub) {
            return ua;
        }

        if (CGAL::collinear(c, a, b)) {
            // Nearer first so that original polygon edges are likely retained
            // (not sure if it matters).
            return va.squared_length() < vb.squared_length();
        }

        // This is a less functor, so we return true if c,a,b is a left turn, which means that a is CCW before b
        return CGAL::left_turn(c, a, b);
    }
};

void build_radial_neighbour_map(const std::vector<Polygon_2>& polygons, double radius, std::map<Point_2, std::vector<Point_2>>& neighbour_map) {
    for (auto& poly : polygons) {
        for (auto it = poly.edges_begin(); it != poly.edges_end(); ++it) {
            auto source = it->source();
            auto target = it->target();
            neighbour_map[source].push_back(target);
            neighbour_map[target].push_back(source);
        }
    }

    // Box_intersection_d package to find close vertices and connect them as well
    typedef CGAL::Box_intersection_d::Box_with_handle_d<double, 2, Point_2, CGAL::Box_intersection_d::ID_EXPLICIT> Box;
    std::vector<Box> boxes;
    for (auto& poly : polygons) {
        for (auto it = poly.vertices_begin(); it != poly.vertices_end(); ++it) {
            const auto pb = it->bbox();
            boxes.emplace_back(
                CGAL::Bbox_2(pb.xmin() - radius, pb.ymin() - radius, pb.xmax() + radius, pb.ymax() + radius),
                *it);
        }
    }
    CGAL::box_self_intersection_d(boxes.begin(), boxes.end(), [&](const Box& a, const Box& b) {
        if ((a.handle() - b.handle()).squared_length() <= (radius * radius)) {
            neighbour_map[a.handle()].push_back(b.handle());
            neighbour_map[b.handle()].push_back(a.handle());
        }
    });

    // radial sort
    for (auto& p : neighbour_map) {
        auto& nb = p.second;
        std::sort(nb.begin(), nb.end(), Ccw_radial_sort(p.first));
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
    const Polygon_list& outer_perimiter,
    const SegmentLookup& segment_lookup,
    const K::FT& max_projection_distance
){
    std::list<std::pair<Point_2, Point_2>> constructed_segments;

    std::set<Point_2> processed_vertices;

    while (true) {
        // The idea was to peal off 1-degree vertices when projecting them did not result into
        // nearby intersections with the outer perimiter. This in case there would be turns near
        // the perimeter, which would be eliminated by pealing off the vertices, which would then
        // require out of the loop because of invalidated iterators. For now we decided to stick
        // to a projection of the vertex onto the perimeter segment when the projection distance
        // exceeds a threshold.
        bool broke_out = false;

        for (auto it = G.vertices_begin(); it != G.vertices_end(); ++it) {
            if (it->second.size() == 1) {
                auto& M = it->first;

                if (processed_vertices.find(M) != processed_vertices.end()) {
                    continue;
                }

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
                    for (auto& bnd : outer_perimiter) {
                        // if point M is contained in bnd interior:
                        // if (!bnd.has_on_unbounded_side(M)) {
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
                                            if (dist < (max_projection_distance * max_projection_distance)) {
                                                closest_segment = seg;
                                                closest_intersection_point = *xp;
                                                sq_distance_along_ray = dist;
                                            } else {
                                            
                                            }                                            
                                        }
                                    }
                                }
                            }

                            if (closest_intersection_point) {
                                constructed_segments.push_front({M, *closest_intersection_point});
                                processed_vertices.insert(M);
                                break;
#if 0
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
#endif
                            } else {
                                
                                // Loop over boundary segments, and project point onto it, take the closest
                                K::FT closest_distance = std::numeric_limits<double>::infinity();
                                boost::optional<CGAL::Point_2<K>> closest_point;
                                for (auto& poly : outer_perimiter) {
                                    for (auto jt = poly.edges_begin(); jt != poly.edges_end(); ++jt) {
                                        auto seg = *jt;
                                        auto Pp = seg.supporting_line().projection(M);
                                        if (seg.has_on(Pp)) {
                                            auto d = CGAL::squared_distance(Pp, M);
                                            if (d < (max_projection_distance * max_projection_distance)) {
                                                if (d < closest_distance) {
                                                    closest_distance = d;
                                                    closest_point = Pp;
                                                }
                                            }
                                        }
                                    }
                                }

                                if (closest_point) {
                                    constructed_segments.push_front({M, *closest_point});
                                    processed_vertices.insert(M);
                                }
                            }
                        }
                    }
                }

#if 0
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
#endif
            }
        }

        if (!broke_out) {
            break;
        }
    }

    return constructed_segments;
}

std::list<std::pair<Point_2, Point_2>>
extend_end_vertices_based_on_input_simple(
    DebugWriter& debug_output,
    const Graph2D<K>& G,
    const Polygon_list& outer_perimiter,
    const K::FT& max_projection_distance,
    int pass,
    Logger& logger)
{
    auto max_intersection_distance = max_projection_distance / 4;

    using ValidationSegmentList = std::list<CGAL::Segment_3<K>>;
    using ValidationSegmentIt = ValidationSegmentList::iterator;
    using ValidationTreeTraits = CGAL::AABB_traits<K, CGAL::AABB_segment_primitive<K, ValidationSegmentIt>>;
    using ValidationTree = CGAL::AABB_tree<ValidationTreeTraits>;

    const auto& to_3d = [](const Point_2& p) {
        return CGAL::Point_3<K>(p.x(), p.y(), 0);
    };

    const auto& to_2d = [](const CGAL::Point_3<K>& p) {
        return CGAL::Point_2<K>(p.x(), p.y());
    };

    ValidationSegmentList validation_segments;
    for (auto it = G.edges_begin(); it != G.edges_end(); ++it) {
        if (it->first != it->second) {
            validation_segments.emplace_back(to_3d(it->first), to_3d(it->second));
        }
    }

    ValidationTree validation_tree(validation_segments.begin(), validation_segments.end());

    const auto has_intersection = [&](const Segment_2& candidate) {
        // @nb still disabled.
        return false;
        std::vector<ValidationSegmentIt> intersected_segments;
        validation_tree.all_intersected_primitives(CGAL::Segment_3<K>(to_3d(candidate.source()), to_3d(candidate.target())), std::back_inserter(intersected_segments));

        for (auto it : intersected_segments) {
            auto existing = CGAL::Segment_2<K>(to_2d(it->source()), to_2d(it->target()));
            auto intersection = CGAL::intersection(candidate, existing);
            if (!intersection) {
                continue;
            }

            if (auto* point = variant_get<Point_2>(&*intersection)) {
                const bool candidate_endpoint = *point == candidate.source() || *point == candidate.target();
                const bool existing_endpoint = *point == existing.source() || *point == existing.target();
                if (candidate_endpoint && existing_endpoint) {
                    continue;
                }
            }

            return true;
        }

        return false;
    };

    const auto& process_point = [&](const Point_2& M, const Point_2& incoming) {
        bool within_any_perimeter = false;
        for (auto& bnd : outer_perimiter) {
            // if point M is contained in bnd interior:
            // if (!bnd.has_on_unbounded_side(M)) {
            if (bnd.has_on_bounded_side(M)) {
                within_any_perimeter = true;
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
                                if (dist < (max_intersection_distance * max_intersection_distance)) {
                                    if (has_intersection(CGAL::Segment_2<K>(M, *xp))) {
                                        debug_output.write_segment(M, *xp, "exterior_extension_intersection");
                                    } else {
                                        closest_segment = seg;
                                        closest_intersection_point = *xp;
                                        sq_distance_along_ray = dist;
                                    }
                                } else {
                                }
                            }
                        }
                    }
                }

                if (closest_intersection_point) {
                    return closest_intersection_point;
                    // constructed_segments.push_front({M, *closest_intersection_point});
                } else {

                    // Loop over boundary segments, and project point onto it, take the closest
                    K::FT closest_distance = std::numeric_limits<double>::infinity();
                    boost::optional<CGAL::Point_2<K>> closest_point;
                    for (auto& poly : outer_perimiter) {
                        for (auto jt = poly.edges_begin(); jt != poly.edges_end(); ++jt) {
                            auto seg = *jt;
                            auto Pp = seg.supporting_line().projection(M);
                            if (seg.has_on(Pp)) {
                                auto d = CGAL::squared_distance(Pp, M);
                                if (d < (max_projection_distance * max_projection_distance)) {
                                    if (d < closest_distance) {
                                        if (has_intersection(CGAL::Segment_2<K>(M, Pp))) {
                                            debug_output.write_segment(M, Pp, "exterior_projection_intersection");
                                        } else {
                                            closest_distance = d;
                                            closest_point = Pp;
                                        }
                                    }
                                }
                            }
                        }
                    }

                    if (closest_point) {
                        return closest_point;
                        // constructed_segments.push_front({M, *closest_point});
                    } else {

                        for (auto& poly : outer_perimiter) {
                            for (auto it = poly.begin(); it != poly.end(); ++it) {
                                auto Pp = *it;
                                auto d = CGAL::squared_distance(Pp, M);
                                if (d < (max_projection_distance * max_projection_distance)) {
                                    if (has_intersection(CGAL::Segment_2<K>(M, Pp))) {
                                        debug_output.write_segment(M, Pp, "exterior_nearby_intersection");
                                    } else {
                                        if (d < closest_distance) {
                                            closest_distance = d;
                                            closest_point = Pp;
                                        }
                                    }
                                }
                            }
                        }

                        if (closest_point) {
                            return closest_point;
                        } else {
                        }
                    }
                }
            } else if (bnd.has_on_boundary(M)) {
                return boost::optional<Point_2>{M};
            }
        }
        if (within_any_perimeter) {
            logger.Message(Logger::LOG_WARNING, "ARR", 2, "Within boundary but no projection or intersection solution was found");
        } else {
            logger.Message(Logger::LOG_WARNING, "ARR", 3, "Point is outside all boundaries");
        }
        return boost::optional<Point_2>{};
    };

    using solution_length_point_incoming = std::tuple<K::FT, Point_2, Point_2>;
    std::vector<solution_length_point_incoming> solutions;

    for (auto it = G.vertices_begin(); it != G.vertices_end(); ++it) {
        if (it->second.size() == 1) {
            auto& M = it->first;
            if (auto result = process_point(M, *it->second.begin())) {
                if (*result == M) {
                    std::ostringstream message;
                    message << "Point is already on perimeter (" << M.x() << " " << M.y() << ")";
                    logger.Message(Logger::LOG_NOTICE, "ARR", 4, message.str());
                    continue;
                }
                auto d = (M - *result).squared_length();
                solutions.emplace_back(d, M, *it->second.begin());
            } else {
                std::ostringstream message;
                message << "Unable to find projection or intersection point for interior boundary pass "
                        << pass << " [round 1] (" << M.x() << " " << M.y() << ")";
                logger.Message(Logger::LOG_WARNING, "ARR", 5, message.str());
            }
        }
    }

    std::sort(solutions.begin(), solutions.end());
    std::list<std::pair<Point_2, Point_2>> constructed_segments;

    for (auto& [d, point, incoming] : solutions) {
        if (auto result = process_point(point, incoming)) {
            constructed_segments.push_front({point, *result});
            debug_output.write_segment(point, *result, "exterior_constructed_segment");

            auto d = CGAL::squared_distance(point, *result);
            std::ostringstream message;
            message << "Projection or intersection distance: " << std::sqrt(CGAL::to_double(d));
            logger.Message(Logger::LOG_DEBUG, "ARR", 6, message.str());
            validation_segments.emplace_back(to_3d(point), to_3d(*result));
            auto inserted_it = std::prev(validation_segments.end());
            validation_tree.insert(inserted_it, validation_segments.end());
        } else {
            std::ostringstream message;
            message << "Unable to find projection or intersection point for interior boundary pass "
                    << pass << " [round 2] (" << point.x() << " " << point.y() << ")";
            logger.Message(Logger::LOG_WARNING, "ARR", 7, message.str());
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

class Segment_2_less {
    public:
    bool operator()(const Segment_2& a, const Segment_2& b) const {
        if (a.source() != b.source()) {
            return a.source() < b.source();
        }
        return a.target() < b.target();
    }
};

std::vector<K::FT> arrangement_cell_iou(DebugWriter& debug_output, Arrangement_2& left, Arrangement_2& right, Logger& logger) {

    using Walk_pl = CGAL::Arr_walk_along_line_point_location<Arrangement_2>;
    Walk_pl walk_pl(right);

    std::set<Arrangement_2::Face_const_handle> visited_faces_on_right;

    std::vector<K::FT> return_values;

    K::FT max_iou_deviation = 1;
    std::array<Polygon_2, 2> max_deviation_poly_pair;

    for (auto it = left.faces_begin(); it != left.faces_end(); ++it) {
        if (!it->is_unbounded()) {
            // convert arr facet to polygon with holes
            auto polygon_exterior = circ_to_poly(it->outer_ccb());
            Polygon_with_holes_2 pwh(polygon_exterior);
            for (auto hit = it->inner_ccbs_begin(); hit != it->inner_ccbs_end(); ++hit) {
                pwh.add_hole(circ_to_poly(*hit));
            }
            // if (!pwh.outer_boundary().is_simple()) {
            //     throw std::runtime_error("Polygon with holes has a non-simple outer boundary");
            // }

            CGAL::Polygon_triangulation_decomposition_2<K> decompositor;
            std::vector<Polygon_2> temp;
            decompositor(pwh, std::back_inserter(temp));

            std::set<Point_2> visited_points;

            while (true) {
                // select triangle edge that has largest squared edge length times distance from polygon exterior
                K::FT max_score = -std::numeric_limits<double>::infinity();
                Point_2 best_point;
                for (auto& tri : temp) {
                    for (size_t i = 0; i < 3; ++i) {
                        size_t j = (i + 1) % 3;
                        auto& pi = tri.vertex(i);
                        auto& pj = tri.vertex(j);

                        auto center_point = CGAL::ORIGIN + (((pi - CGAL::ORIGIN) + (pj - CGAL::ORIGIN)) / 2);

                        K::FT min_dist = std::numeric_limits<double>::infinity();
                        for (auto eit = polygon_exterior.edges_begin(); eit != polygon_exterior.edges_end(); ++eit) {
                            auto ep = eit->source();
                            auto eq = eit->target();
                            Segment_2 seg(ep, eq);
                            auto dist = CGAL::squared_distance(center_point, seg);
                            if (dist < min_dist) {
                                min_dist = dist;
                            }
                        }

                        auto sq_length = CGAL::squared_distance(pi, pj);

                        auto score = sq_length * min_dist;
                        if (score > max_score && visited_points.count(center_point) == 0) {
                            max_score = score;
                            best_point = center_point;
                        }
                    }
                }

                if (max_score == -std::numeric_limits<double>::infinity()) {
                    // no more points to try
                    return_values.push_back(0);
                    break;
                }

                visited_points.insert(best_point);

                debug_output.write_point(best_point, "representative_point representative_point_" + std::to_string(std::distance(left.faces_begin(), it)));

                auto res = walk_pl.locate(best_point);
                if (auto* v = variant_get<Arrangement_2::Face_const_handle>(&res)) {
                    if ((*v)->is_unbounded()) {
                        // try next point
                        continue;
                    }
                    if (visited_faces_on_right.count(*v) > 0) {
                        // Maybe we should be more permissive, try some other points etc.
                        return_values.push_back(0);
                        logger.Message(Logger::LOG_WARNING, "ARR", 8, "Already visited face on right; skipping point");
                    } else {
                        // convert arr facet to polygon with holes
                        auto polygon_exterior = circ_to_poly((*v)->outer_ccb());
                        Polygon_with_holes_2 pwh_right(polygon_exterior);
                        for (auto hit = (*v)->inner_ccbs_begin(); hit != (*v)->inner_ccbs_end(); ++hit) {
                            pwh_right.add_hole(circ_to_poly(*hit));
                        }
                        // if (!pwh_right.outer_boundary().is_simple()) {
                        //     throw std::runtime_error("Polygon with holes has a non-simple outer boundary");
                        // }

                        // compute intersection over union of pwh and the original polygon
                        if (CGAL::do_intersect(pwh, pwh_right)) {
                            std::vector<Polygon_with_holes_2> result;
                            CGAL::intersection(pwh, pwh_right, std::back_inserter(result));
                            typename K::FT intersection_area = 0;
                            for (auto& r : result) {
                                auto poly_area = r.outer_boundary().area();
                                for (auto& h : r.holes()) {
                                    poly_area -= CGAL::abs(h.area());
                                }
                                intersection_area += poly_area;
                            }
                            CGAL::Polygon_with_holes_2<K> poly12;
                            CGAL::join(pwh, pwh_right, poly12);
                            typename K::FT union_area = poly12.outer_boundary().area();
                            for (auto& h : poly12.holes()) {
                                union_area -= CGAL::abs(h.area());
                            }
                            return_values.push_back(intersection_area / union_area);

                            auto& v = return_values.back();
                            if (v < max_iou_deviation) {
                                max_iou_deviation = v;
                                max_deviation_poly_pair = {pwh.outer_boundary(), pwh_right.outer_boundary()};
                            }
                        } else {
                            logger.Message(Logger::LOG_WARNING, "ARR", 9, "No intersection; skipping point");
                            return_values.push_back(0);
                        }
                    }
                    visited_faces_on_right.insert(*v);
                    break;
                } else {
                    // Not in facet on right, retry another point
                    continue;
                }
            }
        }
    }

    if (max_iou_deviation != 1) {
        debug_output.write_polygon(max_deviation_poly_pair[0], "max_iou_deviation_left");
        debug_output.write_polygon(max_deviation_poly_pair[1], "max_iou_deviation_right");
    }

    return return_values;
}

void clean_noisy_paths(DebugWriter& debug_output, Arrangement_2& arr, SegmentLookup& segment_lookup, double& threshold, Logger& logger) {
    using SK = CGAL::Simple_cartesian<double>;
    CGAL::Cartesian_converter<K, SK> C{};

    auto other = [](const Segment_2& e, const Point_2& v) {
        return (e.source() == v) ? e.target() : e.source();
    };

    std::set<Segment_2, Segment_2_less> edges;
    for (auto he = arr.edges_begin(); he != arr.edges_end(); ++he) {
        auto a = he->source()->point();
        auto b = he->target()->point();
        if (a < b) {
            edges.insert({a, b});
        } else {
            edges.insert({b, a});
        }
    }

    auto edge_badness = [&](const Segment_2& e) -> double {
        auto closest = segment_lookup.n_closest_input_segments(e, 2);
        if (closest.size() != 2) {
            throw std::runtime_error("Unable to locate two nearby edges");
        }

        auto get_dir = [&](const Segment_2& s) {
            auto a = C(s.source());
            auto b = C(s.target());
            SK::Vector_2 v = b - a;
            double l = std::sqrt(v.squared_length());
            if (l <= 1e-12) {
                return std::make_pair(SK::Vector_2(0, 0), 0.);
            }
            return std::make_pair(v / l, l);
        };

        auto [own_dir, own_length] = get_dir(e);

        auto angle = [&](const SK::Vector_2& ov) {
            double d = std::abs(own_dir * ov);
            if (d > 1.0) {
                d = 1.0;
            }
            return std::acos(d);
        };

        double best = std::numeric_limits<double>::infinity();
        for (auto& s : closest) {
            auto [dv, dl] = get_dir(s);
            best = std::min(best, angle(dv));
        }
        return (best + 0.01) / own_length;
    };

    std::map<Segment_2, double, Segment_2_less> badnesses;
    for (auto& e : edges) {
        badnesses[e] = edge_badness(e);
    }

    {
        std::vector<double> tmp;
        tmp.reserve(badnesses.size());
        for (auto& p : badnesses) {
            tmp.push_back(p.second);
        }
        std::nth_element(tmp.begin(), tmp.begin() + tmp.size() / 2, tmp.end());
        double med = tmp[tmp.size() / 2];
        threshold = 4.0 * med;
    }

    std::set<Segment_2, Segment_2_less> bad_edges;
    for (auto& p : badnesses) {
        if (p.second > threshold) {
            bad_edges.insert(p.first);
        }
    }

    std::map<Point_2, std::vector<Segment_2>> topo, bad_topo;

    for (auto& e : edges) {
        topo[e.source()].push_back(e);
        topo[e.target()].push_back(e);
    }
    for (auto& e : bad_edges) {
        bad_topo[e.source()].push_back(e);
        bad_topo[e.target()].push_back(e);
    }

    std::set<Point_2> break_vertices;
    for (auto& p : bad_topo) {
        const auto& v = p.first;
        if (!(topo[v].size() == 2 && bad_topo[v].size() == 2)) {
            break_vertices.insert(v);
        }
    }

    std::set<Segment_2, Segment_2_less> seen;
    std::vector<std::vector<Point_2>> bad_paths;

    for (auto& s : break_vertices) {
        for (auto& e0 : bad_topo[s]) {
            if (seen.count(e0)) {
                continue;
            }

            Point_2 v = s;
            std::vector<Point_2> path;
            path.push_back(s);

            auto e = e0;
            while (true) {
                seen.insert(e);
                v = other(e, v);
                path.push_back(v);

                if (break_vertices.count(v)) {
                    break;
                }

                auto& inc = bad_topo[v];
                std::vector<Segment_2> nxt;
                nxt.reserve(2);
                for (auto& ee : inc) {
                    if (ee != e && !seen.count(ee)) {
                        nxt.push_back(ee);
                    }
                }
                if (nxt.size() != 1) {
                    break;
                }
                e = nxt[0];
            }

            if (path.size() > 1) {
                bad_paths.push_back(std::move(path));
            }
        }
    }

    std::set<std::pair<Point_2, Point_2>> to_remove;
    std::vector<std::pair<Point_2, Point_2>> to_insert;

    auto dirs_from = [&](const Point_2& v, const std::set<Segment_2, Segment_2_less>& path_edges) {
        std::vector<Vector_2> ds;
        for (auto& ee : topo[v]) {
            if (path_edges.count(ee) || bad_edges.count(ee)) {
                continue;
            }
            Point_2 u = other(ee, v);
            ds.push_back(v - u);
        }
        return ds;
    };

    auto collapse_path = [&](const std::vector<Point_2>& path) -> std::optional<Point_2> {
        std::set<Segment_2, Segment_2_less> path_edges;
        for (size_t i = 0; i + 1 < path.size(); ++i) {
            auto* a = &path[i];
            auto* b = &path[i + 1];
            if (*a < *b) {
                path_edges.insert({*a, *b});
            } else {
                path_edges.insert({*b, *a});
            }
        }

        const auto& a0 = path.front();
        const auto& b0 = path.back();

        auto das = dirs_from(a0, path_edges);
        auto dbs = dirs_from(b0, path_edges);
        if (das.empty() || dbs.empty()) {
            return std::nullopt;
        }

        K::FT best_ke = std::numeric_limits<double>::infinity();
        std::optional<K::Point_2> best_x;

        for (auto& da : das) {
            for (auto& db : dbs) {
                CGAL::Ray_2<K> r1(a0, da);
                CGAL::Ray_2<K> r2(b0, db);

                auto x = CGAL::intersection(r1, r2);
                if (x) {
                    if (auto* xp = variant_get<CGAL::Point_2<K>>(&*x)) {
                        // @todo does it matter that this is squared?
                        auto ke = CGAL::squared_distance(*xp, a0) + CGAL::squared_distance(*xp, b0);
                        if (ke < best_ke) {
                            best_ke = ke;
                            best_x = *xp;
                        }
                    }
                }
            }
        }

        return best_x;
    };

    auto process_modifications = [&](
                                     Arrangement_2& arr_,
                                     const std::set<std::pair<Point_2, Point_2>>& to_remove_,
                                     const std::vector<std::pair<Point_2, Point_2>>& to_insert_) {
        for (auto& e : to_remove_) {
            bool removed = false;
            for (auto he = arr_.edges_begin(); he != arr_.edges_end(); ++he) {
                auto a = he->source()->point();
                auto b = he->target()->point();
                if ((a == e.first && b == e.second) || (a == e.second && b == e.first)) {
                    CGAL::remove_edge(arr_, he);
                    removed = true;
                    break;
                }
            }
            if (!removed) {
                logger.Message(Logger::LOG_WARNING, "ARR", 10, "Unable to locate edge for removal; skipping");
            }
        }

        for (auto& pq : to_insert_) {
            if (pq.first == pq.second) {
                continue;
            }
            CGAL::insert(arr_, Segment_2(pq.first, pq.second));
        }
    };

    size_t path_index = 0;
    for (auto& path : bad_paths) {
        decltype(to_remove) to_remove_this_path;
        decltype(to_insert) to_insert_this_path;

        for (size_t i = 0; i < path.size() - 1; ++i) {
            auto& a = path[i];
            auto& b = path[i + 1];

            debug_output.write_segment(a, b, "arr_bad_path path_nr_" + std::to_string(path_index));
        }

        auto x = collapse_path(path);
        if (!x) {
            // std::cerr << "Unable to collapse path, skipping" << std::endl;
            continue;
        }

        double orig_length = 0.;
        for (size_t i = 0; i < path.size() - 1; ++i) {
            auto& a = path[i];
            auto& b = path[i + 1];
            orig_length += std::sqrt(CGAL::to_double(CGAL::squared_distance(a, b)));
        }

        double new_length = std::sqrt(CGAL::to_double((path.front() - *x).squared_length())) + std::sqrt(CGAL::to_double((path.back() - *x).squared_length()));

        if (new_length > orig_length * 2 || orig_length > new_length * 2) {
            // std::cerr << "Collapsing path would increase length too much, skipping" << std::endl;
            continue;
        }

        for (size_t i = 0; i < path.size(); ++i) {
            auto& v = path[i];
            if (CGAL::squared_distance(v, *x) < 1.e-5) {
                // std::cerr << "Collapsing path would create near-duplicate vert to previous path, skipping" << std::endl;
                continue;
            }
        }

        for (size_t i = 0; i < path.size() - 1; ++i) {
            auto& a = path[i];
            auto& b = path[i + 1];
            if (a < b) {
                to_remove.insert({a, b});
                to_remove_this_path.insert({a, b});
            } else {
                to_remove.insert({b, a});
                to_remove_this_path.insert({b, a});
            }
        }
        auto s = path.front();
        auto t = path.back();
        if (s != *x) {
            to_insert.push_back({s, *x});
            to_insert_this_path.push_back({s, *x});

            debug_output.write_segment(s, *x, "corrected_path path_nr_" + std::to_string(path_index));
        }
        if (t != *x) {
            to_insert.push_back({t, *x});
            to_insert_this_path.push_back({t, *x});

            debug_output.write_segment(t, *x, "corrected_path path_nr_" + std::to_string(path_index));
        }

        path_index += 1;

#if 1
        process_modifications(arr, to_remove_this_path, to_insert_this_path);
#else
        auto arr_copy = arr;
        process_modifications(arr_copy, to_remove_this_path, to_insert_this_path);
        auto ious = arrangement_cell_iou(debug_output, arr, arr_copy, logger);
        for (auto& iou : ious) {
            std::cerr << " - cell iou: " << CGAL::to_double(iou) << std::endl;
        }
        std::swap(arr_copy, arr);
#endif
    }

    process_modifications(arr, to_remove, to_insert);
}

template <typename Vec>
void next_circular(typename Vec::const_iterator& it, const Vec& vec) {
    std::advance(it, 1);
    if (it == vec.end()) {
        it = vec.begin();
    }
}

template <typename Vec>
void previous_circular(typename Vec::const_iterator& it, const Vec& vec) {
    if (it == vec.begin()) {
        it = vec.end();
    }
    std::advance(it, -1);
}

template <typename Vec>
std::size_t circular_distance(typename Vec::const_iterator first,
                              typename Vec::const_iterator last,
                              const Vec& vec) {
    if (first <= last) {
        return static_cast<std::size_t>(last - first);
    }
    return static_cast<std::size_t>(vec.end() - first) + static_cast<std::size_t>(last - vec.begin());
}

template <typename Vec, typename Pred>
std::pair<typename Vec::const_iterator,
          typename Vec::const_iterator>
longest_wrapping_true_run(const Vec& v, Pred pred) {
    using It = typename Vec::const_iterator;

    const auto n = v.size();
    if (n == 0) {
        return {v.end(), v.end()};
    }

    // Find best non-wrapping run
    std::size_t best_len = 0;
    std::size_t best_start = 0;

    std::size_t curr_len = 0;
    std::size_t curr_start = 0;

    for (std::size_t i = 0; i < n; ++i) {
        if (pred(v[i])) {
            if (curr_len == 0) {
                curr_start = i;
            }
            ++curr_len;
            if (curr_len > best_len) {
                best_len = curr_len;
                best_start = curr_start;
            }
        } else {
            curr_len = 0;
        }
    }

    // Count leading true
    std::size_t leading = 0;
    while (leading < n && pred(v[leading])) {
        ++leading;
    }

    // All true
    if (leading == n) {
        return {v.begin(), v.end()};
    }

    // Count trailing true
    std::size_t trailing = 0;
    while (trailing < n && pred(v[n - 1 - trailing])) {
        ++trailing;
    }

    // Wrapped run = [n - trailing, n) + [0, leading)
    const std::size_t wrapped_len = leading + trailing;

    if (wrapped_len > best_len) {
        It first = v.begin() + static_cast<std::ptrdiff_t>(n - trailing);
        It last = v.begin() + static_cast<std::ptrdiff_t>(leading);
        return {first, last};
    }

    It first = v.begin() + static_cast<std::ptrdiff_t>(best_start);
    It last = first + static_cast<std::ptrdiff_t>(best_len);
    return {first, last};
}

void clean_noisy_bounds(DebugWriter& debug_output, Arrangement_2& arr, SegmentLookup& segment_lookup, double threshold) {
    using SK = CGAL::Simple_cartesian<double>;
    CGAL::Cartesian_converter<K, SK> C{};

    auto other = [](const Segment_2& e, const Point_2& v) {
        return (e.source() == v) ? e.target() : e.source();
    };

    auto edge_badness = [&](const Segment_2& e) -> double {
        auto closest = segment_lookup.n_closest_input_segments(e, 2);
        if (closest.size() != 2) {
            throw std::runtime_error("Unable to locate two nearby edges");
        }

        auto get_dir = [&](const Segment_2& s) {
            auto a = C(s.source());
            auto b = C(s.target());
            SK::Vector_2 v = b - a;
            double l = std::sqrt(v.squared_length());
            if (l <= 1e-12) {
                return std::make_pair(SK::Vector_2(0, 0), 0.);
            }
            return std::make_pair(v / l, l);
        };

        auto [own_dir, own_length] = get_dir(e);

        auto angle = [&](const SK::Vector_2& ov) {
            double d = std::abs(own_dir * ov);
            if (d > 1.0) {
                d = 1.0;
            }
            return std::acos(d);
        };

        double best = std::numeric_limits<double>::infinity();
        for (auto& s : closest) {
            auto [dv, dl] = get_dir(s);
            best = std::min(best, angle(dv));
        }
        return (best + 0.01) / own_length;
    };

    size_t facet_index = 0;
    for (auto it = arr.faces_begin(); it != arr.faces_end(); ++it, ++facet_index) {
        if (!it->is_unbounded()) {
            std::set<std::pair<Point_2, Point_2>> to_remove;
            std::vector<std::pair<Point_2, Point_2>> to_insert;

            std::vector<Segment_2> segs;
            std::vector<Arrangement_2::Vertex_const_handle> vertices;
            std::vector<Arrangement_2::Halfedge_handle> halfedges;

            auto circ = it->outer_ccb();
            do {
                auto a = circ->source()->point();
                auto b = circ->target()->point();
                segs.emplace_back(a, b);
                vertices.push_back(circ->source());
                halfedges.push_back(circ);
                ++circ;
            } while (circ != it->outer_ccb());

            std::vector<double> badnesses;
            for (auto& e : segs) {
                badnesses.push_back(edge_badness(e));
            }

            auto bit = std::min_element(badnesses.begin(), badnesses.end());
            if (*bit > threshold) {
                // std::cerr << "All edges are good, skipping" << std::endl;
                continue;
            }

            auto it_pair = longest_wrapping_true_run(badnesses, [&](double d) { return d > threshold; });
            auto N = circular_distance(it_pair.first, it_pair.second, badnesses);

            if (N == 0) {
                // std::cerr << "Unable to find run of bad edges, skipping" << std::endl;
                continue;
            }

            std::vector<std::vector<Point_2>> incoming_paths;

            auto jt = it_pair.first;
            for (std::size_t k = 0; k < N; ++k, next_circular(jt, badnesses)) {

                auto he = halfedges[std::distance(badnesses.cbegin(), jt)];
                to_remove.insert({he->source()->point(), he->target()->point()});
                debug_output.write_segment(he->source()->point(), he->target()->point(), "arr_bad_bound facet_" + std::to_string(facet_index));

                Arrangement_2::Vertex_handle v = he->source();

                // circle around other edges onto v
                Arrangement_2::Halfedge_around_vertex_circulator first, curr;
                first = curr = v->incident_halfedges();
                do {
                    Arrangement_2::Vertex_handle u = curr->source();
                    if (curr->face() != it && curr->twin()->face() != it) {

                        // loop until we find a 3-degree vertex, or we come back to the start
                        std::vector<Point_2> path{v->point(), u->point()};
                        auto he = curr;

                        while (u->degree() == 2 && u != v && path.size() < 10) {
                            std::vector<Arrangement_2::Halfedge_handle> hes;

                            {
                                Arrangement_2::Halfedge_around_vertex_circulator first, curr;
                                first = curr = u->incident_halfedges();
                                do {
                                    hes.push_back(curr);
                                    curr++;
                                } while (curr != first);
                            }

                            auto next_he = hes.front() != he && hes.front() != he->twin() ? hes.front() : hes.back();
                            auto next_v = next_he->target() != u ? next_he->target() : next_he->source();

                            path.push_back(next_v->point());
                            u = next_v;
                        }
                        incoming_paths.push_back(std::move(path));
                    }
                } while (++curr != first);
            }

            const std::size_t start =
                static_cast<std::size_t>(std::distance(badnesses.cbegin(), it_pair.first));

            auto n = badnesses.size();

            auto wrap = [n](std::ptrdiff_t i) -> std::size_t {
                i %= static_cast<std::ptrdiff_t>(n);
                if (i < 0) {
                    i += static_cast<std::ptrdiff_t>(n);
                }
                return static_cast<std::size_t>(i);
            };

            const std::size_t ib = start;
            const std::size_t ia = wrap(static_cast<std::ptrdiff_t>(start) - 1);
            const std::size_t ic = wrap(static_cast<std::ptrdiff_t>(start + N));
            const std::size_t id = wrap(static_cast<std::ptrdiff_t>(start + N + 1));

            auto a = vertices.begin() + static_cast<std::ptrdiff_t>(ia);
            auto b = vertices.begin() + static_cast<std::ptrdiff_t>(ib);
            auto c = vertices.begin() + static_cast<std::ptrdiff_t>(ic);
            auto d = vertices.begin() + static_cast<std::ptrdiff_t>(id);

            CGAL::Ray_2<K> r1((*a)->point(), (*b)->point());
            CGAL::Ray_2<K> r2((*d)->point(), (*c)->point());

            auto x = CGAL::intersection(r1, r2);
            if (x) {
                if (auto* xp = variant_get<CGAL::Point_2<K>>(&*x)) {
                    to_insert.emplace_back((*b)->point(), *xp);
                    to_insert.emplace_back((*c)->point(), *xp);

                    debug_output.write_segment((*b)->point(), *xp, "corrected_bound facet_" + std::to_string(facet_index));
                    debug_output.write_segment((*c)->point(), *xp, "corrected_bound facet_" + std::to_string(facet_index));
                }
            } else {
                CGAL::Line_2<K> r1((*a)->point(), (*b)->point());
                CGAL::Line_2<K> r2((*d)->point(), (*c)->point());

                auto x = CGAL::intersection(r1, r2);
                if (x) {
                    if (auto* xp = variant_get<CGAL::Point_2<K>>(&*x)) {
                        to_insert.emplace_back((*b)->point(), *xp);
                        to_insert.emplace_back((*c)->point(), *xp);

                        debug_output.write_segment((*b)->point(), *xp, "corrected_bound facet_" + std::to_string(facet_index));
                        debug_output.write_segment((*c)->point(), *xp, "corrected_bound facet_" + std::to_string(facet_index));
                    }
                }
            }
        }
    }
}

void remove_colinear_vertices(Arrangement_2& arr) {
    std::set<Arrangement_2::Halfedge_handle> to_remove;
    std::set<std::pair<Point_2, Point_2>> to_add;
    while (true) {
        bool removed_this_round = false;
        for (auto it = arr.vertices_begin(); it != arr.vertices_end(); ++it) {
            if (it->degree() == 2) {
                Arrangement_2::Halfedge_around_vertex_circulator first, curr;
                first = curr = it->incident_halfedges();
                size_t i = 0;
                std::array<Point_2, 2> pts;
                std::array<Arrangement_2::Halfedge_handle, 2> hes;
                do {
                    Arrangement_2::Vertex_const_handle u = curr->source();
                    hes[i] = curr;
                    pts[i++] = u->point();
                } while (++curr != first);

                using SK = CGAL::Simple_cartesian<double>;
                CGAL::Cartesian_converter<K, SK> C{};

                auto a = C(pts[0]);
                auto b = C(it->point());
                auto c = C(pts[1]);

                SK::Vector_2 ab = b - a;
                SK::Vector_2 ac = c - a;
                ab /= std::sqrt(ab.squared_length());
                ac /= std::sqrt(ac.squared_length());

                double d = ab * ac;
                if (std::acos(d) < 1e-12) {
                    CGAL::remove_edge(arr, hes[0]);
                    CGAL::remove_edge(arr, hes[1]);
                    CGAL::insert(arr, Segment_2(pts[0], pts[1]));
                    removed_this_round = true;
                    break;
                };
            }
        }
        if (!removed_this_round) {
            break;
        }
    }
}

class timer {
  public:
    class entry {
      public:
        entry() : logger_(nullptr) {}

        entry(
            std::map<std::string, std::chrono::high_resolution_clock::time_point>::const_iterator start_it,
            Logger& logger)
            : start_it(start_it)
            , logger_(&logger) {}

        void stop() {
            if (start_it && logger_) {
                auto end = std::chrono::high_resolution_clock::now();
                auto duration = std::chrono::duration<double, std::milli>(end - start_it.value()->second).count();
                std::ostringstream message;
                message << "Timing for " << start_it.value()->first << ": " << duration << " ms";
                logger_->Message(Logger::LOG_PERF, "ARR", 11, message.str());
            }     
        }

      private:
        std::optional<std::map<std::string, std::chrono::high_resolution_clock::time_point>::const_iterator> start_it;
        Logger* logger_;
    };

    timer(Logger& logger, bool enabled = true)
        : logger_(logger)
        , enabled_(enabled) {}

    entry start(const std::string& name) {
        if (enabled_) {
            return entry(timings_.insert({name, std::chrono::high_resolution_clock::now()}).first, logger_);
        } else {
            return entry();
        }
    }

  private:
    std::map<
        std::string,
        std::chrono::high_resolution_clock::time_point>
        timings_;

    Logger& logger_;
    bool enabled_;
};

size_t delete_same_facet_edge_pairs(Arrangement_2& arr) {
    size_t n_deleted = 0;
    for (auto it = arr.edges_begin(); it != arr.edges_end();) {
        decltype(it) current = it++;
        if (current->face() == current->twin()->face()) {
            arr.remove_edge(current);
            n_deleted++;
        }
    }
    return n_deleted;
}

void arrange_cgal_polygons(
    svgfill::arrange_polygon_settings settings,
    const std::vector<Polygon_2>& input_polygons_,
    std::vector<Polygon_2>& output_polygons,
    Logger& logger,
    double polygon_offset_distance = -1.) {

    static const double OVERLAP_RESOLUTION_DISTANCE = 1.e-1;
    // even larger amount of inset so that outer perimeter is safely within all input polygons even when overlap resolution is applied
    // no, `1.e-2 + 1.e-5` creates issues with the outer perimeter, are there other tolerances in play?
    static const double OUTER_PERIMITER_ADDITIONAL_INSET_AMOUNT = 1.e-5; 

    DebugWriter debug_output;
    if (settings.debug_output) {
        auto t = std::time(nullptr);
        auto tm = *std::localtime(&t);

        std::ostringstream oss;
        oss << std::put_time(&tm, "arrangement_%Y%m%d%H%M%S");
        auto now = oss.str();
        debug_output = DebugWriter(true, now);
    } else {
        debug_output = DebugWriter(false, "");
    }

    timer timer(logger, settings.debug_output);

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

    // before overlap elimition we can (and should) still smooth
    /*
    * @todo
    for (auto& r : input_polygons) {
        smooth_polygon(polygon_offset_distance / 100., r);
    }
    */

    t0.stop();
    t0 = timer.start("overlap elimination");

    eliminate_overlaps(debug_output, OVERLAP_RESOLUTION_DISTANCE, input_polygons);

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
        smooth_polygon(polygon_offset_distance / 1000., r);
    }

    debug_output.write_polygons(input_polygons, "processed_input");

    std::vector<Polygon_2> outer_perimiter;
    if (settings.outer_perimiter_algo == 0) {
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
        outer_perimiter = create_and_convert_offset_polygon(
            // Because polygon_offset is inexact, make sure our inset distance is slightly larger
            // std::nexttoward(-polygon_offset_distance, -std::numeric_limits<double>::infinity()),

            // 1.e-8 even was too little and still resulted in slivers of triangle around the perimeter
            -polygon_offset_distance - OUTER_PERIMITER_ADDITIONAL_INSET_AMOUNT,
            fused_removed_close_points);

        debug_output.write_polygons(outer_perimiter, "outer_perimiter");
    } else {
        std::map<Point_2, std::vector<Point_2>> neighbour_map;
        build_radial_neighbour_map(input_polygons, polygon_offset_distance, neighbour_map);

        auto start_vertex = neighbour_map.rbegin()->first;
        auto next_vertex = neighbour_map.rbegin()->second.front();

        std::vector<Point_2> cycle = {start_vertex, next_vertex};
        while (cycle.back() != cycle.front()) {
            const auto& incoming_from = *(cycle.rbegin() + 1);
            const auto& nb = neighbour_map[cycle.back()];
            auto it = std::find(nb.begin(), nb.end(), incoming_from);
            // cycle it -1 around nb
            if (it == nb.begin()) {
                it = nb.end() - 1;
            } else {
                --it;
            }
            cycle.push_back(*it);
        }
        outer_perimiter.emplace_back(cycle.begin(), cycle.end());
    }

    t0.stop();
    t0 = timer.start("corridor creation");

    // Subtract original polygons from outer perimeter
    std::vector<Polygon_with_holes_2> difference_result, difference_result_subdivided;
    for (auto& i : outer_perimiter) {
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

    SegmentLookup segment_lookup(input_polygons);

    // subdivide difference_result to have better more detailed triangulation and therefore less-pronounced artefacts in midpoint network

    // We store correspondence of subdivision points to input polygons when subdividing so that we do not need to query, which is expensive, when building the line graph later on.
    std::map<Point_2, SegmentLookup::PolygonIt> point_lookup;

    auto subdivision_length = polygon_offset_distance / settings.subdivision_factor;

    for (auto& pwh : difference_result) {
        difference_result_subdivided.push_back(subdivide_polygon_on_same_input(segment_lookup, subdivision_length, pwh, point_lookup));
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

    auto [line_graph, midpoint_to_segment, segment_to_input_facet] = build_line_graph(input_polygons, point_lookup, triangular_polygons);
    for (auto& p : line_graph) {
        for (auto& q : p.second) {
            debug_output.write_segment(p.first, q, "network_1");
        }
    }

    t0.stop();

    t0 = timer.start("center line cleaning");

    Graph2D<K> G;

    {
        // this is applied for both algos
        auto eliminated_segments = eliminate_triangles(line_graph);
        for (auto e : eliminated_segments) {
            debug_output.write_segment(e.first, e.second, "eliminated");
            for (int i = 0; i < 2; ++i) {
                auto it = line_graph.find(e.first);
                if (it == line_graph.end()) {
                    logger.Message(Logger::LOG_WARNING, "ARR", 12, "Unable to locate vertex for elimination; skipping");
                    continue;
                }
                auto& neighbours = it->second;
                neighbours.erase(std::remove(neighbours.begin(), neighbours.end(), e.second), neighbours.end());
                if (neighbours.empty()) {
                    line_graph.erase(it);
                }
                std::swap(e.first, e.second);
            }
        }
    }

    Graph2D<K> G_orig(line_graph);

    auto apply_line_cleaning_algo_1 = [&]() {
        Graph2D<K> G2(line_graph);
        G = G2.weld_vertices();
        for (auto it = G.edges_begin(); it != G.edges_end(); ++it) {
            debug_output.write_segment(it->first, it->second, "network_b_2");
        }
        eliminate_colinear_vertices(G);
        edge_slide(G);
        for (auto it = G.edges_begin(); it != G.edges_end(); ++it) {
            debug_output.write_segment(it->first, it->second, "network_b_3");
        }
    };

    if (settings.line_cleaning_algo == 0) {
        G = join_segment_runs(debug_output, line_graph, midpoint_to_segment, subdivision_length * 4, logger);
        Arrangement_2 arr;
        G.to_arrangement(arr);
        Graph2D<K> G2;
        G2.from_arrangement(arr);
        eliminate_colinear_vertices(G2);
        G = G2;
        for (auto it = G.edges_begin(); it != G.edges_end(); ++it) {
            debug_output.write_segment(it->first, it->second, "network_a_2");
        }
    } else {
        apply_line_cleaning_algo_1();
    }

    t0.stop();

    t0 = timer.start("topology");

    std::list<std::pair<Point_2, Point_2>> segments, segments1, segments2;
    bool fallback_to_line_cleaning_algo_1 = false;
    
    if (settings.line_cleaning_algo == 0) {
        segments1 = extend_end_vertices_based_on_input_simple(debug_output, G, outer_perimiter, subdivision_length * 16, 0, logger);
        segments2 = extend_end_vertices_based_on_input_simple(debug_output, G_orig, outer_perimiter, subdivision_length * 16, 1, logger);
        
        Arrangement_2 arr_clean;
        G.to_arrangement(arr_clean);
        for (auto& pq : segments1) {
            if (pq.first == pq.second) {
                continue;
            }
            CGAL::insert(arr_clean, Segment_2(pq.first, pq.second));
        }

        Arrangement_2 arr_orig;
        G_orig.to_arrangement(arr_orig);
        for (auto& pq : segments2) {
            if (pq.first == pq.second) {
                continue;
            }
            CGAL::insert(arr_orig, Segment_2(pq.first, pq.second));
        }

        for (auto& p : outer_perimiter) {
            for (auto it = p.edges_begin(); it != p.edges_end(); ++it) {
                auto source = it->source();
                auto target = it->target();
                if (source == target) {
                    continue;
                }
                CGAL::insert(arr_orig, Segment_2(source, target));
                CGAL::insert(arr_clean, Segment_2(source, target));
            }
        }

        delete_same_facet_edge_pairs(arr_clean);
        delete_same_facet_edge_pairs(arr_orig);

        debug_output.write_polygons(arr_clean, "iou_left");
        debug_output.write_polygons(arr_orig, "iou_right");

        auto ious = arrangement_cell_iou(debug_output, arr_clean, arr_orig, logger);
        /*
        for (auto& iou : ious) {
            std::cout << " " << CGAL::to_double(iou - 1);
        }
        std::cout << std::endl;
        */

        auto it = std::min_element(ious.begin(), ious.end());

        if (it != ious.end() && (*it < 0.45)) {
            std::ostringstream message;
            message << "Significant difference between cleaned and original arrangement; using original for topology reconstruction: "
                    << *it;
            logger.Message(Logger::LOG_WARNING, "ARR", 13, message.str());
            fallback_to_line_cleaning_algo_1 = true;
            apply_line_cleaning_algo_1();
        } else {
            segments = segments1;
        }
    }

    if (settings.line_cleaning_algo != 0 || fallback_to_line_cleaning_algo_1) {
        segments = extend_end_vertices_based_on_input(G, midpoint_to_segment, segment_to_input_facet, outer_perimiter, segment_lookup, subdivision_length * 4);
    }   

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

    if (settings.topology_reconstruction_algo != 0) {
        // Write input polygons to arrangement_2
        // We no longer do this because we add the outer perimiter now, subdivided by the corridor network which is extended and intersected with the outer perimiter
        for (auto& poly : input_polygons) {
            for (size_t i = 0; i != poly.size(); ++i) {
                auto j = (i + 1) % poly.size();
                if (poly.vertex(i) == poly.vertex(j)) {
                    continue;
                }
                CGAL::insert(arr, Segment_2(poly.vertex(i), poly.vertex(j)));
            }
        }
    } else {
        // Write outer perimeter to arrangement_2
        for (auto& p : outer_perimiter) {
            for (auto it = p.edges_begin(); it != p.edges_end(); ++it) {
                auto source = it->source();
                auto target = it->target();
                if (source == target) {
                    continue;
                }
                CGAL::insert(arr, Segment_2(source, target));
            }
        }
    }

    debug_output.write_polygons(arr, "arr_faces");


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

    if (settings.topology_reconstruction_algo != 0) {
        fuse_corridor_halves_with_input(arr, G, segment_lookup, input_polygons, debug_output);
    }

    if (settings.perform_cleanup && settings.line_cleaning_algo != 0) {
        remove_colinear_vertices(arr);
        double threshold;
        clean_noisy_paths(debug_output, arr, segment_lookup, threshold, logger);
        remove_colinear_vertices(arr);
        // clean_noisy_bounds(debug_output, arr, segment_lookup, threshold);
    }

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

bool svgfill::arrange_polygons(
    arrange_polygon_settings settings,
    const std::vector<svgfill::polygon_2>& polygons,
    std::vector<svgfill::polygon_2>& arranged,
    Logger& logger) {
    std::vector<Polygon_2> cgal_polygons, cgal_polygons_out;
    std::transform(polygons.begin(), polygons.end(), std::back_inserter(cgal_polygons), [](auto& poly) {
        Polygon_2 result;
        std::transform(poly.boundary.begin(), poly.boundary.end(), std::back_inserter(result), [](auto& p) {
            return Point_2(p[0], p[1]);
        });
        return result;
    });
    arrange_cgal_polygons(settings, cgal_polygons, cgal_polygons_out, logger);
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
    Logger logger;
    logger.SetOutput(&std::cout, &std::cerr);
    logger.Verbosity(Logger::LOG_PERF);

    if (argc == 2) {
        using json = nlohmann::json;
        std::ifstream file(argv[1]);
        json jsonData;
        file >> jsonData;
        size_t i = 0;
        for (const auto& item : jsonData.items()) {
            logger.Message(Logger::LOG_NOTICE, "ARR", 14, "Processing arrangement " + std::to_string(i));
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
            arrange_cgal_polygons(arrange_polygon_settings{}, input_polygons, output, logger);
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
    arrange_cgal_polygons(arrange_polygon_settings{}, input_polygons, output, logger);

    return 0;
}

#endif
