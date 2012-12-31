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

#include "IfcUtil.h"
#include <iostream>

void IfcEntityList::push(IfcUtil::IfcSchemaEntity l) {
	if ( l ) ls.push_back(l);
}
void IfcEntityList::push(IfcEntities l) {
	for( it i = l->begin(); i != l->end(); ++i  ) {
		if ( *i ) ls.push_back(*i);
	}
}
int IfcEntityList::Size() const { return (unsigned int) ls.size(); }
IfcEntityList::it IfcEntityList::begin() { return ls.begin(); }
IfcEntityList::it IfcEntityList::end() { return ls.end(); }
IfcUtil::IfcSchemaEntity IfcEntityList::operator[] (int i) {
	return ls[i];
}
IfcEntities IfcEntityList::getInverse(Ifc2x3::Type::Enum c) {
	IfcEntities l = IfcEntities(new IfcEntityList());
	for( it i = begin(); i != end(); ++i  ) {
		l->push((*i)->entity->getInverse(c));
	}
	return l;
}
IfcEntities IfcEntityList::getInverse(Ifc2x3::Type::Enum c, int ar, const std::string& a) {
	IfcEntities l = IfcEntities(new IfcEntityList());
	for( it i = begin(); i != end(); ++i  ) {
		l->push((*i)->entity->getInverse(c,ar,a));
	}
	return l;
}
 
bool IfcUtil::IfcEntitySelect::is(Ifc2x3::Type::Enum v) const { return entity->is(v); }
Ifc2x3::Type::Enum IfcUtil::IfcEntitySelect::type() const { return entity->type(); }
IfcUtil::IfcEntitySelect::IfcEntitySelect(IfcSchemaEntity b) { entity = b->entity; }
IfcUtil::IfcEntitySelect::IfcEntitySelect(IfcAbstractEntityPtr e) { entity = e; }
bool IfcUtil::IfcEntitySelect::isSimpleType() { return false; }
IfcUtil::IfcEntitySelect::~IfcEntitySelect() { delete entity; }

bool IfcUtil::IfcArgumentSelect::is(Ifc2x3::Type::Enum v) const { return _type == v; }
Ifc2x3::Type::Enum IfcUtil::IfcArgumentSelect::type() const { return _type; }
IfcUtil::IfcArgumentSelect::IfcArgumentSelect(Ifc2x3::Type::Enum t, ArgumentPtr a) { _type = t; arg = a; }
ArgumentPtr IfcUtil::IfcArgumentSelect::wrappedValue() { return arg; }
bool IfcUtil::IfcArgumentSelect::isSimpleType() { return true; }
IfcUtil::IfcArgumentSelect::~IfcArgumentSelect() { delete arg; }
