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

#include "H5Cpp.h"

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

		std::string name_;
		schema_definition schema_;

		H5::H5File* file;
		H5::Group schema_group;
		H5::Group population_group;

		// TODO: const
		H5::CompType* instance_reference;
		const H5::DataType* object_reference_type;

		std::map<IfcSchema::Type::Enum, H5::DataType*> declared_types;
		// TODO: why? get_datatype()
		std::map<IfcParse::simple_type::data_type, const H5::DataType*> default_types;
		std::map<std::string, const H5::DataType*> overridden_types;
		std::map<IfcParse::simple_type::data_type, std::string> default_type_names;
		std::map<IfcUtil::ArgumentType, std::string> default_cpp_type_names;

		std::map<IfcSchema::Type::Enum, std::vector<IfcUtil::IfcBaseClass*> > sorted_entities;
		std::vector<IfcSchema::Type::Enum> dataset_names;

		H5::DataType* map_type(const IfcParse::parameter_type* pt);
		H5::CompType* map_entity(const IfcParse::entity* e);
		H5::DataType* map_select(const IfcParse::select_type* pt);
		H5::DataType* commit(H5::DataType* dt, const std::string& name);

		void init_default_types();
		void visit_select(const IfcParse::select_type* pt, std::set<const IfcParse::declaration*>& leafs);
		std::string flatten_aggregate_name(const IfcParse::parameter_type* at) const;
		std::pair<size_t, size_t> make_instance_reference(const IfcUtil::IfcBaseClass* instance) const;
		void write_select(void*& ptr, IfcUtil::IfcBaseClass* instance, const H5::CompType* datatype) const;

		void write_schema(const schema_definition& schema);
		void write_population(const IfcFile& f, bool compress);

		template <typename T>
		const H5::DataType* get_datatype() const {
			return default_types.find(IfcUtil::cpp_to_schema_type<T>::schema_type)->second;
		}

		void advance(void*& ptr, size_t n) const;
		
		template <typename T>
		void write(void*& ptr, const T& t) const;
		
		template <>
		void write(void*& ptr, const std::string& s) const;

		void write_vlen_t(void*& ptr, size_t n_elements, void* vlen_data) const;

		template <typename T>
		void write_number_of_size(void*& ptr, size_t n, T i) const;

		template <typename T>
		void write_aggregate(void*& ptr, const T& ts) const;
	public:
		typedef std::pair<std::string, const H5::DataType*> compound_member;

		IfcHdf5File(const IfcFile* f, const std::string& name, bool compress)
			: name_(name)
			, schema_(*f->schema())
		{
			write_schema(*f->schema());
			write_population(*f, compress);
		};
	};

}

#endif
