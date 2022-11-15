#include "validation_utils.h"

double facet_area(const cgal_shape_t::Facet_handle& f) {
	auto p0 = f->facet_begin()->vertex()->point();
	auto p1 = f->facet_begin()->next()->vertex()->point();
	auto p2 = f->facet_begin()->next()->next()->vertex()->point();
	return std::sqrt(CGAL::to_double(CGAL::cross_product(p0 - p1, p2 - p1).squared_length()));
}

void dump_facet(const cgal_shape_t::Facet_handle& f) {
	auto p0 = f->facet_begin()->vertex()->point();
	auto p1 = f->facet_begin()->next()->vertex()->point();
	auto p2 = f->facet_begin()->next()->next()->vertex()->point();
	auto V = CGAL::cross_product(p0 - p1, p2 - p1);
	auto d = std::sqrt(CGAL::to_double(V.squared_length()));
	if (d > 1.e-20) {
		V /= d;
	}

	std::ostringstream oss;
	oss.precision(8);
	oss << "Facet with area " << facet_area(f) << " and normal ("
		<< CGAL::to_double(V.cartesian(0)) << " " << CGAL::to_double(V.cartesian(1)) << " "
		<< CGAL::to_double(V.cartesian(2)) << ")";

	auto osss = oss.str();
	std::wcout << osss.c_str() << std::endl;
}