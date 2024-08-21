#include "IfcFile.h"

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
    // Define a template to check if a type is in a boost::variant
    template<typename Variant, typename T>
    struct is_type_in_variant;

    // Specialization for boost::variant
    template<typename T, typename... Types>
    struct is_type_in_variant<boost::variant<Types...>, T>
    {
        // Recursive template to check if T is one of Types
        static constexpr bool value = (std::is_same<T, Types>::value || ...);
    };

    // Helper variable template (C++14 and beyond)
    template<typename Variant, typename T>
    constexpr bool is_type_in_variant_v = is_type_in_variant<Variant, T>::value;


    IfcUtil::ArgumentType get_element_type(IfcUtil::ArgumentType aggregate) {
        switch (aggregate) {
        case IfcUtil::Argument_AGGREGATE_OF_INT:
            return IfcUtil::Argument_INT;
        case IfcUtil::Argument_AGGREGATE_OF_DOUBLE:
            return IfcUtil::Argument_DOUBLE;
        case IfcUtil::Argument_AGGREGATE_OF_STRING:
            return IfcUtil::Argument_STRING;
        case IfcUtil::Argument_AGGREGATE_OF_BINARY:
            return IfcUtil::Argument_BINARY;
        case IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE:
            return IfcUtil::Argument_ENTITY_INSTANCE;

        case IfcUtil::Argument_AGGREGATE_OF_EMPTY_AGGREGATE:
            return IfcUtil::Argument_EMPTY_AGGREGATE;
        case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_INT:
            return IfcUtil::Argument_AGGREGATE_OF_INT;
        case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_DOUBLE:
            return IfcUtil::Argument_AGGREGATE_OF_DOUBLE;
        case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE:
            return IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE;

        default:
            return IfcUtil::Argument_UNKNOWN;
        }
    }

    bool can_coerce(IfcUtil::ArgumentType target, IfcUtil::ArgumentType source) {
        if (source == IfcUtil::Argument_EMPTY_AGGREGATE) {
            return target == IfcUtil::Argument_AGGREGATE_OF_INT ||
                target == IfcUtil::Argument_AGGREGATE_OF_DOUBLE ||
                target == IfcUtil::Argument_AGGREGATE_OF_STRING ||
                target == IfcUtil::Argument_AGGREGATE_OF_BINARY ||
                target == IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE ||
                target == IfcUtil::Argument_AGGREGATE_OF_EMPTY_AGGREGATE ||
                target == IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_INT ||
                target == IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_DOUBLE ||
                target == IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE;
        } if (source == IfcUtil::Argument_AGGREGATE_OF_EMPTY_AGGREGATE) {
            return target == IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_INT ||
                target == IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_DOUBLE ||
                target == IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE;
        } else if (source == IfcUtil::Argument_BOOL && target == IfcUtil::Argument_LOGICAL) {
            return true;
        } else {
            // @todo make it configurable to coerce int to double, which is not standard compliant?
            auto elt = get_element_type(target);
            auto els = get_element_type(source);
            if (elt != IfcUtil::Argument_UNKNOWN && els != IfcUtil::Argument_UNKNOWN) {
                return can_coerce(elt, els);
            }
            return false;
        }
    }

    // we need to have a compatibility between (#123, IfcLengthMeasure(123.))
    // which are different token kinds
    void get_token_type(std::vector<uint8_t>& r, const boost::variant<IfcUtil::IfcBaseClass*,IfcParse::Token, IfcParse::parse_context*>& v) {
        r.push_back((uint8_t)v.which());
        if (v.which() == 0) {
            // pass
        } else if (v.which() == 1) {
            r.push_back((uint8_t)boost::get<IfcParse::Token>(v).type);
        } else if (v.which() == 2) {
            // @todo check for empty aggregate
            get_token_type(r, boost::get<IfcParse::parse_context*>(v)->tokens_.front());
        }
    }

    bool can_coerce(const std::vector<uint8_t>& target, const std::vector<uint8_t>& source) {
        if (target == std::vector<uint8_t>{0, 0} && source == std::vector<uint8_t>{1, IfcParse::Token_IDENTIFIER}) {
            return true;
        }
        if (source == std::vector<uint8_t>{0, 0} && target == std::vector<uint8_t>{1, IfcParse::Token_IDENTIFIER}) {
            return true;
        }
        return source == target;
    }

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
                fn(EnumerationReference(decl->as_enumeration_type(), decl->as_enumeration_type()->lookup_enum_offset(IfcParse::TokenFunc::asStringRef(t))));
            }
        } else if (t.type == IfcParse::Token_FLOAT) {
            fn(IfcParse::TokenFunc::asFloat(t));
        } else if (t.type == IfcParse::Token_IDENTIFIER) {
            fn(IfcParse::reference_or_simple_type{ InstanceReference{ IfcParse::TokenFunc::asIdentifier(t) } });
        } else if (t.type == IfcParse::Token_INT) {
            fn(IfcParse::TokenFunc::asInt(t));
        } else if (t.type == IfcParse::Token_STRING) {
            fn(IfcParse::TokenFunc::asStringRef(t));
        }
    }

    template <typename Fn>
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

        auto append_to_aggregate_storage = [&aggregate_storage](auto v) {
            if constexpr (is_type_in_variant_v<possible_aggregation_types_t, std::vector<std::decay_t<decltype(v)>>>) {
                if (aggregate_storage.which() == 0) {
                    aggregate_storage = std::vector<std::decay_t<decltype(v)>>{ v };
                } else {
                    auto* vec_ptr = boost::get< std::vector<std::decay_t<decltype(v)>>>(&aggregate_storage);
                    if (vec_ptr) {
                        vec_ptr->push_back(v);
                    } else {
                        // inconsistent aggregate valuation
                    }
                }
            } else {
                // unsupported aggregate type
            }
        };

        for (auto& t : p.tokens_) {
            boost::apply_visitor([&aggregate_storage, &append_to_aggregate_storage, aggr](auto& v) {
                if constexpr (std::is_same_v<std::decay_t<decltype(v)>, IfcParse::Token>) {
                    // @todo get aggregate of enumeration
                    dispatch_token(v, aggr && aggr->type_of_element()->as_named_type() ? aggr->type_of_element()->as_named_type()->declared_type() : nullptr, append_to_aggregate_storage);
                } else if constexpr (std::is_same_v<std::decay_t<decltype(v)>, IfcParse::parse_context*>) {
                    /*construct_(*v, [&aggregate_storage](auto& v) {
                        if (aggregate_storage.which() == 0) {
                            aggregate_storage = std::vector<std::decay_t<decltype(v)>>{ v };
                        } else {
                            boost::get<std::vector<std::decay_t<decltype(v)>>>(aggregate_storage).push_back(v);
                        }
                    });*/
                    // Too deeply nested list
                } else {
                    append_to_aggregate_storage(v);
                }
            }, t);
        }

        boost::apply_visitor(fn, aggregate_storage);
    }
}

IfcEntityInstanceData IfcParse::parse_context::construct(int name, unresolved_references& references_to_resolve, const IfcParse::declaration* decl) {
    std::vector<const IfcParse::parameter_type*> parameter_types;

    if ((decl != nullptr) && (decl->as_type_declaration() != nullptr)) {
        parameter_types = { decl->as_type_declaration()->declared_type() };
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

    if ((decl != nullptr) && (tokens_.size() != parameter_types.size())) {
        // warning
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

        boost::apply_visitor([this, &storage, name, &references_to_resolve, index, param_type](auto& v) {
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
                    while (pt->as_named_type()) {
                        pt = pt->as_named_type()->declared_type()->as_type_declaration()->declared_type();
                    }
                }
                construct_(*v, pt ? pt->as_aggregation_type() : nullptr, [this, &storage, name, &references_to_resolve, index](const auto& v) {
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