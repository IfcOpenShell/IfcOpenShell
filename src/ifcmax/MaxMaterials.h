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
 * This file defines materials for use in 3ds Max for several IFC datatypes     *
 *                                                                              *
 ********************************************************************************/

#include <string>

#include "Max.h"
#include "stdmat.h"

StdMat2* GetMaterial(const std::string& s) {
	StdMat2* mat = NewDefaultStdMat();
	TimeValue t (-1);
	mat->SetSpecular(Color(0.2f,0.2f,0.2f),t);
	mat->SetAmbient(Color(0.1f,0.1f,0.1f),t);
	mat->SetWire( s == "IfcSpace" || s == "IfcOpeningElement" );
	if ( s == "IfcSite" ) { mat->SetDiffuse(Color(0.75f,0.8f,0.65f),t); }
	if ( s == "IfcSlab" ) { mat->SetDiffuse(Color(0.4f,0.4f,0.4f),t); }
	if ( s == "IfcWallStandardCase" ) { mat->SetDiffuse(Color(0.9f,0.9f,0.9f),t); }
	if ( s == "IfcWall" ) { mat->SetDiffuse(Color(0.9f,0.9f,0.9f),t); }
	if ( s == "IfcWindow" ) { mat->SetDiffuse(Color(0.75f,0.8f,0.75f),t); mat->SetSpecular(Color(1.0f,1.0f,1.0f),t); 
	mat->SetAmbient(Color(0.0f,0.0f,0.0f),t); mat->SetShininess(500.0f,t); mat->SetOpacity(0.3f,t); }
	if ( s == "IfcDoor" ) { mat->SetDiffuse(Color(0.55f,0.3f,0.15f),t); }
	if ( s == "IfcBeam" ) { mat->SetDiffuse(Color(0.75f,0.7f,0.7f),t); }
	if ( s == "IfcRailing" ) { mat->SetDiffuse(Color(0.75f,0.7f,0.7f),t); }
	if ( s == "IfcMember" ) { mat->SetDiffuse(Color(0.75f,0.7f,0.7f),t); }
	return mat;
}