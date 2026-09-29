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

#ifndef IFCGEOMELEMENT_H
#define IFCGEOMELEMENT_H

#include <string>
#include <algorithm>
#include <memory>

#include "../ifcparse/argument.h"
#include "../ifcparse/global_id.h"
#include "../ifcparse/logger.h"
#include "../ifcparse/instance_data.h"

#include "../ifcgeom/representation.h"
#include "../ifcgeom/ifc_geom_api.h"

namespace ifcopenshell::geom {

	class transformation {
	private:
		ifcopenshell::geom::settings settings_;
		ifcopenshell::geom::taxonomy::matrix4::ptr matrix_, matrix_orig_units_;
	public:
        transformation(const ifcopenshell::geom::settings& settings, const ifcopenshell::geom::taxonomy::matrix4::ptr& matrix)
            : settings_(settings), matrix_(matrix)
		{
            const bool convert = settings.get<ifcopenshell::geom::settings::ConvertBackUnits>().get();
            auto unit_magnitude = settings.get<ifcopenshell::geom::settings::LengthUnit>().get();
            if (matrix_ && convert && unit_magnitude != 1.0) {
				matrix_orig_units_ = ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::matrix4>(*matrix);
                // only multiple the translation components of the matrix with the unit magnitude, not the rotation/scaling components
                matrix_orig_units_->components().col(3).head<3>() /= unit_magnitude;
            } else {
                matrix_orig_units_ = nullptr;
			}
        }
		const ifcopenshell::geom::taxonomy::matrix4::ptr& data() const {
            if (matrix_orig_units_) {
				return matrix_orig_units_;
            }
			if (matrix_) {
				return matrix_;
			}
			static ifcopenshell::geom::taxonomy::matrix4::ptr iden = ifcopenshell::geom::taxonomy::make<ifcopenshell::geom::taxonomy::matrix4>();
			return iden;
		}
	};

	class element {
	private:
		int _id;
		int _parent_id;
		std::string _name;
		std::string _type;
		std::string _guid;
		std::string _context;
		std::string _unique_id;
		ifcopenshell::geom::transformation _transformation;
		const express::entity product_;
		std::vector<const ifcopenshell::geom::element*> _parents;
		std::vector<std::shared_ptr<const ifcopenshell::geom::element>> _parent_storage;

		friend class iterator;
		void set_parents(std::vector<std::unique_ptr<ifcopenshell::geom::element>>&& newparents) {
			_parents.clear();
			_parent_storage.clear();
			for (auto& parent : newparents) {
				_parents.push_back(parent.get());
				_parent_storage.emplace_back(std::move(parent));
			}
		}
	public:

		friend bool operator == (const element& element1, const element& element2) {
			return element1.id() == element2.id();
		}

		// Use the id to compare, or the elevation is the elements are IfcBuildingStoreys and the elevation is set
		friend bool operator < (const element& element1, const element& element2) {
			if (element1.type() == "IfcBuildingStorey" && element2.type() == "IfcBuildingStorey") {
				size_t attr_index = element1.product().declaration().as_entity()->attribute_index("Elevation");
				auto elev_attr1 = element1.product().get_attribute_value(attr_index);
				auto elev_attr2 = element2.product().get_attribute_value(attr_index);

				if (!elev_attr1.isNull() && !elev_attr2.isNull()) {
					double elev1 = elev_attr1;
					double elev2 = elev_attr2;

					return elev1 < elev2;
				}
			}

			return element1.id() < element2.id();
		}

		int id() const { return _id; }
		int parent_id() const { return _parent_id; }
		const std::string& name() const { return _name; }
		const std::string& type() const { return _type; }
		const std::string& guid() const { return _guid; }
		// Return the representation's identifier (e.g. "Body") if present, or it's context type (e.g. "Model").
		const std::string& context() const { return _context; }
		const std::string& unique_id() const { return _unique_id; }
		const ifcopenshell::geom::transformation& transformation() const { return _transformation; }
		const express::entity& product() const { return product_; }
		const std::vector<const ifcopenshell::geom::element*>& parents() const { return _parents; }
		void SetParents(std::vector<const ifcopenshell::geom::element*>& newparents) {
			_parent_storage.clear();
			_parents = newparents;
		}

		element(const ifcopenshell::geom::settings& settings, int id, int parent_id, const std::string& name, const std::string& type,
            const std::string& guid, const std::string& context, const ifcopenshell::geom::taxonomy::matrix4::ptr& trsf, const express::entity& product)
			: _id(id), _parent_id(parent_id), _name(name), _type(type), _guid(guid), _context(context), _transformation(settings, trsf)
            , product_(product)
		{
			std::ostringstream oss;

			if (type == "IfcProject") {
				oss << "project";
			} else {
				try {
					oss << "product-" << ifcopenshell::global_id(guid).formatted();
				} catch (const std::exception& e) {
					oss << "product";
					ifcopenshell::logger::root().error("GEO", 39, e);
				}
			}

			if (!_context.empty()) {
				std::string ctx = _context;
                boost::to_lower(ctx);
                boost::replace_all(ctx, " ", "-");
				oss << "-" << ctx;
			}

			_unique_id = oss.str();
		}
		virtual ~element() {}
	};

	class native_element : public element {
	private:
		std::shared_ptr<ifcopenshell::geom::native> _geometry;
	public:
		const std::shared_ptr<ifcopenshell::geom::native>& geometry_pointer() const { return _geometry; }
		const ifcopenshell::geom::native& geometry() const { return *_geometry; }
		native_element(int id, int parent_id, const std::string& name, const std::string& type, const std::string& guid,
            const std::string& context, const ifcopenshell::geom::taxonomy::matrix4::ptr& trsf, const std::shared_ptr<ifcopenshell::geom::native>& geometry,
			const express::entity& product)
			: element(geometry->settings(), id, parent_id, name, type, guid, context, trsf, product)
			, _geometry(geometry)
		{}

		bool calculate_projected_surface_area(double& along_x, double& along_y, double& along_z) const {
			return geometry().calculate_projected_surface_area(this->transformation().data(), along_x, along_y, along_z);
		}
		native_element(const native_element& other) = default;
	private:
		native_element& operator=(const native_element& other);
	};

	class triangulation_element : public element {
	private:
		std::shared_ptr< ifcopenshell::geom::triangulation > _geometry;
	public:
		const ifcopenshell::geom::triangulation& geometry() const { return *_geometry; }
		const std::shared_ptr< ifcopenshell::geom::triangulation>& geometry_pointer() const { return _geometry; }
		triangulation_element(const ifcopenshell::geom::native_element& shape_model)
			: element(shape_model)
			, _geometry(std::make_shared<ifcopenshell::geom::triangulation>(shape_model.geometry()))
		{}
		triangulation_element(const ifcopenshell::geom::element& source, const std::shared_ptr<ifcopenshell::geom::triangulation>& geometry)
			: element(source)
			, _geometry(geometry)
		{}
		triangulation_element(const triangulation_element& other) = default;
	private:
		triangulation_element& operator=(const triangulation_element& other);
	};

	class serialized_element : public element {
	private:
		std::shared_ptr<ifcopenshell::geom::serialization> _geometry;
	public:
		const ifcopenshell::geom::serialization& geometry() const { return *_geometry; }
		serialized_element(const native_element& shape_model)
			: element(shape_model)
			, _geometry(std::make_shared<ifcopenshell::geom::serialization>(shape_model.geometry()))
		{}
		serialized_element(const serialized_element& other) = default;
	private:
		serialized_element& operator=(const serialized_element& other);
	};
}

#endif
