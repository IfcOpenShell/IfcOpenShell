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

#ifndef IFCSHAPELIST_H
#define IFCSHAPELIST_H

#include "../ifcgeom/IfcGeomRenderStyles.h"
#include "../ifcgeom/ConversionSettings.h"
#include "../ifcgeom/taxonomy.h"

#include <memory>
#include <vector>

namespace IfcGeom {	

	namespace Representation {
		class IFC_GEOM_API Triangulation;
	}

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

	class IFC_GEOM_API OpaqueNumber {
	public:
		virtual double to_double() const = 0;
		virtual std::string to_string() const = 0;

		virtual ~OpaqueNumber() {}

		virtual OpaqueNumber* operator+(OpaqueNumber* other) const = 0;
		virtual OpaqueNumber* operator-(OpaqueNumber* other) const = 0;
		virtual OpaqueNumber* operator*(OpaqueNumber* other) const = 0;
		virtual OpaqueNumber* operator/(OpaqueNumber* other) const = 0;
		virtual bool operator==(OpaqueNumber* other) const = 0;
		virtual bool operator<(OpaqueNumber* other) const = 0;
		virtual OpaqueNumber* operator-() const = 0;
		virtual OpaqueNumber* clone() const = 0;
	};

	// @todo this can simply be a template class, to remove the need for the NumberEpeck in CGAL kernel.
	class IFC_GEOM_API NumberNativeDouble : public OpaqueNumber {
	private:
		double value_;

		template <double (*Fn)(double, double)>
		OpaqueNumber* binary_op(OpaqueNumber* other) const {
			auto nnd = dynamic_cast<NumberNativeDouble*>(other);
			if (nnd) {
				return new NumberNativeDouble(Fn(value_, nnd->value_));
			} else {
				return nullptr;
			}
		}

		template <bool(*Fn)(double, double)>
		bool binary_op_bool(OpaqueNumber* other) const {
			auto nnd = dynamic_cast<NumberNativeDouble*>(other);
			if (nnd) {
				return Fn(value_, nnd->value_);
			} else {
				return false;
			}
		}

		template <double(*Fn)(double)>
		OpaqueNumber* unary_op() const {
			return new NumberNativeDouble(Fn(value_));
		}
	public:
		NumberNativeDouble(double v)
			: value_(v) {}

		virtual double to_double() const {
			return value_;
		}

		virtual std::string to_string() const;

		virtual OpaqueNumber* operator+(OpaqueNumber* other) const {
			return binary_op<add_<double>>(other);
		}
		virtual OpaqueNumber* operator-(OpaqueNumber* other) const {
			return binary_op<subtract_<double>>(other);
		}
		virtual OpaqueNumber* operator*(OpaqueNumber* other) const {
			return binary_op<multiply_<double>>(other);
		}
		virtual OpaqueNumber* operator/(OpaqueNumber* other) const {
			return binary_op<divide_<double>>(other);
		}
		virtual bool operator==(OpaqueNumber* other) const {
			return binary_op_bool<equals_<double>>(other);
		}
		virtual bool operator<(OpaqueNumber* other) const {
			return binary_op_bool<less_than_<double>>(other);
		}
		virtual OpaqueNumber* operator-() const {
			return unary_op<negate_<double>>();
		}
		virtual OpaqueNumber* clone() const {
			return new NumberNativeDouble(value_);
		}
	};

	template <size_t N>
	struct IFC_GEOM_API OpaqueCoordinate {
	private:
		std::array<OpaqueNumber*, N> values;

		static void copy_(std::array<OpaqueNumber*, N>& dest, const std::array<OpaqueNumber*, N>& src) {
			for (size_t i = 0; i < N; ++i) {
				dest[i] = (src[i] != nullptr) ? src[i]->clone() : nullptr;
			}
		}
	public:
		template <typename... Args>
		OpaqueCoordinate(Args... args) {
			static_assert(sizeof...(args) == N, "Incorrect number of arguments provided");
			init_<0>(args...);
		}

		OpaqueCoordinate() {
			for (auto it = values.begin(); it != values.end(); ++it) {
				*it = nullptr;
			}
		}

		OpaqueCoordinate(const OpaqueCoordinate& other) {
			copy_(values, other.values);
		}

		OpaqueCoordinate& operator=(const OpaqueCoordinate& other) {
			if (this != &other) {
				copy_(values, other.values);
			}
			return *this;
		}

		~OpaqueCoordinate() {
			for (auto it = values.begin(); it != values.end(); ++it) {
				delete *it;
			}
		}

		OpaqueNumber* get(size_t i) const {
			if (i >= N) {
				return nullptr;
			}
			return values[i];
		}

		void set(size_t i, OpaqueNumber* n) {
			if (i < N) {
				values[i] = n->clone();
			}
		}
	private:
		template <size_t Index, typename... Args>
		void init_(OpaqueNumber* value, Args... args) {
			values[Index] = value;
			if constexpr (Index + 1 < N) {
				init_<Index + 1>(args...);
			}
		}
	};

	class IFC_GEOM_API ConversionResultShape {
	public:
		virtual void Triangulate(ifcopenshell::geometry::Settings settings, const ifcopenshell::geometry::taxonomy::matrix4& place, Representation::Triangulation* t, int item_id, int surface_style_id) const = 0;
		IfcGeom::Representation::Triangulation* Triangulate(const ifcopenshell::geometry::Settings& settings) const;
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
		
		virtual OpaqueNumber* length() = 0;
		virtual OpaqueNumber* area() = 0;
		virtual OpaqueNumber* volume() = 0;

		virtual OpaqueCoordinate<3> position() = 0;
		virtual OpaqueCoordinate<3> axis() = 0;
		virtual OpaqueCoordinate<4> plane_equation() = 0;

		virtual std::vector<ConversionResultShape*> convex_decomposition() = 0;
		virtual ConversionResultShape* halfspaces() = 0;
		virtual ConversionResultShape* box() = 0;
		virtual ConversionResultShape* solid() = 0;

		virtual std::vector<ConversionResultShape*> vertices() = 0;
		virtual std::vector<ConversionResultShape*> edges() = 0;
		virtual std::vector<ConversionResultShape*> facets() = 0;

		virtual ConversionResultShape* add(ConversionResultShape*) = 0;
		virtual ConversionResultShape* subtract(ConversionResultShape*) = 0;
		virtual ConversionResultShape* intersect(ConversionResultShape*) = 0;

		virtual void map(OpaqueCoordinate<4>& from, OpaqueCoordinate<4>& to) = 0;
		virtual void map(const std::vector<OpaqueCoordinate<4>>& from, const std::vector<OpaqueCoordinate<4>>& to) = 0;
		virtual ConversionResultShape* moved(ifcopenshell::geometry::taxonomy::matrix4::ptr) const = 0;

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
	};

	typedef std::vector<ConversionResult> ConversionResults;


	namespace util {
		// @todo this is now moved to occt kernel, do we need something similar in cgal?
		// bool flatten_shape_list(const IfcGeom::ConversionResults& shapes, TopoDS_Shape& result, bool fuse, double tol);
	}
}
#endif
