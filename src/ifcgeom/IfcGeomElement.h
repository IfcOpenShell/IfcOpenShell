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

#include "../ifcgeom/IfcGeomRepresentation.h"
#include "../ifcgeom/IfcGeomIteratorSettings.h"


namespace IfcGeom {

	template <typename P>
	class Matrix {
	private:
		std::vector<P> _data;
	public:
		Matrix(const ElementSettings& settings, const gp_Trsf& trsf) {
			// Convert the gp_Trsf into a 4x3 Matrix
			// Note that in case the CONVERT_BACK_UNITS setting is enabled
			// the translation component of the matrix needs to be divided
			// by the magnitude of the IFC model length unit because
			// internally in IfcOpenShell everything is measured in meters.
			for(int i = 1; i < 5; ++i) {
				for (int j = 1; j < 4; ++j) {
					const double trsf_value = trsf.Value(j,i);
					const double matrix_value = i == 4 && settings.convert_back_units()
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
		gp_Trsf trsf;
		Matrix<P> _matrix;
	public:
		Transformation(const ElementSettings& settings, const gp_Trsf& trsf)
			: trsf(trsf)
			, _matrix(settings, trsf) 
		{}
		const gp_Trsf& data() const { return trsf; }
		const Matrix<P>& matrix() const { return _matrix; }
	};

	template <typename P>
	class Element {
	private:
		int _id;
		int _parent_id;
		std::string _name;
		std::string _type;
		std::string _guid;
		Transformation<P> _transformation;
	public:
		int id() const { return _id; }
		int parent_id() const { return _parent_id; }
		const std::string& name() const { return _name; }
		const std::string& type() const { return _type; }
		const std::string& guid() const { return _guid; }
		const Transformation<P>& transformation() const { return _transformation; }
		Element(const ElementSettings& settings, int id, int parent_id, const std::string& name, const std::string& type, const std::string& guid, const gp_Trsf& trsf)
			: _id(id), _parent_id(parent_id), _name(name), _type(type), _guid(guid), _transformation(settings, trsf)
		{}
		virtual ~Element() {}
	};

	template <typename P>
	class ShapeModelElement : public Element<P> {
	private:
		Representation::BRep* _geometry;
	public:
		const Representation::BRep& geometry() const { return *_geometry; }
		ShapeModelElement(int id, int parent_id, const std::string& name, const std::string& type, const std::string& guid, const gp_Trsf& trsf, Representation::BRep* geometry)
			: Element(geometry->settings(),id,parent_id,name,type,guid,trsf)
			, _geometry(geometry)
		{}
		virtual ~ShapeModelElement() {
			delete _geometry;
		}
	private:
		ShapeModelElement(const ShapeModelElement& other);
		ShapeModelElement& operator=(const ShapeModelElement& other);		
	};

	template <typename P>
	class TriangulationElement : public Element<P> {
	private:
		Representation::Triangulation<P>* _geometry;
	public:
		const Representation::Triangulation<P>& geometry() const { return *_geometry; }
		TriangulationElement(const ShapeModelElement<P>& shape_model)
			: Element<P>(shape_model)
			, _geometry(new Representation::Triangulation<P>(shape_model.geometry()))
		{}
		virtual ~TriangulationElement() {
			delete _geometry;
		}
	private:
		TriangulationElement(const TriangulationElement& other);
		TriangulationElement& operator=(const TriangulationElement& other);
	};

	template <typename P>
	class SerializedElement : public Element<P> {
	private:
		Representation::Serialization* _geometry;
	public:
		const Representation::Serialization& geometry() const { return *_geometry; }
		SerializedElement(const ShapeModelElement<P>& shape_model)
			: Element<P>(shape_model)
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