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

#include "Federation.h"

#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <QSaveFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonValue>
#include <QUuid>

namespace {
constexpr const char* kSchema = "ifcfed/1";

QString resolvePath(const QString& fed_dir, const QString& stored) {
    if (stored.isEmpty()) return stored;
    QFileInfo fi(stored);
    if (fi.isAbsolute()) return QDir::cleanPath(stored);
    return QDir::cleanPath(QDir(fed_dir).absoluteFilePath(stored));
}

// Returns abs_path relative to fed_dir if abs_path lives under fed_dir,
// otherwise returns abs_path unchanged.
QString relativizePath(const QString& fed_dir, const QString& abs_path) {
    QString fed_canon = QDir::cleanPath(fed_dir);
    QString abs_canon = QDir::cleanPath(abs_path);
    if (!fed_canon.endsWith('/')) fed_canon += '/';
    if (abs_canon.startsWith(fed_canon)) {
        return QDir(fed_canon).relativeFilePath(abs_canon);
    }
    return abs_canon;
}
}  // namespace

Federation::Federation(QObject* parent) : QObject(parent) {}

QString Federation::generateId() {
    return QUuid::createUuid().toString(QUuid::WithoutBraces);
}

bool Federation::isFederationPath(const QString& path) {
    return path.endsWith(".ifcfed", Qt::CaseInsensitive);
}

void Federation::clear() {
    file_path_.clear();
    name_.clear();
    created_ = QDateTime();
    modified_ = QDateTime();
    models_.clear();
    has_home_view_ = false;
    home_view_ = HomeView{};
    setDirty(false);
}

void Federation::markClean() {
    setDirty(false);
}

void Federation::setDirty(bool d) {
    if (dirty_ == d) return;
    dirty_ = d;
    emit dirtyChanged(d);
}

const Federation::Model* Federation::findById(const QString& fed_id) const {
    for (const auto& m : models_) {
        if (m.id == fed_id) return &m;
    }
    return nullptr;
}

QString Federation::addModel(const QString& source_path,
                              const QString& display_name) {
    if (source_path.isEmpty()) return {};
    if (isFederationPath(source_path)) return {};  // no nested federations

    Model m;
    m.id = generateId();
    m.display_name = display_name.isEmpty()
        ? QFileInfo(source_path).fileName()
        : display_name;
    m.source_kind = "local";
    m.source_path = QDir::cleanPath(QFileInfo(source_path).absoluteFilePath());
    models_.push_back(std::move(m));
    setDirty(true);
    return models_.back().id;
}

void Federation::removeModel(const QString& fed_id) {
    for (auto it = models_.begin(); it != models_.end(); ++it) {
        if (it->id == fed_id) {
            models_.erase(it);
            setDirty(true);
            return;
        }
    }
}

void Federation::setHomeView(const HomeView& hv) {
    home_view_ = hv;
    has_home_view_ = true;
    setDirty(true);
}

void Federation::clearHomeView() {
    if (!has_home_view_) return;
    has_home_view_ = false;
    home_view_ = HomeView{};
    setDirty(true);
}

bool Federation::load(const QString& path,
                      QStringList* warnings,
                      QString* err) {
    QFile f(path);
    if (!f.open(QIODevice::ReadOnly)) {
        if (err) *err = QString("Cannot open %1: %2").arg(path, f.errorString());
        return false;
    }
    QByteArray bytes = f.readAll();
    f.close();

    QJsonParseError pe;
    QJsonDocument doc = QJsonDocument::fromJson(bytes, &pe);
    if (doc.isNull() || !doc.isObject()) {
        if (err) *err = QString("Parse error in %1: %2").arg(path, pe.errorString());
        return false;
    }
    QJsonObject root = doc.object();

    clear();
    file_path_ = QDir::cleanPath(QFileInfo(path).absoluteFilePath());
    QString fed_dir = QFileInfo(file_path_).absolutePath();

    QString schema = root.value("schema").toString();
    if (schema != kSchema && warnings) {
        *warnings << QString("Unknown schema '%1' (expected '%2'); attempting to load anyway.")
                         .arg(schema, kSchema);
    }

    name_ = root.value("name").toString();
    created_ = QDateTime::fromString(root.value("created").toString(), Qt::ISODate);
    modified_ = QDateTime::fromString(root.value("modified").toString(), Qt::ISODate);

    QJsonArray arr = root.value("models").toArray();
    for (int i = 0; i < arr.size(); ++i) {
        if (!arr[i].isObject()) {
            if (warnings) *warnings << QString("models[%1] is not an object; skipping.").arg(i);
            continue;
        }
        QJsonObject mo = arr[i].toObject();

        Model m;
        m.id = mo.value("id").toString();
        if (m.id.isEmpty()) m.id = generateId();
        m.display_name = mo.value("display_name").toString();

        QJsonObject so = mo.value("source").toObject();
        m.source_kind = so.value("kind").toString("local");
        if (m.source_kind != "local") {
            if (warnings)
                *warnings << QString("models[%1]: unsupported source kind '%2'; entry kept but not loaded.")
                                 .arg(i).arg(m.source_kind);
            // Keep raw stored path so save() round-trips correctly.
            m.source_path = so.value("path").toString();
            models_.push_back(std::move(m));
            continue;
        }

        QString stored = so.value("path").toString();
        if (stored.isEmpty()) {
            if (warnings) *warnings << QString("models[%1]: missing source.path; skipping.").arg(i);
            continue;
        }
        m.source_path = resolvePath(fed_dir, stored);

        if (m.display_name.isEmpty())
            m.display_name = QFileInfo(m.source_path).fileName();

        QJsonValue vv = mo.value("visible");
        if (vv.isBool()) m.visible = vv.toBool();

        models_.push_back(std::move(m));
    }

    QJsonValue hv = root.value("home_view");
    if (hv.isObject()) {
        QJsonObject ho = hv.toObject();
        QJsonArray ta = ho.value("target").toArray();
        HomeView v;
        if (ta.size() == 3) {
            v.target = QVector3D(float(ta[0].toDouble()),
                                 float(ta[1].toDouble()),
                                 float(ta[2].toDouble()));
        }
        v.distance = float(ho.value("distance").toDouble(50.0));
        v.yaw      = float(ho.value("yaw").toDouble(45.0));
        v.pitch    = float(ho.value("pitch").toDouble(30.0));
        home_view_ = v;
        has_home_view_ = true;
    }

    setDirty(false);
    return true;
}

bool Federation::save(const QString& path, QString* err) {
    QString abs_path = QDir::cleanPath(QFileInfo(path).absoluteFilePath());
    QString fed_dir = QFileInfo(abs_path).absolutePath();

    QJsonObject root;
    root["schema"] = kSchema;
    if (!name_.isEmpty()) root["name"] = name_;

    if (!created_.isValid()) created_ = QDateTime::currentDateTimeUtc();
    modified_ = QDateTime::currentDateTimeUtc();
    root["created"]  = created_.toUTC().toString(Qt::ISODate);
    root["modified"] = modified_.toUTC().toString(Qt::ISODate);

    QJsonArray arr;
    for (const auto& m : models_) {
        QJsonObject mo;
        mo["id"] = m.id;
        mo["display_name"] = m.display_name;

        QJsonObject so;
        so["kind"] = m.source_kind;
        if (m.source_kind == "local") {
            so["path"] = relativizePath(fed_dir, m.source_path);
        } else {
            // Round-trip raw value for unsupported kinds.
            so["path"] = m.source_path;
        }
        mo["source"] = so;

        if (!m.visible) mo["visible"] = false;

        arr.append(mo);
    }
    root["models"] = arr;

    if (has_home_view_) {
        QJsonObject ho;
        QJsonArray ta;
        ta.append(double(home_view_.target.x()));
        ta.append(double(home_view_.target.y()));
        ta.append(double(home_view_.target.z()));
        ho["target"]   = ta;
        ho["distance"] = double(home_view_.distance);
        ho["yaw"]      = double(home_view_.yaw);
        ho["pitch"]    = double(home_view_.pitch);
        root["home_view"] = ho;
    } else {
        root["home_view"] = QJsonValue();  // null
    }

    QSaveFile f(abs_path);
    if (!f.open(QIODevice::WriteOnly | QIODevice::Truncate)) {
        if (err) *err = QString("Cannot write %1: %2").arg(abs_path, f.errorString());
        return false;
    }
    f.write(QJsonDocument(root).toJson(QJsonDocument::Indented));
    if (!f.commit()) {
        if (err) *err = QString("Failed to commit %1: %2").arg(abs_path, f.errorString());
        return false;
    }

    file_path_ = abs_path;
    setDirty(false);
    return true;
}
