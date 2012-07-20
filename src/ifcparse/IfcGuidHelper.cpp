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
 * Please consider this a placeholder for an actual GlobalId generation         *
 * algorithm. A real implementation could for example be based on Boost::uuid   *
 *                                                                              *
 ********************************************************************************/

#include <time.h>

#include "IfcWrite.h"

static const char* chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_$";

IfcWrite::IfcGuidHelper::IfcGuidHelper() {
	if ( ! seeded ) { srand((unsigned int)time(0)); seeded = true; }
	data.resize(length);
	for ( unsigned int i = 0; i < length; ++ i ) {
		data[i] = chars[rand()%strlen(chars)];
	}
}
IfcWrite::IfcGuidHelper::operator std::string() const {
	return data;
}

bool IfcWrite::IfcGuidHelper::seeded = false;