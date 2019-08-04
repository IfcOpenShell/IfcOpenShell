#include <boost/variant.hpp>

#include <exception>

namespace ifcopenshell {

namespace geometry {

namespace taxonomy {

struct item {
    int instance_id;
    virtual item* clone() const = 0;

	item(int id) : instance_id(id) {}
};

struct matrix4 : public item {
    enum tag_t {
        IDENTITY, AFFINE_WO_SCALE, AFFINE_W_UNIFORM_SCALE, AFFINE_W_NONUNIFORM_SCALE, OTHER
    };
    tag_t tag;
    std::array<double, 16> components;
    matrix4() : components({1. ,0., 0., 0., 0., 1., 0., 0., 0., 0., 1. ,0., 0., 0., 0., 1.}), tag(IDENTITY) {}

	virtual item* clone() const { return new matrix4(*this); }
};

struct geom_item : public item {
    // geometry::style surface_style;
    matrix4 matrix;

	geom_item(int id) : item(id) {}
	geom_item(int id, matrix4 m) : item(id), matrix(m) {}
};

template <size_t N>
struct cartesian_base : public geom_item {
	std::array<double, N> components;

	cartesian_base(double x, double y, double z = 0.) : components{ {x, y, z} } {}
};

struct point3 : public cartesian_base<3> {
    virtual item* clone() const { return new point3(*this); }

	point3(double x, double y, double z = 0.) : cartesian_base(x, y, z) {}
};

struct direction3 : public cartesian_base<3> {
	virtual item* clone() const { return new direction3(*this); }

	direction3(double x, double y, double z = 0.) : cartesian_base(x, y, z) {}
};

struct line : public geom_item {
	virtual item* clone() const { return new line(*this); }
};

struct circle : public geom_item {
	virtual item* clone() const { return new circle(*this); }
};

struct ellipse : public geom_item {
	virtual item* clone() const { return new ellipse(*this); }
};

struct bspline : public geom_item {
	virtual item* clone() const { return new bspline(*this); }
};

typedef boost::variant<line, circle, ellipse, bspline> curve;

struct edge : public geom_item {
	boost::variant<point3, double> start, end;
	boost::optional<curve> basis;

	virtual item* clone() const { return new edge(*this); }
};

struct loop : public geom_item {
	std::vector<edge> edges;

	virtual item* clone() const { return new loop(*this); }
};

struct face : public geom_item {
	loop outer;
	std::vector<loop> inner;

	virtual item* clone() const { return new face(*this); }

	face(int id, loop o) : geom_item(id), outer(o) {}
	face(int id, loop o, std::vector<loop> i) : geom_item(id), outer(o), inner(i) {}
	face(int id, matrix4 m, loop o) : geom_item(id, m), outer(o) {}
	face(int id, matrix4 m, loop o, std::vector<loop> i) : geom_item(id, m), outer(o), inner(i) {}
};

struct sweep : public geom_item {
    face basis;

	sweep(int id, face b) : geom_item(id), basis(b) {}
	sweep(int id, matrix4 m, face b) : geom_item(id, m), basis(b) {}
};

struct extrusion : public sweep {
    direction3 direction;
    double depth;

	virtual item* clone() const { return new extrusion(*this); }
	extrusion(int id, matrix4 m, face basis, direction3 dir, double d) : sweep(id, m, basis), direction(dir), depth(d) {}
};

class topology_error : public std::runtime_error {

};

}



}

}
