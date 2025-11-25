#ifndef GRAPH_2D_H
#define GRAPH_2D_H

#ifdef SVGFILL_DEBUG
#include <nlohmann/json.hpp>
#endif

template <typename Kernel>
class Graph2D {
public:
    typedef typename Kernel::Point_2 Point_2;
    typedef std::pair<Point_2, Point_2> Edge;

    Graph2D() {}

    Graph2D(const std::map<Point_2, std::vector<Point_2>>& input_adjacency_list) {
        for (const auto& kv : input_adjacency_list) {
            const Point_2& u = kv.first;
            const std::vector<Point_2>& neighbors = kv.second;
            for (const Point_2& v : neighbors) {
                if (u != v) { // no self-edges
                    adjacency_list[u].insert(v);
                    adjacency_list[v].insert(u);  // Since it's undirected
                }
            }
        }
        assert_symmetric();
    }

    Graph2D(const CGAL::Polygon_2<Kernel>& loop) {
        for (auto it = loop.vertices_begin(); it != loop.vertices_end(); ++it) {
            auto next_it = std::next(it);
            if (next_it == loop.vertices_end()) {
                next_it = loop.vertices_begin();
            }
            adjacency_list[*it].insert(*next_it);
            adjacency_list[*next_it].insert(*it);
        }
    }

    bool is_loop() const {
        if (adjacency_list.size() < 3) {
            return false;
        }
        for (const auto& p : adjacency_list) {
            if (p.second.size() != 2) {
                return false;
            }
        }
        return true;
    }

    auto find(const Point_2& p) {
        return adjacency_list.find(p);
    }

    boost::optional< CGAL::Segment_2<Kernel> > query(const Point_2& p, typename Kernel::FT eps) {
        boost::optional< CGAL::Segment_2<Kernel> > closest_segment;
        typename Kernel::FT closest_distance = std::numeric_limits<double>::infinity();
        for (auto& p1 : adjacency_list) {
            for (auto& p2 : p1.second) {
                CGAL::Segment_2<Kernel>seg(p1.first, p2);
                auto dist = CGAL::squared_distance(p, seg);
                if (dist < eps * eps && dist < closest_distance) {
                    closest_distance = dist;
                    closest_segment = seg;
                }
            }
        }
        return closest_segment;
    }

    void refine(const CGAL::Segment_2<Kernel>& seg, const Point_2& p) {
        remove_edge(seg.source(), seg.target());
        insert(seg.source(), p);
        insert(p, seg.target());
    }

    std::vector<Point_2> shorted_path(const Point_2& start, const Point_2& goal) const {
        auto& adj = adjacency_list;
        if (adj.count(start) == 0 || adj.count(goal) == 0) return {};

        std::map<Point_2, Point_2> predecessor;
        std::queue<Point_2> q;

        // seed BFS
        predecessor[start] = start;  // mark start as "seen"
        q.push(start);

        // BFS
        bool found = false;
        while (!q.empty() && !found) {
            Point_2 u = q.front(); q.pop();
            for (auto& v : adj.at(u)) {
                // if v has no predecessor yet, it's unseen
                if (!predecessor.count(v)) {
                    predecessor[v] = u;
                    q.push(v);
                    if (v == goal) { found = true; break; }
                }
            }
        }

        if (!found) return {};

        // reconstruct path
        std::vector<Point_2> path;
        for (Point_2 cur = goal; cur != start; cur = predecessor[cur])
            path.push_back(cur);
        path.push_back(start);
        std::reverse(path.begin(), path.end());
        return path;
    }


    std::vector<Point_2> shorted_path(const Point_2& start, const std::set<Point_2>& goal) const {
        auto& adj = adjacency_list;
        if (adj.count(start) == 0) return {};

        std::map<Point_2, Point_2> predecessor;
        std::queue<Point_2> q;

        // seed BFS
        predecessor[start] = start;  // mark start as "seen"
        q.push(start);

        Point_2 used_goal;

        // BFS
        bool found = false;
        while (!q.empty() && !found) {
            Point_2 u = q.front(); q.pop();
            for (auto& v : adj.at(u)) {
                // if v has no predecessor yet, it's unseen
                if (!predecessor.count(v)) {
                    predecessor[v] = u;
                    q.push(v);
                    if (goal.find(v) != goal.end()) {
                        found = true;
                        used_goal = v;
                        break;
                    }
                }
            }
        }

        if (!found) return {};

        // reconstruct path
        std::vector<Point_2> path;
        for (Point_2 cur = used_goal; cur != start; cur = predecessor[cur])
            path.push_back(cur);
        path.push_back(start);
        std::reverse(path.begin(), path.end());
        return path;
    }


    void move(const Point_2& from, const Point_2& to) {
        // @todo should check for intersections?
        auto it = adjacency_list.find(from);
        if (it != adjacency_list.end()) {
            auto neighbours = it->second;
            for (auto& n : neighbours) {
                adjacency_list[n].erase(from);
                adjacency_list[n].insert(to);
            }
            adjacency_list.erase(it);
            adjacency_list.insert({ to, neighbours });
        }
    }

    bool is_valid() const {
        typedef CGAL::Box_intersection_d::Box_with_handle_d<double, 2, size_t, CGAL::Box_intersection_d::ID_EXPLICIT> Box;
        std::vector<Box> boxes;
        std::vector<CGAL::Segment_2<Kernel>> segments;
        for (const auto& p : adjacency_list) {
            for (const auto& q : p.second) {
                if (p.first < q) {
                    segments.emplace_back(p.first, q);
                }
            }
        }
        for (auto it = segments.begin(); it != segments.end(); ++it) {
            boxes.emplace_back(it->bbox(), std::distance(segments.begin(), it));
        }
        bool any = false;
        CGAL::box_self_intersection_d(boxes.begin(), boxes.end(), [this, &segments, &any](const Box& a, const Box& b) {
            auto& seg1 = segments[a.handle()];
            auto& seg2 = segments[b.handle()];
            // Skip topologically connected segments
            if (seg1.source() == seg2.source() || seg1.source() == seg2.target() || seg1.target() == seg2.source() || seg1.target() == seg2.target()) {
                return;
            }
            if (CGAL::do_intersect(seg1, seg2)) {
                any = true;
            }
        });
        return any;
    }

    // Eliminates a vertex with exactly two neighbors by connecting its neighbors
    typename std::map<Point_2, std::set<Point_2>>::iterator eliminate_vertex(typename std::map<Point_2, std::set<Point_2>>::iterator it) {
        if (it == adjacency_list.end()) {
            // Vertex not found
            return adjacency_list.end();
        }
        const std::set<Point_2>& neighbors = it->second;
        if (neighbors.size() != 2) {
            // Not exactly two neighbors
            return adjacency_list.end();
        }
        // Get the two neighbors
        auto neighbor_it = neighbors.begin();
        auto u = *neighbor_it++;
        auto w = *neighbor_it;
        auto v = it->first;

        // Remove all edge between v and u
        adjacency_list[u].erase(v);
        adjacency_list[v].erase(u);

        // Remove all edge between v and w
        adjacency_list[w].erase(v);
        adjacency_list[v].erase(w);

        // Add edge between u and w
        adjacency_list[u].insert(w);
        adjacency_list[w].insert(u);

        // Remove v from adjacency_list
        auto jt = adjacency_list.erase(it);

        assert_symmetric();

        return jt;
    }

    Graph2D weld_vertices() const {
        std::set<Point_2> points;
        for (auto& p : adjacency_list) {
            points.insert(p.first);
            for (auto& q : p.second) {
                points.insert(q);
            }
        }

        using It = typename std::set<Point_2>::iterator;
        using Box = CGAL::Box_intersection_d::Box_with_handle_d<double, 2, Point_2 const*>;

        std::vector<Box> boxes;
        for (auto it = points.begin(); it != points.end(); ++it) {
            constexpr double offset = 1.e-3;
            auto b = it->bbox();
            boxes.emplace_back(
                CGAL::Bbox_2(b.xmin() - offset, b.ymin() - offset, b.xmax() + offset, b.ymax() + offset),
                &*it
            );
        }

        std::vector<std::pair<Point_2 const*, Point_2 const*>> overlaps;

        CGAL::box_self_intersection_d(boxes.begin(), boxes.end(), [&overlaps](const Box& a, const Box& b) {
            overlaps.emplace_back(a.handle(), b.handle());
        });

        std::map<Point_2, std::vector<Point_2>> input_adjacency_list;

        {
            std::map<Point_2 const*, std::vector<Point_2 const*>> adj;
            for (const auto& edge : overlaps) {
                adj[edge.first].push_back(edge.second);
                adj[edge.second].push_back(edge.first);
            }
            for (auto& p : points) {
                adj[&p];
            }

            std::map<Point_2 const*, bool> visited;
            std::vector<std::vector<Point_2 const*>> connected_components;

            for (auto& p : adj) {
                if (!visited[p.first]) {
                    connected_components.emplace_back();

                    std::stack<Point_2 const*> stack;
                    stack.push(p.first);
                    visited[p.first] = true;

                    while (!stack.empty()) {
                        auto u = stack.top();
                        stack.pop();
                        connected_components.back().push_back(u);

                        for (auto& neighbor : adj[u]) {
                            if (!visited[neighbor]) {
                                visited[neighbor] = true;
                                stack.push(neighbor);
                            }
                        }
                    }
                }
            }

            std::map<Point_2, Point_2> mapping;

            for (auto& comp : connected_components) {
                Point_2 avg(0, 0);
                for (auto& c : comp) {
                    avg += (*c - CGAL::ORIGIN);
                }
                avg = CGAL::ORIGIN + ((avg - CGAL::ORIGIN) / comp.size());

                for (auto& c : comp) {
                    mapping[*c] = avg;
                }
            }

            for (auto& comp : connected_components) {
                for (auto& c : comp) {
                    const auto& C = mapping[*c];
                    for (auto& n : adjacency_list.find(*c)->second) {
                        const auto& N = mapping[n];
                        if (C != N) {
                            if (std::find(input_adjacency_list[C].begin(), input_adjacency_list[C].end(), N) == input_adjacency_list[C].end()) {
                                input_adjacency_list[C].push_back(N);
                            }
                        }
                    }
                }
            }
        }

        return Graph2D(input_adjacency_list);
    }

    void assert_symmetric() {
#ifdef SVGFILL_DEBUG
#if 0
        for (auto& p : adjacency_list) {
            if (p.second.find(p.first) != p.second.end()) {
                std::cout << "!! " << p.first << " self-edge" << std::endl;
                throw std::runtime_error("self-edge");
            }
        }
        nlohmann::json json_obj = nlohmann::json::array();
        for (auto& p : adjacency_list) {
            if (p.second.size() == 0) {
                continue;
            }

            nlohmann::json pair = nlohmann::json::array();
            nlohmann::json coord = nlohmann::json::array();
            nlohmann::json values = nlohmann::json::array();
            coord.push_back(
                CGAL::to_double(p.first.x())
            );
            coord.push_back(
                CGAL::to_double(p.first.y())
            );
            pair.push_back(coord);
            for (auto& q : p.second) {
                auto& r = adjacency_list[q];
                for (auto& s : r) {
                    nlohmann::json coord = nlohmann::json::array();
                    coord.push_back(
                        CGAL::to_double(s.x())
                    );
                    coord.push_back(
                        CGAL::to_double(s.y())
                    );
                    values.push_back(coord);
                }
                if (r.find(p.first) == r.end()) {
                    for (auto& s : r) {
                        std::cout << "  " << s << std::endl;
                    }
                    std::cout << "!! " << p.first << " not found in neighbours of " << q << std::endl;
                    throw std::runtime_error("internal error");
                }
            }
            pair.push_back(values);
            json_obj.push_back(
                pair
            );
        }

        static int fff = 0;
        std::ofstream file("graph_" + std::to_string(fff++) + ".json");
        file << json_obj.dump(2);
#endif
#endif
    }

    void remove_edge(const Point_2& u, const Point_2& v) {
        adjacency_list[u].erase(v);
        adjacency_list[v].erase(u);
        assert_symmetric();
    }

    void insert(const Point_2& u, const Point_2& v) {
        adjacency_list[u].insert(v);
        adjacency_list[v].insert(u);
        assert_symmetric();
    }

    // Iterators over vertices
    typedef typename std::map<Point_2, std::set<Point_2>>::const_iterator vertex_const_iterator;
    typedef typename std::map<Point_2, std::set<Point_2>>::iterator vertex_iterator;

    vertex_const_iterator vertices_begin() const {
        return adjacency_list.cbegin();
    }

    vertex_const_iterator vertices_end() const {
        return adjacency_list.cend();
    }

    vertex_iterator vertices_begin() {
        return adjacency_list.begin();
    }

    vertex_iterator vertices_end() {
        return adjacency_list.end();
    }

    // Edge iterator class
    class EdgeIterator {
    public:
        typedef std::forward_iterator_tag iterator_category;
        typedef Edge value_type;
        typedef ptrdiff_t difference_type;
        typedef const Edge* pointer;
        typedef const Edge& reference;

        EdgeIterator() : outer_it_(), inner_it_(), graph_(nullptr) {}
        EdgeIterator(const Graph2D* graph, typename std::map<Point_2, std::set<Point_2>>::const_iterator outer_it)
            : outer_it_(outer_it), graph_(graph) {
            if (outer_it_ != graph_->adjacency_list.end()) {
                inner_it_ = outer_it_->second.begin();
                advance_to_valid();
            }
        }

        reference operator*() const {
            current_edge_ = Edge(outer_it_->first, *inner_it_);
            return current_edge_;
        }

        pointer operator->() const {
            current_edge_ = Edge(outer_it_->first, *inner_it_);
            return &current_edge_;
        }

        EdgeIterator& operator++() {
            ++inner_it_;
            advance_to_valid();
            return *this;
        }

        EdgeIterator operator++(int) {
            EdgeIterator tmp = *this;
            ++(*this);
            return tmp;
        }

        bool operator==(const EdgeIterator& other) const {
            return outer_it_ == other.outer_it_ && (outer_it_ == graph_->adjacency_list.end() || inner_it_ == other.inner_it_);
        }

        bool operator!=(const EdgeIterator& other) const {
            return !(*this == other);
        }

    private:
        void advance_to_valid() {
            while (outer_it_ != graph_->adjacency_list.end()) {
                while (inner_it_ != outer_it_->second.end() && *inner_it_ < outer_it_->first) {
                    ++inner_it_;
                }
                if (inner_it_ != outer_it_->second.end()) {
                    break;
                }
                ++outer_it_;
                if (outer_it_ != graph_->adjacency_list.end()) {
                    inner_it_ = outer_it_->second.begin();
                }
            }
        }

        mutable Edge current_edge_;
        typename std::map<Point_2, std::set<Point_2>>::const_iterator outer_it_;
        typename std::set<Point_2>::const_iterator inner_it_;
        const Graph2D* graph_;
    };

    EdgeIterator edges_begin() const {
        return EdgeIterator(this, adjacency_list.begin());
    }

    EdgeIterator edges_end() const {
        return EdgeIterator(this, adjacency_list.end());
    }

private:
    std::map<Point_2, std::set<Point_2>> adjacency_list;
};

#endif
