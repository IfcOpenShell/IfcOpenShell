/********************************************************************************
 *                                                                              *
 * This file is part of IfcOpenShell.                                           *
 *                                                                              *
 * IfcOpenShell is free software: you can redistribute it and/or modify         *
 * it under the terms of the Lesser GNU General Public License as published by  *
 * the Free Software Foundation, either version 3.0 of the License, or          *
 * (at your option) any later version.                                          *
 *                                                                              *
 * IfcOpenShell is distributed in the hope that it will be useful,              *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
 * Lesser GNU General Public License for more details.                          *
 *                                                                              *
 * You should have received a copy of the Lesser GNU General Public License     *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.         *
 *                                                                              *
 ********************************************************************************/

#ifndef CONVERSIONRESULT_H
#define CONVERSIONRESULT_H

#include "../ifcgeom/render_styles.h"
#include "../ifcgeom/conversion_settings.h"
#include "../ifcgeom/taxonomy.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <iomanip>
#include <limits>
#include <memory>
#include <string_view>
#include <sstream>
#include <stdexcept>
#include <type_traits>
#include <typeinfo>
#include <utility>
#include <vector>
#include <unordered_map>

struct edge_key {
	int v1, v2;

	// These are not part of the hash or equality,
	// but retained to easily created a directed
	// graph of the original boundary edges. Since
	// the boundary edges are exactly those with
	// count=1 we don't need to worry about
	// conflicting original vertex indices.
	int ov1, ov2;

	edge_key(int a, int b)
		: ov1(a)
		, ov2(b)
	{
		if (a < b) {
			v1 = a;
			v2 = b;
		} else {
			v1 = b;
			v2 = a;
		}
	}

	bool operator==(const edge_key& other) const {
		return v1 == other.v1 && v2 == other.v2;
	}
};

#ifndef SWIG
namespace std {
	template <>
	struct hash<edge_key> {
		std::size_t operator()(const edge_key& ek) const {
			return std::hash<int>()(ek.v1) ^ std::hash<int>()(ek.v2);
		}
	};
}
#endif

namespace ifcopenshell::geom {

	class IFC_GEOM_API triangulation;

#ifndef SWIG
	template <typename T>
	constexpr T add_(T a, T b) {
		return a + b;
	}

	template <typename T>
	constexpr T subtract_(T a, T b) {
		return a - b;
	}

	template <typename T>
	constexpr T multiply_(T a, T b) {
		return a * b;
	}

	template <typename T>
	constexpr T divide_(T a, T b) {
		return a / b;
	}

	template <typename T>
	constexpr bool equals_(T a, T b) {
		return a == b;
	}

	template <typename T>
	constexpr bool less_than_(T a, T b) {
		return a < b;
	}

	template <typename T>
	constexpr T negate_(T a) {
		return -a;
	}
#endif

	class IFC_GEOM_API opaque_number {
	protected:
		struct number_concept {
			virtual ~number_concept() {}
			virtual double to_double() const = 0;
			virtual std::string to_string() const = 0;
			virtual std::shared_ptr<const number_concept> add(const number_concept& other) const = 0;
			virtual std::shared_ptr<const number_concept> subtract(const number_concept& other) const = 0;
			virtual std::shared_ptr<const number_concept> multiply(const number_concept& other) const = 0;
			virtual std::shared_ptr<const number_concept> divide(const number_concept& other) const = 0;
			virtual std::shared_ptr<const number_concept> negate() const = 0;
			virtual std::shared_ptr<const number_concept> from_double(double value) const = 0;
            virtual std::shared_ptr<const number_concept> from_int(int value) const = 0;
            virtual bool equals(const number_concept& other) const = 0;
			virtual bool less_than(const number_concept& other) const = 0;
			virtual const std::type_info& type() const = 0;
			virtual const void* value_ptr() const = 0;
		};

#ifndef SWIG
		template <typename T, typename = void>
		struct has_exact : std::false_type {};

		template <typename T>
		struct has_exact<T, std::void_t<decltype(std::declval<const T&>().exact())>> : std::true_type {};
#endif

		template <typename T>
		struct number_model : number_concept {
			T value;

			number_model(const T& v)
				: value(v) {}

			static const number_model& as_same(const number_concept& other) {
				auto same = dynamic_cast<const number_model*>(&other);
				if (same == nullptr) {
					throw std::runtime_error("Incompatible opaque number types");
				}
				return *same;
			}

			virtual double to_double() const {
				return static_cast<double>(value);
			}

			virtual std::string to_string() const {
				std::stringstream ss;
				if constexpr (has_exact<T>::value) {
					ss << value.exact();
				} else {
					if constexpr (std::is_floating_point<T>::value) {
						ss << std::setprecision(std::numeric_limits<T>::digits10 + 1);
					}
					ss << value;
				}
				return ss.str();
			}

			virtual std::shared_ptr<const number_concept> add(const number_concept& other) const {
				return std::make_shared<number_model>(value + as_same(other).value);
			}

			virtual std::shared_ptr<const number_concept> subtract(const number_concept& other) const {
				return std::make_shared<number_model>(value - as_same(other).value);
			}

			virtual std::shared_ptr<const number_concept> multiply(const number_concept& other) const {
				return std::make_shared<number_model>(value * as_same(other).value);
			}

			virtual std::shared_ptr<const number_concept> divide(const number_concept& other) const {
				return std::make_shared<number_model>(value / as_same(other).value);
			}

			virtual std::shared_ptr<const number_concept> negate() const {
				return std::make_shared<number_model>(-value);
			}

			virtual std::shared_ptr<const number_concept> from_double(double v) const {
				return std::make_shared<number_model>(T(v));
			}

			virtual std::shared_ptr<const number_concept> from_int(int v) const {
                return std::make_shared<number_model>(T(v));
            }

			virtual bool equals(const number_concept& other) const {
				return value == as_same(other).value;
			}

			virtual bool less_than(const number_concept& other) const {
				return value < as_same(other).value;
			}

			virtual const std::type_info& type() const {
				return typeid(T);
			}

			virtual const void* value_ptr() const {
				return &value;
			}
		};

		template <typename T>
		struct is_shared_ptr : std::false_type {};

		template <typename T>
		struct is_shared_ptr<std::shared_ptr<T>> : std::true_type {};

	private:
		std::shared_ptr<const number_concept> data_;

		const number_concept& data() const {
			if (!data_) {
				throw std::runtime_error("Empty opaque number");
			}
			return *data_;
		}

	protected:
		opaque_number(std::shared_ptr<const number_concept> data)
			: data_(std::move(data)) {}

	public:
		opaque_number() = default;
		virtual ~opaque_number() = default;

#ifndef SWIG
		template <
			typename T,
			typename Decayed = std::decay_t<T>,
			typename = std::enable_if_t<!std::is_base_of<opaque_number, Decayed>::value && !is_shared_ptr<Decayed>::value>>
		explicit opaque_number(T&& value)
			: data_(std::make_shared<number_model<Decayed>>(std::forward<T>(value))) {}
#endif

		double to_double() const {
			return data().to_double();
		}

		std::string to_string() const {
			return data().to_string();
		}

		bool empty() const {
			return !data_;
		}

		template <typename T>
		const T& value_as() const {
			if (data().type() != typeid(T)) {
				throw std::runtime_error("Unexpected opaque number type");
			}
			return *static_cast<const T*>(data().value_ptr());
		}

		opaque_number add(const opaque_number& other) const {
			return opaque_number(data().add(other.data()));
		}

		opaque_number subtract(const opaque_number& other) const {
			return opaque_number(data().subtract(other.data()));
		}

		opaque_number multiply(const opaque_number& other) const {
			return opaque_number(data().multiply(other.data()));
		}

		opaque_number divide(const opaque_number& other) const {
			return opaque_number(data().divide(other.data()));
		}

		opaque_number negated() const {
			return opaque_number(data().negate());
		}

		opaque_number abs() const {
            auto zero = data().from_int(0);
            return opaque_number(data().less_than(*zero) ? data().negate() : *this);
        }

		opaque_number same_type(double value) const {
			return opaque_number(data().from_double(value));
		}

		opaque_number same_type(int value) const {
            return opaque_number(data().from_int(value));
        }

		bool equals(const opaque_number& other) const {
			return data().equals(other.data());
		}

		bool less_than(const opaque_number& other) const {
			return data().less_than(other.data());
		}

		opaque_number operator+(const opaque_number& other) const {
			return add(other);
		}

		opaque_number operator-(const opaque_number& other) const {
			return subtract(other);
		}

		opaque_number operator*(const opaque_number& other) const {
			return multiply(other);
		}

		opaque_number operator/(const opaque_number& other) const {
			return divide(other);
		}

		bool operator==(const opaque_number& other) const {
			return equals(other);
		}

		bool operator<(const opaque_number& other) const {
			return less_than(other);
		}

		opaque_number operator-() const {
			return negated();
		}
	};
#ifndef SWIG
	template <size_t N>
	struct IFC_GEOM_API opaque_coordinate {
	private:
		std::array<opaque_number, N> values_;

		static opaque_number as_number(opaque_number value) {
			return value;
		}

	public:
#ifndef SWIG
		template <typename... Args, typename = std::enable_if_t<sizeof...(Args) == N>>
		opaque_coordinate(Args&&... args) {
			init_<0>(std::forward<Args>(args)...);
		}
#endif

		opaque_coordinate() = default;

		std::size_t size() const {
			return N;
		}

		opaque_number get(size_t i) const {
			if (i >= N) {
				return opaque_number();
			}
			return values_[i];
		}

		double get_double(size_t i) const {
			return get(i).to_double();
		}

		void set(size_t i, const opaque_number& n) {
			if (i < N) {
				values_[i] = n;
			}
		}

		std::vector<double> to_double() const {
			std::vector<double> result;
			result.reserve(N);
			for (const auto& value : values_) {
				result.push_back(value.to_double());
			}
			return result;
		}

		opaque_coordinate operator-() const {
			opaque_coordinate result;
			for (size_t i = 0; i < N; ++i) {
				result.values_[i] = values_[i].negated();
			}
			return result;
		}

		opaque_coordinate operator+(const opaque_coordinate& other) const {
			opaque_coordinate result;
			for (size_t i = 0; i < N; ++i) {
				result.values_[i] = values_[i].add(other.values_[i]);
			}
			return result;
		}

		opaque_coordinate operator-(const opaque_coordinate& other) const {
			opaque_coordinate result;
			for (size_t i = 0; i < N; ++i) {
				result.values_[i] = values_[i].subtract(other.values_[i]);
			}
			return result;
		}

		opaque_coordinate operator*(const opaque_number& scalar) const {
			opaque_coordinate result;
			for (size_t i = 0; i < N; ++i) {
				result.values_[i] = values_[i].multiply(scalar);
			}
			return result;
		}

		opaque_coordinate operator/(const opaque_number& scalar) const {
			opaque_coordinate result;
			for (size_t i = 0; i < N; ++i) {
				result.values_[i] = values_[i].divide(scalar);
			}
			return result;
		}

		opaque_coordinate scale(double scalar) const {
			return *this * values_[0].same_type(scalar);
		}

		opaque_number dot(const opaque_coordinate& other) const {
			if constexpr (N == 0) {
				return opaque_number(0.0);
			} else {
				opaque_number result = values_[0].multiply(other.values_[0]);
				for (size_t i = 1; i < N; ++i) {
					result = result.add(values_[i].multiply(other.values_[i]));
				}
				return result;
			}
		}

		double norm() const {
			return std::sqrt(dot(*this).to_double());
		}

		opaque_coordinate normalized() const {
			const double length = norm();
			if (length == 0.0) {
				return *this;
			}
			return *this / values_[0].same_type(length);
		}

		opaque_coordinate normalized_by_max_abs() const {
			double max_abs = 0.0;
			for (const auto& value : values_) {
				max_abs = (std::max)(max_abs, std::fabs(value.to_double()));
			}
			if (max_abs == 0.0) {
				return *this;
			}
			return *this / values_[0].same_type(max_abs);
		}

	private:
		template <size_t Index, typename Arg, typename... Args>
		void init_(Arg&& value, Args&&... args) {
			values_[Index] = as_number(std::forward<Arg>(value));
			if constexpr (Index + 1 < N) {
				init_<Index + 1>(std::forward<Args>(args)...);
			}
		}
	};
#else
	template <size_t N>
	struct IFC_GEOM_API opaque_coordinate {
		opaque_coordinate();
		opaque_coordinate(const opaque_coordinate& other);
		opaque_coordinate& operator=(const opaque_coordinate& other);
		~opaque_coordinate();
		std::size_t size() const;
		opaque_number get(size_t i) const;
		double get_double(size_t i) const;
		void set(size_t i, const opaque_number& n);
		std::vector<double> to_double() const;
	};
#endif

	class IFC_GEOM_API conversion_result_shape {
	public:
#ifdef SWIG
		virtual std::string backend_id() const = 0;
#else
		virtual std::string_view backend_id() const = 0;
#endif
		virtual void triangulate(ifcopenshell::geom::settings settings, const ifcopenshell::geom::taxonomy::matrix4& place, triangulation* t, int item_id, int surface_style_id, ifcopenshell::logger& logger = ifcopenshell::logger::root()) const = 0;
		ifcopenshell::geom::triangulation* triangulate(const ifcopenshell::geom::settings& settings, ifcopenshell::logger& logger = ifcopenshell::logger::root()) const;
		virtual void serialize(const ifcopenshell::geom::taxonomy::matrix4& place, std::string&) const = 0;

		virtual int surface_genus() const = 0;
		virtual bool is_manifold() const = 0;

		virtual int num_vertices() const = 0;
		virtual int num_edges() const = 0;
		virtual int num_faces() const = 0;

		// @todo choose one prototype
		virtual double bounding_box(void*&) const = 0;
		// @todo this must be something with a virtual dtor so that we can delete it.
		virtual std::pair<opaque_coordinate<3>, opaque_coordinate<3>> bounding_box() const = 0;
		virtual void set_box(void* b) = 0;

		virtual opaque_number length() = 0;
		virtual opaque_number area() = 0;
		virtual opaque_number volume() = 0;

		virtual opaque_coordinate<3> position() = 0;
		virtual opaque_coordinate<3> axis() = 0;
		virtual opaque_coordinate<4> plane_equation() = 0;

		virtual std::vector<conversion_result_shape*> convex_decomposition() = 0;
		virtual conversion_result_shape* halfspaces() = 0;
		virtual conversion_result_shape* box() = 0;
		virtual conversion_result_shape* solid() = 0;
		virtual conversion_result_shape* wrap_in_compound() = 0;

		virtual std::vector<conversion_result_shape*> vertices() = 0;
		virtual std::vector<conversion_result_shape*> edges() = 0;
		virtual std::vector<conversion_result_shape*> facets() = 0;

		virtual conversion_result_shape* add(conversion_result_shape*) = 0;
		virtual conversion_result_shape* subtract(conversion_result_shape*) = 0;
		virtual conversion_result_shape* intersect(conversion_result_shape*) = 0;
		virtual conversion_result_shape* concat(conversion_result_shape*) = 0;

		virtual std::size_t map(opaque_coordinate<4>& from, opaque_coordinate<4>& to) = 0;
		virtual std::size_t map(const std::vector<opaque_coordinate<4>>& from, const std::vector<opaque_coordinate<4>>& to) = 0;
		virtual conversion_result_shape* moved(ifcopenshell::geom::taxonomy::matrix4::ptr) const = 0;

		virtual bool surface_area_along_direction(double tol, const ifcopenshell::geom::taxonomy::matrix4::ptr&, double& along_x, double& along_y, double& along_z) const = 0;

		virtual ~conversion_result_shape() {}

	};

	class IFC_GEOM_API conversion_result {
	private:
		int id;
		ifcopenshell::geom::taxonomy::matrix4::ptr placement_;
		std::shared_ptr<conversion_result_shape> shape_;
		ifcopenshell::geom::taxonomy::style::ptr style_;
	public:
		conversion_result(int id, ifcopenshell::geom::taxonomy::matrix4::ptr placement, conversion_result_shape* shape, ifcopenshell::geom::taxonomy::style::ptr style)
			: id(id), placement_(placement ? placement : ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::matrix4>()), shape_(shape), style_(style)
		{}
		conversion_result(int id, ifcopenshell::geom::taxonomy::matrix4::ptr placement, conversion_result_shape* shape)
			: id(id), placement_(placement ? placement : ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::matrix4>()), shape_(shape)
		{}
		conversion_result(int id, conversion_result_shape* shape, ifcopenshell::geom::taxonomy::style::ptr style)
			: id(id), placement_(ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::matrix4>()), shape_(shape), style_(style)
		{}
		conversion_result(int id, conversion_result_shape* shape)
			: id(id), placement_(ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::matrix4>()), shape_(shape)
		{}
		void append(ifcopenshell::geom::taxonomy::matrix4::ptr trsf);
		void prepend(ifcopenshell::geom::taxonomy::matrix4::ptr trsf);
		std::shared_ptr<conversion_result_shape> shape() const { return shape_; }
		ifcopenshell::geom::taxonomy::matrix4::ptr placement() const { return placement_; }
		bool hasStyle() const { return !!style_; }
		const ifcopenshell::geom::taxonomy::style& style() const { return *style_; }
		ifcopenshell::geom::taxonomy::style::ptr style_ptr() const { return style_; }
		void setStyle(ifcopenshell::geom::taxonomy::style::ptr newStyle) { style_ = newStyle; }
		int ItemId() const { return id; }
		conversion_result_shape* apply_transform(double unit_scale = 1.) const {
			if (unit_scale != 1.) {
				auto m = ifcopenshell::geom::taxonomy::matrix4::ptr(placement_->clone_());
				m->pre_multiply_scale(unit_scale);
				return shape_->moved(m);
			} else {
				return shape_->moved(placement_);
			}
		}
	};

#ifndef SWIG
	namespace util {
		// @todo this is now moved to occt kernel, do we need something similar in cgal?
		// bool flatten_shape_list(const std::vector<ifcopenshell::geom::conversion_result>& shapes, TopoDS_Shape& result, bool fuse, double tol);

		// Function to find boundary loops from triangles
		template <typename NT>
		std::vector<std::vector<int>> find_boundary_loops(const std::vector<NT>& positions, const std::vector<std::tuple<int, int, int>>& triangles) {
			std::unordered_map<edge_key, int> edge_count;

			// Count how many triangles each edge belongs to
			for (const auto& triangle : triangles) {
				int v1, v2, v3;
				std::tie(v1, v2, v3) = triangle;

				edge_count[{v1, v2}]++;
				edge_count[{v2, v3}]++;
				edge_count[{v3, v1}]++;
			}

			// Boundary edges have count 1
			std::vector<edge_key> boundary_edges;
			for (auto& p : edge_count) {
				if (p.second == 1) {
					boundary_edges.push_back(p.first);
				}
			}

			// We retained original directed edges so we build
			// a mapping out of these directed edges.
			std::unordered_map<int, int> vertex_successors;
			for (const auto& e : boundary_edges) {
				vertex_successors[e.ov1] = e.ov2;
			}

			std::vector<std::vector<int>> loops;
			while (!vertex_successors.empty()) {
				loops.emplace_back();
				auto it = vertex_successors.begin();
				loops.back() = { it->first, it->second };
				vertex_successors.erase(it);

				int current = loops.back().back();
				while (!vertex_successors.empty() && current != loops.back().front()) {
					auto next = vertex_successors[current];
					if (loops.back().front() != next) {
						loops.back().push_back(next);
					}
					vertex_successors.erase(current);
					current = next;
				}
			}

			// Sort the loops by smallest x-coord of their constituent positions
			// In order to put the outermost loop in front
			if (loops.size() > 1) {
				std::vector<std::pair<NT, size_t>> min_xs;
				for (auto& l : loops) {
					NT min_x = std::numeric_limits<double>::infinity();
					for (auto& i : l) {
						const auto& x = positions[i * 3];
						if (x < min_x) {
							min_x = x;
						}
					}
					min_xs.push_back({ min_x, min_xs.size() });
				}
				std::sort(min_xs.begin(), min_xs.end());
				decltype(loops) loops_copy;
				for (auto& p : min_xs) {
					loops_copy.emplace_back(std::move(loops[p.second]));
				}
				std::swap(loops, loops_copy);
			}

			return loops;
		}
	}
#endif
}

#endif
