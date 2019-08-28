#ifndef TAXONOMY_H
#define TAXONOMY_H

#include "../ifcparse/IfcBaseClass.h"

#include <boost/variant.hpp>

#include <Eigen/Dense>

#include <map>
#include <string>
#include <tuple>
#include <exception>
#include <cstdalign>

namespace ifcopenshell {

namespace geometry {

namespace taxonomy {

class topology_error : public std::runtime_error {
public:
	topology_error() : std::runtime_error("Generic topology error") {}
};

enum kinds { MATRIX4, POINT3, DIRECTION3, LINE, CIRCLE, ELLIPSE, BSPLINE_CURVE, EDGE, LOOP, FACE, SHELL, EXTRUSION, NODE, COLLECTION, COLOUR, STYLE };

struct item {
	const IfcUtil::IfcBaseClass* instance;
    virtual item* clone() const = 0;
	virtual kinds kind() const = 0;
	virtual void reverse() { throw taxonomy::topology_error(); }

	item(const IfcUtil::IfcBaseClass* instance = nullptr) : instance(instance) {}

	EIGEN_MAKE_ALIGNED_OPERATOR_NEW
};

struct matrix4 : public item {
    enum tag_t {
        IDENTITY, AFFINE_WO_SCALE, AFFINE_W_UNIFORM_SCALE, AFFINE_W_NONUNIFORM_SCALE, OTHER
    };
    tag_t tag;
	
	Eigen::Matrix4d components;

	matrix4(const Eigen::Matrix4d& c) : components(c), tag(OTHER) {}
    matrix4() : components(Eigen::Matrix4d::Identity()), tag(IDENTITY) {}

	virtual item* clone() const { return new matrix4(*this); }
	virtual kinds kind() const { return MATRIX4; }
};

struct colour : public item {
	Eigen::Vector3d components;

	virtual item* clone() const { return new colour(*this); }
	virtual kinds kind() const { return COLOUR; }

	colour() : components(Eigen::Vector3d::Zero()) {}
	colour(double r, double g, double b) { components << r, g, b; }

	const double& r() const { return components[0]; }
	const double& g() const { return components[1]; }
	const double& b() const { return components[2]; }
};

struct style : public item {
	// @todo this is not very efficient wrt alignment
	boost::optional<std::string> name;
	boost::optional<colour> diffuse;
	boost::optional<colour> specular;
	boost::optional<double> specularity, transparency;

	virtual item* clone() const { return new style(*this); }
	virtual kinds kind() const { return STYLE; }

	// @todo equality implementation based on values?
	bool operator==(const style& other) const { return instance == other.instance; }

	style() {}
	style(const std::string& name) : name(name) {}
};

struct geom_item : public item {
    style surface_style;
    matrix4 matrix;

	geom_item(const IfcUtil::IfcBaseClass* instance = nullptr) : item(instance) {}
	geom_item(const IfcUtil::IfcBaseClass* instance, matrix4 m) : item(instance), matrix(m) {}
	geom_item(matrix4 m) : matrix(m) {}
};

template <size_t N>
struct cartesian_base : public geom_item {
	Eigen::Vector3d components;

	cartesian_base() : components(Eigen::Vector3d::Zero()) {}
	cartesian_base(double x, double y, double z = 0.) { components << x, y, z; }
};

struct point3 : public cartesian_base<3> {
    virtual item* clone() const { return new point3(*this); }
	virtual kinds kind() const { return POINT3; }

	point3(double x = 0., double y = 0., double z = 0.) : cartesian_base(x, y, z) {}
};

struct direction3 : public cartesian_base<3> {
	virtual item* clone() const { return new direction3(*this); }
	virtual kinds kind() const { return DIRECTION3; }

	direction3(double x = 0., double y = 0., double z = 0.) : cartesian_base(x, y, z) {}
};

struct curve : public geom_item {};

struct line : public curve {
	point3 origin;
	direction3 direction;

	virtual item* clone() const { return new line(*this); }
	virtual kinds kind() const { return LINE; }
};

struct circle : public curve {
	point3 origin;
	direction3 x;
	direction3 z;
	double radius;

	virtual item* clone() const { return new circle(*this); }
	virtual kinds kind() const { return CIRCLE; }
};

struct ellipse : public circle {
	double radius2;

	virtual item* clone() const { return new ellipse(*this); }
	virtual kinds kind() const { return ELLIPSE; }
};

struct bspline_curve : public curve {
	virtual item* clone() const { return new bspline_curve(*this); }
	virtual kinds kind() const { return BSPLINE_CURVE; }
};

struct trimmed_curve : public curve {
	boost::variant<point3, double> start, end;
	// @todo somehow account for the fact that curve in IFC can be trimmed curve, polyline and composite curve as well.
	curve* basis;
	bool orientation;

	trimmed_curve() : basis(nullptr), orientation(true) {}
	
	virtual void reverse() {
		std::swap(start, end);
		orientation = !orientation;
	}
};

struct edge : public trimmed_curve {
	// @todo how to express similarity between trimmed_curve and edge?
	virtual item* clone() const { return new edge(*this); }
	virtual kinds kind() const { return EDGE; }
};

struct collection : public geom_item {
	std::vector<item*> children;

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
};

struct shell : public collection {
	boost::optional<bool> closed;

	virtual item* clone() const { return new shell(*this); }
	virtual kinds kind() const { return SHELL; }
};

struct face : public collection {
	virtual item* clone() const { return new face(*this); }
	virtual kinds kind() const { return FACE; }
};

struct loop : public collection {
	boost::optional<bool> external;

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
};

struct node : public geom_item {
	std::map<std::string, geom_item*> representations;
	std::vector<node*> children;

	virtual item* clone() const { return new node(*this); }
	virtual kinds kind() const { return NODE; }
};

namespace impl {
	typedef std::tuple<matrix4, point3, direction3, line, circle, ellipse, bspline_curve, edge, loop, face, shell, extrusion, node, collection> KindsTuple;
	typedef std::tuple<line, circle, ellipse, bspline_curve> CurvesTuple;
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