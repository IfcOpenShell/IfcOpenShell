#include "IfcFile.h"
#include "IfcLogger.h"

IfcParse::parse_context::~parse_context() {
    for (auto& t : tokens_) {
        boost::apply_visitor([](auto& v) {
            if constexpr (std::is_same_v<std::decay_t<decltype(v)>, parse_context*>) {
                delete v;
            }
        }, t);
    }
}

IfcParse::parse_context& IfcParse::parse_context::push() {
    auto* pc = new IfcParse::parse_context;
    tokens_.push_back(pc);
    return *pc;
}

void IfcParse::parse_context::push(Token t) {
    tokens_.push_back(t);
}

void IfcParse::parse_context::push(IfcUtil::IfcBaseClass* inst) {
    tokens_.push_back(inst);
}

namespace {
    template<typename Variant, typename T>
    struct is_type_in_variant;

    // Specialization when there are multiple types in the variant
    template<typename T, typename First, typename... Rest>
    struct is_type_in_variant<boost::variant<First, Rest...>, T>
    {
        static constexpr bool value = std::is_same<T, First>::value || is_type_in_variant<boost::variant<Rest...>, T>::value;
    };

    // Specialization when there is only one type left in the variant
    template<typename T, typename Last>
    struct is_type_in_variant<boost::variant<Last>, T>
    {
        static constexpr bool value = std::is_same<T, Last>::value;
    };

    template<typename Variant, typename T>
    constexpr bool is_type_in_variant_v = is_type_in_variant<Variant, T>::value;

    struct InstanceReference {
        int v;
        operator int() const {
            return v;
        }
    };

    template <typename Fn>
    void dispatch_token(IfcParse::Token t, IfcParse::declaration* decl, Fn fn) {
        if (t.type == IfcParse::Token_BINARY) {
            fn(IfcParse::TokenFunc::asBinary(t));
        } else if (t.type == IfcParse::Token_BOOL) {
            fn(IfcParse::TokenFunc::asBool(t));
        } else if (t.type == IfcParse::Token_ENUMERATION) {
            if (decl->as_enumeration_type()) {
                try {
                    fn(EnumerationReference(decl->as_enumeration_type(), decl->as_enumeration_type()->lookup_enum_offset(IfcParse::TokenFunc::asStringRef(t))));
                } catch (IfcParse::IfcException& e) {
                    Logger::Error(e);
                }
            }
        } else if (t.type == IfcParse::Token_FLOAT) {
            fn(IfcParse::TokenFunc::asFloat(t));
        } else if (t.type == IfcParse::Token_IDENTIFIER) {
            fn(IfcParse::reference_or_simple_type{ InstanceReference{ IfcParse::TokenFunc::asIdentifier(t) } });
        } else if (t.type == IfcParse::Token_INT) {
            fn(IfcParse::TokenFunc::asInt(t));
        } else if (t.type == IfcParse::Token_STRING) {
            fn(IfcParse::TokenFunc::asStringRef(t));
        } else if (t.type == IfcParse::Token_OPERATOR && t.value_char == '*') {
            // This is only in place for the validator
            fn(Derived{});
        }
    }

    template <size_t Depth, typename Fn>
    void construct_(IfcParse::parse_context& p, const IfcParse::aggregation_type* aggr, Fn fn) {
        if (p.tokens_.empty()) {
            // @todo instead of ugly if-else we could also default initialize the respective
            // variant types below.
            if (aggr) {
                auto aggr_type = IfcUtil::make_aggregate(IfcUtil::from_parameter_type(aggr->type_of_element()));
                if (aggr_type == IfcUtil::Argument_AGGREGATE_OF_INT) {
                    fn(std::vector<int>{});
                } else if (aggr_type == IfcUtil::Argument_AGGREGATE_OF_DOUBLE) {
                    fn(std::vector<double>{});
                } else if (aggr_type == IfcUtil::Argument_AGGREGATE_OF_STRING) {
                    fn(std::vector<std::string>{});
                } else if (aggr_type == IfcUtil::Argument_AGGREGATE_OF_BINARY) {
                    fn(std::vector<boost::dynamic_bitset<>>{});
                } else if (aggr_type == IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE) {
                    fn(aggregate_of_instance::ptr(new aggregate_of_instance));
                } else if (aggr_type == IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_INT) {
                    fn(std::vector<std::vector<int>>{});
                } else if (aggr_type == IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_DOUBLE) {
                    fn(std::vector<std::vector<double>>{});
                } else if (aggr_type == IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE) {
                    fn(aggregate_of_aggregate_of_instance::ptr(new aggregate_of_aggregate_of_instance));
                }
            }
            return;
        }

        typedef boost::variant<
            Blank,

            std::vector<int>,
            std::vector<double>,
            std::vector<std::string>,
            std::vector<boost::dynamic_bitset<>>,
            std::vector<IfcParse::reference_or_simple_type>,

            std::vector<std::vector<int>>,
            std::vector<std::vector<double>>,
            std::vector<std::vector<IfcParse::reference_or_simple_type>>
        > possible_aggregation_types_t;

        possible_aggregation_types_t aggregate_storage;

        auto append_to_aggregate_storage = [&aggregate_storage](const auto& v) {
            if constexpr (is_type_in_variant_v<possible_aggregation_types_t, std::vector<std::decay_t<decltype(v)>>>) {
                if (aggregate_storage.which() == 0) {
                    aggregate_storage = std::vector<std::decay_t<decltype(v)>>{ v };
                } else {
                    auto* vec_ptr = boost::get<std::vector<std::decay_t<decltype(v)>>>(&aggregate_storage);
                    if (vec_ptr) {
                        vec_ptr->push_back(v);
                    } else {
                        // @todo would be cool if we can trace this back to file offset
                        auto current = boost::apply_visitor([](auto v) { 
                            if constexpr (!std::is_same_v<decltype(v), Blank>) {
                                return std::string(typeid(typename decltype(v)::value_type).name());
                            } else {
                                // Cannot occur as aggregate_storage.which() == 0
                                // is another branch several statements up. But is
                                // needed for consistency of return type.
                                return std::string{};
                            }
                        }, aggregate_storage);
                        Logger::Error("Inconsistent aggregate valuation while attempting to append " + std::string(typeid(decltype(v)).name()) + " to an aggregate of " + current);

                        // @todo boolean -> logical upgrade
                        // wait a second... there are no aggregate of bool / logical in the schema..
                        // 
                        // if constexpr (std::is_same_v<std::decay_t<decltype(v)>, bool>) {
                        //     auto* vec_ptr = boost::get<std::vector<boost::tribool>(&aggregate_storage);
                        //     vec_ptr->push_back(v);
                        // }
                        // if constexpr (std::is_same_v<std::decay_t<decltype(v)>, boost::tribool>) {
                        //     auto* vec_ptr = boost::get<std::vector<bool>(&aggregate_storage);
                        //     std::vector<boost::tribool> ps(vec_ptr->begin(), vec_ptr->end());
                        //     ps.push_back(v);
                        //     aggregate_storage = ps;
                        // }
                    }
                }
            } else {
                // @todo would be cool if we can trace this back to file offset
                Logger::Error(std::string("Aggregates of ") + typeid(decltype(v)).name() + " are not supported in the IfcOpenShell parser");
            }
        };

        for (auto& t : p.tokens_) {
            boost::apply_visitor([&aggregate_storage, &append_to_aggregate_storage, aggr](const auto& v) {
                if constexpr (std::is_same_v<std::decay_t<decltype(v)>, IfcParse::Token>) {
                    // @todo get aggregate of enumeration
                    dispatch_token(v, aggr && aggr->type_of_element()->as_named_type() ? aggr->type_of_element()->as_named_type()->declared_type() : nullptr, append_to_aggregate_storage);
                } else if constexpr (std::is_same_v<std::decay_t<decltype(v)>, IfcParse::parse_context*>) {
                    // nested list
                    if constexpr (Depth < 3) {
                        construct_<Depth + 1>(*v, nullptr, append_to_aggregate_storage);
                    }
                } else {
                    append_to_aggregate_storage(IfcParse::reference_or_simple_type{ v });
                }
            }, t);
        }

        boost::apply_visitor(fn, aggregate_storage);
    }
}

IfcEntityInstanceData IfcParse::parse_context::construct(int name, unresolved_references& references_to_resolve, const IfcParse::declaration* decl, boost::optional<size_t> expected_size) {
    std::vector<const IfcParse::parameter_type*> parameter_types;
    std::unique_ptr<IfcParse::named_type> transient_named_type;

    if ((decl != nullptr) && (decl->as_type_declaration() != nullptr)) {
        parameter_types = { decl->as_type_declaration()->declared_type() };
    } else if ((decl != nullptr) && (decl->as_enumeration_type() != nullptr)) {
        transient_named_type.reset(new IfcParse::named_type(const_cast<IfcParse::declaration*>(decl)));
        parameter_types = { &*transient_named_type };
    } else if ((decl != nullptr) && (decl->as_entity() != nullptr)) {
        auto entity_attrs = decl->as_entity()->all_attributes();
        std::transform(
            entity_attrs.begin(),
            entity_attrs.end(),
            std::back_inserter(parameter_types),
            [](auto* attr) {
                return attr->type_of_attribute();
            }
        );
    }

    if (((decl != nullptr) && (tokens_.size() != parameter_types.size())) ||
        expected_size && *expected_size != tokens_.size())
    {
        size_t expected = expected_size ? *expected_size : parameter_types.size();
        Logger::Warning("Expected " + std::to_string(expected) + " attribute values, found " + std::to_string(tokens_.size()) + " for instance #" + std::to_string(name > 0 ? name : 0));
    }

    if (tokens_.empty()) {
        return IfcEntityInstanceData(storage_t(0));
    }

    storage_t storage(decl != nullptr
        ? (std::min)(parameter_types.size(), tokens_.size())
        : tokens_.size()
    );

    auto it = tokens_.begin();
    auto kt = parameter_types.begin();
    for (; it != tokens_.end() && ((decl == nullptr) || kt != parameter_types.end()); ++it) {
        auto& token = *it;
        // @todo coerce to expected type, e.g empty -> std::vector<int>, bool -> logical
        const IfcParse::parameter_type* param_type = nullptr;
        if (decl != nullptr) {
            param_type = *kt;
        }

        auto index = (uint8_t) std::distance(tokens_.begin(), it);

        boost::apply_visitor([this, &storage, name, &references_to_resolve, index, param_type](const auto& v) {
            if constexpr (std::is_same_v<std::decay_t<decltype(v)>, IfcParse::Token>) {
                dispatch_token(v, param_type && param_type->as_named_type() ? param_type->as_named_type()->declared_type() : nullptr, [this, &storage, name, &references_to_resolve, index](auto v) {
                    if constexpr (std::is_same_v<std::decay_t<decltype(v)>, IfcParse::reference_or_simple_type>) {
                        references_to_resolve.push_back(std::make_pair(
                            // @todo previously this was storage but apparently the 
                            // pointer is not constant with the moving and temporary nature
                            // maybe it ought to be and in that case a pointer is more direct
                            MutableAttributeValue{ name, index },
                            v
                        ));
                    } else {
                        storage.set(index, v);
                    }
                });
            } else if constexpr (std::is_same_v<std::decay_t<decltype(v)>, IfcParse::parse_context*>) {
                const auto *pt = param_type;
                if (pt) {
                    while (pt->as_named_type() && pt->as_named_type()->declared_type()->as_type_declaration()) {
                        pt = pt->as_named_type()->declared_type()->as_type_declaration()->declared_type();
                    }
                }
                construct_<0>(*v, pt ? pt->as_aggregation_type() : nullptr, [this, &storage, name, &references_to_resolve, index](const auto& v) {
                    if constexpr (std::is_same_v<std::decay_t<decltype(v)>, std::vector<reference_or_simple_type>>) {
                        references_to_resolve.push_back({ {name, index }, v });
                    } else if constexpr (std::is_same_v<std::decay_t<decltype(v)>, std::vector<std::vector<reference_or_simple_type>>>) {
                        references_to_resolve.push_back({ {name, index }, v });
                    } else {
                        storage.set(index, v);
                    }
                });
            } else {
                storage.set(index, v);
            }
        }, token);

        if (decl != nullptr) {
            ++kt;
        }
    }

    return IfcEntityInstanceData(std::move(storage));
}
