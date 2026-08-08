#ifndef IFC_GEOM_SERIALIZATION_H
#define IFC_GEOM_SERIALIZATION_H

#include "../../ifcparse/express.h"
#include "../../plugin/plugin.h"
#include "../../ifcgeom/ConversionResult.h"

#include "ifc_geomserialization_api.h"

#include <boost/function.hpp>

#include <map>
#include <string>

class TopoDS_Shape;

namespace ifcopenshell {
	class file;
}

namespace ifcopenshell::geom {
class IFC_GEOMSERIALIZATION_API opencascade_geometry_ifc_writer_registry {
public:
	typedef boost::function3<express::base, ifcopenshell::file&, const conversion_result_shape&, double> tesselate_fn;
	typedef boost::function3<express::base, ifcopenshell::file&, const conversion_result_shape&, bool> serialise_fn;

	void bind(const std::string& schema_name, serialise_fn serialise, tesselate_fn tesselate, const ifcopenshell::plugin::module& module = ifcopenshell::plugin::module());
	express::base tesselate(ifcopenshell::file& f, const conversion_result_shape& shape, double deflection) const;
	express::base serialise(ifcopenshell::file& f, const conversion_result_shape& shape, bool advanced) const;

private:
	struct entry {
		serialise_fn serialise_;
		tesselate_fn tesselate_;
		ifcopenshell::plugin::module module_;
	};

	std::map<std::string, entry> entries_;
};

IFC_GEOMSERIALIZATION_API opencascade_geometry_ifc_writer_registry& opencascade_geometry_ifc_writer_registry_instance();

IFC_GEOMSERIALIZATION_API express::base tesselate(ifcopenshell::file& f, const conversion_result_shape& shape, double deflection);
IFC_GEOMSERIALIZATION_API express::base serialise(ifcopenshell::file& f, const conversion_result_shape& shape, bool advanced);
IFC_GEOMSERIALIZATION_API express::base tesselate(ifcopenshell::file& f, const TopoDS_Shape& shape, double deflection);
IFC_GEOMSERIALIZATION_API express::base serialise(ifcopenshell::file& f, const TopoDS_Shape& shape, bool advanced);
} // namespace ifcopenshell::geom

#endif
