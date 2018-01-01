#include "Kernel.h"

IfcGeom::Kernel::Kernel(IfcParse::IfcFile* file) {
	if (file != 0) {
		if (file->schema() == 0) {
			throw IfcParse::IfcException("No schema associated with file");
		}

		const std::string& schema_name = file->schema()->name();
		implementation_ = impl::kernel_implementations().construct(schema_name, file);
	}
}

int IfcGeom::Kernel::count(const TopoDS_Shape& s, TopAbs_ShapeEnum t) {
	int i = 0;
	TopExp_Explorer exp(s, t);
	for (; exp.More(); exp.Next()) {
		++i;
	}
	return i;
}

IfcGeom::impl::KernelFactoryImplementation& IfcGeom::impl::kernel_implementations() {
	static KernelFactoryImplementation impl;
	return impl;
}

extern void init_KernelImplementation_Ifc2x3(IfcGeom::impl::KernelFactoryImplementation*);
extern void init_KernelImplementation_Ifc4(IfcGeom::impl::KernelFactoryImplementation*);

IfcGeom::impl::KernelFactoryImplementation::KernelFactoryImplementation() {
	init_KernelImplementation_Ifc2x3(this);
	init_KernelImplementation_Ifc4(this);
}

void IfcGeom::impl::KernelFactoryImplementation::bind(const std::string& schema_name, IfcGeom::impl::kernel_fn fn) {
	const std::string schema_name_lower = boost::to_lower_copy(schema_name);
	this->insert(std::make_pair(schema_name_lower, fn));
}

IfcGeom::Kernel* IfcGeom::impl::KernelFactoryImplementation::construct(const std::string& schema_name, IfcParse::IfcFile* file) {
	const std::string schema_name_lower = boost::to_lower_copy(schema_name);
	std::map<std::string, IfcGeom::impl::kernel_fn>::const_iterator it;
	it = this->find(schema_name_lower);
	if (it == end()) {
		throw IfcParse::IfcException("No geometry kernel registered for " + schema_name);
	}
	return it->second(file);
}
