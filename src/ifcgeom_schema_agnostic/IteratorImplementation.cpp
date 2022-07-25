#include "IteratorImplementation.h"

#include <boost/preprocessor/stringize.hpp>
#include <boost/preprocessor/seq/for_each.hpp>
#include <boost/algorithm/string/case_conv.hpp>

// Declares the schema-based external iterator initialization routines:
// - extern void init_IteratorImplementation_Ifc2x3(IteratorFactoryImplementation*);
// - ...
#define EXTERNAL_DEFS(r, data, elem) \
	extern void BOOST_PP_CAT(init_IteratorImplementation_Ifc, elem)(IteratorFactoryImplementation*);

// Declares the schema-based external iterator initialization routines:
// - init_IteratorImplementation_Ifc2x3(this);
// - ...
#define CALL_DEFS(r, data, elem) \
	BOOST_PP_CAT(init_IteratorImplementation_Ifc, elem)(this);

IFC_GEOM_API IteratorFactoryImplementation& iterator_implementations() {
	static IteratorFactoryImplementation impl;
	return impl;
}

BOOST_PP_SEQ_FOR_EACH(EXTERNAL_DEFS, , SCHEMA_SEQ)

IteratorFactoryImplementation::IteratorFactoryImplementation() {
	BOOST_PP_SEQ_FOR_EACH(CALL_DEFS, , SCHEMA_SEQ)
}

void IteratorFactoryImplementation::bind(const std::string& schema_name, iterator_fn fn) {
	const std::string schema_name_lower = boost::to_lower_copy(schema_name);
	this->insert(std::make_pair(schema_name_lower, fn));
}

IfcGeom::IteratorImplementation* IteratorFactoryImplementation::construct(const std::string& schema_name, const IfcGeom::IteratorSettings& settings, IfcParse::IfcFile* file, const std::vector<IfcGeom::filter_t>& filters, int num_threads) {
	const std::string schema_name_lower = boost::to_lower_copy(schema_name);
	typename std::map<std::string, iterator_fn>::const_iterator it;
	it = this->find(schema_name_lower);
	if (it == this->end()) {
		throw IfcParse::IfcException("No geometry iterator registered for " + schema_name);
	}
	return it->second(settings, file, filters, num_threads);
}
