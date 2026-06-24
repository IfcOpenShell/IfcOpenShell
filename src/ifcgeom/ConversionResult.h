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

#include "../ifcgeom/IfcGeomRenderStyles.h"
#include "../ifcgeom/ConversionSettings.h"
#include "../ifcgeom/taxonomy.h"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <iomanip>
#include <limits>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <type_traits>
#include <typeinfo>
#include <utility>
#include <vector>
#include <unordered_map>

struct EdgeKey {
	int v1, v2;

	// These are not part of the hash or equality,
	// but retained to easily created a directed
	// graph of the original boundary edges. Since
	// the boundary edges are exactly those with
	// count=1 we don't need to worry about
	// conflicting original vertex indices.
	int ov1, ov2;

	EdgeKey(int a, int b)
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

	bool operator==(const EdgeKey& other) const {
		return v1 == other.v1 && v2 == other.v2;
	}
};

namespace std {
	template <>
	struct hash<EdgeKey> {
		std::size_t operator()(const EdgeKey& ek) const {
			return std::hash<int>()(ek.v1) ^ std::hash<int>()(ek.v2);
		}
	};
}

namespace IfcGeom {	

	namespace Representation {
		class IFC_GEOM_API Triangulation;
	}

	class IFC_GEOM_API OpaqueNumber {
	protected:
		struct NumberConcept {
			virtual ~NumberConcept() {}
			virtual double to_double() const = 0;
			virtual std::string to_string() const = 0;
			virtual std::shared_ptr<const NumberConcept> add(const NumberConcept& other) const = 0;
			virtual std::shared_ptr<const NumberConcept> subtract(const NumberConcept& other) const = 0;
			virtual std::shared_ptr<const NumberConcept> multiply(const NumberConcept& other) const = 0;
			virtual std::shared_ptr<const NumberConcept> divide(const NumberConcept& other) const = 0;
			virtual std::shared_ptr<const NumberConcept> negate() const = 0;
			virtual std::shared_ptr<const NumberConcept> from_double(double value) const = 0;
            virtual std::shared_ptr<const NumberConcept> from_int(int value) const = 0;
            virtual bool equals(const NumberConcept& other) const = 0;
			virtual bool less_than(const NumberConcept& other) const = 0;
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
		struct NumberModel : NumberConcept {
			T value;

			NumberModel(const T& v)
				: value(v) {}

			static const NumberModel& as_same(const NumberConcept& other) {
				auto same = dynamic_cast<const NumberModel*>(&other);
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

			virtual std::shared_ptr<const NumberConcept> add(const NumberConcept& other) const {
				return std::make_shared<NumberModel>(value + as_same(other).value);
			}

			virtual std::shared_ptr<const NumberConcept> subtract(const NumberConcept& other) const {
				return std::make_shared<NumberModel>(value - as_same(other).value);
			}

			virtual std::shared_ptr<const NumberConcept> multiply(const NumberConcept& other) const {
				return std::make_shared<NumberModel>(value * as_same(other).value);
			}

			virtual std::shared_ptr<const NumberConcept> divide(const NumberConcept& other) const {
				return std::make_shared<NumberModel>(value / as_same(other).value);
			}

			virtual std::shared_ptr<const NumberConcept> negate() const {
				return std::make_shared<NumberModel>(-value);
			}

			virtual std::shared_ptr<const NumberConcept> from_double(double v) const {
				return std::make_shared<NumberModel>(T(v));
			}

			virtual std::shared_ptr<const NumberConcept> from_int(int v) const {
                return std::make_shared<NumberModel>(T(v));
            }

			virtual bool equals(const NumberConcept& other) const {
				return value == as_same(other).value;
			}

			virtual bool less_than(const NumberConcept& other) const {
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
		std::shared_ptr<const NumberConcept> data_;

		const NumberConcept& data() const {
			if (!data_) {
				throw std::runtime_error("Empty opaque number");
			}
			return *data_;
		}

	protected:
		OpaqueNumber(std::shared_ptr<const NumberConcept> data)
			: data_(std::move(data)) {}

	public:
		OpaqueNumber() = default;
		virtual ~OpaqueNumber() = default;

#ifndef SWIG
		template <
			typename T,
			typename Decayed = std::decay_t<T>,
			typename = std::enable_if_t<!std::is_base_of<OpaqueNumber, Decayed>::value && !is_shared_ptr<Decayed>::value>>
		explicit OpaqueNumber(T&& value)
			: data_(std::make_shared<NumberModel<Decayed>>(std::forward<T>(value))) {}
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

		OpaqueNumber add(const OpaqueNumber& other) const {
			return OpaqueNumber(data().add(other.data()));
		}

		OpaqueNumber subtract(const OpaqueNumber& other) const {
			return OpaqueNumber(data().subtract(other.data()));
		}

		OpaqueNumber multiply(const OpaqueNumber& other) const {
			return OpaqueNumber(data().multiply(other.data()));
		}

		OpaqueNumber divide(const OpaqueNumber& other) const {
			return OpaqueNumber(data().divide(other.data()));
		}

		OpaqueNumber negated() const {
			return OpaqueNumber(data().negate());
		}

		OpaqueNumber abs() const {
            auto zero = data().from_int(0);
            return OpaqueNumber(data().less_than(*zero) ? data().negate() : *this);
        }

		OpaqueNumber same_type(double value) const {
			return OpaqueNumber(data().from_double(value));
		}

		OpaqueNumber same_type(int value) const {
            return OpaqueNumber(data().from_int(value));
        }

		bool equals(const OpaqueNumber& other) const {
			return data().equals(other.data());
		}

		bool less_than(const OpaqueNumber& other) const {
			return data().less_than(other.data());
		}

		OpaqueNumber operator+(const OpaqueNumber& other) const {
			return add(other);
		}

		OpaqueNumber operator-(const OpaqueNumber& other) const {
			return subtract(other);
		}

		OpaqueNumber operator*(const OpaqueNumber& other) const {
			return multiply(other);
		}

		OpaqueNumber operator/(const OpaqueNumber& other) const {
			return divide(other);
		}

		bool operator==(const OpaqueNumber& other) const {
			return equals(other);
		}

		bool operator<(const OpaqueNumber& other) const {
			return less_than(other);
		}

		OpaqueNumber operator-() const {
			return negated();
		}
	};

	template <size_t N>
	struct IFC_GEOM_API OpaqueCoordinate {
	private:
		std::array<OpaqueNumber, N> values_;

		static OpaqueNumber as_number(OpaqueNumber value) {
			return value;
		}

	public:
#ifndef SWIG
		template <typename... Args, typename = std::enable_if_t<sizeof...(Args) == N>>
		OpaqueCoordinate(Args&&... args) {
			init_<0>(std::forward<Args>(args)...);
		}
#endif

		OpaqueCoordinate() = default;

		std::size_t size() const {
			return N;
		}

		OpaqueNumber get(size_t i) const {
			if (i >= N) {
				return OpaqueNumber();
			}
			return values_[i];
		}

		double get_double(size_t i) const {
			return get(i).to_double();
		}

		void set(size_t i, const OpaqueNumber& n) {
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

		OpaqueCoordinate operator-() const {
			OpaqueCoordinate result;
			for (size_t i = 0; i < N; ++i) {
				result.values_[i] = values_[i].negated();
			}
			return result;
		}

		OpaqueCoordinate operator+(const OpaqueCoordinate& other) const {
			OpaqueCoordinate result;
			for (size_t i = 0; i < N; ++i) {
				result.values_[i] = values_[i].add(other.values_[i]);
			}
			return result;
		}

		OpaqueCoordinate operator-(const OpaqueCoordinate& other) const {
			OpaqueCoordinate result;
			for (size_t i = 0; i < N; ++i) {
				result.values_[i] = values_[i].subtract(other.values_[i]);
			}
			return result;
		}

		OpaqueCoordinate operator*(const OpaqueNumber& scalar) const {
			OpaqueCoordinate result;
			for (size_t i = 0; i < N; ++i) {
				result.values_[i] = values_[i].multiply(scalar);
			}
			return result;
		}

		OpaqueCoordinate operator/(const OpaqueNumber& scalar) const {
			OpaqueCoordinate result;
			for (size_t i = 0; i < N; ++i) {
				result.values_[i] = values_[i].divide(scalar);
			}
			return result;
		}

		OpaqueCoordinate scale(double scalar) const {
			return *this * values_[0].same_type(scalar);
		}

		OpaqueNumber dot(const OpaqueCoordinate& other) const {
			if constexpr (N == 0) {
				return OpaqueNumber(0.0);
			} else {
				OpaqueNumber result = values_[0].multiply(other.values_[0]);
				for (size_t i = 1; i < N; ++i) {
					result = result.add(values_[i].multiply(other.values_[i]));
				}
				return result;
			}
		}

		double norm() const {
			return std::sqrt(dot(*this).to_double());
		}

		OpaqueCoordinate normalized() const {
			const double length = norm();
			if (length == 0.0) {
				return *this;
			}
			return *this / values_[0].same_type(length);
		}

		OpaqueCoordinate normalized_by_max_abs() const {
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

	class IFC_GEOM_API ConversionResultShape {
	public:
        virtual std::string type() const = 0;

		virtual void Triangulate(ifcopenshell::geometry::Settings settings, const ifcopenshell::geometry::taxonomy::matrix4& place, Representation::Triangulation* t, int item_id, int surface_style_id, Logger& logger = Logger::Root()) const = 0;
		IfcGeom::Representation::Triangulation* Triangulate(const ifcopenshell::geometry::Settings& settings, Logger& logger = Logger::Root()) const;
		virtual void Serialize(const ifcopenshell::geometry::taxonomy::matrix4& place, std::string&) const = 0;
				
		virtual int surface_genus() const = 0;
		virtual bool is_manifold() const = 0;
		
		virtual int num_vertices() const = 0;
		virtual int num_edges() const = 0;
		virtual int num_faces() const = 0;
			
		// @todo choose one prototype
		virtual double bounding_box(void*&) const = 0;
		// @todo this must be something with a virtual dtor so that we can delete it.
		virtual std::pair<OpaqueCoordinate<3>, OpaqueCoordinate<3>> bounding_box() const = 0;
		virtual void set_box(void* b) = 0;
		
		virtual OpaqueNumber length() = 0;
		virtual OpaqueNumber area() = 0;
		virtual OpaqueNumber volume() = 0;

		virtual OpaqueCoordinate<3> position() = 0;
		virtual OpaqueCoordinate<3> axis() = 0;
		virtual OpaqueCoordinate<4> plane_equation() = 0;

		virtual std::vector<ConversionResultShape*> convex_decomposition() = 0;
		virtual ConversionResultShape* halfspaces() = 0;
		virtual ConversionResultShape* box() = 0;
		virtual ConversionResultShape* solid() = 0;
		virtual ConversionResultShape* wrap_in_compound() = 0;

		virtual std::vector<ConversionResultShape*> vertices() = 0;
		virtual std::vector<ConversionResultShape*> edges() = 0;
		virtual std::vector<ConversionResultShape*> facets() = 0;

		virtual ConversionResultShape* add(ConversionResultShape*) = 0;
		virtual ConversionResultShape* subtract(ConversionResultShape*) = 0;
		virtual ConversionResultShape* intersect(ConversionResultShape*) = 0;
		virtual ConversionResultShape* concat(ConversionResultShape*) = 0;

		virtual std::size_t map(OpaqueCoordinate<4>& from, OpaqueCoordinate<4>& to) = 0;
		virtual std::size_t map(const std::vector<OpaqueCoordinate<4>>& from, const std::vector<OpaqueCoordinate<4>>& to) = 0;
		virtual ConversionResultShape* moved(ifcopenshell::geometry::taxonomy::matrix4::ptr) const = 0;
		
		virtual bool surface_area_along_direction(double tol, const ifcopenshell::geometry::taxonomy::matrix4::ptr&, double& along_x, double& along_y, double& along_z) const = 0;

		virtual ~ConversionResultShape() {}
		
	};

	class IFC_GEOM_API ConversionResult {
	private:
		int id;
		ifcopenshell::geometry::taxonomy::matrix4::ptr placement_;
		std::shared_ptr<ConversionResultShape> shape_;
		ifcopenshell::geometry::taxonomy::style::ptr style_;
	public:
		ConversionResult(int id, ifcopenshell::geometry::taxonomy::matrix4::ptr placement, ConversionResultShape* shape, ifcopenshell::geometry::taxonomy::style::ptr style)
			: id(id), placement_(placement ? placement : ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::matrix4>()), shape_(shape), style_(style)
		{}
		ConversionResult(int id, ifcopenshell::geometry::taxonomy::matrix4::ptr placement, ConversionResultShape* shape)
			: id(id), placement_(placement ? placement : ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::matrix4>()), shape_(shape)
		{}
		ConversionResult(int id, ConversionResultShape* shape, ifcopenshell::geometry::taxonomy::style::ptr style)
			: id(id), placement_(ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::matrix4>()), shape_(shape), style_(style)
		{}
		ConversionResult(int id, ConversionResultShape* shape)
			: id(id), placement_(ifcopenshell::geometry::taxonomy::make<ifcopenshell::geometry::taxonomy::matrix4>()), shape_(shape)
		{}
		void append(ifcopenshell::geometry::taxonomy::matrix4::ptr trsf);
		void prepend(ifcopenshell::geometry::taxonomy::matrix4::ptr trsf);
		std::shared_ptr<ConversionResultShape> Shape() const { return shape_; }
		ifcopenshell::geometry::taxonomy::matrix4::ptr Placement() const { return placement_; }
		bool hasStyle() const { return !!style_; }
		const ifcopenshell::geometry::taxonomy::style& Style() const { return *style_; }
		ifcopenshell::geometry::taxonomy::style::ptr StylePtr() const { return style_; }
		void setStyle(ifcopenshell::geometry::taxonomy::style::ptr newStyle) { style_ = newStyle; }
		int ItemId() const { return id; }
		ConversionResultShape* apply_transform(double unit_scale = 1.) const {
			if (unit_scale != 1.) {
				auto m = ifcopenshell::geometry::taxonomy::matrix4::ptr(placement_->clone_());
				m->pre_multiply_scale(unit_scale);
				return shape_->moved(m);
			} else {
				return shape_->moved(placement_);
			}
		}
	};

	typedef std::vector<ConversionResult> ConversionResults;


	namespace util {
		// @todo this is now moved to occt kernel, do we need something similar in cgal?
		// bool flatten_shape_list(const IfcGeom::ConversionResults& shapes, TopoDS_Shape& result, bool fuse, double tol);

		// Function to find boundary loops from triangles
		template <typename NT>
		std::vector<std::vector<int>> find_boundary_loops(const std::vector<NT>& positions, const std::vector<std::tuple<int, int, int>>& triangles) {
			std::unordered_map<EdgeKey, int> edge_count;

			// Count how many triangles each edge belongs to
			for (const auto& triangle : triangles) {
				int v1, v2, v3;
				std::tie(v1, v2, v3) = triangle;

				edge_count[{v1, v2}]++;
				edge_count[{v2, v3}]++;
				edge_count[{v3, v1}]++;
			}

			// Boundary edges have count 1
			std::vector<EdgeKey> boundary_edges;
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
}

#endif
