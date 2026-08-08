#ifdef IFOPSH_WITH_ROCKSDB

#include "RocksDbSerializer.h"

#include <rocksdb/options.h>

#include <cstdint>
#include <cstring>

#include "../ifcparse/logger.h"

RocksDbSerializer::RocksDbSerializer(const std::string& input_filename, const std::string& rocksdb_filename, const std::vector<std::string>& skip_supertypes, ::logger* logger)
	: input_filename_(input_filename)
	, rocksdb_filename_(rocksdb_filename)
	, skip_supertypes_(skip_supertypes)
{
}

namespace {
	// @nb copied from instance_data.cpp but operating on unresolved instances
	bool serialize(std::string& val, const ifcopenshell::reference_or_simple_type& t)
	{
		auto s = sizeof(size_t);
		val.resize(s + 2);
		val[0] = type_encoder::encode_type<express::base>();
		// 1 = entity - stored by id (entity name)
		// 2 = type - stored by identity (internal counter in class)
		val[1] = t.index() == 0 ? 'i' : 't';
		size_t iden;
		if (auto* name = std::get_if<ifcopenshell::instance_reference>(&t)) {
			iden = *name;
		} else if (auto* inst = std::get_if<express::base>(&t)) {
			iden = (*inst).identity();
		}
		memcpy(val.data() + 2, &iden, s);
		return true;
	}

	bool serialize(std::string& val, const std::vector<ifcopenshell::reference_or_simple_type>& t)
	{
		// no attempt at alignment
		val.resize(t.size() * (sizeof(size_t) + 1) + 1);
		val[0] = type_encoder::encode_type<std::vector<express::base>>();
		char* ptr = val.data() + 1;
		for (auto it = t.begin(); it != t.end(); ++it) {
			*ptr = it->index() == 0 ? 'i' : 't';
			ptr++;
			size_t iden = 0;
			if (auto* name = std::get_if<ifcopenshell::instance_reference>(&*it)) {
				iden = *name;
			} else if (auto* inst = std::get_if<express::base>(&*it)) {
				iden = (*inst).identity();
			}
			memcpy(ptr, &iden, sizeof(size_t));
			ptr += sizeof(size_t);
		}
		return true;
	}

	bool serialize(std::string& val, const std::vector<std::vector<ifcopenshell::reference_or_simple_type>>& t)
	{
		std::ostringstream oss;
		oss.put(type_encoder::encode_type<std::vector<std::vector<express::base>>>());

		auto write_size = [&oss](size_t sz) {
			std::string size_str;
			size_str.resize(sizeof(size_t));
			memcpy(size_str.data(), &sz, sizeof(size_t));
			oss.write(size_str.data(), size_str.size());
		};

		// write_size(t.size());

		for (auto it = t.begin(); it != t.end(); ++it) {
			// size of inner aggregate
			write_size(it->size() * 9);

			// values
			for (auto jt = it->begin(); jt != it->end(); ++jt) {
				char c = jt->index() == 0 ? 'i' : 't';
				oss.put(c);
				size_t iden = 0;
				if (auto* name = std::get_if<ifcopenshell::instance_reference>(&*jt)) {
					iden = *name;
				} else if (auto* inst = std::get_if<express::base>(&*jt)) {
					iden = (*inst).identity();
				}
				std::string iden_str;
				iden_str.resize(sizeof(size_t));
				memcpy(iden_str.data(), &iden, sizeof(size_t));
				oss.write(iden_str.data(), iden_str.size());
			}
		}

		val = oss.str();

		return true;
	}
}

namespace {
	template <typename T>
	std::string to_string_fixed_width(const T& t, size_t w) {
		// @todo currently inactive
		std::ostringstream oss;
		oss << /*std::setfill('0') << std::setw(w) <<*/ t;
		return oss.str();
	}
}

void RocksDbSerializer::write_streaming_() {
	ifcopenshell::impl::rocks_db_file_storage storage(rocksdb_filename_, nullptr);

	std::string tmp;

	// Resolved lazily from the first non-header declaration encountered, because
	// the schema is only known once the header has been read.
	const ifcopenshell::declaration* ifcroot_type = nullptr;

	ifcopenshell::instance_streamer streamer(input_filename_);

	// We do not want to coerce attribute counts here, because we want
	// to store exactly what is in the file for validation purposes
	streamer.coerce_attribute_count = false;

	while (streamer) {
		auto inst = streamer.read_instance();
		if (inst) {
			// name can be zero in case of header instances
			auto name = std::get<0>(*inst);
			const auto* decl = std::get<1>(*inst);
			const auto& data = std::get<2>(*inst);

			const bool is_header = decl->schema() == &Header_section_schema::get_schema();

			if (!is_header && decl->as_entity() && !skip_supertypes_.empty()) {
				bool skip = false;
				for (const auto& super : skip_supertypes_) {
					if (decl->is(super)) {
						skip = true;
						break;
					}
				}
				if (skip) {
					streamer.references().clear();
					streamer.inverses().clear();
					continue;
				}
			}

			std::vector<express::base> simple_type_instances;

			for (size_t i = 0; i < data->storage_->size(); i++) {
				auto val = data->get_attribute_value(i);
				val.apply_visitor([&](const auto& t) {
					using T = std::decay_t<decltype(t)>;
					if constexpr (std::is_same_v<T, express::base>) {
						// instance is per definition a simple type here, because instance
						// references are not resolved yet, but provided in vector of
						// references
						simple_type_instances.push_back(t);
					}
					rocks_db_attribute_storage{}.set(&storage, decl, name, i, t);
				});
			}

			std::set<size_t> type_identities_wrote_as_refs;

			for (auto& p : streamer.references()) {
				// @nb cast to int in order not be interpreted as a char when appending to string
				int index = p.first.index_;

				auto key = (is_header ? "h|" : (decl->as_entity() ? "i|" : "t|")) +
					(is_header ? decl->name() : std::to_string(p.first.name_)) + "|" +
					std::to_string(index);

				if (storage.db->Get(storage.ropts, key, &tmp) == rocksdb::Status::OK() && tmp.size() == (sizeof(size_t) + 2) && tmp[0] == type_encoder::encode_type<express::base>() && tmp[1] == 't')
				{
					size_t iden;
					memcpy(&iden, tmp.data() + 2, sizeof(size_t));
					key = "t|" + std::to_string(iden) + "|0";
					type_identities_wrote_as_refs.insert(iden);
				}

				std::visit([&](const auto& v) {
					serialize(tmp, v);

					using T = std::decay_t<decltype(v)>;

					if constexpr (std::is_same_v<T, ifcopenshell::reference_or_simple_type>) {
						if (auto* inst = std::get_if<express::base>(&v)) {
							// So this never happens?
							simple_type_instances.push_back(*inst);
						}
					} else if constexpr (std::is_same_v<T, std::vector<ifcopenshell::reference_or_simple_type>>) {
						for (auto const& inner : v) {
							if (auto* inst = std::get_if<express::base>(&inner)) {
								simple_type_instances.push_back(*inst);
							}
						}
					} else if constexpr (std::is_same_v<T, std::vector<std::vector<ifcopenshell::reference_or_simple_type>>>) {
						for (auto const& inner : v) {
							for (auto const& innermost : inner) {
								if (auto* inst = std::get_if<express::base>(&innermost)) {
									simple_type_instances.push_back(*inst);
								}
							}
						}
					}
				}, p.second);

				storage.db->Put(
					storage.wopts,
					key, tmp);

				auto write_inverse = [&](const ifcopenshell::reference_or_simple_type& v) {
					if (auto* ref = std::get_if<ifcopenshell::instance_reference>(&v)) {
						auto key = "v|" + to_string_fixed_width(*ref, 10) + "|" + to_string_fixed_width(decl->index_in_schema(), 4) + "|" + to_string_fixed_width(index, 2);
						static std::string s;
						uint32_t vv = name;
						s.resize(sizeof(uint32_t));
						memcpy(s.data(), &vv, sizeof(uint32_t));
						storage.db->Merge(
							storage.wopts, key, s);
					}
				};

				std::visit([&](auto const& val) {
					using T = std::decay_t<decltype(val)>;

					if constexpr (std::is_same_v<T, ifcopenshell::reference_or_simple_type>) {
						write_inverse(val);
					} else if constexpr (std::is_same_v<T, std::vector<ifcopenshell::reference_or_simple_type>>) {
						std::for_each(val.begin(), val.end(), write_inverse);
					} else if constexpr (std::is_same_v<T, std::vector<std::vector<ifcopenshell::reference_or_simple_type>>>) {
						for (auto const& inner : val) {
							std::for_each(inner.begin(), inner.end(), write_inverse);
						}
					}
				}, p.second);
			}

			for (const auto& inst : simple_type_instances) {
				std::string s(sizeof(size_t), ' ');
				size_t v = inst.declaration().index_in_schema();
				memcpy(s.data(), &v, sizeof(size_t));

				storage.db->Put(
					storage.wopts,
					(inst.declaration().as_entity() ? "i|" : "t|") + std::to_string(inst.identity()) + "|_", s);

				if (type_identities_wrote_as_refs.find(inst.identity()) != type_identities_wrote_as_refs.end()) {
					// already written as reference, skip
					// only applies to the value though, the type declaration still needs to be written
					continue;
				}

				auto val = inst.get_attribute_value(0);
				// @todo if statement?
				// if (val.array_.storage_ptr->size() > 0) {
					val.apply_visitor([&](const auto& t) {
						rocks_db_attribute_storage{}.set(&storage, &inst.declaration(), inst.identity(), 0, t);
					});
				// }

				// @nb we also need to delete them
				// not anymore, as they are now registered as unique_ptr in the in_memory_file_storage
				// delete inst;
			}

			// Entity type as numeric ref to index_in_schema
			if (!is_header) {
				std::string s(sizeof(size_t), ' ');
				size_t v = decl->index_in_schema();
				memcpy(s.data(), &v, sizeof(size_t));
				storage.db->Put(
					storage.wopts,
					(decl->as_entity() ? "i|" : "t|") + std::to_string(name) + "|_", s);

				{
					size_t v = name;
					std::string s(sizeof(size_t), ' ');
					memcpy(s.data(), &v, sizeof(size_t));
					storage.db->Merge(storage.wopts, "t|" + std::to_string(decl->index_in_schema()), s);
				}

				// GlobalId as numeric ref to instance name, so that the guid map in
				// rocks_db_file_storage can resolve by_guid() lookups.
				if (ifcroot_type == nullptr) {
					ifcroot_type = decl->schema()->declaration_by_name("IfcRoot");
				}
				if (decl->is(*ifcroot_type)) {
					// @nb attribute counts are not coerced, so the attribute may be absent
					const bool has_guid = data->storage_->size() > 0 && data->get_attribute_value(0).type() == ifcopenshell::Argument_STRING;
					if (has_guid) {
						size_t v = name;
						std::string s(sizeof(size_t), ' ');
						memcpy(s.data(), &v, sizeof(size_t));
						storage.db->Put(storage.wopts, "g|" + (std::string)data->get_attribute_value(0), s);
					} else {
						::logger::root().error("Instance #" + std::to_string(name) + " has no GlobalId, omitted from guid index");
					}
				}
			}

			streamer.references().clear();
			streamer.inverses().clear();
		}
	}
}

void RocksDbSerializer::finalize() {
	write_streaming_();
}


#endif
