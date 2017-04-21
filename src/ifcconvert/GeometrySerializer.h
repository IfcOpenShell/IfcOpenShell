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

#ifndef GEOMETRYSERIALIZER_H
#define GEOMETRYSERIALIZER_H

#ifdef IFCCONVERT_DOUBLE_PRECISION
typedef double real_t;
#else
typedef float real_t;
#endif

#include "../ifcconvert/Serializer.h"
#include "../ifcgeom/IfcGeomIterator.h"

class SerializerSettings : public IfcGeom::IteratorSettings
{
public:
    enum Setting
    {
        /// Use entity names instead of unique IDs for naming elements.
        /// Applicable for OBJ, DAE, and SVG output.
        USE_ELEMENT_NAMES = 1 << (IfcGeom::IteratorSettings::NUM_SETTINGS + 1),
        /// Use entity GUIDs instead of unique IDs for naming elements.
        /// Applicable for OBJ, DAE, and SVG output.
        USE_ELEMENT_GUIDS = 1 << (IfcGeom::IteratorSettings::NUM_SETTINGS + 2),
        /// Use material names instead of unique IDs for naming materials.
        /// Applicable for OBJ and DAE output.
        USE_MATERIAL_NAMES = 1 << (IfcGeom::IteratorSettings::NUM_SETTINGS + 3),
		/// Use element types instead of unique IDs for naming elements.
		/// Applicable for DAE output.
		USE_ELEMENT_TYPES = 1 << (IfcGeom::IteratorSettings::NUM_SETTINGS + 4),
		/// Order the elements using their IfcBuildingStorey parent
		/// Applicable for DAE output
		USE_ELEMENT_HIERARCHY = 1 << (IfcGeom::IteratorSettings::NUM_SETTINGS + 5),
        /// Number of different setting flags.
        NUM_SETTINGS = 5
    };

    SerializerSettings()
        : precision(DEFAULT_PRECISION)
    {
        memset(offset, 0, sizeof(offset));
    }

    /// Optional offset that is applied to serialized objects, (0,0,0) by default.
    double offset[3];

    /// Sets the precision used to format floating-point values, 15 by default.
    /// Use a negative value to use the system's default precision (should be 6 typically).
    short precision;

    enum { DEFAULT_PRECISION = 15 };
};

class GeometrySerializer : public Serializer {
public:
    GeometrySerializer(const SerializerSettings& settings) : settings_(settings) {}
	virtual ~GeometrySerializer() {} 

	virtual bool isTesselated() const = 0;
	virtual void write(const IfcGeom::TriangulationElement<real_t>* o) = 0;
	virtual void write(const IfcGeom::BRepElement<real_t>* o) = 0;
	virtual void setUnitNameAndMagnitude(const std::string& name, float magnitude) = 0;

    const SerializerSettings& settings() const { return settings_; }
    SerializerSettings& settings() { return settings_; }

protected:
    SerializerSettings settings_;
};

#endif
