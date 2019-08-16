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

enum kinds { MATRIX4, POINT3, DIRECTION3, LINE, CIRCLE, ELLIPSE, BSPLINE, EDGE, LOOP, FACE, EXTRUSION, NODE, COLOUR, STYLE };

struct item {
	const IfcUtil::IfcBaseClass* instance;
    virtual item* clone() const = 0;
	virtual kinds kind() const = 0;

	item(const IfcUtil::IfcBaseClass* instance = nullptr) : instance(instance) {}

	EIGEN_MAKE_ALIGNED_OPERATOR_NEW
};

struct matrix4 : public item {
    enum tag_t {
        IDENTITY, AFFINE_WO_SCALE, AFFINE_W_UNIFORM_SCALE, AFFINE_W_NONUNIFORM_SCALE, OTHER
    };
    tag_t tag;
	
	Eigen::Matrix4d components;

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

	point3(double x, double y, double z = 0.) : cartesian_base(x, y, z) {}
};

struct direction3 : public cartesian_base<3> {
	virtual item* clone() const { return new direction3(*this); }
	virtual kinds kind() const { return DIRECTION3; }

	direction3(double x, double y, double z = 0.) : cartesian_base(x, y, z) {}
};

struct line : public geom_item {
	virtual item* clone() const { return new line(*this); }
	virtual kinds kind() const { return LINE; }
};

struct circle : public geom_item {
	virtual item* clone() const { return new circle(*this); }
	virtual kinds kind() const { return CIRCLE; }
};

struct ellipse : public geom_item {
	virtual item* clone() const { return new ellipse(*this); }
	virtual kinds kind() const { return ELLIPSE; }
};

struct bspline : public geom_item {
	virtual item* clone() const { return new bspline(*this); }
	virtual kinds kind() const { return BSPLINE; }
};

typedef boost::variant<line, circle, ellipse, bspline> curve;

struct edge : public geom_item {
	boost::variant<point3, double> start, end;
	boost::optional<curve> basis;

	virtual item* clone() const { return new edge(*this); }
	virtual kinds kind() const { return EDGE; }
};

struct loop : public geom_item {
	std::vector<edge> edges;

	virtual item* clone() const { return new loop(*this); }
	virtual kinds kind() const { return LOOP; }
};

struct face : public geom_item {
	loop outer;
	std::vector<loop> inner;

	virtual item* clone() const { return new face(*this); }
	virtual kinds kind() const { return FACE; }

	face(const IfcUtil::IfcBaseClass* instance, loop o) : geom_item(instance), outer(o) {}
	face(const IfcUtil::IfcBaseClass* instance, loop o, std::vector<loop> i) : geom_item(instance), outer(o), inner(i) {}
	face(const IfcUtil::IfcBaseClass* instance, matrix4 m, loop o) : geom_item(instance, m), outer(o) {}
	face(const IfcUtil::IfcBaseClass* instance, matrix4 m, loop o, std::vector<loop> i) : geom_item(instance, m), outer(o), inner(i) {}
};

struct sweep : public geom_item {
    face basis;

	sweep(const IfcUtil::IfcBaseClass* instance, face b) : geom_item(instance), basis(b) {}
	sweep(const IfcUtil::IfcBaseClass* instance, matrix4 m, face b) : geom_item(instance, m), basis(b) {}
};

struct extrusion : public sweep {
    direction3 direction;
    double depth;

	virtual item* clone() const { return new extrusion(*this); }
	virtual kinds kind() const { return EXTRUSION; }

	extrusion(const IfcUtil::IfcBaseClass* instance, matrix4 m, face basis, direction3 dir, double d) : sweep(instance, m, basis), direction(dir), depth(d) {}
};

struct node : public geom_item {
	std::map<std::string, geom_item*> representations;
	std::vector<node*> children;

	virtual item* clone() const { return new node(*this); }
	virtual kinds kind() const { return NODE; }

	node(const IfcUtil::IfcBaseClass* instance, matrix4 m, const std::map<std::string, geom_item*>& representations, const std::vector<node*>& children) : geom_item(instance, m), representations(representations), children(children) {}
};

namespace impl {
	// enum kinds { MATRIX4, POINT3, DIRECTION3, LINE, CIRCLE, ELLIPSE, BSPLINE, EDGE, LOOP, FACE, EXTRUSION, NODE };
	typedef std::tuple<matrix4, point3, direction3, line, circle, ellipse, bspline, edge, loop, face, extrusion, node> KindsTuple;
}

struct type_by_kind {
	template <std::size_t N>
	using type = typename std::tuple_element<N, impl::KindsTuple>::type;

	static const size_t max = std::tuple_size< impl::KindsTuple>::value;
};

class topology_error : public std::runtime_error {
public:
	topology_error() : std::runtime_error("Generic topology error") {}
};

}



}

}

#endif