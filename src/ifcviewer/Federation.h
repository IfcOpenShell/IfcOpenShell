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

#ifndef FEDERATION_H
#define FEDERATION_H

#include <QObject>
#include <QString>
#include <QStringList>
#include <QDateTime>
#include <QVector3D>

#include <vector>

// In-memory representation of an .ifcfed file (IFC federation).
//
// A federation is a named, ordered list of model sources plus an optional
// "home view" camera state.  Source paths can be relative (resolved against
// the .ifcfed's directory) or absolute.  Save() reserialises paths relative
// when they live under the federation file's directory tree, absolute
// otherwise — Save As recomputes against the new location.
//
// Round-trip-only fields today (no UI to edit, but preserved across load/
// save): per-model `visible`, future cloud `source.kind`s.
class Federation : public QObject {
    Q_OBJECT
public:
    struct HomeView {
        QVector3D target;
        float distance = 50.0f;
        float yaw = 45.0f;     // degrees
        float pitch = 30.0f;   // degrees
    };

    struct Model {
        QString id;                       // stable, persisted
        QString display_name;
        QString source_kind = "local";    // future: "http", "speckle", ...
        QString source_path;              // resolved absolute when kind == "local"
        bool visible = true;
    };

    explicit Federation(QObject* parent = nullptr);

    // Round-trip
    bool load(const QString& path, QStringList* warnings, QString* err);
    bool save(const QString& path, QString* err);

    // Mutations
    void clear();
    QString addModel(const QString& source_path,
                     const QString& display_name = QString());
    void removeModel(const QString& fed_id);
    void setHomeView(const HomeView& hv);
    void clearHomeView();

    // Accessors
    const std::vector<Model>& models() const { return models_; }
    const Model* findById(const QString& fed_id) const;
    bool isDirty() const { return dirty_; }
    void markClean();
    QString filePath() const { return file_path_; }
    QString name() const { return name_; }
    bool hasHomeView() const { return has_home_view_; }
    const HomeView& homeView() const { return home_view_; }

signals:
    void dirtyChanged(bool dirty);

private:
    void setDirty(bool d);
    static QString generateId();
    static bool isFederationPath(const QString& path);

    QString file_path_;
    QString name_;
    QDateTime created_;
    QDateTime modified_;
    std::vector<Model> models_;
    bool has_home_view_ = false;
    HomeView home_view_;
    bool dirty_ = false;
};

#endif // FEDERATION_H
