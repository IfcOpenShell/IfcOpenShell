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


#include "HdfSerializer.h"

#include "../ifcgeom_schema_agnostic/IfcGeomRenderStyles.h"

#include "../ifcparse/utils.h"

#include <boost/lexical_cast.hpp>
#include <iomanip>



HdfSerializer::HdfSerializer(const std::string& hdf_filename, const SerializerSettings& settings)
	: GeometrySerializer(settings)
	, hdf_filename(hdf_filename)
	, DATASET_NAME_POSITIONS("Positions")
	, DATASET_NAME_NORMALS("Normals")
	, DATASET_NAME_INDICES("Indices")
	, DATASET_NAME_OCCT("OCCT Text")

{
	guids = {};
}


bool HdfSerializer::ready() {
	//todo: check whether the file exists
	return true;
}

void HdfSerializer::writeHeader() {
	const H5std_string  FILE_NAME(hdf_filename);
	file = H5::H5File(FILE_NAME, H5F_ACC_TRUNC);

}


void HdfSerializer::write(const IfcGeom::BRepElement<real_t>* o) {

	std::string guid = o->guid();

	H5::Group elementGroup;

	H5::Group meshGroup;
	H5::DataSet positionsDataset;
	H5::DataSet normalsDataset;
	H5::DataSet indicesDataset;

	H5::Group OCCTGroup;
	H5::DataSet OCCTDataset;
	
	const IfcGeom::Representation::BRep& brepmesh = o->geometry();
	const IfcGeom::Representation::Serialization serialization(brepmesh);
	std::string brep_data = serialization.brep_data();

	const IfcGeom::TriangulationElement<real_t>triangular_element(*o);
	const IfcGeom::Representation::Triangulation<real_t>& mesh = triangular_element.geometry();
	const int vcount = (int)mesh.verts().size() / 3;
	const int fcount = (int)mesh.faces().size() / 3;
	const bool isyup = settings().get(SerializerSettings::USE_Y_UP);

	std::string value = o->type();

	if (fcount > 0) {

		guids.insert(guid);
		elementGroup = file.createGroup(guid);

		meshGroup = elementGroup.createGroup("Triangle Mesh");
		OCCTGroup = elementGroup.createGroup("OCCT Data");

		H5::StrType str_type(0, H5T_VARIABLE);
		H5:: DataSpace attrdspace(H5S_SCALAR);
		H5::Attribute att = elementGroup.createAttribute("IFC entity type", str_type, attrdspace);
		att.write(str_type, value);

		const int   RANK = 2;
		hsize_t     dimsf[2];
		dimsf[0] = vcount;
		dimsf[1] = 3;
		H5::DataSpace dataspace(RANK, dimsf);

		hsize_t     dimsfaces[2];
		dimsfaces[0] = fcount;
		dimsfaces[1] = 3;
		H5::DataSpace face_dataspace(RANK, dimsfaces);

		const int RANK_OCCT = 1;
		hsize_t     dimsocct[2];
		dimsocct[0] = 1;
		dimsfaces[1] = 1;
		H5::DataSpace occt_dataspace(RANK_OCCT, dimsocct);
		OCCTDataset = OCCTGroup.createDataSet(DATASET_NAME_OCCT, str_type, occt_dataspace);
		OCCTDataset.write(brep_data, str_type);

		indicesDataset = meshGroup.createDataSet(DATASET_NAME_INDICES, H5::PredType::NATIVE_INT, face_dataspace);
		positionsDataset = meshGroup.createDataSet(DATASET_NAME_POSITIONS, H5::PredType::NATIVE_DOUBLE, dataspace);
		normalsDataset = meshGroup.createDataSet(DATASET_NAME_NORMALS, H5::PredType::NATIVE_DOUBLE, dataspace);

		positionsDataset.write(mesh.verts().data(), H5::PredType::NATIVE_DOUBLE);
		normalsDataset.write(mesh.normals().data(), H5::PredType::NATIVE_DOUBLE);
		indicesDataset.write(mesh.faces().data(), H5::PredType::NATIVE_INT);
		


	
	}
}
