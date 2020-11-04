#ifndef TAXONOMY_H
#define TAXONOMY_H

#include "../ifcparse/IfcBaseClass.h"

#include <boost/variant.hpp>

#include <Eigen/Dense>

#include <map>
#include <string>
#include <tuple>
#include <exception>

namespace ifcopenshell {

namespace geometry {

namespace taxonomy {

class topology_error : public std::runtime_error {
public:
	topology_error() : std::runtime_error("Generic topology error") {}
	topology_error(const char* const s) : std::runtime_error(s) {}
};

enum kinds { MATRIX4, POINT3, DIRECTION3, LINE, CIRCLE, ELLIPSE, BSPLINE_CURVE, PLANE, EDGE, LOOP, FACE, SHELL, EXTRUSION, NODE, COLLECTION, BOOLEAN_RESULT, COLOUR, STYLE };

struct item {
	const IfcUtil::IfcBaseClass* instance;

	boost::optional<bool> orientation;

    virtual item* clone() const = 0;
	virtual kinds kind() const = 0;
	virtual void print(std::ostream&, int indent=0) const = 0;
	virtual void reverse() { throw taxonomy::topology_error(); }

	item(const IfcUtil::IfcBaseClass* instance = nullptr) : instance(instance) {}

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
			this->components_ = new T;
		}
		return *this->components_;
	}
};

struct matrix4 : public item, public eigen_base<Eigen::Matrix4d> {
    enum tag_t {
        IDENTITY, AFFINE_WO_SCALE, AFFINE_W_UNIFORM_SCALE, AFFINE_W_NONUNIFORM_SCALE, OTHER
    };
    tag_t tag;

	matrix4() : eigen_base(), tag(IDENTITY) {}
	matrix4(const Eigen::Matrix4d& c) : eigen_base(c), tag(OTHER) {}
	matrix4(const Eigen::Vector3d& o, const Eigen::Vector3d& z, const Eigen::Vector3d& x) : tag(AFFINE_WO_SCALE) {
		auto X = x.normalized();
		auto Y = z.cross(x).normalized();
		auto Z = z.normalized();
		components_ = new Eigen::Matrix4d;
		(*components_) <<
			X(0), Y(0), Z(0), o(0),
			X(1), Y(1), Z(1), o(1),
			X(2), Y(2), Z(2), o(2),
			0, 0, 0, 1.;
	}

	bool is_identity() const {
		return !components_ || components_->isIdentity();
	}

	void print(std::ostream& o, int indent = 0) const {
		print_impl(o, "matrix4", indent);
	}

	virtual item* clone() const { return new matrix4(*this); }
	virtual kinds kind() const { return MATRIX4; }
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

	void print(std::ostream& o, int indent = 0) const {
		o << std::string(indent, ' ') << "bspline curve" << std::endl;
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
	// @todo how to express similarity between trimmed_curve and edge?
	virtual item* clone() const { return new edge(*this); }
	virtual kinds kind() const { return EDGE; }
};

struct collection : public geom_item {
	std::vector<item*> children;

	collection() {}
	collection(const collection& other) {
		std::transform(other.children.begin(), other.children.end(), std::back_inserter(children), std::mem_fun(&item::clone));
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
		o << std::string(indent, ' ') << "collection" << std::endl;
		if (!matrix.components_->isIdentity()) {
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

struct shell : public collection {
	boost::optional<bool> closed;

	virtual item* clone() const { return new shell(*this); }
	virtual kinds kind() const { return SHELL; }
};

struct surface : public geom_item {};

struct plane : public surface {
	virtual item* clone() const { return new plane(*this); }
	virtual kinds kind() const { return PLANE; }

	void print(std::ostream& o, int) const {
		o << "not implemented";
	}
};

struct face : public collection {
	item* basis;

	virtual item* clone() const { return new face(*this); }
	virtual kinds kind() const { return FACE; }
};

struct loop : public collection {
	boost::optional<bool> external, closed;

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

struct node : public collection {
	std::map<std::string, geom_item*> representations;

	virtual item* clone() const { return new node(*this); }
	virtual kinds kind() const { return NODE; }
};

struct boolean_result : public collection {
	enum operation_t {
		UNION, SUBTRACTION, INTERSECTION
	};

	virtual item* clone() const { return new boolean_result(*this); }
	virtual kinds kind() const { return BOOLEAN_RESULT; }
	operation_t operation;
};

namespace impl {
	typedef std::tuple<matrix4, point3, direction3, line, circle, ellipse, bspline_curve, plane, edge, loop, face, shell, extrusion, node, collection, boolean_result> KindsTuple;
	typedef std::tuple<line, circle, ellipse, bspline_curve, loop, edge> CurvesTuple;
}

struct type_by_kind {
	template <std::size_t N>
	using type = typename std::tuple_element<N, impl::KindsTuple>::type;

	static const size_t max = std::tuple_size< impl::KindsTuple>::value;
};

struct curves {
	template <std::size_t N>
	using type = typename std::tuple_element<N, impl::CurvesTuple>::type;

	static const size_t max = std::tuple_size< impl::CurvesTuple>::value;
};


}



}

}

#endif