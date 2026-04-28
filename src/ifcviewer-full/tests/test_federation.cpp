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

#include <catch2/catch_test_macros.hpp>

#include <QCoreApplication>
#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QSignalSpy>
#include <QTemporaryDir>
#include <QVector3D>

#include <atomic>

namespace {

// Catch2 owns main(), so QCoreApplication can't live in a TU constructor.
// Lazily construct it (intentionally leaked) the first time any test asks.
void ensureQApp() {
    if (QCoreApplication::instance()) return;
    static int argc = 1;
    static char arg0[] = "test_federation";
    static char* argv[] = { arg0, nullptr };
    new QCoreApplication(argc, argv);
}

QString writeStubFile(const QString& path) {
    // Federation::addModel cleanPath()s + absolutePath()s; the file doesn't
    // need to exist to be added, but for some tests we want a real path under
    // a temp dir so QFileInfo gives a stable answer.
    QFileInfo fi(path);
    QDir().mkpath(fi.absolutePath());
    QFile f(path);
    REQUIRE(f.open(QIODevice::WriteOnly));
    f.write("stub");
    f.close();
    return QDir::cleanPath(fi.absoluteFilePath());
}

QJsonObject readJsonFile(const QString& path) {
    QFile f(path);
    REQUIRE(f.open(QIODevice::ReadOnly));
    QJsonDocument doc = QJsonDocument::fromJson(f.readAll());
    REQUIRE(doc.isObject());
    return doc.object();
}

} // namespace

TEST_CASE("Federation starts empty and not dirty", "[federation]") {
    ensureQApp();
    Federation fed;
    REQUIRE(fed.models().empty());
    REQUIRE_FALSE(fed.isDirty());
    REQUIRE_FALSE(fed.hasHomeView());
    REQUIRE(fed.filePath().isEmpty());
}

TEST_CASE("addModel emits dirty=true; markClean clears it; remove re-dirties", "[federation]") {
    ensureQApp();
    QTemporaryDir tmp;
    REQUIRE(tmp.isValid());

    Federation fed;
    QSignalSpy spy(&fed, &Federation::dirtyChanged);

    QString abs = writeStubFile(tmp.filePath("a.ifc"));
    QString id = fed.addModel(abs);
    REQUIRE_FALSE(id.isEmpty());
    REQUIRE(fed.isDirty());
    REQUIRE(spy.count() == 1);
    REQUIRE(spy.takeFirst().at(0).toBool() == true);

    fed.markClean();
    REQUIRE_FALSE(fed.isDirty());
    REQUIRE(spy.count() == 1);
    REQUIRE(spy.takeFirst().at(0).toBool() == false);

    fed.removeModel(id);
    REQUIRE(fed.isDirty());
    REQUIRE(spy.count() == 1);
    REQUIRE(spy.takeFirst().at(0).toBool() == true);
}

TEST_CASE("addModel rejects empty paths and nested .ifcfed sources", "[federation]") {
    ensureQApp();
    Federation fed;
    REQUIRE(fed.addModel("").isEmpty());
    REQUIRE(fed.addModel("nested.ifcfed").isEmpty());
    REQUIRE(fed.addModel("nested.IfcFed").isEmpty());  // case-insensitive
    REQUIRE(fed.models().empty());
    REQUIRE_FALSE(fed.isDirty());
}

TEST_CASE("setHomeView / clearHomeView toggle dirty + has_home_view", "[federation]") {
    ensureQApp();
    Federation fed;
    QSignalSpy spy(&fed, &Federation::dirtyChanged);

    Federation::HomeView hv;
    hv.target = QVector3D(1, 2, 3);
    hv.distance = 12.5f;
    hv.yaw = 33.0f;
    hv.pitch = 22.0f;
    fed.setHomeView(hv);
    REQUIRE(fed.hasHomeView());
    REQUIRE(fed.isDirty());
    REQUIRE(spy.count() == 1);

    fed.markClean();
    spy.clear();

    fed.clearHomeView();
    REQUIRE_FALSE(fed.hasHomeView());
    REQUIRE(fed.isDirty());
    REQUIRE(spy.count() == 1);

    // Idempotent when already cleared.
    fed.markClean();
    spy.clear();
    fed.clearHomeView();
    REQUIRE_FALSE(fed.isDirty());
    REQUIRE(spy.count() == 0);
}

TEST_CASE("save then load round-trips models, transform, visibility, home view", "[federation]") {
    ensureQApp();
    QTemporaryDir tmp;
    REQUIRE(tmp.isValid());

    QString src1 = writeStubFile(tmp.filePath("models/wall.ifc"));
    QString src2 = writeStubFile(tmp.filePath("models/slab.ifc"));
    QString fed_path = tmp.filePath("project.ifcfed");

    Federation src;
    QString id1 = src.addModel(src1, "Wall");
    QString id2 = src.addModel(src2);  // default display_name from filename
    REQUIRE_FALSE(id1.isEmpty());
    REQUIRE_FALSE(id2.isEmpty());

    Federation::HomeView hv;
    hv.target = QVector3D(10, 20, 30);
    hv.distance = 77.0f;
    hv.yaw = 11.0f;
    hv.pitch = 7.0f;
    src.setHomeView(hv);

    QString err;
    REQUIRE(src.save(fed_path, &err));
    REQUIRE(err.isEmpty());
    REQUIRE_FALSE(src.isDirty());
    REQUIRE(QFileInfo::exists(fed_path));

    Federation dst;
    QStringList warnings;
    REQUIRE(dst.load(fed_path, &warnings, &err));
    REQUIRE(err.isEmpty());
    REQUIRE(warnings.isEmpty());

    REQUIRE(dst.models().size() == 2);
    REQUIRE(dst.models()[0].id == id1);
    REQUIRE(dst.models()[0].display_name == "Wall");
    REQUIRE(dst.models()[0].source_path == src1);
    REQUIRE(dst.models()[1].id == id2);
    REQUIRE(dst.models()[1].display_name == "slab.ifc");
    REQUIRE(dst.models()[1].source_path == src2);

    REQUIRE(dst.hasHomeView());
    REQUIRE(dst.homeView().target == QVector3D(10, 20, 30));
    REQUIRE(dst.homeView().distance == 77.0f);
    REQUIRE(dst.homeView().yaw == 11.0f);
    REQUIRE(dst.homeView().pitch == 7.0f);

    REQUIRE_FALSE(dst.isDirty());
    REQUIRE(QFileInfo(dst.filePath()) == QFileInfo(fed_path));
}

TEST_CASE("save stores paths relative when under fed_dir, absolute otherwise", "[federation]") {
    ensureQApp();
    QTemporaryDir root;
    REQUIRE(root.isValid());

    // Layout:
    //   <root>/fed_root/project.ifcfed
    //   <root>/fed_root/sub/inside.ifc       (under fed_dir)
    //   <root>/elsewhere/outside.ifc         (not under fed_dir)
    QString fed_dir = root.filePath("fed_root");
    QDir().mkpath(fed_dir);
    QString fed_path = fed_dir + "/project.ifcfed";
    QString inside  = writeStubFile(fed_dir + "/sub/inside.ifc");
    QString outside = writeStubFile(root.filePath("elsewhere/outside.ifc"));

    Federation fed;
    fed.addModel(inside);
    fed.addModel(outside);

    QString err;
    REQUIRE(fed.save(fed_path, &err));

    QJsonObject root_obj = readJsonFile(fed_path);
    QJsonArray models = root_obj.value("models").toArray();
    REQUIRE(models.size() == 2);

    QString stored_inside  = models[0].toObject().value("source").toObject()
                                .value("path").toString();
    QString stored_outside = models[1].toObject().value("source").toObject()
                                .value("path").toString();

    REQUIRE_FALSE(QFileInfo(stored_inside).isAbsolute());
    REQUIRE(stored_inside == "sub/inside.ifc");
    REQUIRE(QFileInfo(stored_outside).isAbsolute());
    REQUIRE(QDir::cleanPath(stored_outside) == outside);

    // Reload: source_path is resolved back to absolute either way.
    Federation reload;
    QStringList warnings;
    REQUIRE(reload.load(fed_path, &warnings, &err));
    REQUIRE(reload.models()[0].source_path == inside);
    REQUIRE(reload.models()[1].source_path == outside);
}

TEST_CASE("Save-As to a different directory recomputes path relativity", "[federation]") {
    ensureQApp();
    QTemporaryDir root;
    REQUIRE(root.isValid());

    // Original layout: source lives under fed_root, fed file under fed_root.
    QString fed_dir_a = root.filePath("fed_a");
    QString fed_dir_b = root.filePath("fed_b");
    QDir().mkpath(fed_dir_a);
    QDir().mkpath(fed_dir_b);
    QString src = writeStubFile(fed_dir_a + "/sub/m.ifc");
    QString fed_a = fed_dir_a + "/proj.ifcfed";
    QString fed_b = fed_dir_b + "/proj.ifcfed";

    Federation fed;
    fed.addModel(src);

    QString err;
    REQUIRE(fed.save(fed_a, &err));
    QString stored_a = readJsonFile(fed_a).value("models").toArray()[0]
                           .toObject().value("source").toObject()
                           .value("path").toString();
    REQUIRE_FALSE(QFileInfo(stored_a).isAbsolute());

    // Save-As under a sibling directory: source is no longer under fed_dir,
    // so it must be stored as absolute.
    REQUIRE(fed.save(fed_b, &err));
    QString stored_b = readJsonFile(fed_b).value("models").toArray()[0]
                           .toObject().value("source").toObject()
                           .value("path").toString();
    REQUIRE(QFileInfo(stored_b).isAbsolute());
    REQUIRE(QDir::cleanPath(stored_b) == src);

    // After Save-As, filePath() reflects the new location.
    REQUIRE(QFileInfo(fed.filePath()) == QFileInfo(fed_b));
}

TEST_CASE("load on a missing file fails with an error and does not crash", "[federation]") {
    ensureQApp();
    Federation fed;
    QStringList warnings;
    QString err;
    REQUIRE_FALSE(fed.load("/this/path/does/not/exist.ifcfed", &warnings, &err));
    REQUIRE_FALSE(err.isEmpty());
}

TEST_CASE("load on malformed JSON fails with an error", "[federation]") {
    ensureQApp();
    QTemporaryDir tmp;
    REQUIRE(tmp.isValid());
    QString bad = tmp.filePath("bad.ifcfed");
    {
        QFile f(bad);
        REQUIRE(f.open(QIODevice::WriteOnly));
        f.write("{ this is not json");
        f.close();
    }
    Federation fed;
    QStringList warnings;
    QString err;
    REQUIRE_FALSE(fed.load(bad, &warnings, &err));
    REQUIRE_FALSE(err.isEmpty());
}
