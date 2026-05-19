#ifndef LINEAR_SWEEP_HELPER_H
#define LINEAR_SWEEP_HELPER_H

#include "taxonomy.h"
#include "ConversionSettings.h"

#include "ifc_geom_api.h"

namespace ifcopenshell {

	namespace geometry {
		
		struct IFC_GEOM_API cross_section {
			double dist_along;
			taxonomy::geom_item::ptr section_geometry;
			Eigen::Vector3d offset;
			boost::optional<Eigen::Matrix3d> rotation;

			bool operator <(const cross_section& other) const {
				return dist_along < other.dist_along;
			}
		};

		IFC_GEOM_API taxonomy::loft::ptr make_loft(const Settings& settings_, const IfcUtil::IfcBaseClass* inst, const taxonomy::function_item::ptr& directrix, std::vector<cross_section>& cross_sections);
	}

}

#endif