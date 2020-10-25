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

#ifndef IFCMAX_H
#define IFCMAX_H

#include "Max.h"

extern ClassDesc* GetIFCImpDesc();

class IFCImp : public SceneImport 
{
public:
	int ExtCount();                   //  = 1
	const TCHAR * Ext(int n);         //  = "IFC"
	const TCHAR * LongDesc();         //  = "IfcOpenShell IFC Importer for 3ds Max"
	const TCHAR * ShortDesc();        //  = "Industry Foundation Classes"
	const TCHAR * AuthorName();       //  = "Thomas Krijnen"
	const TCHAR * CopyrightMessage(); //  = "Copyright (c) 2011-2016 IfcOpenShell"
	const TCHAR * OtherMessage1();    //  = ""
	const TCHAR * OtherMessage2();    //  = ""
	unsigned int Version();           //  = 12
	void	ShowAbout(HWND hWnd);
	int		DoImport(const TCHAR *name,ImpInterface *ei,Interface *i, BOOL suppressPrompts);
};

#endif
