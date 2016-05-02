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

#include "IfcGeomMaterial.h"

static double black[3] = {0.,0.,0.};

IfcGeom::Material::Material(const IfcGeom::SurfaceStyle* style) : style(style) {}
bool IfcGeom::Material::hasDiffuse() const { return style->Diffuse() ? true : false; }
bool IfcGeom::Material::hasSpecular() const { return style->Specular() ? true : false; }
bool IfcGeom::Material::hasTransparency() const { return style->Transparency() ? true : false; }
bool IfcGeom::Material::hasSpecularity() const { return style->Specularity() ? true : false; }
const double* IfcGeom::Material::diffuse() const { if (hasDiffuse()) return &((*style->Diffuse()).R()); else return black; }
const double* IfcGeom::Material::specular() const { if (hasSpecular()) return &((*style->Specular()).R()); else return black; }
double IfcGeom::Material::transparency() const { if (hasTransparency()) return *style->Transparency(); else return 0; }
double IfcGeom::Material::specularity() const { if (hasSpecularity()) return *style->Specularity(); else return 0; }
const std::string &IfcGeom::Material::name() const { return style->Name(); }
const std::string &IfcGeom::Material::original_name() const { return style->original_name(); }
bool IfcGeom::Material::operator==(const IfcGeom::Material& other) const { return style == other.style; }
