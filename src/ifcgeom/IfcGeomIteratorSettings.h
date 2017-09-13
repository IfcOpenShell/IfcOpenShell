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

#ifndef IFCGEOMITERATORSETTINGS_H
#define IFCGEOMITERATORSETTINGS_H

#include "ifc_geom_api.h"
#include "../ifcparse/IfcException.h"
#include "../ifcparse/IfcBaseClass.h"

namespace IfcGeom
{
    class IFC_GEOM_API IteratorSettings
    {
    public:
        /// Enumeration of setting identifiers. These settings define the
        /// behaviour of various aspects of IfcOpenShell.
        enum Setting
        {
            /// Specifies whether vertices are welded, meaning that the coordinates
            /// vector will only contain unique xyz-triplets. This results in a 
            /// manifold mesh which is useful for modelling applications, but might 
            /// result in unwanted shading artifacts in rendering applications.
            WELD_VERTICES = 1,
            /// Specifies whether to apply the local placements of building elements
            /// directly to the coordinates of the representation mesh rather than
            /// to represent the local placement in the 4x3 matrix, which will in that
            /// case be the identity matrix.
            USE_WORLD_COORDS = 1 << 1,
            /// Internally IfcOpenShell measures everything in meters. This settings
            /// specifies whether to convert IfcGeomObjects back to the units in which
            /// the geometry in the IFC file is specified.
            CONVERT_BACK_UNITS = 1 << 2,
            /// Specifies whether to use the Open Cascade BREP format for representation
            /// items rather than to create triangle meshes. This is useful is IfcOpenShell
            /// is used as a library in an application that is also built on Open Cascade.
            USE_BREP_DATA = 1 << 3,
            /// Specifies whether to sew IfcConnectedFaceSets (open and closed shells) to
            /// TopoDS_Shells or whether to keep them as a loose collection of faces.
            SEW_SHELLS = 1 << 4,
            /// Specifies whether to compose IfcOpeningElements into a single compound
            /// in order to speed up the processing of opening subtractions.
            FASTER_BOOLEANS = 1 << 5,
            /// Disables the subtraction of IfcOpeningElement representations from
            /// the related building element representations.
            DISABLE_OPENING_SUBTRACTIONS = 1 << 6,
            /// Disables the triangulation of the topological representations. Useful if
            /// the client application understands Open Cascade's native format.
            DISABLE_TRIANGULATION = 1 << 7,
            /// Applies default materials to entity instances without a surface style.
            APPLY_DEFAULT_MATERIALS = 1 << 8,
            /// Specifies whether to include subtypes of IfcCurve.
            INCLUDE_CURVES = 1 << 9,
            /// Specifies whether to exclude subtypes of IfcSolidModel and IfcSurface.
            EXCLUDE_SOLIDS_AND_SURFACES = 1 << 10,
            /// Disables computation of normals. Saves time and file size and is useful
            /// in instances where you're going to recompute normals for the exported
            /// model in other modelling application in any case.
            NO_NORMALS = 1 << 11,
            /// Generates UVs by using simple box projection. Requires normals.
            /// Applicable for OBJ and DAE output.
            GENERATE_UVS = 1 << 12,
            /// Specifies whether to slice representations according to associated IfcLayerSets.
            APPLY_LAYERSETS = 1 << 13,
			/// Search for a parent of type IfcBuildingStorey for each representation
			SEARCH_FLOOR = 1 << 14,
			///
			SITE_LOCAL_PLACEMENT = 1 << 15,
            /// Number of different setting flags.
            NUM_SETTINGS = 15
        };
        /// Used to store logical OR combination of setting flags.
        typedef unsigned SettingField;

        IteratorSettings()
            : settings_(WELD_VERTICES) // OR options that default to true here
            , deflection_tolerance_(1.e-3)
        {
        }

        /// Note that this is independent of the IFC length unit, one millimeter by default.
        double deflection_tolerance() const { return deflection_tolerance_; }

        void set_deflection_tolerance(double value)
        {
            /// @todo Using deflection tolerance of 1e-6 or smaller hangs the conversion, research more in-depth.
            /// This bug can be reproduced e.g. with the Duplex model that can be found from http://www.nibs.org/?page=bsa_commonbimfiles#project1
            deflection_tolerance_ = value;
            if (deflection_tolerance_ <= 1e-6) {
                Logger::Message(Logger::LOG_WARNING, "Deflection tolerance cannot be set to <= 1e-6; using the default value 1e-3");
                deflection_tolerance_ = 1e-3;
            }
        }

        /// Get boolean value for a single settings or for a combination of settings.
        bool get(SettingField setting) const
        {
            /// @todo If unknown setting value/combination: throw IfcParse::IfcException("Invalid IteratorSetting")?
            return (settings_ & setting) != 0;
        }

        /// Set boolean value for a single settings or for a combination of settings.
        void set(SettingField setting, bool value)
        {
            /// @todo If unknown setting value/combination: throw IfcParse::IfcException("Invalid IteratorSetting")?
            if (value) {
                settings_ |= setting;
            } else {
                settings_ &= ~setting;
            }
        }

    protected:
        SettingField settings_;
        double deflection_tolerance_;
    };

    class IFC_GEOM_API ElementSettings : public IteratorSettings
    {
    public:
        ElementSettings(const IteratorSettings& settings,
            double unit_magnitude,
            const std::string& element_type)
            : IteratorSettings(settings)
            , unit_magnitude_(unit_magnitude)
            , element_type_(element_type)
        {
        }

        double unit_magnitude() const { return unit_magnitude_; }
        const std::string& element_type() const { return element_type_; }

    private:
        double unit_magnitude_;
        std::string element_type_;
    };
}

#endif
