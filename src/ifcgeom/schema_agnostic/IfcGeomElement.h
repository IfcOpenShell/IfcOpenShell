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

#include "../../ifcparse/IfcGlobalId.h"
#include "../../ifcparse/Argument.h"

#include "../../ifcgeom/schema_agnostic/IfcGeomRepresentation.h"
#include "../../ifcgeom/schema_agnostic/IfcGeomIteratorSettings.h"

#include "ifc_geom_api.h"

namespace IfcGeom {

	template <typename P>
	class Matrix {
	private:
		std::vector<P> _data;
	public:
		Matrix(const ElementSettings& settings, const IfcGeom::ConversionResultPlacement* trsf) {
			// Convert the gp_Trsf into a 4x3 Matrix
			// Note that in case the CONVERT_BACK_UNITS setting is enabled
			// the translation component of the matrix needs to be divided
			// by the magnitude of the IFC model length unit because
			// internally in IfcOpenShell everything is measured in meters.
			for(int i = 1; i < 5; ++i) {
				for (int j = 1; j < 4; ++j) {
					const double trsf_value = (trsf == nullptr)
						? (i == j ? 1. : 0.)
						: trsf->Value(j,i);
					const double matrix_value = (i == 4 && settings.get(IteratorSettings::CONVERT_BACK_UNITS))
						? trsf_value / settings.unit_magnitude()
						: trsf_value;
					_data.push_back(static_cast<P>(matrix_value));
				}
			}
		}
		const std::vector<P>& data() const { return _data; }
	};

	template <typename P>
	class Transformation {
	private:
		ElementSettings settings_;
		ConversionResultPlacement* trsf_;
		Matrix<P> matrix_;
	public:
		Transformation(const ElementSettings& settings, const IfcGeom::ConversionResultPlacement* trsf)
			: settings_(settings)
			, trsf_(trsf ? trsf->clone() : nullptr)
			, matrix_(settings, trsf) 
		{}
		const IfcGeom::ConversionResultPlacement* data() const { return trsf_; }
		const Matrix<P>& matrix() const { return matrix_; }

		Transformation inverted() const {
			return Transformation(settings_, trsf_->inverted());
		}

		Transformation multiplied(const Transformation& other) const {
			return Transformation(settings_, trsf_->multiplied(other.data()));
		}
	};

	template <typename P = double, typename PP = P>
	class Element {
	private:
		int _id;
		int _parent_id;
		std::string _name;
		std::string _type;
		std::string _guid;
		std::string _context;
		std::string _unique_id;
		Transformation<PP> _transformation;
        IfcUtil::IfcBaseEntity* product_;
		std::vector<const IfcGeom::Element<P, PP>*> _parents;
	public:

		friend bool operator == (const Element<P, PP> & element1, const Element<P, PP> & element2) {
			return element1.id() == element2.id();
		}

		// Use the id to compare, or the elevation is the elements are IfcBuildingStoreys and the elevation is set
		friend bool operator < (const Element<P, PP> & element1, const Element<P, PP> & element2) {
			if (element1.type() == "IfcBuildingStorey" && element2.type() == "IfcBuildingStorey") {
				size_t attr_index = element1.product()->declaration().attribute_index("Elevation");
				Argument* elev_attr1 = element1.product()->data().getArgument(attr_index);
				Argument* elev_attr2 = element2.product()->data().getArgument(attr_index);

				if (!elev_attr1->isNull() && !elev_attr2->isNull()) {
					double elev1 = *elev_attr1;
					double elev2 = *elev_attr2;

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
		const std::string& context() const { return _context; }
		const std::string& unique_id() const { return _unique_id; }
		const Transformation<PP>& transformation() const { return _transformation; }
        IfcUtil::IfcBaseEntity* product() const { return product_; }
		const std::vector<const IfcGeom::Element<P, PP>*> parents() const { return _parents; }
		void SetParents(std::vector<const IfcGeom::Element<P, PP>*> newparents) { _parents = newparents; }

		Element(const ElementSettings& settings, int id, int parent_id, const std::string& name, const std::string& type,
            const std::string& guid, const std::string& context, const IfcGeom::ConversionResultPlacement* trsf, IfcUtil::IfcBaseEntity* product)
			: _id(id), _parent_id(parent_id), _name(name), _type(type), _guid(guid), _context(context), _transformation(settings, trsf)
            , product_(product)
		{ 
			std::ostringstream oss;

			if (type == "IfcProject") {
				oss << "project";
			} else {
				try {
					oss << "product-" << IfcParse::IfcGlobalId(guid).formatted();
				} catch (const std::exception& e) {
					oss << "product";
					Logger::Error(e);
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
		virtual ~Element() {}
	};

	template <typename P = double, typename PP = P>
	class NativeElement : public Element<P, PP> {
	private:
		boost::shared_ptr<Representation::BRep> _geometry;
	public:
		const boost::shared_ptr<Representation::BRep>& geometry_pointer() const { return _geometry; }
		const Representation::BRep& geometry() const { return *_geometry; }
		NativeElement(int id, int parent_id, const std::string& name, const std::string& type, const std::string& guid,
            const std::string& context, const IfcGeom::ConversionResultPlacement* trsf, const boost::shared_ptr<Representation::BRep>& geometry,
			IfcUtil::IfcBaseEntity* product)
			: Element<P, PP>(geometry->settings() ,id, parent_id, name, type, guid, context, trsf, product)
			, _geometry(geometry)
		{}

		bool calculate_projected_surface_area(double& along_x, double& along_y, double& along_z) const {
			return geometry().calculate_projected_surface_area(this->transformation().data(), along_x, along_y, along_z);
		}
	private:
		NativeElement(const NativeElement& other);
		NativeElement& operator=(const NativeElement& other);		
	};

	template <typename P = double, typename PP = P>
	class TriangulationElement : public Element<P, PP> {
	private:
		boost::shared_ptr< Representation::Triangulation<P> > _geometry;
	public:
		const Representation::Triangulation<P>& geometry() const { return *_geometry; }
		const boost::shared_ptr< Representation::Triangulation<P> >& geometry_pointer() const { return _geometry; }
		TriangulationElement(const NativeElement<P, PP>& shape_model)
			: Element<P, PP>(shape_model)
			, _geometry(boost::shared_ptr<Representation::Triangulation<P> >(new Representation::Triangulation<P>(shape_model.geometry())))
		{}
		TriangulationElement(const Element<P, PP>& element, const boost::shared_ptr<Representation::Triangulation<P> >& geometry)
			: Element<P, PP>(element)
			, _geometry(geometry)
		{}
	private:
		TriangulationElement(const TriangulationElement& other);
		TriangulationElement& operator=(const TriangulationElement& other);
	};

	template <typename P = double, typename PP = P>
	class SerializedElement : public Element<P, PP> {
	private:
		Representation::Serialization* _geometry;
	public:
		const Representation::Serialization& geometry() const { return *_geometry; }
		SerializedElement(const NativeElement<P, PP>& shape_model)
			: Element<P, PP>(shape_model)
			, _geometry(new Representation::Serialization(shape_model.geometry()))
		{}
		virtual ~SerializedElement() {
			delete _geometry;
		}
	private:
		SerializedElement(const SerializedElement& other);
		SerializedElement& operator=(const SerializedElement& other);
	};
}

#endif
