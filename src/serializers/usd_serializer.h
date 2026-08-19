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

#ifndef USDSERIALIZER_H
#define USDSERIALIZER_H

#ifdef WITH_USD

#define __TBB_NO_IMPLICIT_LINKAGE 1
#define __TBB_LIB_NAME bier

#include "../serializers/serializers_api.h"
#include "../ifcgeom/geometry_serializer.h"
#include "../ifcparse/utils.h"

// undefine opencascade Handle macro, because it conflicts with USD
// Macro source code lives in Standard_Handle.hxx.
#pragma push_macro("Handle")
#undef Handle

#include "pxr/pxr.h"
#include "pxr/usd/usd/stage.h"
#include "pxr/base/vt/array.h"
#include "pxr/usd/usdGeom/mesh.h"
#include "pxr/usd/usdShade/material.h"

// redefine Handle macro.
#pragma pop_macro("Handle")

#include <vector>
#include <string>
#include <algorithm>
#include <map>

namespace usd_utils {
	// creates a valid USD path from a string
	inline std::string toPath(std::string& s) {
		std::replace_if(s.begin(), s.end(),
			[](char c) { return c < 48 || (c < 65 && c > 57) || (c < 97 && c > 90) || c > 122; },
			'_');
		return s;
	}

  	template<typename T>
  	pxr::VtArray<T> toVtArray(const std::vector<T>& vec) {
    	auto array = pxr::VtArray<T>(vec.size());
		for (std::size_t i = 0; i < vec.size(); ++i)
			array[i] = vec[i];
		return array;
  	}
}

class SERIALIZERS_API usd_serializer : public ifcopenshell::geom::write_only_geometry_serializer {
private:
    bool ready_ = false;
	const std::string filename_;
	std::string parent_path_;
    pxr::UsdStageRefPtr stage_;
	std::map<std::string, pxr::UsdShadeMaterial> materials_;
	std::map<std::string, std::string> meshes_;

	std::vector<pxr::UsdShadeMaterial> createMaterials(const std::vector<ifcopenshell::geom::taxonomy::style::ptr>&);
	template <typename T>
	T writeNode(const ifcopenshell::geom::element*, const ifcopenshell::geom::element* = nullptr);
	std::vector<std::pair<ifcopenshell::geom::element const*, ifcopenshell::geom::element const*>> parents_;

	std::set<int> written_;
	std::map<int, std::string> paths_;
	std::map<int, ifcopenshell::geom::taxonomy::matrix4::ptr> placements_;
	std::set<std::string> emitted_names_;
	std::map<int, std::string> element_names_;
public:
	usd_serializer(const std::string&, const ifcopenshell::geom::settings& settings, ifcopenshell::logger* logger = nullptr);
	virtual ~usd_serializer();
	bool ready() { return ready_; }
	void writeHeader();
	void write(const ifcopenshell::geom::triangulation_element*);
	void write(const ifcopenshell::geom::native_element*) {}
	void finalize();
	bool isTesselated() const { return true; }
	void setUnitNameAndMagnitude(const std::string&, float) {}
	void setFile(ifcopenshell::file&) {}
	std::string object_id_unique(const ifcopenshell::geom::element* o);
};

#endif

#endif
