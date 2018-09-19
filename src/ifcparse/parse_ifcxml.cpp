#define BOOST_RESULT_OF_USE_DECLTYPE

#include "IfcFile.h"

#include <libxml/parser.h>

#include <boost/algorithm/string/predicate.hpp>
#include <boost/range/adaptor/transformed.hpp>
#include <boost/range/algorithm/copy.hpp>

// For debug printing on release builds
// #undef NDEBUG

// ifcXML is quite radically different for ifc2x3 and ifc4. ifc2x3 follows
// iso 10303 part 28 and puts all attribute values in XML text nodes. ifc4
// has attributes in actual XML attributes and may include inverse attributes
// to make trees more compact.
enum ifcxml_dialect {
	ifcxml_dialect_ifc2x3,
	ifcxml_dialect_ifc4,
	ifcxml_dialect_unknown
};

// "Dereferences" a named_attribute. For example:
// IfcCompoundPlaneAngleMeasure -> LIST [3:4] OF INTEGER
void follow_named(const IfcParse::parameter_type*& pt) {
	while (pt->as_named_type()) {
		if (pt->as_named_type()->declared_type()->as_type_declaration()) {
			pt = pt->as_named_type()->declared_type()->as_type_declaration()->declared_type();
		} else {
			break;
		}
	}
}

// The ifcXML parser uses SAX so we need to keep a stack of where we are in
// the file. These different kinds of nodes could be subclasses but aren't
// for ease in pushing to std::vector.
class stack_node {
public:
	enum node_type { stack_empty, node_instance, node_instance_attribute, node_aggregate, node_aggregate_element, node_inverse, node_select, node_header, node_header_entry };

	std::vector<Argument*> aggregate_elements;
protected:
	node_type type_;
	IfcUtil::IfcBaseClass* inst_;
	int idx_;
	const IfcParse::entity::inverse_attribute* inv_;
	std::string tagname_;
	std::string id_in_file_;
	const IfcParse::parameter_type* aggregate_elem_type_;
		
	stack_node()
		: type_(stack_empty)
		, inst_(nullptr)
		, idx_(-1)
		, inv_(nullptr)
		, aggregate_elem_type_(nullptr) {}

public:
	static stack_node instance(const std::string& id_in_file, IfcUtil::IfcBaseClass* inst) {
		stack_node n;
		n.type_ = node_instance;
		n.inst_ = inst;
		n.id_in_file_ = id_in_file;
		return n;
	}

	static stack_node instance_attribute(IfcUtil::IfcBaseClass* inst, int idx) {
		stack_node n;
		n.type_ = node_instance_attribute;
		n.inst_ = inst;
		n.idx_ = idx;
		return n;
	}

	static stack_node aggregate(IfcUtil::IfcBaseClass* inst, int idx) {
		stack_node n;
		n.type_ = node_aggregate;
		n.inst_ = inst;
		n.idx_ = idx;
		return n;
	}

	static stack_node aggregate_element(const IfcParse::parameter_type* aggregate_elem_type, int idx) {
		stack_node n;
		n.type_ = node_aggregate_element;
		n.idx_ = idx;
		n.aggregate_elem_type_ = aggregate_elem_type;
		return n;
	}

	static stack_node inverse(IfcUtil::IfcBaseClass* inst, const IfcParse::entity::inverse_attribute* inv) {
		stack_node n;
		n.type_ = node_inverse;
		n.inst_ = inst;
		n.inv_ = inv;
		return n;
	}

	static stack_node select(IfcUtil::IfcBaseClass* inst, int idx) {
		stack_node n;
		n.type_ = node_select;
		n.inst_ = inst;
		n.idx_ = idx;
		return n;
	}

	static stack_node header() {
		stack_node n;
		n.type_ = node_header;
		return n;
	};

	static stack_node header_entry(const std::string& tagname) {
		stack_node n;
		n.type_ = node_header_entry;
		n.tagname_ = tagname;
		return n;
	};

	node_type ntype() const { return type_; }

	IfcUtil::IfcBaseClass* inst() const { return inst_; }
	int idx() const { return idx_; }
	const IfcParse::entity::inverse_attribute* inv_attr() const { return inv_; }
	const std::string& tagname() const { return tagname_; }
	const std::string& id_in_file() const { return id_in_file_; }
	const IfcParse::parameter_type* aggregate_elem_type() const { return aggregate_elem_type_; }

	std::string repr() const {
		std::stringstream ss;
		static const char* const node_type_names[] = { "empty", "inst", "attr", "aggr", "agelem", "inv", "sel", "head", "hdentry" };
		ss << "[" << node_type_names[type_] << "] ";
		if (inst_) {
			ss << inst_->declaration().name() << " ";
		}
		if (type_ == node_aggregate) {
			ss << "{" << aggregate_elements.size() << " elems} ";
		}
		if (idx_ != -1) {
			ss << idx_ << " ";
		}
		return ss.str();
	}
};

struct ifcxml_parse_state {
	IfcParse::IfcFile* file;
	std::vector<stack_node> stack;
	std::map<std::string, int> idmap;
	std::vector<std::pair<IfcWrite::IfcWriteArgument*, std::string> > forward_references;
	ifcxml_dialect dialect;
};

// ifc4 allows for aggregates to be concatenated using whitespace.
template <typename T>
std::vector<T> split(const std::string& value) {
	std::vector<std::string> strs;
	boost::split(strs, value, [](char c) { return c == ' '; }, boost::token_compress_on);
	std::vector<T> r(strs.size());
	boost::copy(strs | boost::adaptors::transformed([](const std::string& s) {
		return boost::lexical_cast<T>(s);
	}), r.begin());
	return r;
}

Argument* parse_attribute_value(const IfcParse::parameter_type* ty, const std::string& value) {
	auto v = new IfcWrite::IfcWriteArgument();

	auto cpp_type = IfcUtil::from_parameter_type(ty);
	
	if (cpp_type == IfcUtil::Argument_STRING) {
		v->set(value);
	} else if (cpp_type == IfcUtil::Argument_ENUMERATION) {
		auto enum_type = ty->as_named_type()->declared_type()->as_enumeration_type();

		std::vector<std::string>::const_iterator it = std::find(
			enum_type->enumeration_items().begin(),
			enum_type->enumeration_items().end(),
			boost::to_upper_copy(value));

		if (it != enum_type->enumeration_items().end()) {
			v->set(IfcWrite::IfcWriteArgument::EnumerationReference(it - enum_type->enumeration_items().begin(), it->c_str()));
		}		
	} else if (cpp_type == IfcUtil::Argument_INT) {
		v->set(boost::lexical_cast<int>(value));
	} else if (cpp_type == IfcUtil::Argument_DOUBLE) {
		v->set(boost::lexical_cast<double>(value));
	} else if (cpp_type == IfcUtil::Argument_BOOL) {
		v->set(boost::to_lower_copy(value) == "true");
	} else if (cpp_type == IfcUtil::Argument_AGGREGATE_OF_INT) {
		v->set(split<int>(value));
	} else if (cpp_type == IfcUtil::Argument_AGGREGATE_OF_DOUBLE) {
		v->set(split<double>(value));
	}

	if (v->isNull()) {
		Logger::Error("Attribute '" + value + "' not succesfully parsed");
		delete v;
		v = nullptr;
	}

	return v;
}

static void end_element(void* user, const xmlChar* tag) {
	ifcxml_parse_state* state = (ifcxml_parse_state*)user;

	if (state->file == nullptr) {
		return;
	}
	
	if (!state->stack.empty() && state->stack.back().ntype() == stack_node::node_aggregate) {
		const auto& back = state->stack.back();
		auto& elems = state->stack.back().aggregate_elements;
		auto li = new IfcParse::ArgumentList(elems.size());
		size_t i = 0;
		for (auto& elem : elems) {
			li->arguments()[i++] = elem;
		}
		back.inst()->data().attributes()[back.idx()] = li;
	}

	if (state->dialect == ifcxml_dialect_ifc2x3 && state->stack.back().ntype() == stack_node::node_instance) {
		if (state->stack.back().inst() != nullptr) {
			state->idmap[state->stack.back().id_in_file()] = state->file->addEntity(state->stack.back().inst())->data().id();
		}
	}

	const std::string tagname = (char*)tag;

	// ignore uos ex:iso_10303_28 (ifc2x3) and ifc:ifcXML (ifc4)
	if (tagname != "uos" && tagname != "ex:iso_10303_28" && tagname != "ifc:ifcXML" && tagname != "ifcXML") {
		state->stack.pop_back();
	}	
}

static void process_characters(void* user, const xmlChar* ch, int len) {
	ifcxml_parse_state* state = (ifcxml_parse_state*)user;

	if (state->file == nullptr) {
		return;
	}

	std::string txt((char*) ch, len);

	stack_node::node_type state_type = stack_node::stack_empty;
	if (!state->stack.empty()) {
		state_type = state->stack.back().ntype();
	}

	if (!state->stack.empty() && state->stack.back().inst() != nullptr && state->stack.back().inst()->declaration().as_type_declaration()) {
		auto pt = state->stack.back().inst()->declaration().as_type_declaration()->declared_type();
		auto val = parse_attribute_value(pt, txt);
		if (val) {
			// type declaration always at idx 0
			state->stack.back().inst()->data().setArgument(0, val);
		}
	} else if (state_type == stack_node::node_header_entry) {
		const std::string tagname = boost::replace_all_copy(state->stack.back().tagname(), "ex:", "");
		auto& header = state->file->header();
		if (tagname == "name") {
			header.file_name().name(txt);
		} else if (tagname == "time_stamp") {
			header.file_name().time_stamp(txt);
		} else if (tagname == "author") {
			header.file_name().author({ txt });
		} else if (tagname == "organization") {
			header.file_name().organization({ txt });
		} else if (tagname == "preprocessor_version") {
			header.file_name().preprocessor_version(txt);
		} else if (tagname == "originating_system") {
			header.file_name().originating_system(txt);
		} else if (tagname == "authorization") {
			header.file_name().authorization(txt);
		} else if (tagname == "documentation") {
			header.file_description().description({ txt });
		} else {
			Logger::Error("Unrecognized header entry " + tagname);
		}
	} else if (state_type == stack_node::node_instance_attribute) {
		auto pt = state->stack.back().inst()->declaration().as_entity()->attribute_by_index(state->stack.back().idx())->type_of_attribute();
		auto cpp_type = IfcUtil::from_parameter_type(pt);
		if (cpp_type != IfcUtil::Argument_ENTITY_INSTANCE) {
			auto val = parse_attribute_value(pt, txt);
			if (val) {
				state->stack.back().inst()->data().setArgument(state->stack.back().idx(), val);
			}
		}
	} else if (state_type == stack_node::node_aggregate_element) {
		auto pt = state->stack.back().aggregate_elem_type();
		auto val = parse_attribute_value(pt, txt);
		if (val) {
			(*(state->stack.rbegin() + 1)).aggregate_elements.push_back(val);
		}
	}
}

static void start_element(void* user, const xmlChar* tag, const xmlChar** attrs) {
	ifcxml_parse_state* state = (ifcxml_parse_state*)user;
	std::string tagname = (char*) tag;

#ifndef NDEBUG
	std::cout << "stack:" << std::endl;
	{
		int i = 1;
		for (auto& n : state->stack) {
			std::cout << "  " << (i++) << ":" << n.repr() << std::endl;
		}
	}
	std::cout << std::string(state->stack.size(), ' ') << "<" << tagname << ">";
#endif

	std::vector<std::pair<std::string, std::string> > attributes;

	if (attrs) {
		std::string attrname;
		int i = 0;
		while (attrs[i] != NULL) {
			if (i % 2) {
				const std::string value = (char*) attrs[i];
#ifndef NDEBUG
				std::cout << " " << attrname << "='" << value << "'";
#endif
				attributes.push_back(std::make_pair(attrname, value));

				if ((tagname == "ifc:ifcXML" || tagname == "ifcXML") && attrname == "xsi:schemaLocation" && boost::starts_with(value, "http://www.buildingsmart-tech.org/ifcXML/IFC4")) {
					state->file = new IfcParse::IfcFile(IfcParse::schema_by_name("IFC4"));
					state->file->parsing_complete() = false;
					state->dialect = ifcxml_dialect_ifc4;
					goto end;
				} else if (tagname == "ex:iso_10303_28" && attrname == "xsi:schemaLocation" && boost::starts_with(value, "http://www.iai-tech.org/ifcXML/IFC2x3")) {
					state->file = new IfcParse::IfcFile(IfcParse::schema_by_name("IFC2X3"));
					state->file->parsing_complete() = false;
					state->dialect = ifcxml_dialect_ifc2x3;
					goto end;
				}
			} else {
				attrname = (char*) attrs[i];
			}
			i++;
		}
	}

	if (state->file == nullptr) {
		return;
	}

	{
		// ifcXML id attributes are commonly numeric identifiers prefixed with 'i' (as
		// XML identifiers need to start with a alphabetic character). This convention
		// is not always followed, so a mapping is kept from XML string attribute to
		// numeric index into the IfcParse::IfcFile.
		std::string id_in_file;

		// Create an attribute value from an instance. Potentially NULL in case it is a
		// forward reference to an instance not yet encountered.
		auto instance_to_attribute = [&state](const boost::variant<std::string, IfcUtil::IfcBaseClass*>& inst_or_ref, Argument*& attr, IfcUtil::IfcBaseClass*& inst) {
			IfcWrite::IfcWriteArgument* wattr = new IfcWrite::IfcWriteArgument;
			attr = wattr;
			if (inst_or_ref.which() == 0) {
				inst = nullptr;
				// This attribute is NULL initially and after parsing the complete
				// file populated in a subsequent step.
				state->forward_references.push_back(std::make_pair((IfcWrite::IfcWriteArgument*) attr, boost::get<std::string>(inst_or_ref)));
			} else {
				inst = boost::get<IfcUtil::IfcBaseClass*>(inst_or_ref);
				wattr->set(inst);
			}
		};

		// Create or reference an instance from the file and set attributes based on XML attributes.
		auto create_instance = [&state, &attributes, &id_in_file](const IfcParse::declaration* decl) {
			boost::optional<std::string> id;
			boost::variant<std::string, IfcUtil::IfcBaseClass*> rv;

			for (auto& pair : attributes) {
				if (pair.first == "id" || pair.first == "href" || pair.first == "ref") {
					id = id_in_file = pair.second;
					if (pair.first == "href" || pair.first == "ref") {
						if (state->idmap.find(pair.second) == state->idmap.end()) {
							rv = pair.second;
							return rv;
						} else {
							rv = state->file->instance_by_id(state->idmap[pair.second]);
							return rv;
						}
					}
				} else if (pair.first == "xsi:type") {
					decl = state->file->schema()->declaration_by_name(pair.second)->as_entity();
				}
			}

			auto untyped = new IfcEntityInstanceData(decl);
			
			const IfcParse::entity* entity = decl->as_entity();
			if (entity) {
				for (auto& pair : attributes) {
					if (pair.first == "id" || pair.first == "xsi:type" || pair.first == "pos") {
						continue;
					}

					auto idx = entity->attribute_index(pair.first);
					if (idx != -1) {
						auto attr = entity->attribute_by_index(idx);
						auto val = parse_attribute_value(attr->type_of_attribute(), pair.second);
						if (val) {
							untyped->setArgument(idx, val);
						}
					} else {
						Logger::Error("Unknown attribute '" + pair.first + "' on entity '" + entity->name() + "' with value '" + pair.second + "'");
					}
				}
			}

			IfcUtil::IfcBaseClass* newinst = state->file->schema()->instantiate(untyped);
			
			if (state->dialect == ifcxml_dialect_ifc4) {
				// In IFC2X3 not added directly because attrs such as GlobalId are in
				// subsequent child nodes
				newinst = state->file->addEntity(newinst);
				if (id) {
					state->idmap[*id] = newinst->data().id();
				}
			}

			rv = newinst;
			return rv;
		};

		stack_node::node_type state_type = stack_node::stack_empty;
		if (!state->stack.empty()) {
			state_type = state->stack.back().ntype();
		}

		const std::string tagname_copy = boost::replace_all_copy(tagname, "-wrapper", "");

		if (state_type == stack_node::node_select) {
			const IfcParse::declaration* decl = state->file->schema()->declaration_by_name(tagname_copy);
			Argument* attr;
			IfcUtil::IfcBaseClass* inst;
			auto inst_ = create_instance(decl);
			instance_to_attribute(inst_, attr, inst);
			state->stack.back().inst()->data().setArgument(state->stack.back().idx(), attr);
			state->stack.push_back(stack_node::instance(id_in_file, inst));
		} else if (state_type == stack_node::node_aggregate) {
			
			const IfcParse::parameter_type* attribute_type = state->stack.back().inst()->declaration().as_entity()->attribute_by_index(state->stack.back().idx())->type_of_attribute();
			follow_named(attribute_type);
			const IfcParse::parameter_type* element_type = attribute_type->as_aggregation_type()->type_of_element();
			follow_named(element_type);

			int aggrpos = -1;
			
			/*
			auto it = std::find_if(attributes.begin(), attributes.end(), [](const std::pair<std::string, std::string>& p) {
				return p.first == "pos";
			});
			boost::lexical_cast<int>(it->second);
			*/

			if (element_type->as_simple_type()) {		
				state->stack.push_back(stack_node::aggregate_element(element_type, aggrpos));
			} else {
				const IfcParse::declaration* decl = state->file->schema()->declaration_by_name(tagname_copy);
				auto inst_or_ref = create_instance(decl);
				IfcUtil::IfcBaseClass* inst;
				Argument* attr;
				instance_to_attribute(inst_or_ref, attr, inst);
				state->stack.back().aggregate_elements.push_back(attr);
				state->stack.push_back(stack_node::instance(id_in_file, inst));
			}
		} else if (state_type == stack_node::node_instance) {
			const IfcParse::entity* current = state->stack.back().inst()->declaration().as_entity();
			if (current == nullptr) {
				Logger::Error("'" + state->stack.back().inst()->declaration().name() + "' is not an entity, unable to set attribute '" + tagname + "'");
				// We need to push something on the stack. Likely there has been some extra indirection that is not understood.
				state->stack.push_back(state->stack.back());
			} else {
				auto idx = current->attribute_index(tagname);
				if (idx == -1) {
					auto inverses = current->all_inverse_attributes();
					auto found = std::find_if(inverses.begin(), inverses.end(), [&tagname](const IfcParse::entity::inverse_attribute* attr) {
						return attr->name() == tagname;
					});
					if (found == inverses.end()) {
						Logger::Error("Unknown attribute " + tagname);
						state->stack.push_back(state->stack.back());
					} else {
						if ((*found)->bound1() == 0 && (*found)->bound2() == 1) {
							auto inst_or_ref = create_instance((*found)->entity_reference());
							IfcUtil::IfcBaseClass* inst;
							Argument* attr;
							instance_to_attribute(inst_or_ref, attr, inst);
							if (inst != nullptr) {
								int idx = (*found)->entity_reference()->attribute_index(
									(*found)->attribute_reference()
								);
								IfcWrite::IfcWriteArgument* attr_inv = new IfcWrite::IfcWriteArgument();
								attr_inv->set(state->stack.back().inst());
								inst->data().setArgument(idx, attr_inv);
								state->stack.push_back(stack_node::instance(id_in_file, inst));
							} else {
								Logger::Error("Unknown attribute " + tagname);
								state->stack.push_back(state->stack.back());
							}
						} else {
							state->stack.push_back(stack_node::inverse(state->stack.back().inst(), *found));
						}
					}
				} else {
					const IfcParse::parameter_type* attribute_type = current->attribute_by_index(idx)->type_of_attribute();
					if (state->dialect == ifcxml_dialect_ifc2x3) {
						follow_named(attribute_type);
						if (attribute_type->as_aggregation_type()) {
							state->stack.push_back(stack_node::aggregate(state->stack.back().inst(), idx));
						} else {
							state->stack.push_back(stack_node::instance_attribute(state->stack.back().inst(), idx));
						}
					} else {
						if (IfcUtil::from_parameter_type(attribute_type) == IfcUtil::Argument_ENTITY_INSTANCE) {
							if (auto entity = attribute_type->as_named_type()->declared_type()->as_entity()) {
								auto inst_or_reference = create_instance(entity);
								Argument* attr;
								IfcUtil::IfcBaseClass* newinst;
								instance_to_attribute(inst_or_reference, attr, newinst);
								state->stack.back().inst()->data().setArgument(idx, attr);
								state->stack.push_back(stack_node::instance(id_in_file, newinst));
							} else if (auto select = attribute_type->as_named_type()->declared_type()->as_select_type()) {
								// Select types cause an additional indirection, so the current stack node is simply repeated
								state->stack.push_back(stack_node::select(state->stack.back().inst(), idx));
							}
						} else if (attribute_type->as_aggregation_type()) {
							state->stack.push_back(stack_node::aggregate(state->stack.back().inst(), idx));
						}
					}
				}
			}
		} else if (state->file) {
			if (state_type == stack_node::node_header) {
				state->stack.push_back(stack_node::header_entry(tagname));
			} else if (tagname == "ex:iso_10303_28_header" || tagname == "header") {
				state->stack.push_back(stack_node::header());
			} else if (tagname == "uos") {
				// intentially empty, ignored in end_element() as well
			} else {
				const IfcParse::declaration* decl = state->file->schema()->declaration_by_name(tagname);
				if (!decl) {
					Logger::Error("Not found in schema " + tagname);
					goto end;
				}

				const IfcParse::entity* entity = decl->as_entity();
				if (!entity && state_type != stack_node::node_instance_attribute) {
					Logger::Error("Not an entity definition " + tagname);
					goto end;
				}

				auto inst_or_ref = create_instance(decl);
				IfcUtil::IfcBaseClass* inst;
				Argument* attr;
				instance_to_attribute(inst_or_ref, attr, inst);

				if (state_type == stack_node::node_inverse) {
					int idx = state->stack.back().inv_attr()->entity_reference()->attribute_index(
						state->stack.back().inv_attr()->attribute_reference()
					);
					IfcWrite::IfcWriteArgument* attr_inv = new IfcWrite::IfcWriteArgument();
					attr_inv->set(state->stack.back().inst());
					if (inst) {
						inst->data().setArgument(idx, attr_inv);
					} else {
						Logger::Error("Internal error, inverse attribute not processed");
					}
				} else if (state_type == stack_node::node_instance_attribute) {
					state->stack.back().inst()->data().attributes()[state->stack.back().idx()] = attr;
				}

				if (entity == nullptr) {
					// Type declaration, immediately populate attr 0
					state->stack.push_back(stack_node::instance_attribute(inst, 0));
				} else {
					state->stack.push_back(stack_node::instance(id_in_file, inst));
				}
			}
		}
	}

end:
#ifndef NDEBUG
	std::cout << std::endl;
#endif
	return;
}

#ifdef WITH_IFCXML
IFC_PARSE_API IfcParse::IfcFile* IfcParse::parse_ifcxml(const std::string& filename) {
	ifcxml_parse_state state;
	state.file = nullptr;
	state.dialect = ifcxml_dialect_unknown;
	
	xmlSAXHandler handler;
	memset(&handler, 0, sizeof(xmlSAXHandler));
	handler.startElement = start_element;
	handler.endElement = end_element;
	handler.characters = process_characters;

	xmlSAXUserParseFile(&handler, &state, filename.c_str());

	for (const auto& pair : state.forward_references) {
		auto it = state.idmap.find(pair.second);
		if (it == state.idmap.end()) {
			Logger::Error("Instance with id '" + pair.second + "' not encountered");
		} else {
			pair.first->set(state.file->instance_by_id(it->second));
		}
	}

	state.file->parsing_complete() = true;
	state.file->build_inverses();

	return state.file;
}
#endif
