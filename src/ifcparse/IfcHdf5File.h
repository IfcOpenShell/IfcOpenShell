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

#ifndef IFCHDF5FILE_H
#define IFCHDF5FILE_H

#define SORT_ON_NAME

#include <H5Cpp.h>

#include "../ifcparse/Hdf5Settings.h"
#include "../ifcparse/IfcUtil.h"
#include "../ifcparse/IfcFile.h"

namespace IfcParse {

	class IfcHdf5File {
	private:
		class allocator_t {
		private:
			// TODO: Change this?
			mutable std::vector<uint8_t*> buffers;
		public:
			void* allocate(size_t n) const {
				return new uint8_t[n];
			}
			void free() {
				std::vector<uint8_t*>::const_iterator it;
				for (it = buffers.begin(); it != buffers.end(); ++it) {
					delete[] *it;
				}
				buffers.clear();
			}
			~allocator_t() {
				free();
			}
		};

		allocator_t allocator;
		Hdf5Settings settings_;

		std::string name_;
		schema_definition schema_;
		IfcFile& ifcfile_;

		H5::H5File* file;
		H5::Group schema_group;
		H5::Group population_group;

		// TODO: const
		H5::CompType* instance_reference;
		const H5::DataType* object_reference_type;

		std::map<IfcSchema::Type::Enum, H5::DataType*> declared_types;

#ifdef SORT_ON_NAME
		std::map<IfcSchema::Type::Enum, std::vector<uint32_t> > sorted_entities;
#else
		std::map<IfcSchema::Type::Enum, std::vector<IfcUtil::IfcBaseClass*> > sorted_entities;
#endif
		std::vector<IfcSchema::Type::Enum> dataset_names;

		H5::DataType* map_type(const IfcParse::parameter_type* pt);
		H5::CompType* map_entity(const IfcParse::entity* e);
		H5::DataType* map_select(const IfcParse::select_type* pt);
		H5::DataType* commit(H5::DataType* dt, const std::string& name);

		void init_default_types();
		void visit_select(const IfcParse::select_type* pt, std::set<const IfcParse::declaration*>& leafs);
		std::string flatten_aggregate_name(const IfcParse::parameter_type* at) const;
		std::pair<size_t, size_t> make_instance_reference(const IfcUtil::IfcBaseClass* instance) const;
		// void write_select(void*& ptr, IfcUtil::IfcBaseClass* instance, const H5::CompType* datatype) const;

		void write_schema(const schema_definition& schema, IfcFile& f);
		void write_population(IfcFile& f);

		template <typename T>
		const H5::DataType* get_datatype() const {
			return default_types.find(IfcUtil::cpp_to_schema_type<T>::schema_type)->second;
		}

		H5::DataSet create_dataset(const std::string& path, H5::DataType datatype, int rank, hsize_t* dimensions);
		
		void write_header(H5::Group& group, IfcSpfHeader& header);

		template <typename T>
		void write_instance(void*& ptr, T& visitor, H5::DataType& datatype, IfcUtil::IfcBaseEntity* v);

		// TODO: Obviously change this;
		void* mapper_;
	public:
		typedef std::pair<std::string, const H5::DataType*> compound_member;
		
		
		IfcHdf5File(IfcFile* f, const std::string& name, const Hdf5Settings& settings)
			: name_(name)
			, schema_(*f->schema())
			, ifcfile_(*f)
			, settings_(settings)
		{
			write_schema(schema_, ifcfile_);
			write_population(ifcfile_);
		};

		static void convert_to_spf(const std::string& name, std::ostream& output);
	};

}

#endif
