#ifndef TAXONOMY_H
#define TAXONOMY_H

#include "../ifcparse/IfcBaseClass.h"

#include <boost/variant.hpp>

#include <Eigen/Dense>

#include <map>
#include <string>
#include <tuple>
#include <exception>

// @todo don't do std::less but use hashing and cache hash values.

namespace ifcopenshell {

namespace geometry {

namespace taxonomy {

class topology_error : public std::runtime_error {
public:
	topology_error() : std::runtime_error("Generic topology error") {}
	topology_error(const char* const s) : std::runtime_error(s) {}
};

enum kinds { MATRIX4, POINT3, DIRECTION3, LINE, CIRCLE, ELLIPSE, BSPLINE_CURVE, OFFSET_CURVE, PLANE, CYLINDER, BSPLINE_SURFACE, EDGE, LOOP, FACE, SHELL, SOLID, LOFT, EXTRUSION, REVOLVE, SURFACE_CURVE_SWEEP, NODE, COLLECTION, BOOLEAN_RESULT, COLOUR, STYLE };

const std::string& kind_to_string(kinds k);

struct item {
	const IfcUtil::IfcBaseInterface* instance;

	boost::optional<bool> orientation;

    virtual item* clone() const = 0;
	virtual kinds kind() const = 0;
	virtual void print(std::ostream&, int indent=0) const = 0;
	virtual void reverse() { throw taxonomy::topology_error(); }

	item(const IfcUtil::IfcBaseInterface* instance = nullptr) : instance(instance) {}

	virtual ~item() {}
};

bool less(const item*, const item*);

struct less_functor {
	bool operator()(const item* a, const item* b) const {
		return less(a, b);
	}
};

namespace {

	template <typename T>
	const T& eigen_defaults();

	template <>
	const Eigen::Vector3d& eigen_defaults<Eigen::Vector3d>() {
		static Eigen::Vector3d identity = Eigen::Vector3d::Zero();
		return identity;
	}

	template <>
	const Eigen::Matrix4d& eigen_defaults<Eigen::Matrix4d>() {
		static Eigen::Matrix4d identity = Eigen::Matrix4d::Identity();
		return identity;
	}

}

template <typename T>
struct eigen_base {
	T* components_;

	eigen_base() {
		components_ = nullptr;
	}

	eigen_base(const eigen_base& other) {
		this->components_ = other.components_ ? new T(*other.components_) : nullptr;
	}

	eigen_base(const T& other) {
		this->components_ = new T(other);
	}

	eigen_base& operator=(const eigen_base& other) {
		if (this != &other) {
			this->components_ = other.components_ ? new T(*other.components_) : nullptr;
		}
		return *this;
	}

	void print_impl(std::ostream& o, const std::string& class_name, int indent = 0) const {
		o << std::string(indent, ' ') << class_name;
		if (this->components_) {
			int n = T::RowsAtCompileTime * T::ColsAtCompileTime;
			for (size_t i = 0; i < n; ++i) {
				o << " " << (*components_)(i);
			}
		}
		o << std::endl;
	}

	virtual ~eigen_base() {
		delete this->components_;
	}

	const T& ccomponents() const {
		if (this->components_) {
			return *this->components_;
		} else {
			return eigen_defaults<T>();
		}
	}

	T& components() {
		if (!this->components_) {
			this->components_ = new T(eigen_defaults<T>());
		}
		return *this->components_;
	}

	explicit operator bool() const {
		return components_;
	}
};

struct matrix4 : public item, public eigen_base<Eigen::Matrix4d> {
private:
	void init(const Eigen::Vector3d& o, const Eigen::Vector3d& z, const Eigen::Vector3d& x) {
		auto X = x.normalized();
		auto Y = z.cross(x).normalized();
		auto Z = z.normalized();
		components_ = new Eigen::Matrix4d;
		(*components_) <<
			X(0), Y(0), Z(0), o(0),
			X(1), Y(1), Z(1), o(1),
			X(2), Y(2), Z(2), o(2),
			0, 0, 0, 1.;
		if (is_identity()) {
			// @todo detect this earlier to save us the heapalloc.
			delete components_;
			components_ = nullptr;
			tag = IDENTITY;
		}
	}
public:

    enum tag_t {
        IDENTITY, AFFINE_WO_SCALE, AFFINE_W_UNIFORM_SCALE, AFFINE_W_NONUNIFORM_SCALE, OTHER
    };
    tag_t tag;

	matrix4() : eigen_base(), tag(IDENTITY) {}
	matrix4(const Eigen::Matrix4d& c) : eigen_base(c), tag(OTHER) {}
	matrix4(const Eigen::Vector3d& o, const Eigen::Vector3d& z, const Eigen::Vector3d& x) : tag(AFFINE_WO_SCALE) {
		init(o, z, x);
	}
	matrix4(const Eigen::Vector3d& o, const Eigen::Vector3d& z) : tag(AFFINE_WO_SCALE) {
		auto x = Eigen::Vector3d(1, 0, 0);
		auto y = z.cross(x);
		if (y.squaredNorm() < 1.e-7) {
			x = Eigen::Vector3d(0, 0, 1);
		}
		init(o, z, x);
	}

	bool is_identity() const {
		return !components_ || components_->isIdentity();
	}

	void print(std::ostream& o, int indent = 0) const {
		print_impl(o, "matrix4", indent);
	}

	virtual item* clone() const { return new matrix4(*this); }
	virtual kinds kind() const { return MATRIX4; }

	Eigen::Vector3d translation_part() const { return ccomponents().col(3).head<3>(); }
};

struct colour : public item, public eigen_base<Eigen::Vector3d> {
	void print(std::ostream& o, int indent = 0) const {
		print_impl(o, "colour", indent);
	}

	virtual item* clone() const { return new colour(*this); }
	virtual kinds kind() const { return COLOUR; }

	colour() : eigen_base() {}
	colour(double r, double g, double b) { components() << r, g, b; }

	const double& r() const { return ccomponents()[0]; }
	const double& g() const { return ccomponents()[1]; }
	const double& b() const { return ccomponents()[2]; }
};

struct style : public item {
	std::string name;
	colour diffuse;
	colour specular;
	double specularity, transparency;

	void print(std::ostream& o, int indent = 0) const {
		o << std::string(indent, ' ') << "style" << std::endl;
		o << std::string(indent, ' ') << "     " << "name" << (name) << std::endl;
		if (diffuse.components_) {
			o << std::string(indent, ' ') << "     " << "diffuse" << (name) << std::endl;
			diffuse.print(o, indent + 5 + 7);
		}
		if (specular.components_) {
			o << std::string(indent, ' ') << "     " << "specular" << (name) << std::endl;
			specular.print(o, indent + 5 + 8);
		}
		// @todo
	}

	virtual item* clone() const { return new style(*this); }
	virtual kinds kind() const { return STYLE; }

	// @todo equality implementation based on values?
	bool operator==(const style& other) const { return instance == other.instance; }

	style() : specularity(std::numeric_limits<double>::quiet_NaN()), transparency(std::numeric_limits<double>::quiet_NaN()) {}
	style(const std::string& name) : name(name), specularity(std::numeric_limits<double>::quiet_NaN()), transparency(std::numeric_limits<double>::quiet_NaN()) {}

	bool has_specularity() const {
		return !std::isnan(specularity);
	}

	bool has_transparency() const {
		return !std::isnan(transparency);
	}
};

struct geom_item : public item {
    style* surface_style;
    matrix4 matrix;

	geom_item(const IfcUtil::IfcBaseClass* instance = nullptr) : item(instance), surface_style(nullptr) {}
	geom_item(const IfcUtil::IfcBaseClass* instance, matrix4 m) : item(instance), surface_style(nullptr), matrix(m) {}
	geom_item(matrix4 m) : surface_style(nullptr), matrix(m) {}
};

// @todo make 4d for easier multiplication
template <size_t N>
struct cartesian_base : public item, public eigen_base<Eigen::Vector3d> {
	cartesian_base() : eigen_base() {}
	cartesian_base(double x, double y, double z = 0.) : eigen_base(Eigen::Vector3d(x, y, z)) {}
};

struct point3 : public cartesian_base<3> {
    virtual item* clone() const { return new point3(*this); }
	virtual kinds kind() const { return POINT3; }

	void print(std::ostream& o, int indent = 0) const {
		print_impl(o, "point3", indent);
	}

	point3() : cartesian_base() {}
	point3(double x, double y, double z = 0.) : cartesian_base(x, y, z) {}
};

struct direction3 : public cartesian_base<3> {
	virtual item* clone() const { return new direction3(*this); }
	virtual kinds kind() const { return DIRECTION3; }

	void print(std::ostream& o, int indent = 0) const {
		print_impl(o, "direction3", indent);
	}

	direction3() : cartesian_base() {}
	direction3(double x, double y, double z = 0.) : cartesian_base(x, y, z) {}
};

struct curve : public geom_item {
	void print_impl(std::ostream& o, const std::string& classname, int indent = 0) const {
		o << std::string(indent, ' ') << classname << std::endl;
		this->matrix.print(o, indent + 4);
	}
};

struct line : public curve {
	virtual item* clone() const { return new line(*this); }
	virtual kinds kind() const { return LINE; }

	void print(std::ostream& o, int indent = 0) const {
		print_impl(o, "line", indent);
	}
};

struct circle : public curve {
	double radius;

	virtual item* clone() const { return new circle(*this); }
	virtual kinds kind() const { return CIRCLE; }

	void print(std::ostream& o, int indent = 0) const {
		print_impl(o, "circle", indent);
	}

	static circle* from_3_points(const Eigen::Vector3d& p1, const Eigen::Vector3d& p2, const Eigen::Vector3d& p3) {
		Eigen::Vector3d t = p2 - p1;
		Eigen::Vector3d u = p3 - p1;
		Eigen::Vector3d v = p3 - p2;

		auto norm = t.cross(u);
		auto mag = norm.dot(norm);

		auto iwsl2 = 1. / (2. * mag);
		auto tt = t.dot(t);
		auto uu = u.dot(u);

		auto orig = p1 + (u * tt * u.dot(v) - t * uu * t.dot(v)) * iwsl2;

		if (!orig.array().isNaN().any()) {
			auto radius = std::sqrt(tt * uu * v.dot(v) * iwsl2 * 0.5f);
			auto ax = norm / std::sqrt(mag);
			

			auto c = new circle;
			c->radius = radius;
			c->matrix = taxonomy::matrix4(orig, ax);
			return c;
		}

		return nullptr;
	}
};

struct ellipse : public circle {
	double radius2;

	virtual item* clone() const { return new ellipse(*this); }
	virtual kinds kind() const { return ELLIPSE; }

	void print(std::ostream& o, int indent = 0) const {
		print_impl(o, "ellipse", indent);
	}
};

struct bspline_curve : public curve {
	virtual item* clone() const { return new bspline_curve(*this); }
	virtual kinds kind() const { return BSPLINE_CURVE; }

	std::vector<point3> control_points;
	std::vector<int> multiplicities;
	std::vector<double> knots;
	boost::optional<std::vector<double>> weights;
	int degree;

	void print(std::ostream& o, int indent = 0) const {
		o << std::string(indent, ' ') << "bspline curve" << std::endl;
	}
};

struct offset_curve : public curve {
	direction3 reference;
	double offset;
	item* basis;

	virtual item* clone() const { return new offset_curve(*this); }
	virtual kinds kind() const { return OFFSET_CURVE; }

	void print(std::ostream& o, int indent = 0) const {
		o << std::string(indent, ' ') << "offset_curve" << std::endl;
	}
};

struct trimmed_curve : public item {
	// @todo The copy constructor of point3 within the variant fails on the avx instruction
	// on the default gcc in Ubuntu 18.04 and a recent AMD Ryzen. Probably due to allignment.
	boost::variant<point3, double> start, end;

	// @todo somehow account for the fact that curve in IFC can be trimmed curve, polyline and composite curve as well.
	item* basis;

	// @todo does this make sense? this is to accomodate for the fact that orientation is defined on both TrimmedCurve as well CompCurveSegment
	boost::optional<bool> orientation_2;

	trimmed_curve() : basis(nullptr), orientation_2(true) {}
	trimmed_curve(const point3& a, const point3& b) : start(a), end(b), basis(nullptr) {}
	
	virtual void reverse() {
		// std::swap(start, end);
		orientation = !orientation;
	}

	void print(std::ostream& o, int indent = 0) const {
		o << std::string(indent, ' ') << "trimmed_curve" << std::endl;
		if (basis) {
			basis->print(o, indent + 4);
		}

		const boost::variant<point3, double> * const start_end[2] = { &start, &end };
		for (int i = 0; i < 2; ++i) {
			o << std::string(indent + 4, ' ') << (i == 0 ? "start" : "end") << std::endl;
			if (start_end[i]->which() == 0) {
				boost::get<point3>(*start_end[i]).print(o, indent + 4);
			} else if (start_end[i]->which() == 1) {
				o << std::string(indent + 4, ' ') << "parameter " << boost::get<double>(*start_end[i]) << std::endl;
			}
		}

		if (this->instance) {
			o << std::string(indent, ' ') << this->instance->data().toString() << std::endl;
		}
	}
};

struct edge : public trimmed_curve {
	edge() : trimmed_curve() {}
	edge(const point3& a, const point3& b) : trimmed_curve(a, b) {}

	// @todo how to express similarity between trimmed_curve and edge?
	virtual item* clone() const { return new edge(*this); }
	virtual kinds kind() const { return EDGE; }
};

// template <typename T=item>
struct collection : public geom_item {
	std::vector<item*> children;

	collection() {}
	collection(const collection& other) {
		std::transform(other.children.begin(), other.children.end(), std::back_inserter(children), std::mem_fn(&item::clone));
	}

	template <typename T>
	std::vector<T*> children_as() const {
		std::vector<T*> ts;
		ts.reserve(children.size());
		std::for_each(children.begin(), children.end(), [&ts](item* i){
			auto v = dynamic_cast<T*>(i);
			if (v) {
				ts.push_back(v);
			}
		});
		return ts;
	}

	virtual item* clone() const { return new collection(*this); }
	virtual kinds kind() const { return COLLECTION; }
	virtual void reverse() { 
		std::reverse(children.begin(), children.end()); 
		for (auto& child : children) {
			child->reverse();
		}
	}

	void print(std::ostream& o, int indent = 0) const {
		o << std::string(indent, ' ') << kind_to_string(kind()) << std::endl;
		if (!matrix.is_identity()) {
			matrix.print(o, indent + 4);
		}
		for (auto& c : children) {
			c->print(o, indent + 4);
		}
	}

	virtual ~collection() {
		for (auto& c : children) {
			delete c;
		}
	}
};

struct shell : public collection /*<face>*/ {
	boost::optional<bool> closed;

	virtual item* clone() const { return new shell(*this); }
	virtual kinds kind() const { return SHELL; }
};

struct solid : public collection /*<face>*/ {
	virtual item* clone() const { return new solid(*this); }
	virtual kinds kind() const { return SOLID; }
};

struct loft : public collection /*<face>*/ {
	item* axis;

	virtual item* clone() const { return new loft(*this); }
	virtual kinds kind() const { return LOFT; }
};

struct surface : public geom_item {};

struct plane : public surface {
	virtual item* clone() const { return new plane(*this); }
	virtual kinds kind() const { return PLANE; }

	void print(std::ostream& o, int) const {
		o << "not implemented";
	}
};

struct cylinder : public surface {
	double radius;

	virtual item* clone() const { return new cylinder(*this); }
	virtual kinds kind() const { return CYLINDER; }

	void print(std::ostream& o, int) const {
		o << "not implemented";
	}
};

struct bspline_surface : public surface {
	virtual item* clone() const { return new bspline_surface(*this); }
	virtual kinds kind() const { return BSPLINE_SURFACE; }

	std::vector<std::vector<point3>> control_points;
	std::array<std::vector<int>, 2> multiplicities;
	std::array<std::vector<double>, 2> knots;
	boost::optional<std::vector<std::vector<double>>> weights;
	std::array<int, 2> degree;

	void print(std::ostream& o, int) const {
		o << "not implemented";
	}
};

struct face : public collection /*<loop>*/ {
	item* basis;

	virtual item* clone() const { return new face(*this); }
	virtual kinds kind() const { return FACE; }
};

struct loop : public collection /*<edge>*/ {
	boost::optional<bool> external, closed;

	bool is_polyhedron() const {
		for (auto& e_ : children) {
			auto e = (taxonomy::edge*) e_;
			if (e->basis != nullptr) {
				if (e->basis->kind() != LINE) {
					return false;
				}
			}
		}
		return true;
	}

	virtual item* clone() const { return new loop(*this); }
	virtual kinds kind() const { return LOOP; }
};

struct sweep : public geom_item {
	face basis;

	sweep(face b) : basis(b) {}
	sweep(matrix4 m, face b) : geom_item(m), basis(b) {}
};

struct extrusion : public sweep {
	direction3 direction;
	double depth;

	virtual item* clone() const { return new extrusion(*this); }
	virtual kinds kind() const { return EXTRUSION; }

	extrusion(matrix4 m, face basis, direction3 dir, double d) : sweep(m, basis), direction(dir), depth(d) {}

	void print(std::ostream& o, int indent = 0) const {
		o << std::string(indent, ' ') << "extrusion " << depth << std::endl;
		direction.print(o, indent + 4);
		basis.print(o, indent + 4);
	}
};

struct revolve : public sweep {
	point3 axis_origin;
	direction3 direction;
	boost::optional<double> angle;

	virtual item* clone() const { return new revolve(*this); }
	virtual kinds kind() const { return REVOLVE; }

	revolve(matrix4 m, face basis, point3 pnt, direction3 dir, const boost::optional<double>& a) : sweep(m, basis), axis_origin(pnt), direction(dir), angle(a) {}

	void print(std::ostream& o, int indent = 0) const {
		o << std::string(indent, ' ') << "revolve" << std::endl;
	}
};

struct surface_curve_sweep : public sweep {
	item* surface;
	item* curve;

	virtual item* clone() const { return new surface_curve_sweep(*this); }
	virtual kinds kind() const { return SURFACE_CURVE_SWEEP; }

	surface_curve_sweep(matrix4 m, face basis, item* surf, item* crv) : sweep(m, basis), surface(surf), curve(crv) {}

	void print(std::ostream& o, int indent = 0) const {
		o << std::string(indent, ' ') << "surface_curve_sweep" << std::endl;
	}
};

struct node : public item {
	std::map<std::string, geom_item*> representations;

	virtual item* clone() const { return new node(*this); }
	virtual kinds kind() const { return NODE; }

	void print(std::ostream&, int = 0) const {}
};

struct boolean_result : public collection {
	enum operation_t {
		UNION, SUBTRACTION, INTERSECTION
	};

	virtual item* clone() const { return new boolean_result(*this); }
	virtual kinds kind() const { return BOOLEAN_RESULT; }
	operation_t operation;

	static const std::string& operation_str(operation_t op) {
		using namespace std::string_literals;
		static std::string s[] = { "union"s, "subtraction"s, "intersection"s };
		return s[(size_t)op];
	}
};

namespace impl {
	typedef std::tuple<matrix4, point3, direction3, line, circle, ellipse, bspline_curve, offset_curve, plane, cylinder, bspline_surface, edge, loop, face, shell, solid, loft, extrusion, revolve, surface_curve_sweep, node, collection, boolean_result> KindsTuple;
	typedef std::tuple<line, circle, ellipse, bspline_curve, offset_curve, loop, edge> CurvesTuple;
	typedef std::tuple<plane, cylinder, bspline_surface> SurfacesTuple;
}

struct type_by_kind {
	template <std::size_t N>
	using type = typename std::tuple_element<N, impl::KindsTuple>::type;

	static const size_t max = std::tuple_size<impl::KindsTuple>::value;
};

struct curves {
	template <std::size_t N>
	using type = typename std::tuple_element<N, impl::CurvesTuple>::type;

	static const size_t max = std::tuple_size<impl::CurvesTuple>::value;
};

struct surfaces {
	template <std::size_t N>
	using type = typename std::tuple_element<N, impl::SurfacesTuple>::type;

	static const size_t max = std::tuple_size<impl::SurfacesTuple>::value;
};

}

	template <typename Fn>
	void visit(const taxonomy::collection* deep, Fn fn) {
		for (auto& c : deep->children) {
			if (c->kind() == taxonomy::COLLECTION) {
				visit((taxonomy::collection*)c, fn);
			} else {
				fn(c);
			}
		}
	}

	template <typename T, typename Fn>
	void visit_2(const taxonomy::collection* c, const Fn& fn) {
		static_assert(std::is_same<T, taxonomy::point3>::value, "@todo Only implemented for point3");
		for (auto& i : c->children) {
			if (dynamic_cast<const taxonomy::collection*>(i)) {
				visit_2<T>(dynamic_cast<const taxonomy::collection*>(i), fn);
			} else if (i->kind() == taxonomy::POINT3) {
				fn((const taxonomy::point3*) i);
			} else if (i->kind() == taxonomy::EDGE) {
				// @todo maybe make edge a collection then as well?
				auto l = (const taxonomy::edge *) i;
				if (l->start.which() == 0) {
					fn(&boost::get<taxonomy::point3>(l->start));
				}
				if (l->end.which() == 0) {
					fn(&boost::get<taxonomy::point3>(l->end));
				}
			}
		}
	}

	taxonomy::collection* flatten(const taxonomy::collection* deep);

	template <typename Fn>
	bool apply_predicate_to_collection(taxonomy::item* i, Fn fn) {
		if (i->kind() == taxonomy::COLLECTION) {
			auto c = (taxonomy::collection*) i;
			for (auto& child : c->children) {
				if (apply_predicate_to_collection(child, fn)) {
					return true;
				}
			}
		} else {
			return fn(i);
		}
	}

	// @nb traverses nested collections
	template <typename Fn>
	taxonomy::collection* filter(taxonomy::collection* collection, Fn fn) {
		auto filtered = new taxonomy::collection;
		for (auto& child : collection->children) {
			if (apply_predicate_to_collection(child, fn)) {
				filtered->children.push_back(child->clone());
			}
		}
		if (filtered->children.empty()) {
			delete filtered;
			return nullptr;
		}
		return filtered;
	}

	// @nb traverses nested collections
	template <typename Fn>
	taxonomy::collection* filter_in_place(taxonomy::collection* collection, Fn fn) {
		for (auto it = --collection->children.end(); it >= collection->children.begin(); --it) {
			if (!apply_predicate_to_collection(*it, fn)) {
				delete *it;
				collection->children.erase(it);
			}
		}
		return collection;
	}

	taxonomy::solid* create_box(double dx, double dy, double dz);
	taxonomy::solid* create_box(double x, double y, double z, double dx, double dy, double dz);

	struct layerset_information {
		std::vector<double> thicknesses;
		std::vector<ifcopenshell::geometry::taxonomy::item*> layers;
		std::vector<ifcopenshell::geometry::taxonomy::style> styles;
	};

	enum connection_type {
		ATPATH,
		ATSTART,
		ATEND,
		NOTDEFINED
	};

	typedef std::tuple<connection_type, connection_type, IfcUtil::IfcBaseEntity*> endpoint_connection;
}

}

#endif