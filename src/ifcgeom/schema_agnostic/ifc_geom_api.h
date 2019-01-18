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

#ifndef IFC_GEOM_API_H
#define IFC_GEOM_API_H

#ifdef IFC_SHARED_BUILD
  #ifdef _WIN32
    #ifdef IFC_GEOM_EXPORTS
      #define IFC_GEOM_API __declspec(dllexport)
    #else
      #define IFC_GEOM_API __declspec(dllimport)
    #endif
  #else // simply assume *nix + GCC-like compiler
    #define IFC_GEOM_API __attribute__((visibility("default")))
  #endif
#else
  #define IFC_GEOM_API
#endif

#endif
