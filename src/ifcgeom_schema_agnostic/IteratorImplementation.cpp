#include "IteratorImplementation.h"

#include <boost/algorithm/string/case_conv.hpp>

IteratorFactoryImplementation& iterator_implementations() {
	static IteratorFactoryImplementation impl;
	return impl;
}

#ifdef HAS_SCHEMA_2x3
extern void init_IteratorImplementation_Ifc2x3(IteratorFactoryImplementation*);
#endif

#ifdef HAS_SCHEMA_4
extern void init_IteratorImplementation_Ifc4(IteratorFactoryImplementation*);
#endif

#ifdef HAS_SCHEMA_4x1
extern void init_IteratorImplementation_Ifc4x1(IteratorFactoryImplementation*);
#endif

#ifdef HAS_SCHEMA_4x2
extern void init_IteratorImplementation_Ifc4x2(IteratorFactoryImplementation*);
#endif

#ifdef HAS_SCHEMA_4x3_rc1
extern void init_IteratorImplementation_Ifc4x3_rc1(IteratorFactoryImplementation*);
#endif

#ifdef HAS_SCHEMA_4x3_rc2
extern void init_IteratorImplementation_Ifc4x3_rc2(IteratorFactoryImplementation*);
#endif

IteratorFactoryImplementation::IteratorFactoryImplementation() {
#ifdef HAS_SCHEMA_2x3
	init_IteratorImplementation_Ifc2x3(this);
#endif	
#ifdef HAS_SCHEMA_4
	init_IteratorImplementation_Ifc4(this);
#endif	
#ifdef HAS_SCHEMA_4x1
	init_IteratorImplementation_Ifc4x1(this);
#endif	
#ifdef HAS_SCHEMA_4x2
	init_IteratorImplementation_Ifc4x2(this);
#endif	
#ifdef HAS_SCHEMA_4x3_rc1
	init_IteratorImplementation_Ifc4x3_rc1(this);
#endif	
#ifdef HAS_SCHEMA_4x3_rc2
	init_IteratorImplementation_Ifc4x3_rc2(this);
#endif
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
