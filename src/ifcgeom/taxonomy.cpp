#include "../ifcparse/IfcLogger.h"
#include "taxonomy.h"
#include "profile_helper.h"
#include "piecewise_function_impl.h"

using namespace ifcopenshell::geometry::taxonomy;

namespace {
	bool compare(const trimmed_curve& a, const trimmed_curve& b);

	bool compare(const collection& a, const collection& b);

	bool compare(const loop& a, const loop& b);

	bool compare(const face& a, const face& b);

	bool compare(const shell& a, const shell& b);

	bool compare(const solid& a, const solid& b);

	bool compare(const loft& a, const loft& b);

	bool compare(const boolean_result& a, const boolean_result& b);

	template <typename T>
	bool compare(const eigen_base<T>& t, const eigen_base<T>& u) {
		if (t.components_ == nullptr && u.components_ == nullptr) {
			return false;
		}
		else if (t.components_ == nullptr && u.components_ != nullptr) {
			return true;
		}
		else if (t.components_ != nullptr && u.components_ == nullptr) {
			return false;
		}

		auto t_begin = t.components_->data();
		auto t_end = t.components_->data() + t.components_->size();

		auto u_begin = u.components_->data();
		auto u_end = u.components_->data() + u.components_->size();

		return std::lexicographical_compare(t_begin, t_end, u_begin, u_end);
	}

	bool compare(const line& a, const line& b) {
		return compare(*a.matrix, *b.matrix);
	}

	bool compare(const plane& a, const plane& b) {
		return compare(*a.matrix, *b.matrix);
	}

	bool compare(const circle& a, const circle& b) {
		if (a.radius == b.radius) {
			return compare(*a.matrix, *b.matrix);
		}
		return a.radius < b.radius;
	}

	bool compare(const ellipse& a, const ellipse& b) {
		if (a.radius == b.radius && a.radius2 == b.radius2) {
			return compare(*a.matrix, *b.matrix);
		}
		return
			std::tie(a.radius, a.radius2) <
			std::tie(b.radius, b.radius2);
	}

	bool compare(const bspline_curve&, const bspline_curve&) {
		throw std::runtime_error("not implemented");
	}

	template <typename T>
	typename std::enable_if<std::is_base_of<item, T>::value, int>::type less_to_order(const T& a, const T& b) {
		const bool a_lt_b = compare(a, b);
		const bool b_lt_a = compare(b, a);
		return a_lt_b ?
			-1 : (!b_lt_a ? 0 : 1);
	}

	template <typename T>
	typename std::enable_if<!std::is_base_of<item, T>::value, int>::type less_to_order(const T& a, const T& b) {
		const bool a_lt_b = a < b;
		const bool b_lt_a = b < a;
		return a_lt_b ?
			-1 : (!b_lt_a ? 0 : 1);
	}

	template <typename T>
	int less_to_order_optional(const boost::optional<T>& a, const boost::optional<T>& b) {
		if (a && b) {
			return less_to_order(*a, *b);
		}
		else if (!a && !b) {
			return 0;
		}
		else if (a) {
			return 1;
		}
		else {
			return -1;
		}
	}

	int compare(const boost::variant<boost::blank, point3::ptr, double>& a, const boost::variant<boost::blank, point3::ptr, double>& b) {
		bool a_lt_b, b_lt_a;
		if (a.which() == 0) {
			return 0;
		} else if (a.which() == 1) {
			a_lt_b = compare(*boost::get<point3::ptr>(a), *boost::get<point3::ptr>(b));
			b_lt_a = compare(*boost::get<point3::ptr>(b), *boost::get<point3::ptr>(a));
		} else {
			a_lt_b = std::less<double>()(boost::get<double>(a), boost::get<double>(b));
			b_lt_a = std::less<double>()(boost::get<double>(b), boost::get<double>(a));
		}
		return a_lt_b ?
			-1 : (!b_lt_a ? 0 : 1);
	}

	bool compare(const extrusion& a, const extrusion& b) {
		// @todo extrusions can also have non-identity matrices right? perhaps it's time
		//       for a dedicated transform node and not on the abstract geom_item.
		const int order[3] = {
			less_to_order(a.basis, b.basis),
			less_to_order(a.direction, b.direction),
			a.depth < b.depth ? -1 : (a.depth == b.depth ? 0 : 1)
		};
		auto it = std::find_if(std::begin(order), std::end(order), [](int x) { return x; });
		if (it == std::end(order)) return false;
		return *it == -1;
	}

	bool compare(const node&, const node&) {
		throw std::runtime_error("not implemented");
	}

	bool compare(const offset_curve&, const offset_curve&) {
		throw std::runtime_error("not implemented");
	}

	bool compare(const revolve&, const revolve&) {
		throw std::runtime_error("not implemented");
	}

	bool compare(const bspline_surface&, const bspline_surface&) {
		throw std::runtime_error("not implemented");
	}

	bool compare(const cylinder&, const cylinder&) {
		throw std::runtime_error("not implemented");
	}

	bool compare(const sphere&, const sphere&) {
		throw std::runtime_error("not implemented");
	}

	bool compare(const torus&, const torus&) {
		throw std::runtime_error("not implemented");
	}

	bool compare(const sweep_along_curve&, const sweep_along_curve&) {
		throw std::runtime_error("not implemented");
	}

	bool compare(const piecewise_function&, const piecewise_function&) {
		throw std::runtime_error("not implemented");
	}

	bool compare(const style& a, const style& b) {
		const int order[5] = {
			less_to_order(a.name, b.name),
			less_to_order(a.diffuse, b.diffuse),
			less_to_order(a.specular, b.specular),
			less_to_order(a.specularity, b.specularity),
			less_to_order(a.transparency, b.transparency)
		};
		auto it = std::find_if(std::begin(order), std::end(order), [](int x) { return x; });
		if (it == std::end(order)) return false;
		return *it == -1;
	}

	/* A compile-time for loop over the taxonomy kinds */
	template <size_t N>
	struct dispatch_comparison {
		static bool dispatch(const item* a, const item* b) {
			if (N == a->kind() && N == b->kind()) {
				auto A = static_cast<const type_by_kind::type<N>*>(a);
				auto B = static_cast<const type_by_kind::type<N>*>(b);
				return compare(*A, *B);
			}
			else {
				return dispatch_comparison<N + 1>::dispatch(a, b);
			}
		}
	};

	template <>
	struct dispatch_comparison<type_by_kind::max> {
		static bool dispatch(const item*, const item*) {
			return false;
		}
	};
}

bool ifcopenshell::geometry::taxonomy::less(item::const_ptr a, item::const_ptr b) {
	if (a == b) {
		return false;
	}

	int a_kind = a->kind();
	int b_kind = b->kind();

	if (a_kind != b_kind) {
		return a_kind < b_kind;
	}

#ifdef TAXONOMY_USE_SHARED_PTR
	return dispatch_comparison<0>::dispatch(a.get(), b.get());
#endif
}


namespace {
	bool compare(const trimmed_curve& a, const trimmed_curve& b) {
		int a_which_start = a.start.which();
		int a_which_end = a.end.which();
		int b_which_start = b.start.which();
		int b_which_end = b.end.which();
		if (std::tie(a.orientation, a_which_start, a_which_end) ==
			std::tie(b.orientation, b_which_start, b_which_end)) {

			int start_state = compare(a.start, b.start);

			if (start_state == 0) {

				int end_state = compare(a.end, b.end);

				if (end_state == 0) {

					int a_has_basis = !!a.basis;
					int b_has_basis = !!a.basis;

					if (a_has_basis == b_has_basis) {

						if (!a_has_basis) {
							// Finally, equality
							return false;
						}
						else {
							return less(a.basis, b.basis);
						}

					}
					else {
						return a_has_basis < b_has_basis;
					}

				}
				else {
					return end_state == -1;
				}

			}
			else {
				return start_state == -1;
			}

		}
		else {
			return
				std::tie(a.orientation, a_which_start, a_which_end) <
				std::tie(b.orientation, b_which_start, b_which_end);
		}
	}

	template <typename T>
	bool compare_collection(const collection_base<T>& a, const collection_base<T>& b) {
		if (a.children.size() == b.children.size()) {
			auto at = a.children.begin();
			auto bt = b.children.begin();
			for (; at != a.children.end(); ++at, ++bt) {
				const bool a_lt_b = less(*at, *bt);
				const bool b_lt_a = less(*bt, *at);
				if (!a_lt_b && !b_lt_a) {
					// Elements equal.
					continue;
				}
				return a_lt_b;
			}
			// Vectors equal, compare matrix (in case of mapped items).
			return compare(*a.matrix, *b.matrix);
		}
		else {
			return a.children.size() < b.children.size();
		}
	}

	bool compare(const loop& a, const loop& b) {
		return compare_collection<edge>(a, b);
	}

	bool compare(const face& a, const face& b) {
		return compare_collection<loop>(a, b);
	}

	bool compare(const shell& a, const shell& b) {
		return compare_collection<face>(a, b);
	}

	bool compare(const solid& a, const solid& b) {
		return compare_collection<shell>(a, b);
	}

	bool compare(const loft& a, const loft& b) {
		return compare_collection<face>(a, b);
	}

	bool compare(const collection& a, const collection& b) {
		return compare_collection<geom_item>(a, b);
	}

	bool compare(const boolean_result& a, const boolean_result& b) {
		return compare_collection<geom_item>(a, b);
	}
}

ifcopenshell::geometry::taxonomy::solid::ptr ifcopenshell::geometry::create_box(double dx, double dy, double dz) {
	return create_box(0., 0., 0., dx, dy, dz);
}

ifcopenshell::geometry::taxonomy::solid::ptr ifcopenshell::geometry::create_box(double x, double y, double z, double dx, double dy, double dz) {
	auto solid = make<taxonomy::solid>();
	auto shell = make<taxonomy::shell>();
	solid->children.push_back(shell);

	// x = 0
	{
		auto face = make<taxonomy::face>();
		auto loop = make<taxonomy::loop>();
		face->children.push_back(loop);
		loop->external = true;
		shell->children.push_back(face);

		std::array<taxonomy::point3::ptr, 4> points{
			taxonomy::make<taxonomy::point3>(x + 0, y + 0,  z + 0),
			taxonomy::make<taxonomy::point3>(x + 0, y + dy, z + 0),
			taxonomy::make<taxonomy::point3>(x + 0, y + dy, z + dz),
			taxonomy::make<taxonomy::point3>(x + 0, y + 0,  z + dz)
		};

		loop->children.push_back(make<taxonomy::edge>(points[0], points[1]));
		loop->children.push_back(make<taxonomy::edge>(points[1], points[2]));
		loop->children.push_back(make<taxonomy::edge>(points[2], points[3]));
		loop->children.push_back(make<taxonomy::edge>(points[3], points[0]));
	}

	// x = dx
	{
		auto face = make<taxonomy::face>();
		auto loop = make<taxonomy::loop>();
		face->children.push_back(loop);
		loop->external = true;
		shell->children.push_back(face);

		std::array<taxonomy::point3::ptr, 4> points{
			taxonomy::make<taxonomy::point3>(x + dx, y + 0,  z + 0),
			taxonomy::make<taxonomy::point3>(x + dx, y + 0,  z + dz),
			taxonomy::make<taxonomy::point3>(x + dx, y + dy, z + dz),
			taxonomy::make<taxonomy::point3>(x + dx, y + dy, z + 0)
		};

		loop->children.push_back(make<taxonomy::edge>(points[0], points[1]));
		loop->children.push_back(make<taxonomy::edge>(points[1], points[2]));
		loop->children.push_back(make<taxonomy::edge>(points[2], points[3]));
		loop->children.push_back(make<taxonomy::edge>(points[3], points[0]));
	}

	// y = 0
	{
		auto face = make<taxonomy::face>();
		auto loop = make<taxonomy::loop>();
		face->children.push_back(loop);
		loop->external = true;
		shell->children.push_back(face);

		std::array<taxonomy::point3::ptr, 4> points{
			taxonomy::make<taxonomy::point3>(x + 0,  y + 0, z + 0),
			taxonomy::make<taxonomy::point3>(x + 0,  y + 0, z + dz),
			taxonomy::make<taxonomy::point3>(x + dx, y + 0, z + dz),
			taxonomy::make<taxonomy::point3>(x + dx, y + 0, z + 0)
		};

		loop->children.push_back(make<taxonomy::edge>(points[0], points[1]));
		loop->children.push_back(make<taxonomy::edge>(points[1], points[2]));
		loop->children.push_back(make<taxonomy::edge>(points[2], points[3]));
		loop->children.push_back(make<taxonomy::edge>(points[3], points[0]));
	}

	// y = dy
	{
		auto face = make<taxonomy::face>();
		auto loop = make<taxonomy::loop>();
		face->children.push_back(loop);
		loop->external = true;
		shell->children.push_back(face);

		std::array<taxonomy::point3::ptr, 4> points{
			taxonomy::make<taxonomy::point3>(x + 0, y + dy, z + 0),
			taxonomy::make<taxonomy::point3>(x + dx, y + dy, z + 0),
			taxonomy::make<taxonomy::point3>(x + dx, y + dy, z + dz),
			taxonomy::make<taxonomy::point3>(x + 0, y + dy, z + dz)
		};

		loop->children.push_back(make<taxonomy::edge>(points[0], points[1]));
		loop->children.push_back(make<taxonomy::edge>(points[1], points[2]));
		loop->children.push_back(make<taxonomy::edge>(points[2], points[3]));
		loop->children.push_back(make<taxonomy::edge>(points[3], points[0]));
	}

	// z = 0
	{
		auto face = make<taxonomy::face>();
		auto loop = make<taxonomy::loop>();
		face->children.push_back(loop);
		loop->external = true;
		shell->children.push_back(face);

		std::array<taxonomy::point3::ptr, 4> points{
			taxonomy::make<taxonomy::point3>(x + 0, y + 0, z + 0),
			taxonomy::make<taxonomy::point3>(x + dx, y + 0, z + 0),
			taxonomy::make<taxonomy::point3>(x + dx, y + dy, z + 0),
			taxonomy::make<taxonomy::point3>(x + 0, y + dy, z + 0)
		};

		loop->children.push_back(make<taxonomy::edge>(points[0], points[1]));
		loop->children.push_back(make<taxonomy::edge>(points[1], points[2]));
		loop->children.push_back(make<taxonomy::edge>(points[2], points[3]));
		loop->children.push_back(make<taxonomy::edge>(points[3], points[0]));
	}

	// z = dz
	{
		auto face = make<taxonomy::face>();
		auto loop = make<taxonomy::loop>();
		face->children.push_back(loop);
		loop->external = true;
		shell->children.push_back(face);

		std::array<taxonomy::point3::ptr, 4> points{
			taxonomy::make<taxonomy::point3>(x + 0, y + 0, z + dz),
			taxonomy::make<taxonomy::point3>(x + 0, y + dy, z + dz),
			taxonomy::make<taxonomy::point3>(x + dx, y + dy, z + dz),
			taxonomy::make<taxonomy::point3>(x + dx, y + 0, z + dz)
		};

		loop->children.push_back(make<taxonomy::edge>(points[0], points[1]));
		loop->children.push_back(make<taxonomy::edge>(points[1], points[2]));
		loop->children.push_back(make<taxonomy::edge>(points[2], points[3]));
		loop->children.push_back(make<taxonomy::edge>(points[3], points[0]));
	}

	return solid;
}

///////////////////
piecewise_function::piecewise_function(double start, const spans_t& s, ifcopenshell::geometry::Settings* settings, const IfcUtil::IfcBaseInterface* instance) : implicit_item(instance) {
    impl_ = new piecewise_function_impl(start, s, settings);
}

piecewise_function::piecewise_function(double start, const std::vector<piecewise_function::ptr>& pwfs, ifcopenshell::geometry::Settings* settings, const IfcUtil::IfcBaseInterface* instance) : implicit_item(instance) {
    impl_ = new piecewise_function_impl(start, pwfs, settings);
};

piecewise_function::piecewise_function(const piecewise_function& other) : implicit_item(other) {
    impl_ = other.impl_->clone_();
}

piecewise_function::~piecewise_function() {
    delete impl_;
}

const piecewise_function::spans_t& piecewise_function::spans() const { return impl_->spans(); }
bool piecewise_function::is_empty() const { return impl_->is_empty(); }
double piecewise_function::start() const { return impl_->start(); }
double piecewise_function::end() const { return impl_->end(); }
double piecewise_function::length() const {   return impl_->length(); }

std::vector<double> piecewise_function::evaluation_points() const { return impl_->evaluation_points(); }
std::vector<double> piecewise_function::evaluation_points(double ustart, double uend, unsigned nsteps) const { return impl_->evaluation_points(ustart, uend, nsteps); }
item::ptr piecewise_function::evaluate() const { return impl_->evaluate(); }
item::ptr piecewise_function::evaluate(double ustart, double uend, unsigned nsteps) const { return impl_->evaluate(ustart, uend, nsteps); }
Eigen::Matrix4d piecewise_function::evaluate(double u) const { return impl_->evaluate(u); }

ifcopenshell::geometry::taxonomy::collection::ptr ifcopenshell::geometry::flatten(const taxonomy::collection::ptr& deep) {
	auto flat = make<taxonomy::collection>();
	ifcopenshell::geometry::visit<taxonomy::collection>(deep, [&flat](taxonomy::ptr i) {
		flat->children.push_back(taxonomy::cast<taxonomy::geom_item>(clone(i)));
		});
	return flat;
}

const std::string& ifcopenshell::geometry::taxonomy::kind_to_string(kinds k) {
	using namespace std::string_literals;

	static std::string values[] = {
		"matrix4"s, "point3"s, "direction3"s, "line"s, "circle"s, "ellipse"s, "bspline_curve"s, "offset_curve"s, "plane"s, "cylinder"s, "sphere"s, "torus"s, "bspline_surface"s, "edge"s, "loop"s, "face"s, "shell"s, "solid"s, "loft"s, "extrusion"s, "revolve"s, "sweep_along_curve"s, "node"s, "collection"s, "boolean_result"s, "piecewise_function"s, "colour"s, "style"s,
	};

	return values[k];
}

std::atomic_uint32_t item::counter_(0);

void ifcopenshell::geometry::taxonomy::item::print(std::ostream& o, int indent) const {
	o << std::string(indent, ' ') << kind_to_string(kind()) << std::endl;
}

void ifcopenshell::geometry::taxonomy::matrix4::print(std::ostream& o, int indent) const {
	print_impl(o, kind_to_string(kind()), indent);
}

void ifcopenshell::geometry::taxonomy::colour::print(std::ostream& o, int indent) const {
	print_impl(o, kind_to_string(kind()), indent);
}

void ifcopenshell::geometry::taxonomy::style::print(std::ostream& o, int indent) const {
	o << std::string(indent, ' ') << "style" << std::endl;
	o << std::string(indent, ' ') << "     " << "name " << (name) << std::endl;
	if (diffuse.components_) {
		o << std::string(indent, ' ') << "     " << "diffuse" << std::endl;
		diffuse.print(o, indent + 5 + 7);
	}
	if (specular.components_) {
		o << std::string(indent, ' ') << "     " << "specular" << std::endl;
		specular.print(o, indent + 5 + 8);
	}
	// @todo
}

void ifcopenshell::geometry::taxonomy::point3::print(std::ostream& o, int indent) const {
	print_impl(o, kind_to_string(kind()), indent);
}

void ifcopenshell::geometry::taxonomy::direction3::print(std::ostream& o, int indent) const {
	print_impl(o, kind_to_string(kind()), indent);
}

void ifcopenshell::geometry::taxonomy::line::print(std::ostream& o, int indent) const {
	print_impl(o, kind_to_string(kind()), indent);
}

void ifcopenshell::geometry::taxonomy::circle::print(std::ostream& o, int indent) const {
	print_impl(o, kind_to_string(kind()), indent);
	o << std::string(indent + 4, ' ') << "radius " << radius << std::endl;
}

void ifcopenshell::geometry::taxonomy::ellipse::print(std::ostream& o, int indent) const {
	print_impl(o, kind_to_string(kind()), indent);
	o << std::string(indent + 4, ' ') << "radii " << radius << " " << radius2 << std::endl;
}

void ifcopenshell::geometry::taxonomy::trimmed_curve::print(std::ostream& o, int indent) const {
	o << std::string(indent, ' ') << kind_to_string(kind());
	if (!this->orientation.get_value_or(true)) {
		o << " [R]";
	} else {
		o << " [ ]";
	}
	if (!this->curve_sense.get_value_or(true)) {
		o << " [R]";
	} else {
		o << " [ ]";
	}
	o << std::endl;
	if (basis) {
		basis->print(o, indent + 4);
	}

	const boost::variant<boost::blank, point3::ptr, double>* const start_end[2] = { &start, &end };
	for (int i = 0; i < 2; ++i) {
		o << std::string(indent + 4, ' ') << (i == 0 ? "start" : "end") << std::endl;
		if (start_end[i]->which() == 1) {
			boost::get<point3::ptr>(*start_end[i])->print(o, indent + 4);
		} else if (start_end[i]->which() == 2) {
			o << std::string(indent + 4, ' ') << "parameter " << boost::get<double>(*start_end[i]) << std::endl;
		}
	}

	if (this->instance) {
		std::ostringstream oss;
		this->instance->as<IfcUtil::IfcBaseClass>()->toString(oss);
		o << std::string(indent + 4, ' ') << oss.str() << std::endl;
	}
}

void ifcopenshell::geometry::taxonomy::extrusion::print(std::ostream& o, int indent) const {
	o << std::string(indent, ' ') << "extrusion " << depth << std::endl;
	direction->print(o, indent + 4);
	basis->print(o, indent + 4);
}
