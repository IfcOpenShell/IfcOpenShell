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

#ifndef APPSETTINGS_H
#define APPSETTINGS_H

#include <QObject>
#include <QString>

// Application-wide preferences. Cached in memory, persisted via QSettings to
// the OS-native config location (registry on Windows, plist on macOS, INI on
// Linux). Access via AppSettings::instance().
class AppSettings : public QObject {
    Q_OBJECT
public:
    static AppSettings& instance();

    QString geometryLibrary() const;
    void setGeometryLibrary(const QString& value);

    bool showStats() const;
    void setShowStats(bool value);

    bool backfaceCulling() const;
    void setBackfaceCulling(bool value);

    // When true, the IFC/RocksDB file is kept open (and, on sidecar hits,
    // opened in the background) so element properties can be queried.
    // When false, only geometry is loaded — saves memory and avoids a
    // second file read on sidecar hits, at the cost of no property panel.
    bool loadDataSource() const;
    void setLoadDataSource(bool value);

    // Skip elements with more than this many voids (HasOpenings inverse).
    // Boolean subtraction of many openings is the dominant cost in some
    // pathological exports; dropping those elements keeps load times sane.
    int voidLimit() const;
    void setVoidLimit(int value);

signals:
    void geometryLibraryChanged(const QString& value);
    void showStatsChanged(bool value);
    void backfaceCullingChanged(bool value);
    void loadDataSourceChanged(bool value);
    void voidLimitChanged(int value);

private:
    AppSettings();
    void load();
    void persist();

    QString geometry_library_;
    bool show_stats_ = false;
    bool backface_culling_ = true;
    bool load_data_source_ = true;
    int void_limit_ = 30;
};

#endif // APPSETTINGS_H
