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


typedef struct s1_t {
	int  a, b, c;
} s1_t;


typedef struct s2_t {
	double a, b, c;
} s2_t;

HdfSerializer::HdfSerializer(const std::string& obj_filename, const std::string& mtl_filename, const SerializerSettings& settings)
	: GeometrySerializer(settings)
	, mtl_filename(obj_filename)
	, DATASET_NAME_POSITIONS("Positions")
	, DATASET_NAME_NORMALS("Normals")
	, DATASET_NAME_INDICES("Indices")
	, mtype1(sizeof(s1_t))
	, mtype2(sizeof(s2_t))
	, mtype3(sizeof(s1_t))


{
	guids = {};

	H5::IntType Intdatatype(H5::PredType::NATIVE_INT);
	H5::FloatType datatype(H5::PredType::NATIVE_DOUBLE);
	datatype.setOrder(H5T_ORDER_LE);
	Intdatatype.setOrder(H5T_ORDER_LE);

	const H5std_string MEMBER1("V1");
	const H5std_string MEMBER2("V2");
	const H5std_string MEMBER3("V3");
	mtype1.insertMember(MEMBER1, HOFFSET(s1_t, a), H5::PredType::NATIVE_INT);
	mtype1.insertMember(MEMBER2, HOFFSET(s1_t, c), H5::PredType::NATIVE_INT);
	mtype1.insertMember(MEMBER3, HOFFSET(s1_t, b), H5::PredType::NATIVE_INT);

	const H5std_string POS1("X");
	const H5std_string POS2("Y");
	const H5std_string POS3("Z");
	mtype2.insertMember(POS1, HOFFSET(s2_t, a), datatype);
	mtype2.insertMember(POS2, HOFFSET(s2_t, b), datatype);
	mtype2.insertMember(POS3, HOFFSET(s2_t, c), datatype);

	const H5std_string NOR1("X");
	const H5std_string NOR2("Y");
	const H5std_string NOR3("Z");
	mtype3.insertMember(NOR1, HOFFSET(s1_t, a), Intdatatype);
	mtype3.insertMember(NOR2, HOFFSET(s1_t, b), Intdatatype);
	mtype3.insertMember(NOR3, HOFFSET(s1_t, c), Intdatatype);

}


bool HdfSerializer::ready() {

	//return obj_stream.is_open() && mtl_stream.is_open();
	return true;
}

void HdfSerializer::writeHeader() {
	const H5std_string  FILE_NAME(mtl_filename);
	file = H5::H5File(FILE_NAME, H5F_ACC_TRUNC);

}



void HdfSerializer::write(const IfcGeom::TriangulationElement<real_t>* o) {

	std::string guid = o->guid();
	//Logger::Status(guid);
	//Logger::Status(o->context());
	//Logger::Status("\n");

	H5::Group elementGroup;
	H5::Group meshGroup;
	H5::DataSet positionsDataset;
	H5::DataSet normalsDataset;
	H5::DataSet indicesDataset;


	const IfcGeom::Representation::Triangulation<real_t>& mesh = o->geometry();
	const int vcount = (int)mesh.verts().size() / 3;
	const int fcount = (int)mesh.faces().size() / 3;


	if (fcount > 0) {

		guids.insert(guid);
		elementGroup = file.createGroup(guid);
		meshGroup = elementGroup.createGroup("Triangle Mesh");

		const int   RANK = 2;
		hsize_t     dimsf[2];
		dimsf[0] = vcount;
		dimsf[1] = 1;
		H5::DataSpace dataspace(RANK, dimsf);

		hsize_t     dimsfaces[2];
		dimsfaces[0] = fcount;
		dimsfaces[1] = 1;
		H5::DataSpace face_dataspace(RANK, dimsfaces);


		indicesDataset = meshGroup.createDataSet(DATASET_NAME_INDICES, mtype1, face_dataspace);
		positionsDataset = meshGroup.createDataSet(DATASET_NAME_POSITIONS, mtype2, dataspace);
		normalsDataset = meshGroup.createDataSet(DATASET_NAME_NORMALS, mtype3, dataspace);

		for (std::vector<real_t>::const_iterator it = mesh.verts().begin(); it != mesh.verts().end(); ) {
			const real_t x = *(it++);
			const real_t y = *(it++);
			const real_t z = *(it++);
			double_data_container.push_back(x);
			double_data_container.push_back(y);
			double_data_container.push_back(z);

		}
		positionsDataset.write(double_data_container.data(), mtype2);
		double_data_container.clear();


		for (std::vector<real_t>::const_iterator it = mesh.normals().begin(); it != mesh.normals().end(); ) {
			const real_t x = *(it++);
			const real_t y = *(it++);
			const real_t z = *(it++);
			int_data_container.push_back((int)x);
			int_data_container.push_back((int)y);
			int_data_container.push_back((int)z);

		}
		normalsDataset.write(int_data_container.data(), mtype3);
		int_data_container.clear();


		for (std::vector<int>::const_iterator it = mesh.faces().begin(); it != mesh.faces().end(); ) {
			const real_t x = *(it++);
			const real_t y = *(it++);
			const real_t z = *(it++);
			int_data_container.push_back(x);
			int_data_container.push_back(y);
			int_data_container.push_back(z);

		}
		indicesDataset.write(int_data_container.data(), mtype1);
		int_data_container.clear();


	
	}
}
