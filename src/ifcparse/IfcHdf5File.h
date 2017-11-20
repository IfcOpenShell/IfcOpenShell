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

	class abstract_instance_locator {
	public:
		typedef std::vector< IfcSchema::Type::Enum >::const_iterator const_iterator;

		virtual const_iterator begin() const = 0;
		virtual const_iterator end() const = 0;

		virtual const std::vector<IfcUtil::IfcBaseEntity*>& instances(IfcSchema::Type::Enum) = 0;
		virtual std::pair<int, int> operator()(IfcUtil::IfcBaseClass* v) = 0;
		virtual void make_reference(IfcUtil::IfcBaseClass*, void*&) = 0;
	};

	class instance_enumerator {
	private:
		boost::optional<IfcFile*> file_;
		boost::optional< std::pair<
			IfcSpfHeader*,
			std::map<unsigned int, IfcUtil::IfcBaseClass*>
		> > map_;
	public:
		typedef IfcFile::const_iterator const_iterator;

		instance_enumerator(IfcFile* file)
			: file_(file)
		{}

		template <typename T>
		instance_enumerator(IfcSpfHeader* header, T begin, T end) {
			std::map<unsigned int, IfcUtil::IfcBaseClass*> map;
			std::for_each(begin, end, [&map](IfcUtil::IfcBaseClass* inst) {
				// Use an incrementing id here in order not to fold distinct instances from different files with the same identifier
				map.insert(std::make_pair(map.size(), inst));
			});
			map_ = std::make_pair(header, map);
		}

		const IfcSpfHeader& header() const {
			if (map_) {
				return *map_->first;
			} else if (file_) {
				return (**file_).header();
			} else {
				throw std::runtime_error("");
			}
		}

		const_iterator begin() const {
			if (map_) {
				return map_->second.begin();
			} else if (file_) {
				return (**file_).begin();
			} else {
				throw std::runtime_error("");
			}
		}

		const_iterator end() const {
			if (map_) {
				return map_->second.end();
			} else if (file_) {
				return (**file_).end();
			} else {
				throw std::runtime_error("");
			}
		}

		IfcEntityList::ptr entitiesByType(IfcSchema::Type::Enum t) { 
			if (map_) {
				IfcEntityList::ptr insts(new IfcEntityList);
				for (auto it = begin(); it != end(); ++it) {
					if (it->second->declaration().is(t)) {
						insts->push(it->second);
					}
				}
				return insts;
			} else if (file_) {
				return (**file_).entitiesByType(t);
			} else {
				throw std::runtime_error("");
			}
		}
	};

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

		boost::optional<std::string> name_;
		const schema_definition* schema_;
		instance_enumerator ifcfile_;

		H5::H5File* file_;
		H5::Group schema_group;
		// H5::Group population_group;

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

		template <typename T>
		const H5::DataType* get_datatype() const {
			return default_types.find(IfcUtil::cpp_to_schema_type<T>::schema_type)->second;
		}

		H5::DataSet create_dataset(H5::Group* population_group, const std::string& path, H5::DataType datatype, int rank, hsize_t* dimensions);
		
		void write_header(H5::Group& group, const IfcSpfHeader& header);

		template <typename T>
		void write_instance(void*& ptr, T& visitor, H5::DataType& datatype, IfcUtil::IfcBaseEntity* v);

		// TODO: Obviously change this;
		void* mapper_;
	public:
		typedef std::pair<std::string, const H5::DataType*> compound_member;
		
		void write_schema(IfcFile* f = nullptr);
		void write_population(H5::Group&, instance_enumerator&, IfcParse::abstract_instance_locator* locator = nullptr);
		
		IfcHdf5File(IfcFile* f, const std::string& name, const Hdf5Settings& settings)
			: name_(name)
			, file_(nullptr)
			, schema_(f->schema())
			, ifcfile_(f)
			, settings_(settings)
		{
			write_schema(f);
			instance_enumerator insts = f;
			H5::Group population_group = file_->createGroup("population");
			write_population(population_group, insts);
		};

		IfcHdf5File(H5::H5File& file, const IfcParse::schema_definition& schema, const Hdf5Settings& settings)
			: file_(&file)
			, schema_(&schema)
			, settings_(settings)
			, ifcfile_(nullptr)
		{
		};

		static void convert_to_spf(const std::string& name, std::ostream& output);
	};

}

#endif
