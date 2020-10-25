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

#ifndef IFCCONVERT_UTIL_H
#define IFCCONVERT_UTIL_H

#include <sstream>
#include <vector>

#include <boost/shared_ptr.hpp>

namespace util {
	class string_buffer {
	public:
		class item {
		public:
			virtual std::string str() const = 0;
			virtual ~item() {};
		};
		class string_item : public item {
			std::string s;
		public:
			string_item(const std::string& s) : s(s) {}
			void assign(const std::string& s) { this->s = s; }
			const std::string& value() const { return s; }
			std::string& value() { return s; }
			std::string str() const { return s; }
			virtual ~string_item() {};
		};
		class float_item : public item {
			double d;
		public:
			float_item(const double& d) : d(d) {}
			void assign(const double& d) { this->d = d; }
			const double& value() const { return d; }
			double& value() { return d; }
			std::string str() const { std::stringstream ss; ss << d; return ss.str(); }
			virtual ~float_item() {};
		};
	private:
		std::vector< boost::shared_ptr<item> > items;
		void clear();
		void assign(const std::vector< boost::shared_ptr<item> >& other);
	public:
		boost::shared_ptr<string_item> add(const std::string& s);
		boost::shared_ptr<float_item> add(const double& d);
		std::string str() const;
	};
}

#endif
