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

#ifndef IFCVIEWER_LOG_QT_H
#define IFCVIEWER_LOG_QT_H

// Qt-only adjunct to Log.h. Lets the Qt-using TUs (ViewportWindow,
// OverlayRenderer, Federation, SceneLoader …) keep streaming QString
// values through Log::info()/warn() during the in-flight Qt removal —
// once the QString → std::string sweep (#80) lands these TUs stop
// constructing QStrings in log statements and this header goes away.
//
// Lives in src/ifcviewer/ (NOT in IfcViewerCore), so the web build /
// any future Qt-free ViewportCore TU never includes it and never pulls
// in QString.

#include "Log.h"

#include <QByteArray>
#include <QString>

namespace Log {

// The chain `Log::info() << "tag" << qstr` produces a prvalue Stream
// that's then chained through Stream& returned by the member
// operator<<. So both lvalue-ref and rvalue-ref overloads are needed
// for QString to bind regardless of where it appears in the chain.

inline Stream& operator<<(Stream& s, const QString& qs) {
    const QByteArray utf8 = qs.toUtf8();
    std::fwrite(utf8.constData(), 1, std::size_t(utf8.size()), stderr);
    return s;
}
inline Stream&& operator<<(Stream&& s, const QString& qs) {
    s << qs;
    return std::move(s);
}

inline Stream& operator<<(Stream& s, QStringView qsv) {
    const QByteArray utf8 = qsv.toUtf8();
    std::fwrite(utf8.constData(), 1, std::size_t(utf8.size()), stderr);
    return s;
}
inline Stream&& operator<<(Stream&& s, QStringView qsv) {
    s << qsv;
    return std::move(s);
}

} // namespace Log

#endif  // IFCVIEWER_LOG_QT_H
