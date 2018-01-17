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

	template <typename T>
	class vector_vector_iterator {
	private:
		const std::vector<std::vector<T> >& container_;
		const typename std::vector<std::vector<T> >::const_iterator a_;
		boost::optional<typename std::vector<T>::const_iterator> b_;

	public:
		vector_vector_iterator(const std::vector<std::vector<T> >& container)
			: container_(container)
			, a_(container_.begin())
		{
			if (a_ != container_.end()) {
				b_ = a_->begin();
			}
		}

		vector_vector_iterator(const std::vector<std::vector<T> >& container, typename std::vector<std::vector<T> >::const_iterator x)
			: container_(container)
			, a_(x)
		{
			if (a_ != container_.end()) {
				b_ = a_->begin();
			}
		}

		bool operator==(const vector_vector_iterator<T>& other) const {
			if (a_ != container_.end()) {
				return a_ == other.a_ && b_ == other.b_;
			} else {
				return other.a_ == container_.end();
			}
		}

		bool operator!=(const vector_vector_iterator<T>& other) const {
			return !((*this) == other);
		}

		T& operator*() { return *b_; }
		const T& operator*() const { return *b_; }
		T* operator->() { return b_.operator->(); }

		vector_vector_iterator<T>& operator++() {
			if (!b_) {
				throw std::runtime_error("");
			}
			++(*b_);
			if ((*b_) == a_->end()) {
				do {
					++a_;
				} while (a_ != container_.end() && a_->size() == 0);
				if (a_ != container_.end()) {
					b_ = a_->begin();
				}
			}			
		}
	};

	class instance_categorizer {
	private:
		std::vector< IfcSchema::Type::Enum > dataset_names_;
		std::vector< std::vector<IfcUtil::IfcBaseEntity*> > instances_;
		std::vector<IfcUtil::IfcBaseEntity*> empty_;

	public:

		typedef vector_vector_iterator<IfcUtil::IfcBaseEntity*> const_iterator;

		template <typename ForwardIt>
		instance_categorizer(ForwardIt begin, ForwardIt end) {
			std::set<IfcSchema::Type::Enum> dataset_names_set;
			std::map<IfcSchema::Type::Enum, std::vector<IfcUtil::IfcBaseEntity*> > instances_map;

			std::for_each(begin, end, [&dataset_names_set, &instances_map](IfcUtil::IfcBaseClass* inst) {
				if (inst->declaration().as_entity()) {
					dataset_names_set.insert(inst->declaration().type());
					instances_map[inst->declaration().type()].push_back((IfcUtil::IfcBaseEntity*) inst);
				}
			});

			dataset_names_.assign(dataset_names_set.begin(), dataset_names_set.end());
			for (IfcSchema::Type::Enum ty : dataset_names_) {
				auto&& insts = instances_map[ty];
				std::sort(insts.begin(), insts.end(), [](IfcUtil::IfcBaseEntity* i1, IfcUtil::IfcBaseEntity* i2) {
					return i1->data().id() < i2->data().id();
				});
				instances_.emplace_back(insts);				
			}
		}

		const std::vector<IfcUtil::IfcBaseEntity*>& instances(IfcSchema::Type::Enum t) {
			auto it = std::lower_bound(dataset_names_.begin(), dataset_names_.end(), t);
			if (it == dataset_names_.end() || (*it) != t) return empty_;
			return instances_[std::distance(dataset_names_.begin(), it)];
		}

		const std::vector<IfcSchema::Type::Enum>& dataset_names() const { return dataset_names_; };

		const_iterator begin() const { return const_iterator(instances_); }
		const_iterator end() const { return const_iterator(instances_, instances_.end()); }
	};

	class instance_enumerator {
	private:
		const IfcSpfHeader* header_;
		instance_categorizer* categories_;
	public:
		typedef instance_categorizer::const_iterator const_iterator;

		instance_enumerator()
			: header_(nullptr)
			, categories_(nullptr)
		{}

		explicit instance_enumerator(IfcFile* file)
			: header_(&file->header())
		{
			std::vector<IfcUtil::IfcBaseClass*> temp;
			std::transform(file->begin(), file->end(), std::back_inserter(temp), [](auto& pair) {
				return pair.second;
			});
			categories_ = new instance_categorizer(temp.begin(), temp.end());
		}

		template <typename T>
		instance_enumerator(IfcSpfHeader* header, T begin, T end)
			: header_(header)
			, categories_(new instance_categorizer(begin, end))
		{}

		const IfcSpfHeader& header() const {
			return *header_;
		}

		const std::vector<IfcUtil::IfcBaseEntity*>& by_type(IfcSchema::Type::Enum t) {
			return categories_->instances(t);
		}

		const_iterator begin() const { return categories_->begin(); }
		const_iterator end() const { return categories_->end(); }

		const std::vector<IfcSchema::Type::Enum>& dataset_names() const { return categories_->dataset_names(); }
		instance_categorizer* categorizer() const { return categories_; }
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

		H5::DataSet create_dataset(H5::Group* population_group, const std::string& path, H5::DataType datatype, int rank, hsize_t* dimensions);
		
		void write_header(H5::Group& group, const IfcSpfHeader& header);

		template <typename T>
		void write_instance(void*& ptr, T& visitor, H5::DataType& datatype, IfcUtil::IfcBaseEntity* v);

		// TODO: Obviously change this;
		void* mapper_;
	public:
		typedef std::pair<std::string, const H5::DataType*> compound_member;
		
		void write_schema(IfcParse::instance_categorizer* ifc_file = nullptr);
		void write_population(H5::Group&, instance_enumerator&, IfcParse::abstract_instance_locator* locator = nullptr);
		
		IfcHdf5File(IfcFile* f, const std::string& name, const Hdf5Settings& settings)
			: name_(name)
			, file_(nullptr)
			, schema_(f->schema())
			, ifcfile_(f)
			, settings_(settings)
		{
			write_schema(ifcfile_.categorizer());
			H5::Group population_group = file_->createGroup("population");
			write_population(population_group, ifcfile_);
		};

		IfcHdf5File(H5::H5File& file, const IfcParse::schema_definition& schema, const Hdf5Settings& settings)
			: file_(&file)
			, schema_(&schema)
			, settings_(settings)
		{
		};

		static void convert_to_spf(const std::string& name, std::ostream& output, const boost::optional< std::vector<std::string> >& mount_points = boost::none);
	};

}

#endif
