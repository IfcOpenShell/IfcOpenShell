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

/********************************************************************************
 *                                                                              *
 * This file defines the shared pointer implementation to use, shared pointers  *
 * are used extensively in IfcOpenShell                                         *
 *                                                                              *
 ********************************************************************************/

#ifdef __GNUC__
#include <tr1/memory>
#define SHARED_PTR std::tr1::shared_ptr
#else
#if _MSC_VER >= 1600
// MSVC 2008 does not have shared_ptr by default, but it comes
// in a feature pack. Therefore for IDEs prior to MSVC 2010 the
// shared_ptr that ships with boost is used.
#include <memory>
#define SHARED_PTR std::tr1::shared_ptr
#else
#include <boost/shared_ptr.hpp>
#define SHARED_PTR boost::shared_ptr
#endif
#endif