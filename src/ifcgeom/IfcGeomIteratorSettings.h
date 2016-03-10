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

#include "../ifcparse/IfcException.h"

namespace IfcGeom
{
    class IteratorSettings
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
            /// Use entity names instead of unique IDs for naming elements.
            /// Applicable for OBJ, DAE, and SVG output.
            USE_ELEMENT_NAMES = 1 << 12,
            /// Use entity GUIDs instead of unique IDs for naming elements.
            /// Applicable for OBJ, DAE, and SVG output.
            USE_ELEMENT_GUIDS = 1 << 13,
            /// Use material names instead of unique IDs for naming materials.
            /// Applicable for OBJ and DAE output.
            USE_MATERIAL_NAMES = 1 << 14,
            /// Centers the models upon serialization by the applying the center point of
            /// the scene bounds as an offset. Applicable only for DAE output currently.
            CENTER_MODEL = 1 << 15,
            /// Generates UVs by using simple box projection. Requires normals.
            /// Applicable only for DAE output currently.
            //GENERATE_UVS = 1 << 16,
            //NUM_SETTINGS = 16
        };
        /// Used to store logical OR combination of setting flags.
        typedef unsigned SettingField;

        IteratorSettings()
            : settings_(WELD_VERTICES) // OR options that default to true here
            , deflection_tolerance_(1.e-3)
        {
            memset(offset, 0, sizeof(offset));
        }

        /// Optional offset that is applied to serialized objects, (0,0,0) by default.
        double offset[3];

        /// Note that this is independent of the IFC length unit, one millimeter by default.
        double deflection_tolerance() const { return deflection_tolerance_; }
        /// @todo Sanity check for the value
        void set_deflection_tolerance(double value) { deflection_tolerance_ = value; }

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

    class ElementSettings : public IteratorSettings
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
