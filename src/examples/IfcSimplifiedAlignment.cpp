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

// This example illustrates the basic of building an alignment model.
// The alignment is based on "Bridge Geometry Manual", April 2022
// US Department of Transportation, Federal Highway Administration (FHWA)
// https://www.fhwa.dot.gov/bridge/pubs/hif22034.pdf
//
// Sections and page number for this document are cited in the code comments.
//
// This examples differs from IfcAlignment because it uses utility methods
// to simplify alignment construction

// Disable warnings coming from IfcOpenShell
#pragma warning(disable : 4018 4267 4250 4984 4985)

#include "../ifcparse/Ifc4x3_add2.h"
#include "../ifcparse/IfcAlignmentHelper.h"

#include <fstream>

#define Schema Ifc4x3_add2

// performs basic project setup including created the IfcProject object
// and initializing the project units to FEET
Schema::IfcProject* setup_project(IfcHierarchyHelper<Schema>& file) {
    std::vector<std::string> file_description;
    file_description.push_back("ViewDefinition[Alignment-basedReferenceView]");
    file.header().file_description()->setdescription(file_description);

    auto project = file.addProject();
    project->setName(std::string("FHWA Bridge Geometry Manual Example Alignment"));
    project->setDescription(std::string("C++ Example - Simplified"));

    // set up project units for feet
    // the call to file.addProject() sets up length units as millimeter.
    auto units_in_context = project->UnitsInContext();
    auto units = units_in_context->Units();
    auto begin = units->begin();
    auto iter = begin;
    auto end = units->end();
    for (; iter != end; iter++) {
        auto unit = *iter;
        if (unit->as<Schema::IfcSIUnit>() && unit->as<Schema::IfcSIUnit>()->UnitType() == Schema::IfcUnitEnum::IfcUnit_LENGTHUNIT) {
            auto dimensions = new Schema::IfcDimensionalExponents(1, 0, 0, 0, 0, 0, 0);
            file.addEntity(dimensions);

            auto conversion_factor = new Schema::IfcMeasureWithUnit(new Schema::IfcLengthMeasure(304.80), unit->as<Schema::IfcSIUnit>());
            file.addEntity(conversion_factor);

            auto conversion_based_unit = new Schema::IfcConversionBasedUnit(dimensions, Schema::IfcUnitEnum::IfcUnit_LENGTHUNIT, "FEET", conversion_factor);
            file.addEntity(conversion_based_unit);

            units->remove(unit);                // remove the millimeter unit
            units->push(conversion_based_unit); // add the feet unit
            units_in_context->setUnits(units);  // update the UnitsInContext

            break; // Done!, the length unit was found, so break out of the loop
        }
    }

    return project;
}

int main() {
    IfcHierarchyHelper<Schema> file;

    auto project = setup_project(file);

    //
    // Define horizontal alignment
    //

    // PI Data
    // B.1.1 pg 211
    std::vector<std::pair<double, double>> points{
        { 500.0, 2500.0}, // beginning
        {3340.0,  660.0}, // Point of intersection (PI), Curve #1
        {4340.0, 5000.0}, // Point of intersection (PI), Curve #2
        {7600.0, 4560.0}, // Point of intersection (PI), Curve #3
        {8480.0, 2010.0}  // ending
    };

    // Curve Data
    // B.1.3 pg 212
    std::vector<double> radii{ 1000,1250,950 };

    //
    // Define vertical profile segments
    //

    // Vertical Profile Data
    // Figure B.2 pg 213
    double xStart = 10000.0; // subtract xStart so the points are distance along, not station
    std::vector<std::pair<double,double>> vpoints {
        {10000.0-xStart,100.0}, // Vertical point of beginning (VPOB)
        {12000.0-xStart,135.0}, // Point of vertical intersection (VPI), Curve #1
        {15000.0-xStart,105.0}, // Point of vertical intersection (VPI), Curve #2
        {17400.0-xStart,153.0}, // Point of vertical intersection (VPI), Curve #3
        {19800.0-xStart,105.0}, // Point of vertical intersection (VPI), Curve #4
        {22800.0-xStart, 90.0}  // Vertical poitn of ending (VPOE)
    };

    // Vertical Curve Lengths
    // Figure B.2 pg 213
    std::vector<double> vclengths{1600.0, 1200.0, 2000.0, 800.0};

    // Use utility function to create alignment
    auto alignment = addAlignment(file, "Example Alignment", points, radii, vpoints, vclengths);

    // Define the alignment's relationship with the project

    // IFC 4.1.4.1.1 "Every IfcAlignment must be related to IfcProject using the IfcRelAggregates relationship"
    // https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/concepts/Object_Composition/Aggregation/Alignment_Aggregation_To_Project/content.html
    // IfcProject <-> IfcRelAggregates <-> IfcAlignment
    typename aggregate_of<typename Schema::IfcObjectDefinition>::ptr list_of_alignments_in_project(new aggregate_of<typename Schema::IfcObjectDefinition>());
    list_of_alignments_in_project->push(alignment);
    auto aggregate_alignments_with_project = new Schema::IfcRelAggregates(IfcParse::IfcGlobalId(), nullptr, std::string("Alignments in project"), boost::none, project, list_of_alignments_in_project);
    file.addEntity(aggregate_alignments_with_project);

    // Define the spatial structure of the alignment with respect to the site

    // IFC 4.1.5.1 alignment is referenced in spatial structure of an IfcSpatialElement. In this case IfcSite is the highest level IfcSpatialElement
    // https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/concepts/Object_Connectivity/Alignment_Spatial_Reference/content.html
    // IfcSite <-> IfcRelReferencedInSpatialStructure <-> IfcAlignment
    // This means IfcAlignment is not part of the IfcSite (it is not an aggregate component) but instead IfcAlignment is used within
    // the IfcSite by reference. This implies an IfcAlignment can traverse many IfcSite instances within an IfcProject
    typename Schema::IfcSpatialReferenceSelect::list::ptr list_alignments_referenced_in_site(new Schema::IfcSpatialReferenceSelect::list);
    list_alignments_referenced_in_site->push(alignment);

    // Complete the model by creating sites for the 3 bridges
    for (int i = 1; i <= 3; i++) {
        std::ostringstream os;
        os << "Site of Bridge " << i;
        auto site = file.addSite(project, nullptr);
        site->setName(os.str());

        std::ostringstream description;
        description << "Alignments referenced into the spatial structure of Bridge Site " << i;

        auto rel_referenced_in_spatial_structure = new Schema::IfcRelReferencedInSpatialStructure(IfcParse::IfcGlobalId(), nullptr, boost::none, description.str(), list_alignments_referenced_in_site, site);
        file.addEntity(rel_referenced_in_spatial_structure);
    }

    // That's it - save the model to a file
    std::ofstream ofs("FHWA_Bridge_Geometry_Alignment_Example_Simplified.ifc");
    ofs << file;
}
