#include "IteratorImplementation.h"

#include <boost/algorithm/string/case_conv.hpp>

template <typename P, typename PP>
IteratorFactoryImplementation<P, PP>& iterator_implementations() {
	static IteratorFactoryImplementation<P, PP> impl;
	return impl;
}

template IFC_GEOM_API IteratorFactoryImplementation<float, float>& iterator_implementations<float, float>();
template IFC_GEOM_API IteratorFactoryImplementation<float, double>& iterator_implementations<float, double>();
template IFC_GEOM_API IteratorFactoryImplementation<double, double>& iterator_implementations<double, double>();

#ifdef HAS_SCHEMA_2x3
template <typename P, typename PP>
extern void init_IteratorImplementation_Ifc2x3(IteratorFactoryImplementation<P, PP>*);
#endif

#ifdef HAS_SCHEMA_4
template <typename P, typename PP>
extern void init_IteratorImplementation_Ifc4(IteratorFactoryImplementation<P, PP>*);
#endif

#ifdef HAS_SCHEMA_4x1
template <typename P, typename PP>
extern void init_IteratorImplementation_Ifc4x1(IteratorFactoryImplementation<P, PP>*);
#endif

#ifdef HAS_SCHEMA_4x2
template <typename P, typename PP>
extern void init_IteratorImplementation_Ifc4x2(IteratorFactoryImplementation<P, PP>*);
#endif

#ifdef HAS_SCHEMA_4x3_rc1
template <typename P, typename PP>
extern void init_IteratorImplementation_Ifc4x3_rc1(IteratorFactoryImplementation<P, PP>*);
#endif

#ifdef HAS_SCHEMA_4x3_rc2
template <typename P, typename PP>
extern void init_IteratorImplementation_Ifc4x3_rc2(IteratorFactoryImplementation<P, PP>*);
#endif

template <typename P, typename PP>
IteratorFactoryImplementation<P, PP>::IteratorFactoryImplementation() {
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

template <typename P, typename PP>
void IteratorFactoryImplementation<P, PP>::bind(const std::string& schema_name, typename get_factory_type<P, PP>::type fn) {
	const std::string schema_name_lower = boost::to_lower_copy(schema_name);
	this->insert(std::make_pair(schema_name_lower, fn));
}

template <typename P, typename PP>
IfcGeom::IteratorImplementation<P, PP>* IteratorFactoryImplementation<P, PP>::construct(const std::string& schema_name, const IfcGeom::IteratorSettings& settings, IfcParse::IfcFile* file, const std::vector<IfcGeom::filter_t>& filters, int num_threads) {
	const std::string schema_name_lower = boost::to_lower_copy(schema_name);
	typename std::map<std::string, typename get_factory_type<P, PP>::type>::const_iterator it;
	it = this->find(schema_name_lower);
	if (it == this->end()) {
		throw IfcParse::IfcException("No geometry iterator registered for " + schema_name);
	}
	return it->second(settings, file, filters, num_threads);
}


template class IteratorFactoryImplementation<float, float>;
template class IteratorFactoryImplementation<float, double>;
template class IteratorFactoryImplementation<double, double>;
