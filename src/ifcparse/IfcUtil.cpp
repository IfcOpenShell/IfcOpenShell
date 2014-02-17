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
IfcEntities IfcEntityList::getInverse(IfcSchema::Type::Enum c) {
	IfcEntities l = IfcEntities(new IfcEntityList());
	for( it i = begin(); i != end(); ++i  ) {
		l->push((*i)->entity->getInverse(c));
	}
	return l;
}
IfcEntities IfcEntityList::getInverse(IfcSchema::Type::Enum c, int ar, const std::string& a) {
	IfcEntities l = IfcEntities(new IfcEntityList());
	for( it i = begin(); i != end(); ++i  ) {
		l->push((*i)->entity->getInverse(c,ar,a));
	}
	return l;
}
 
bool IfcUtil::IfcEntitySelect::is(IfcSchema::Type::Enum v) const { return entity->is(v); }
IfcSchema::Type::Enum IfcUtil::IfcEntitySelect::type() const { return entity->type(); }
IfcUtil::IfcEntitySelect::IfcEntitySelect(IfcSchemaEntity b) { entity = b->entity; }
IfcUtil::IfcEntitySelect::IfcEntitySelect(IfcAbstractEntityPtr e) { entity = e; }
bool IfcUtil::IfcEntitySelect::isSimpleType() { return false; }
IfcUtil::IfcEntitySelect::~IfcEntitySelect() { delete entity; }

bool IfcUtil::IfcArgumentSelect::is(IfcSchema::Type::Enum v) const { return _type == v; }
IfcSchema::Type::Enum IfcUtil::IfcArgumentSelect::type() const { return _type; }
IfcUtil::IfcArgumentSelect::IfcArgumentSelect(IfcSchema::Type::Enum t, ArgumentPtr a) { _type = t; arg = a; }
ArgumentPtr IfcUtil::IfcArgumentSelect::wrappedValue() { return arg; }
bool IfcUtil::IfcArgumentSelect::isSimpleType() { return true; }
IfcUtil::IfcArgumentSelect::~IfcArgumentSelect() { delete arg; }

void Logger::SetOutput(std::ostream* l1, std::ostream* l2) { 
	log1 = l1; 
	log2 = l2; 
	if ( ! log2 ) {
		log2 = &log_stream;
	}
}
void Logger::Message(Logger::Severity type, const std::string& message, const IfcAbstractEntityPtr entity) {
	if ( log2 && type >= verbosity ) {
		(*log2) << "[" << severity_strings[type] << "] " << message << std::endl;
		if ( entity ) (*log2) << entity->toString() << std::endl;
	}
}
void Logger::Status(const std::string& message, bool new_line) {
	if ( log1 ) {
		(*log1) << message;
		if ( new_line ) (*log1) << std::endl;
		else (*log1) << std::flush;
	}
}
void Logger::ProgressBar(int progress) {
	if ( log1 ) {
		Status("\r[" + std::string(progress,'#') + std::string(50 - progress,' ') + "]", false);
	}
}
std::string Logger::GetLog() {
	return log_stream.str();
}
void Logger::Verbosity(Logger::Severity v) { verbosity = v; }
Logger::Severity Logger::Verbosity() { return verbosity; }

std::ostream* Logger::log1 = 0;
std::ostream* Logger::log2 = 0;
std::stringstream Logger::log_stream;
Logger::Severity Logger::verbosity = Logger::LOG_NOTICE;
const char* Logger::severity_strings[] = { "Notice","Warning","Error" };