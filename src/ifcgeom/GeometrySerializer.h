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

#include "../ifcgeom/Serializer.h"
#include "../ifcgeom/IfcGeomElement.h"
#include <fstream>

namespace ifcopenshell {
namespace geometry {
inline namespace settings {

	struct UseElementNames : public SettingBase<UseElementNames, bool> {
		static constexpr const char* const name = "use-element-names";
		static constexpr const char* const description = "Use entity instance IfcRoot.Name instead of unique IDs for naming elements upon serialization. "
			"Applicable for OBJ, DAE, STP, and SVG output.";
		static constexpr bool defaultvalue = false;
	};

	struct UseElementGuids : public SettingBase<UseElementGuids, bool> {
		static constexpr const char* const name = "use-element-guids";
		static constexpr const char* const description = "Use entity instance IfcRoot.GlobalId instead of unique IDs for naming elements upon serialization. "
			"Applicable for OBJ, DAE, STP, and SVG output.";
		static constexpr bool defaultvalue = false;
	};

	struct UseElementStepIds : public SettingBase<UseElementStepIds, bool> {
		static constexpr const char* const name = "use-element-step-ids";
		static constexpr const char* const description = "Use the numeric step identifier (entity instance name) for naming elements upon serialization. "
			"Applicable for OBJ, DAE, STP, and SVG output.";
		static constexpr bool defaultvalue = false;
	};

	struct UseElementTypes : public SettingBase<UseElementTypes, bool> {
		static constexpr const char* const name = "use-element-types";
		static constexpr const char* const description = "Use element types instead of unique IDs for naming elements upon serialization. "
			"Applicable to DAE output.";
		static constexpr bool defaultvalue = false;
	};

	struct UseYUp : public SettingBase<UseYUp, bool> {
		static constexpr const char* const name = "y-up";
		static constexpr const char* const description = "Change the 'up' axis to positive Y, default is Z UP. Applicable to OBJ output.";
		static constexpr bool defaultvalue = false;
	};

	struct WriteGltfEcef : public SettingBase<WriteGltfEcef, bool> {
		static constexpr const char* const name = "ecef";
		static constexpr const char* const description = "Write glTF in Earth-Centered Earth-Fixed coordinates. Requires PROJ.";
		static constexpr bool defaultvalue = false;
	};

	struct FloatingPointDigits : public SettingBase<FloatingPointDigits, int> {
		static constexpr const char* const name = "digits";
		static constexpr const char* const description = "Sets the precision to be used to format floating-point values, 15 by default. "
			"Use a negative value to use the system's default precision (should be 6 typically). "
			"Applicable for OBJ and DAE output. For DAE output, value >= 15 means that up to 16 decimals are used, "
			" and any other value means that 6 or 7 decimals are used.";
		static constexpr int defaultvalue = 15;
	};

	struct BaseUri : public SettingBase<BaseUri, std::string> {
		static constexpr const char* const name = "base-uri";
		static constexpr const char* const description = "Base URI for products to be used in RDF-based serializations.";
	};

	struct WktUseSection : public SettingBase<WktUseSection, bool> {
		static constexpr const char* const name = "wkt-use-section";
		static constexpr const char* const description = "Use a geometrical section rather than full polyhedral output and footprint in TTL WKT";
		static constexpr bool defaultvalue = false;
	};

	struct SeparateZUpNode : public SettingBase<SeparateZUpNode, bool> {
        static constexpr const char* const name = "separate-z-up-node";
        static constexpr const char* const description = "Introduce a separate Z-Up node into the GlTF hierarchy instead of multiplying the transform into the root node matrices";
        static constexpr bool defaultvalue = false;
    };

	struct SvgBounds : public SettingBase<SvgBounds, std::string> {
		static constexpr const char* const name = "bounds";
		static constexpr const char* const description = "Specifies the bounding rectangle, for example 512x512, to which the output will be scaled. Only used when converting to SVG.";
	};

	struct SvgScale : public SettingBase<SvgScale, std::string> {
		static constexpr const char* const name = "scale";
		static constexpr const char* const description = "Interprets SVG bounds in mm, centers layout and draw elements to scale. Only used when converting to SVG. Example 1:100.";
	};

	struct SvgCenter : public SettingBase<SvgCenter, std::string> {
		static constexpr const char* const name = "center";
		static constexpr const char* const description = "When using --scale, specifies the location in the range [0 1]x[0 1] around which to center the drawings. Example 0.5x0.5.";
	};

	struct SvgSectionRef : public SettingBase<SvgSectionRef, std::string> {
		static constexpr const char* const name = "section-ref";
		static constexpr const char* const description = "Element at which cross sections should be created.";
	};

	struct SvgElevationRef : public SettingBase<SvgElevationRef, std::string> {
		static constexpr const char* const name = "elevation-ref";
		static constexpr const char* const description = "Element at which drawings should be created.";
	};

	struct SvgElevationRefGuid : public SettingBase<SvgElevationRefGuid, std::string> {
		static constexpr const char* const name = "elevation-ref-guid";
		static constexpr const char* const description = "Element guids at which drawings should be created.";
	};

	struct SvgAutoSection : public SettingBase<SvgAutoSection, bool> {
		static constexpr const char* const name = "auto-section";
		static constexpr const char* const description = "Creates SVG cross section drawings automatically based on model extents.";
		static constexpr bool defaultvalue = false;
	};

	struct SvgAutoElevation : public SettingBase<SvgAutoElevation, bool> {
		static constexpr const char* const name = "auto-elevation";
		static constexpr const char* const description = "Creates SVG elevation drawings automatically based on model extents.";
		static constexpr bool defaultvalue = false;
	};

	struct SvgDrawStoreyHeights : public SettingBase<SvgDrawStoreyHeights, std::string> {
		static constexpr const char* const name = "draw-storey-heights";
		static constexpr const char* const description = "Draws a horizontal line at the height of building storeys in vertical drawings. Accepted values are none, full, and left.";
	};

	struct SvgStoreyHeightLineLength : public SettingBase<SvgStoreyHeightLineLength, double> {
		static constexpr const char* const name = "storey-height-line-length";
		static constexpr const char* const description = "Length of the line when --draw-storey-heights=left.";
	};

	struct SvgUseNamespace : public SettingBase<SvgUseNamespace, bool> {
		static constexpr const char* const name = "svg-xmlns";
		static constexpr const char* const description = "Stores name and guid in a separate namespace as opposed to data-name, data-guid.";
		static constexpr bool defaultvalue = false;
	};

	struct SvgUseHlrPoly : public SettingBase<SvgUseHlrPoly, bool> {
		static constexpr const char* const name = "svg-poly";
		static constexpr const char* const description = "Uses the polygonal algorithm for hidden line rendering.";
		static constexpr bool defaultvalue = false;
	};

	struct SvgUsePrefiltering : public SettingBase<SvgUsePrefiltering, bool> {
		static constexpr const char* const name = "svg-prefilter";
		static constexpr const char* const description = "Prefilter faces and shapes before feeding to the hidden-line algorithm.";
		static constexpr bool defaultvalue = false;
	};

	struct SvgSegmentProjection : public SettingBase<SvgSegmentProjection, bool> {
		static constexpr const char* const name = "svg-segment-projection";
		static constexpr const char* const description = "Segment result of projection with respect to original products.";
		static constexpr bool defaultvalue = false;
	};

	struct SvgPolygonal : public SettingBase<SvgPolygonal, bool> {
		static constexpr const char* const name = "svg-write-poly";
		static constexpr const char* const description = "Approximate every curve as polygonal in SVG output.";
		static constexpr bool defaultvalue = false;
	};

	struct SvgAlwaysProject : public SettingBase<SvgAlwaysProject, bool> {
		static constexpr const char* const name = "svg-project";
		static constexpr const char* const description = "Always enable hidden line rendering instead of only on elevations.";
		static constexpr bool defaultvalue = false;
	};

	struct SvgWithoutStoreys : public SettingBase<SvgWithoutStoreys, bool> {
		static constexpr const char* const name = "svg-without-storeys";
		static constexpr const char* const description = "Do not emit drawings for building storeys.";
		static constexpr bool defaultvalue = false;
	};

	struct SvgNoCss : public SettingBase<SvgNoCss, bool> {
		static constexpr const char* const name = "svg-no-css";
		static constexpr const char* const description = "Do not emit CSS style declarations.";
		static constexpr bool defaultvalue = false;
	};

	struct SvgDoorArcs : public SettingBase<SvgDoorArcs, bool> {
		static constexpr const char* const name = "door-arcs";
		static constexpr const char* const description = "Draw door opening arcs for IfcDoor elements.";
		static constexpr bool defaultvalue = false;
	};

	struct SvgSectionHeight : public SettingBase<SvgSectionHeight, double> {
		static constexpr const char* const name = "section-height";
		static constexpr const char* const description = "Specifies the cut section height for SVG 2D geometry.";
	};

	struct SvgSectionHeightFromStoreys : public SettingBase<SvgSectionHeightFromStoreys, bool> {
		static constexpr const char* const name = "section-height-from-storeys";
		static constexpr const char* const description = "Derives section height from storey elevation. Use --section-height to override the default offset of 1.2.";
		static constexpr bool defaultvalue = false;
	};

	struct SvgPrintSpaceNames : public SettingBase<SvgPrintSpaceNames, bool> {
		static constexpr const char* const name = "print-space-names";
		static constexpr const char* const description = "Prints IfcSpace LongName and Name in the geometry output. Applicable for SVG output.";
		static constexpr bool defaultvalue = false;
	};

	struct SvgPrintSpaceAreas : public SettingBase<SvgPrintSpaceAreas, bool> {
		static constexpr const char* const name = "print-space-areas";
		static constexpr const char* const description = "Prints calculated IfcSpace areas in square meters. Applicable for SVG output.";
		static constexpr bool defaultvalue = false;
	};

	struct SvgSpaceNameTransform : public SettingBase<SvgSpaceNameTransform, std::string> {
		static constexpr const char* const name = "space-name-transform";
		static constexpr const char* const description = "Additional transform to the space labels in SVG.";
	};
}

class SerializerSettings : public SettingsContainer <
	// @todo should we use tuple_cat here to unify the settings into a single class?
    std::tuple<
		UseElementNames,
		UseElementGuids,
		UseElementStepIds,
		UseElementTypes,
		UseYUp,
		WriteGltfEcef,
		FloatingPointDigits,
		BaseUri,
		WktUseSection,
		SeparateZUpNode,
		SvgBounds,
		SvgScale,
		SvgCenter,
		SvgSectionRef,
		SvgElevationRef,
		SvgElevationRefGuid,
		SvgAutoSection,
		SvgAutoElevation,
		SvgDrawStoreyHeights,
		SvgStoreyHeightLineLength,
		SvgUseNamespace,
		SvgUseHlrPoly,
		SvgUsePrefiltering,
		SvgSegmentProjection,
		SvgPolygonal,
		SvgAlwaysProject,
		SvgWithoutStoreys,
		SvgNoCss,
		SvgDoorArcs,
		SvgSectionHeight,
		SvgSectionHeightFromStoreys,
		SvgPrintSpaceNames,
		SvgPrintSpaceAreas,
		SvgSpaceNameTransform>>
{};

}
}

class IFC_GEOM_API stream_or_filename {
private:
	std::shared_ptr<std::ofstream> ofs_;
	std::shared_ptr<std::ostringstream> oss_;
	std::optional<std::string> filename_;

public:
	std::ostream& stream;

	stream_or_filename(const std::string& fn)
		: ofs_(new std::ofstream(ifcopenshell::path::from_utf8(fn).c_str()))
		, filename_(fn)
		, stream(*ofs_)
	{}

	stream_or_filename()
		: oss_(new std::ostringstream)
		, stream(*oss_)
	{}

	std::string get_value() const {
		return oss_->str();
	}

	std::optional<std::string> filename() const {
		return filename_;
	}

	bool is_ready() {
		if (ofs_) {
			return ofs_->is_open();
		} else {
			return true;
		}
	}
};

class IFC_GEOM_API GeometrySerializer : public Serializer {
public:
	enum read_type { READ_BREP, READ_TRIANGULATION };

    GeometrySerializer(const ifcopenshell::geometry::Settings& geometry_settings, const ifcopenshell::geometry::SerializerSettings& settings)
		: geometry_settings_(geometry_settings)
		, settings_(settings)
	{}
	virtual ~GeometrySerializer() {} 

	virtual bool isTesselated() const = 0;
	virtual void write(const IfcGeom::TriangulationElement* o) = 0;
	virtual void write(const IfcGeom::BRepElement* o) = 0;
	virtual void setUnitNameAndMagnitude(const std::string& name, float magnitude) = 0;
	virtual IfcGeom::Element* read(ifcopenshell::file& f, const std::string& guid, const std::string& representation_id, read_type rt = READ_BREP) = 0;

    const ifcopenshell::geometry::SerializerSettings& settings() const { return settings_; }
	ifcopenshell::geometry::SerializerSettings& settings() { return settings_; }

	const ifcopenshell::geometry::Settings& geometry_settings() const { return geometry_settings_; }
	ifcopenshell::geometry::Settings& geometry_settings() { return geometry_settings_; }

    /// Returns ID for the object depending on the used setting.
    virtual std::string object_id(const IfcGeom::Element* o)
    {
        if (settings_.get<ifcopenshell::geometry::settings::UseElementGuids>().get()) return o->guid();
        if (settings_.get<ifcopenshell::geometry::settings::UseElementNames>().get()) return o->name();
		if (settings_.get<ifcopenshell::geometry::settings::UseElementStepIds>().get()) return "id-" + boost::lexical_cast<std::string>(o->id());
		return o->unique_id();
    }

protected:
	ifcopenshell::geometry::Settings geometry_settings_;
	ifcopenshell::geometry::SerializerSettings settings_;
};

class IFC_GEOM_API WriteOnlyGeometrySerializer : public GeometrySerializer {
public:
	WriteOnlyGeometrySerializer(const ifcopenshell::geometry::Settings& geometry_settings, const ifcopenshell::geometry::SerializerSettings& settings) : GeometrySerializer(geometry_settings, settings) {}

	virtual IfcGeom::Element* read(ifcopenshell::file&, const std::string&, const std::string&, read_type = READ_BREP) {
		throw std::runtime_error("Not supported");
	};
};

#endif
