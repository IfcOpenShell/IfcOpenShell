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

#include "../../../src/ifcparse/IfcHdf5File.h"
#include "../../../src/ifcparse/IfcWritableEntity.h"

#include <boost/lexical_cast.hpp>

#include <set>
#include <algorithm>

#pragma warning(disable:4100) 

class ifc_inst_cmp {
public:

	// For these we simply assume that only a single instance exists
	bool operator()(IfcSchema::IfcSite* a, IfcSchema::IfcSite* b) const { return false; }
	bool operator()(IfcSchema::IfcProject* a, IfcSchema::IfcProject* b) const { return false; }
	bool operator()(IfcSchema::IfcBuilding* a, IfcSchema::IfcBuilding* b) const { return false; }
	bool operator()(IfcSchema::IfcPostalAddress* a, IfcSchema::IfcPostalAddress* b) const { return false; }
	bool operator()(IfcSchema::IfcUnitAssignment* a, IfcSchema::IfcUnitAssignment* b) const { return false; }

	bool operator()(IfcSchema::IfcConversionBasedUnit* a, IfcSchema::IfcConversionBasedUnit* b) const {
		return a->Name() < b->Name();
	}

	bool operator()(IfcSchema::IfcDimensionalExponents* a, IfcSchema::IfcDimensionalExponents* b) const {
		// For every attribute (which are all integers) check equality

		unsigned num_attrs = a->data().getArgumentCount();
		for (unsigned i = 0; i < num_attrs; ++i) {
			const int v1 = *a->data().getArgument(i);
			const int v2 = *b->data().getArgument(i);
			if (v1 != v2) {
				return v1 < v2;
			}
		}

		return false;
	}

	bool operator()(IfcSchema::IfcMeasureWithUnit* a, IfcSchema::IfcMeasureWithUnit* b) const {
		// Assume the value component is enough to differentiate

		double v1 = *a->ValueComponent()->data().getArgument(0);
		double v2 = *b->ValueComponent()->data().getArgument(0);
		return v1 < v2;
	}

	bool operator()(IfcSchema::IfcGeometricRepresentationSubContext* a, IfcSchema::IfcGeometricRepresentationSubContext* b) const {
		return a->ContextType() < b->ContextType();
	}

	bool operator()(IfcSchema::IfcGeometricRepresentationContext* a, IfcSchema::IfcGeometricRepresentationContext* b) const {
		return a->ContextType() < b->ContextType();
	}

	bool operator()(IfcSchema::IfcSIUnit* a, IfcSchema::IfcSIUnit* b) const {
		// Assume same units accross files

		return a->UnitType() < b->UnitType();
	}

	bool operator()(IfcSchema::IfcBuildingStorey* a, IfcSchema::IfcBuildingStorey* b) const {
		return a->Name() < b->Name();
	}

	bool operator()(IfcSchema::IfcCartesianPoint* a, IfcSchema::IfcCartesianPoint* b) const {
		return a->Coordinates() < b->Coordinates();
	}

	bool operator()(IfcSchema::IfcDirection* a, IfcSchema::IfcDirection* b) const {
		return a->DirectionRatios() < b->DirectionRatios();
	}

	bool operator()(IfcSchema::IfcAxis2Placement3D* a, IfcSchema::IfcAxis2Placement3D* b) const {
		if (a->Location()->Coordinates() != b->Location()->Coordinates()) {
			return (*this)(a->Location(), b->Location());
		}
		if (b->hasAxis()) {
			if (!a->hasAxis()) {
				return true;
			} else {
				return (*this)(a->Axis(), b->Axis());
			}
		}
		if (b->hasRefDirection()) {
			if (!a->hasRefDirection()) {
				return true;
			} else {
				return (*this)(a->RefDirection(), b->RefDirection());
			}
		}
		return false;
	}

	bool operator()(IfcSchema::IfcLocalPlacement* a, IfcSchema::IfcLocalPlacement* b) const {
		if (b->hasPlacementRelTo()) {
			if (!a->hasPlacementRelTo()) {
				return true;
			} else {
				return (*this)(a->PlacementRelTo(), b->PlacementRelTo());
			}
		}
		return (*this)(a->RelativePlacement(), b->RelativePlacement());
	}

	bool operator()(IfcUtil::IfcBaseClass* a, IfcUtil::IfcBaseClass* b) const {
		if (a->declaration().type() != b->declaration().type()) {
			return a->declaration().type() < b->declaration().type();
			// throw std::runtime_error("Types not matching");
		}

		if (a->declaration().type() == IfcSchema::Type::IfcSite) { return (*this)((IfcSchema::IfcSite*) a, (IfcSchema::IfcSite*) b); }
		if (a->declaration().type() == IfcSchema::Type::IfcConversionBasedUnit) { return (*this)((IfcSchema::IfcConversionBasedUnit*) a, (IfcSchema::IfcConversionBasedUnit*) b); }
		if (a->declaration().type() == IfcSchema::Type::IfcDimensionalExponents) { return (*this)((IfcSchema::IfcDimensionalExponents*) a, (IfcSchema::IfcDimensionalExponents*) b); }
		if (a->declaration().type() == IfcSchema::Type::IfcMeasureWithUnit) { return (*this)((IfcSchema::IfcMeasureWithUnit*) a, (IfcSchema::IfcMeasureWithUnit*) b); }
		if (a->declaration().type() == IfcSchema::Type::IfcProject) { return (*this)((IfcSchema::IfcProject*) a, (IfcSchema::IfcProject*) b); }
		if (a->declaration().type() == IfcSchema::Type::IfcBuilding) { return (*this)((IfcSchema::IfcBuilding*) a, (IfcSchema::IfcBuilding*) b); }
		if (a->declaration().type() == IfcSchema::Type::IfcPostalAddress) { return (*this)((IfcSchema::IfcPostalAddress*) a, (IfcSchema::IfcPostalAddress*) b); }
		if (a->declaration().type() == IfcSchema::Type::IfcUnitAssignment) { return (*this)((IfcSchema::IfcUnitAssignment*) a, (IfcSchema::IfcUnitAssignment*) b); }
		if (a->declaration().type() == IfcSchema::Type::IfcGeometricRepresentationSubContext) { return (*this)((IfcSchema::IfcGeometricRepresentationSubContext*) a, (IfcSchema::IfcGeometricRepresentationSubContext*) b); }
		if (a->declaration().type() == IfcSchema::Type::IfcGeometricRepresentationContext) { return (*this)((IfcSchema::IfcGeometricRepresentationContext*) a, (IfcSchema::IfcGeometricRepresentationContext*) b); }
		if (a->declaration().type() == IfcSchema::Type::IfcSIUnit) { return (*this)((IfcSchema::IfcSIUnit*) a, (IfcSchema::IfcSIUnit*) b); }
		if (a->declaration().type() == IfcSchema::Type::IfcBuildingStorey) { return (*this)((IfcSchema::IfcBuildingStorey*) a, (IfcSchema::IfcBuildingStorey*) b); }
		if (a->declaration().type() == IfcSchema::Type::IfcCartesianPoint) { return (*this)((IfcSchema::IfcCartesianPoint*) a, (IfcSchema::IfcCartesianPoint*) b); }
		if (a->declaration().type() == IfcSchema::Type::IfcDirection) { return (*this)((IfcSchema::IfcDirection*) a, (IfcSchema::IfcDirection*) b); }
		if (a->declaration().type() == IfcSchema::Type::IfcAxis2Placement3D) { return (*this)((IfcSchema::IfcAxis2Placement3D*) a, (IfcSchema::IfcAxis2Placement3D*) b); }
		if (a->declaration().type() == IfcSchema::Type::IfcLocalPlacement) { return (*this)((IfcSchema::IfcLocalPlacement*) a, (IfcSchema::IfcLocalPlacement*) b); }

		// Should these be removed if an owner history is created manually?
		if (a->declaration().type() == IfcSchema::Type::IfcPerson) { return (a->data().id() & 0x1000000) < (b->data().id() & 0x1000000); }
		if (a->declaration().type() == IfcSchema::Type::IfcOrganization) { return (a->data().id() & 0x1000000) < (b->data().id() & 0x1000000); }
		if (a->declaration().type() == IfcSchema::Type::IfcPersonAndOrganization) { return (a->data().id() & 0x1000000) < (b->data().id() & 0x1000000); }
		if (a->declaration().type() == IfcSchema::Type::IfcOwnerHistory) { return (a->data().id() & 0x1000000) < (b->data().id() & 0x1000000); }
		if (a->declaration().type() == IfcSchema::Type::IfcApplication) { return (a->data().id() & 0x1000000) < (b->data().id() & 0x1000000); }
		
		std::cerr << "Unexpected type: " + IfcSchema::Type::ToString(a->declaration().type()) << std::endl;
		throw std::runtime_error("Unexpected type: " + IfcSchema::Type::ToString(a->declaration().type()));
	}
};

class multifile_instance_locator : public IfcParse::abstract_instance_locator {
public:
	typedef std::function<IfcUtil::IfcBaseClass*(IfcUtil::IfcBaseClass*)> mapping_t;
	typedef std::pair<
		std::vector<IfcSchema::Type::Enum>,
		std::vector< std::vector<IfcUtil::IfcBaseEntity*> >
	> population_t;
	typedef std::vector<IfcUtil::IfcBaseClass*>::const_iterator full_const_iterator;
	
private:
	H5::H5File& root_file_;

	mapping_t mapping_;
	std::set<IfcUtil::IfcBaseClass*> initial_population_set_;

	population_t initial_population_;
	population_t subsequent_population_;
	std::vector<IfcUtil::IfcBaseClass*> subsequent_minus_initial_;

	H5::Group& initial_group_;
	H5::Group* subsequent_group_;
	H5::H5File* subsequent_file_;
	std::string root_;

public:

	template <typename ForwardIterator>
	multifile_instance_locator(H5::H5File& root_file, H5::Group& group, mapping_t mapping, ForwardIterator b, ForwardIterator e)
		: root_file_(root_file)
		, mapping_(mapping)
		, initial_group_(group)
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
		throw std::runtime_error("This locator can only be used in referenced profile");
	}

	void make_reference(IfcUtil::IfcBaseClass* v, void*& ptr) {
		v = mapping_(v);
		IfcSchema::Type::Enum t = v->declaration().type();

		population_t* pop;
		H5::Group* group;
		boost::optional<std::string> current_root;
				
		if (initial_population_set_.find(v) != initial_population_set_.end()) {
			pop = &initial_population_;
			group = &initial_group_;
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

		root_file_.reference(ptr, full_path, space);
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

int main(int argc, char** argv) {
	
	std::set<IfcSchema::Type::Enum> shared {
		IfcSchema::Type::IfcSite,
		IfcSchema::Type::IfcConversionBasedUnit,
		IfcSchema::Type::IfcDimensionalExponents,
		IfcSchema::Type::IfcMeasureWithUnit,
		IfcSchema::Type::IfcProject,
		IfcSchema::Type::IfcBuilding,
		IfcSchema::Type::IfcPostalAddress,
		IfcSchema::Type::IfcUnitAssignment,
		IfcSchema::Type::IfcGeometricRepresentationSubContext,
		IfcSchema::Type::IfcGeometricRepresentationContext,
		IfcSchema::Type::IfcSIUnit,
		IfcSchema::Type::IfcBuildingStorey
	};

	std::vector<IfcParse::IfcFile*> files;

	for (int i = 1; i < argc; ++i) {
		files.push_back(new IfcParse::IfcFile());
		files.back()->Init(argv[i]);
	}

	std::set<IfcUtil::IfcBaseClass*> shared_instances;

	for (auto& ty : shared) {	
		std::cout << IfcSchema::Type::ToString(ty) << std::endl;

		for (auto& file : files) {
			IfcEntityList::ptr insts = file->entitiesByType(ty);
			std::vector<IfcUtil::IfcBaseClass*> no_subtypes;
			std::copy_if(insts->begin(), insts->end(), std::back_inserter(no_subtypes), [ty](IfcUtil::IfcBaseClass* inst) {
				return inst->declaration().type() == ty;
			});
			
			std::set<IfcUtil::IfcBaseClass*, ifc_inst_cmp> insts_unique(no_subtypes.begin(), no_subtypes.end());

			if (insts_unique.size() != no_subtypes.size()) {
				throw std::runtime_error("Non-unique instances encountered within file");
			}

			shared_instances.insert(insts_unique.begin(), insts_unique.end());
		}
	}

	std::set<IfcUtil::IfcBaseClass*> shared_instances_and_refs;

	for (auto& inst : shared_instances) {
		IfcEntityList::ptr insts = inst->data().file->traverse(inst);

		// Filter out simple types
		std::vector<IfcUtil::IfcBaseClass*> insts_without_types;
		std::copy_if(insts->begin(), insts->end(), std::back_inserter(insts_without_types), [](IfcUtil::IfcBaseClass* inst) {
			return inst->declaration().as_entity() != nullptr;
		});

		shared_instances_and_refs.insert(insts_without_types.begin(), insts_without_types.end());
	}

	time_t now_;
	time(&now_);
	int now = (int)now_;
	
	IfcSchema::IfcPerson* person = new IfcSchema::IfcPerson(std::string("tfk"), std::string("Krijnen"), std::string("Thomas"), boost::none, boost::none, boost::none, boost::none, boost::none);
	IfcSchema::IfcOrganization* org = new IfcSchema::IfcOrganization(std::string("TU/e"), "Eindhoven University of Technology", boost::none, boost::none, boost::none);
	IfcSchema::IfcPersonAndOrganization* pando = new IfcSchema::IfcPersonAndOrganization(person, org, boost::none);
	IfcSchema::IfcApplication* appl = new IfcSchema::IfcApplication(org, "v1", "IfcOpenShell-HDF5", "IfcOpenShell-HDF5");
	IfcSchema::IfcOwnerHistory* owner_history = new IfcSchema::IfcOwnerHistory(pando, appl, IfcSchema::IfcStateEnum::IfcState_READONLY, IfcSchema::IfcChangeActionEnum::IfcChangeAction_ADDED, now, pando, appl, now);

	std::vector<IfcUtil::IfcBaseClass*> replacements{ person, org, pando, appl, owner_history};

	std::vector<IfcUtil::IfcBaseClass*> shared_instances_and_refs_vector(shared_instances_and_refs.begin(), shared_instances_and_refs.end());

	IfcParse::IfcFile temp;
	for (int i = 0; i < 0x1000001; ++i) temp.FreshId();

	std::for_each(replacements.begin(), replacements.end(), [&shared_instances_and_refs_vector, &temp](IfcUtil::IfcBaseClass* new_inst) {
		temp.addEntity(new_inst);

		shared_instances_and_refs_vector.erase(
			std::remove_if(shared_instances_and_refs_vector.begin(), shared_instances_and_refs_vector.end(), [new_inst](IfcUtil::IfcBaseClass* orig_inst) {
				return orig_inst->declaration().type() == new_inst->declaration().type();
			}),
			shared_instances_and_refs_vector.end()
		);

		shared_instances_and_refs_vector.push_back(new_inst);
	});

	shared_instances_and_refs.clear();
	shared_instances_and_refs.insert(shared_instances_and_refs_vector.begin(), shared_instances_and_refs_vector.end());

	std::for_each(shared_instances_and_refs.begin(), shared_instances_and_refs.end(), [owner_history](IfcUtil::IfcBaseClass* inst) {
		const IfcParse::entity* e = inst->declaration().as_entity();
		if (e) {
			auto attributes = e->all_attributes();
			int index = 0;
			std::for_each(attributes.begin(), attributes.end(), [&index, inst, owner_history](const IfcParse::entity::attribute* attr) {
				const IfcParse::named_type* nt = attr->type_of_attribute()->as_named_type();
				if (nt) {
					const IfcParse::entity* e2 = nt->declared_type()->as_entity();
					if (e2 && e2->type() == IfcSchema::Type::IfcOwnerHistory) {
						IfcWrite::IfcWritableEntity* writable = new IfcWrite::IfcWritableEntity(&inst->data());
						writable->setArgument(index, owner_history);
						inst->data(writable);
					}
				}
				index++;
			});
		}
	});

	/*
	for (auto& i : shared_instances_and_refs) {
		if (shared_instances.find(i) == shared_instances.end()) {
			std::cerr << i->data().toString() << std::endl;
		}
	}

	std::cerr << "----" << std::endl;
	*/

	std::set<IfcUtil::IfcBaseClass*, ifc_inst_cmp> shared_instances_and_refs_unique(shared_instances_and_refs.begin(), shared_instances_and_refs.end());
	
	
	IfcParse::Hdf5Settings settings;
	settings.profile() = IfcParse::Hdf5Settings::standard_referenced;

	std::vector<std::string> names;
	std::vector<std::pair<std::string::const_iterator, std::string::const_iterator>> fixes;
	std::string common_prefix, common_postfix;
	for (int i = 1; i < argc; ++i) {
		names.push_back(argv[i]);
		fixes.push_back({ names.back().begin(), names.back().end() - 1 });
	}

	while (true) {
		std::vector<char> chars;
		std::transform(fixes.begin(), fixes.end(), std::back_inserter(chars), [](auto& pair) {
			if (pair.first == pair.second) return '\0';
			return (*pair.first++);
		});
		auto pred = std::bind(std::equal_to<char>(), std::placeholders::_1, chars.front());
		if (chars.front() != 0 && std::all_of(chars.begin()+1, chars.end(), pred)) {
			common_prefix.push_back(chars.front());
		} else {
			break;
		}
	}

	while (true) {
		std::vector<char> chars;
		std::transform(fixes.begin(), fixes.end(), std::back_inserter(chars), [](auto& pair) {
			if (pair.first == pair.second) return '\0';
			return (*pair.second--);
		});
		auto pred = std::bind(std::equal_to<char>(), std::placeholders::_1, chars.front());
		if (chars.front() != 0 && std::all_of(chars.begin() + 1, chars.end(), pred)) {
			common_postfix.insert(common_postfix.begin(), chars.front());
		} else {
			break;
		}
	}

	H5::H5File file(common_prefix + common_postfix + ".hdf", H5F_ACC_TRUNC);
	H5::Group group1 = file.createGroup("population");

	IfcParse::IfcHdf5File ifc_hdf5(file, get_schema(), settings);
	IfcParse::IfcSpfHeader header;
	header.set_default();

	IfcParse::instance_enumerator shared_insts_enum(&header, shared_instances_and_refs_unique.begin(), shared_instances_and_refs_unique.end());

	multifile_instance_locator* locator = new multifile_instance_locator(file, group1, [&shared_instances_and_refs_unique](IfcUtil::IfcBaseClass* inst) {
		auto it = shared_instances_and_refs_unique.find(inst);
		if (it == shared_instances_and_refs_unique.end()) {
			return inst;
		} else {
			return *it;
		}
	}, shared_instances_and_refs_unique.begin(), shared_instances_and_refs_unique.end());

	ifc_hdf5.write_schema();
	ifc_hdf5.write_population(group1, shared_insts_enum, locator);

	int n = 0;
	for (auto f : files) {
		auto filename = argv[n++ + 1];
		H5::Group discipline_group = file.createGroup(filename);
		H5::Group child_group = discipline_group.createGroup("population");

		locator->next(filename, child_group, f);
		IfcParse::instance_enumerator inst_enum(&f->header(), locator->full_begin(), locator->full_end());
		
		ifc_hdf5.write_population(child_group, shared_insts_enum, locator);
	}

	return 0;
}
