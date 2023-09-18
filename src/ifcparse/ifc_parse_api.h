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

#ifndef IFC_PARSE_API_H
#define IFC_PARSE_API_H

#ifdef IFC_SHARED_BUILD
#ifdef _WIN32
#ifdef IFC_PARSE_EXPORTS
#define IFC_PARSE_API __declspec(dllexport)
#else
#define IFC_PARSE_API __declspec(dllimport)
#endif
#else // simply assume *nix + GCC-like compiler
#define IFC_PARSE_API __attribute__((visibility("default")))
#endif
#else
#define IFC_PARSE_API
#endif

#if defined(__clang__)
#define my_thread_local thread_local
#elif defined(__GNUC__)
#define my_thread_local __thread
#elif __STDC_VERSION__ >= 201112L
#define my_thread_local _Thread_local
#elif defined(_MSC_VER)
#define my_thread_local __declspec(thread)
#elif defined(SWIG)
#else
#error Cannot define thread_local
#endif

#endif
