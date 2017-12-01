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

 class multifile_instance_locator : public IfcParse::abstract_instance_locator {
public:
	typedef std::function<IfcUtil::IfcBaseClass*(IfcUtil::IfcBaseClass*)> mapping_t;
	typedef std::pair<
		std::vector<IfcSchema::Type::Enum>,
		std::vector< std::vector<IfcUtil::IfcBaseEntity*> >
	> population_t;
	typedef std::vector<IfcUtil::IfcBaseClass*>::const_iterator full_const_iterator;
	
private:
	H5::H5File* root_file_;

	mapping_t mapping_;
	std::set<IfcUtil::IfcBaseClass*> initial_population_set_;
	std::set<IfcSchema::Type::Enum> initial_types_included_set_;

	population_t initial_population_;
	population_t subsequent_population_;
	std::vector<IfcUtil::IfcBaseClass*> subsequent_minus_initial_;

	H5::Group* initial_group_;
	H5::Group* subsequent_group_;
	H5::H5File* subsequent_file_;
	std::string root_;

public:

	template <typename ForwardIterator>
	multifile_instance_locator(H5::H5File& root_file, H5::Group& group, mapping_t mapping, ForwardIterator b, ForwardIterator e)
		: root_file_(&root_file)
		, mapping_(mapping)
		, initial_group_(&group)
		, subsequent_group_(nullptr)
	{
		initial_population_set_.insert(b, e);

		std::set<IfcSchema::Type::Enum> names_set;
		std::for_each(b, e, [this, &names_set](IfcUtil::IfcBaseClass* inst) {
			IfcSchema::Type::Enum ty = inst->declaration().type();
			if (names_set.find(ty) == names_set.end()) {
				initial_population_.first.push_back(ty);
				names_set.insert(ty);
			}
		});

		std::sort(initial_population_.first.begin(), initial_population_.first.end());

		std::for_each(this->begin(), this->end(), [this, &b, &e](IfcSchema::Type::Enum t) {
			std::vector<IfcUtil::IfcBaseEntity*> by_type;

			std::for_each(b, e, [t,&by_type](IfcUtil::IfcBaseClass* inst) {
				if (inst->declaration().type() == t && inst->declaration().as_entity()) {
					by_type.push_back((IfcUtil::IfcBaseEntity*) inst);
				}
			});

			std::sort(by_type.begin(), by_type.end(), [](IfcUtil::IfcBaseEntity* i1, IfcUtil::IfcBaseEntity* i2) {
				return i1->data().id() < i2->data().id();
			});

			initial_population_.second.emplace_back(by_type);
		});
	}

	template <typename ForwardIteratorTypes, typename ForwardIteratorInsts>
	multifile_instance_locator(ForwardIteratorTypes types_all_begin, ForwardIteratorTypes types_all_end, ForwardIteratorInsts insts_begin, ForwardIteratorInsts insts_end)
		: subsequent_group_(nullptr)
	{
		initial_population_.first.assign(types_all_begin, types_all_end);
		std::sort(initial_population_.first.begin(), initial_population_.first.end());

		std::for_each(this->begin(), this->end(), [this, &insts_begin, &insts_end](IfcSchema::Type::Enum t) {
			std::vector<IfcUtil::IfcBaseEntity*> by_type;

			std::for_each(insts_begin, insts_end, [t, &by_type](IfcUtil::IfcBaseClass* inst) {
				if (inst->declaration().type() == t && inst->declaration().as_entity()) {
					by_type.push_back((IfcUtil::IfcBaseEntity*) inst);
				}
			});

			std::sort(by_type.begin(), by_type.end(), [](IfcUtil::IfcBaseEntity* i1, IfcUtil::IfcBaseEntity* i2) {
				return i1->data().id() < i2->data().id();
			});

			initial_population_.second.emplace_back(by_type);
		});
	}

	const_iterator begin() const {
		if (subsequent_group_) {
			return subsequent_population_.first.begin();
		} else {
			return initial_population_.first.begin();
		}
	}

	const_iterator end() const {
		if (subsequent_group_) {
			return subsequent_population_.first.end();
		} else {
			return initial_population_.first.end();
		}
	}

	full_const_iterator full_begin() const {
		return subsequent_minus_initial_.begin();
	}

	full_const_iterator full_end() const {
		return subsequent_minus_initial_.end();
	}

	const std::vector<IfcUtil::IfcBaseEntity*>& instances(IfcSchema::Type::Enum t) {
		if (subsequent_group_) {
			return subsequent_population_.second[std::lower_bound(begin(), end(), t) - begin()];
		} else {
			return initial_population_.second[std::lower_bound(begin(), end(), t) - begin()];
		}
	}

	std::pair<int, int> operator()(IfcUtil::IfcBaseClass* v) {
		if (IfcSchema::Type::IsSimple(v->declaration().type())) {
			throw std::exception("Simple type not expected here");
		}

		IfcSchema::Type::Enum t = v->declaration().type();

		// This remains constant for subsequent model serializations?
		auto& dataset_names = initial_population_.first;
		auto tt = std::lower_bound(dataset_names.begin(), dataset_names.end(), t);
		int a = std::distance(dataset_names.begin(), tt);
		int b;

		const std::vector<IfcUtil::IfcBaseEntity*>& insts = instances(t);

		auto it = std::lower_bound(insts.begin(), insts.end(), v, [](IfcUtil::IfcBaseClass* other, IfcUtil::IfcBaseClass* val) {
			// An ordering based on ID is not equivalent to an ordering based on pointer address!
			return other->data().id() < val->data().id();
		});

		if (it == insts.end()) {
			throw std::runtime_error("Unable to find instance");
		}

		b = std::distance(insts.begin(), it);

		return std::make_pair(a, b);
	}

	void make_reference(IfcUtil::IfcBaseClass* v, void*& ptr) {
		v = mapping_(v);
		IfcSchema::Type::Enum t = v->declaration().type();

		population_t* pop;
		H5::Group* group;
		boost::optional<std::string> current_root;
				
		if (initial_population_set_.find(v) != initial_population_set_.end()) {
			pop = &initial_population_;
			group = initial_group_;
			current_root = boost::none;
		} else {
			pop = &subsequent_population_;
			group = subsequent_group_;
			current_root = root_;
		}

		int a = std::lower_bound(pop->first.begin(), pop->first.end(), t) - pop->first.begin();
		auto& vec = pop->second[a];

		hsize_t coord = std::lower_bound(vec.begin(), vec.end(), v, [](IfcUtil::IfcBaseClass* other, IfcUtil::IfcBaseClass* val) {
			return other->data().id() < val->data().id();
		}) - vec.begin();

		hsize_t dims = instances(v->declaration().type()).size();
		H5::DataSpace space(1, &dims);
		space.selectElements(H5S_SELECT_SET, 1, &coord);
		const std::string path = IfcSchema::Type::ToString(pop->first[a]);

		std::string full_path = group->getObjName() + "/" + path + "_instances";

		root_file_->reference(ptr, full_path, space);
		ptr = static_cast<uint8_t*>(ptr) + sizeof(hdset_reg_ref_t);
	}

	void next(const std::string& name, H5::Group& group, IfcParse::IfcFile* f) {
		subsequent_group_ = &group;
		root_ = name;
		
		subsequent_population_.first.clear();
		subsequent_population_.second.clear();
		subsequent_minus_initial_.clear();

		auto f_begin = f->begin();
		auto f_end = f->end();

		std::set<IfcSchema::Type::Enum> names_set;
		std::for_each(f_begin, f_end, [this, &names_set](auto& pair) {
			IfcUtil::IfcBaseClass* inst = mapping_(pair.second);
			if (initial_population_set_.find(inst) == initial_population_set_.end()) {
				IfcSchema::Type::Enum ty = inst->declaration().type();
				if (names_set.find(ty) == names_set.end()) {
					subsequent_population_.first.push_back(ty);
					names_set.insert(ty);
				}
				subsequent_minus_initial_.push_back(inst);
			}
		});
		
		auto& names = subsequent_population_.first;
		std::sort(names.begin(), names.end());

		auto& vecs = subsequent_population_.second;
		vecs.resize(names.size());
		
		std::for_each(f_begin, f_end, [this, &names, &vecs](auto& pair) {
			IfcUtil::IfcBaseClass* inst = mapping_(pair.second);
			if (initial_population_set_.find(inst) == initial_population_set_.end() && inst->declaration().as_entity()) {
				IfcSchema::Type::Enum ty = inst->declaration().type();
				auto a = std::lower_bound(names.begin(), names.end(), ty) - names.begin();
				auto& by_type = vecs[a];
				by_type.push_back((IfcUtil::IfcBaseEntity*) inst);
			}
		});

		std::for_each(vecs.begin(), vecs.end(), [](auto& vec) {
			std::sort(vec.begin(), vec.end(), [](IfcUtil::IfcBaseEntity* i1, IfcUtil::IfcBaseEntity* i2) {
				return i1->data().id() < i2->data().id();
			});
		});
	}
};
