#include <boost/variant.hpp>

namespace ifcopenshell {

namespace geometry {

namespace taxonomy {

struct item {
    int instance_id;
    virtual item* clone() const = 0;
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
};

template <size_t N>
struct cartesian_base : public item {
	std::array<double, N> components;
};

struct point3 : public cartesian_base<3> {
    virtual item* clone() const { return new point3(*this); }
};

struct direction3 : public cartesian_base<3> {
	virtual item* clone() const { return new direction3(*this); }
};

struct line : public item {
	virtual item* clone() const { return new line(*this); }
};

struct circle : public item {
	virtual item* clone() const { return new circle(*this); }
};

struct ellipse : public item {
	virtual item* clone() const { return new ellipse(*this); }
};

struct bspline : public item {
	virtual item* clone() const { return new bspline(*this); }
};

typedef boost::variant<line, circle, ellipse, bspline> curve;

struct edge : public item {
	boost::variant<point3, double> start, end;
	boost::optional<curve> basis;

	virtual item* clone() const { return new edge(*this); }
};

struct boundary : public item {
	std::vector<edge> edges;

	virtual item* clone() const { return new boundary(*this); }
};

struct face : public item {
	boundary outer;
	std::vector<boundary> inner;

	virtual item* clone() const { return new face(*this); }
};

struct sweep : public item {
    face basis;
};

struct extrusion : public sweep {
    direction3 direction;
    double depth;

	virtual item* clone() const { return new extrusion(*this); }
};

}

}

}
