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
#include "Geolocation.h"

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

TEST_CASE("setModelVisible toggles flag, dirty, and signal; idempotent", "[federation]") {
    ensureQApp();
    QTemporaryDir tmp;
    REQUIRE(tmp.isValid());

    Federation fed;
    QString id = fed.addModel(writeStubFile(tmp.filePath("a.ifc")));
    REQUIRE_FALSE(id.isEmpty());
    REQUIRE(fed.findById(id)->visible);  // visible by default
    fed.markClean();

    QSignalSpy dirty_spy(&fed, &Federation::dirtyChanged);
    QSignalSpy vis_spy(&fed, &Federation::modelVisibilityChanged);

    fed.setModelVisible(id, false);
    REQUIRE_FALSE(fed.findById(id)->visible);
    REQUIRE(fed.isDirty());
    REQUIRE(dirty_spy.count() == 1);
    REQUIRE(vis_spy.count() == 1);
    REQUIRE(vis_spy.takeFirst().at(0).toString() == id);

    // Idempotent: same value, no signal, dirty unchanged.
    fed.markClean();
    dirty_spy.clear();
    vis_spy.clear();
    fed.setModelVisible(id, false);
    REQUIRE_FALSE(fed.isDirty());
    REQUIRE(dirty_spy.count() == 0);
    REQUIRE(vis_spy.count() == 0);

    // Unknown fed_id is a no-op (no crash, no signal).
    fed.setModelVisible("not-a-real-id", false);
    REQUIRE_FALSE(fed.isDirty());
    REQUIRE(vis_spy.count() == 0);

    // Toggle back on.
    fed.setModelVisible(id, true);
    REQUIRE(fed.findById(id)->visible);
    REQUIRE(fed.isDirty());
    REQUIRE(vis_spy.count() == 1);
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

    // Hide the second model — exercises the visibility round-trip.
    src.setModelVisible(id2, false);

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
    REQUIRE(dst.models()[0].visible);
    REQUIRE(dst.models()[1].id == id2);
    REQUIRE(dst.models()[1].display_name == "slab.ifc");
    REQUIRE(dst.models()[1].source_path == src2);
    REQUIRE_FALSE(dst.models()[1].visible);

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

TEST_CASE("config / federated_false_origin / model_transformation round-trip "
          "through save+load", "[federation]") {
    ensureQApp();
    QTemporaryDir tmp;
    REQUIRE(tmp.isValid());

    QString src1 = writeStubFile(tmp.filePath("models/wall.ifc"));
    QString fed_path = tmp.filePath("project.ifcfed");

    Federation src;
    QString id1 = src.addModel(src1, "Wall");

    FederationConfig cfg;
    cfg.unit_name   = "FOOT";
    cfg.unit_prefix = "";
    src.setConfig(cfg);

    FederatedFalseOrigin org;
    org.xyz    = Eigen::Vector3d(100.0, 200.0, 30.0);
    org.rz_deg = 45.0;
    src.setFederatedFalseOrigin(org);

    ModelTransformation xf;
    xf.a_frame  = AFrame::ModelLocal;
    xf.a        = Eigen::Vector3d(1.0, 2.0, 3.0);
    xf.b        = Eigen::Vector3d(4.0, 5.0, 6.0);
    xf.rxyz_deg = Eigen::Vector3d(90.0, 0.0, 0.0);
    xf.pivot    = Eigen::Vector3d(7.0, 8.0, 9.0);
    src.setModelTransformation(id1, xf);

    QString err;
    REQUIRE(src.save(fed_path, &err));
    REQUIRE(err.isEmpty());

    Federation dst;
    QStringList warnings;
    REQUIRE(dst.load(fed_path, &warnings, &err));
    REQUIRE(err.isEmpty());
    REQUIRE(warnings.isEmpty());

    REQUIRE(dst.config().unit_name   == "FOOT");
    REQUIRE(dst.config().unit_prefix == "");

    REQUIRE(dst.federatedFalseOrigin().xyz    == org.xyz);
    REQUIRE(dst.federatedFalseOrigin().rz_deg == 45.0);

    REQUIRE(dst.models().size() == 1);
    const auto& m = dst.models()[0];
    REQUIRE(m.id == id1);
    REQUIRE(m.model_transformation.a_frame  == AFrame::ModelLocal);
    REQUIRE(m.model_transformation.a        == xf.a);
    REQUIRE(m.model_transformation.b        == xf.b);
    REQUIRE(m.model_transformation.rxyz_deg == xf.rxyz_deg);
    REQUIRE(m.model_transformation.pivot    == xf.pivot);
}

TEST_CASE("default ModelTransformation is omitted from saved JSON",
          "[federation]") {
    ensureQApp();
    QTemporaryDir tmp;
    REQUIRE(tmp.isValid());

    QString src1 = writeStubFile(tmp.filePath("models/wall.ifc"));
    QString fed_path = tmp.filePath("project.ifcfed");

    Federation src;
    src.addModel(src1, "Wall");
    QString err;
    REQUIRE(src.save(fed_path, &err));

    QJsonObject root = readJsonFile(fed_path);
    QJsonArray models = root.value("models").toArray();
    REQUIRE(models.size() == 1);
    REQUIRE_FALSE(models[0].toObject().contains("model_transformation"));
}

TEST_CASE("composeFederatedFalseOrigin moves the nominated point to the origin",
          "[federation][compose]") {
    FederationConfig cfg;          // METRE, no prefix
    FederatedFalseOrigin org;
    org.xyz    = Eigen::Vector3d(10.0, 20.0, 5.0);
    org.rz_deg = 0.0;

    Eigen::Matrix4d M = composeFederatedFalseOrigin(org, cfg);

    // The nominated point (10, 20, 5) should map to (0, 0, 0).
    Eigen::Vector4d p(10.0, 20.0, 5.0, 1.0);
    Eigen::Vector4d r = M * p;
    REQUIRE(std::abs(r.x()) < 1e-9);
    REQUIRE(std::abs(r.y()) < 1e-9);
    REQUIRE(std::abs(r.z()) < 1e-9);
}

TEST_CASE("composeFederatedFalseOrigin scales by federation unit",
          "[federation][compose]") {
    FederationConfig cfg;
    cfg.unit_name = "FOOT";        // 1 ft = 0.3048 m
    FederatedFalseOrigin org;
    org.xyz = Eigen::Vector3d(1.0, 0.0, 0.0);  // 1 foot in fed coords

    Eigen::Matrix4d M = composeFederatedFalseOrigin(org, cfg);
    // Translation column should be -1 ft = -0.3048 m.
    REQUIRE(std::abs(M(0, 3) - (-0.3048)) < 1e-9);
}

TEST_CASE("helmert metres transform consumes Scale through map unit scale",
          "[federation][georef]") {
    HelmertTransformation params;
    params.e = 500000.0;
    params.n = 7000000.0;
    params.scale = 0.001;  // project mm -> map numeric metres

    const double project_length_to_meters = 0.001;
    const double map_unit_to_meters = project_length_to_meters / params.scale;
    Eigen::Matrix4d M = helmertMetersFromParameters(params, map_unit_to_meters);

    Eigen::Vector4d local_m(10.0, 20.0, 0.0, 1.0);
    Eigen::Vector4d global_m = M * local_m;

    REQUIRE(std::abs(map_unit_to_meters - 1.0) < 1e-12);
    REQUIRE(std::abs(global_m.x() - 500010.0) < 1e-9);
    REQUIRE(std::abs(global_m.y() - 7000020.0) < 1e-9);
}

TEST_CASE("addGroup creates a top-level group; addGroup with parent nests it",
          "[federation][groups]") {
    ensureQApp();
    Federation fed;
    QSignalSpy added_spy(&fed, &Federation::groupAdded);

    QString a = fed.addGroup("Site A");
    REQUIRE_FALSE(a.isEmpty());
    REQUIRE(fed.rootGroups().size() == 1);
    REQUIRE(fed.rootGroups()[0]->id == a);
    REQUIRE(fed.findGroupById(a)->parent == nullptr);
    REQUIRE(fed.isDirty());
    REQUIRE(added_spy.count() == 1);

    QString sub = fed.addGroup("Building 1", a);
    REQUIRE_FALSE(sub.isEmpty());
    REQUIRE(fed.rootGroups().size() == 1);  // still one root
    REQUIRE(fed.rootGroups()[0]->children.size() == 1);
    REQUIRE(fed.rootGroups()[0]->children[0]->id == sub);
    REQUIRE(fed.findGroupById(sub)->parent == fed.findGroupById(a));

    // Unknown parent_id is rejected.
    QString bad = fed.addGroup("Orphan", "no-such-id");
    REQUIRE(bad.isEmpty());

    // allGroups walks parents-before-children.
    auto all = fed.allGroups();
    REQUIRE(all.size() == 2);
    REQUIRE(all[0]->id == a);
    REQUIRE(all[1]->id == sub);
}

TEST_CASE("setModelGroup assigns and reassigns; rejects unknown group",
          "[federation][groups]") {
    ensureQApp();
    QTemporaryDir tmp;
    Federation fed;
    QString mid = fed.addModel(writeStubFile(tmp.filePath("a.ifc")));
    QString gid = fed.addGroup("G");
    fed.markClean();

    QSignalSpy spy(&fed, &Federation::modelGroupChanged);
    fed.setModelGroup(mid, gid);
    REQUIRE(fed.findById(mid)->group_id == gid);
    REQUIRE(fed.isDirty());
    REQUIRE(spy.count() == 1);

    // Idempotent.
    fed.markClean();
    spy.clear();
    fed.setModelGroup(mid, gid);
    REQUIRE_FALSE(fed.isDirty());
    REQUIRE(spy.count() == 0);

    // Unknown group is rejected.
    fed.setModelGroup(mid, "no-such-group");
    REQUIRE(fed.findById(mid)->group_id == gid);
    REQUIRE_FALSE(fed.isDirty());

    // Reassign back to root.
    fed.setModelGroup(mid, QString());
    REQUIRE(fed.findById(mid)->group_id.isEmpty());
    REQUIRE(spy.count() == 1);
}

TEST_CASE("setGroupVisible affects effective visibility cascade",
          "[federation][groups]") {
    ensureQApp();
    QTemporaryDir tmp;
    Federation fed;
    QString mid = fed.addModel(writeStubFile(tmp.filePath("a.ifc")));
    QString outer = fed.addGroup("Outer");
    QString inner = fed.addGroup("Inner", outer);
    fed.setModelGroup(mid, inner);

    REQUIRE(fed.isModelEffectivelyVisible(mid));
    REQUIRE(fed.isGroupChainVisible(inner));

    // Hide the outer group: inner chain visibility flips, model effective
    // visibility flips, but the model's own visible flag is untouched.
    fed.setGroupVisible(outer, false);
    REQUIRE_FALSE(fed.isGroupChainVisible(outer));
    REQUIRE_FALSE(fed.isGroupChainVisible(inner));
    REQUIRE_FALSE(fed.isModelEffectivelyVisible(mid));
    REQUIRE(fed.findById(mid)->visible);

    // Hiding a model directly while its group is also hidden — still
    // effectively hidden.
    fed.setModelVisible(mid, false);
    REQUIRE_FALSE(fed.isModelEffectivelyVisible(mid));

    // Re-show the outer group; model is still hidden by its own flag.
    fed.setGroupVisible(outer, true);
    REQUIRE(fed.isGroupChainVisible(inner));
    REQUIRE_FALSE(fed.isModelEffectivelyVisible(mid));

    fed.setModelVisible(mid, true);
    REQUIRE(fed.isModelEffectivelyVisible(mid));
}

TEST_CASE("setGroupParent rejects cycles and self-parenting",
          "[federation][groups]") {
    ensureQApp();
    Federation fed;
    QString a = fed.addGroup("A");
    QString b = fed.addGroup("B", a);
    QString c = fed.addGroup("C", b);

    // Self-parent: rejected.
    fed.setGroupParent(a, a);
    REQUIRE(fed.findGroupById(a)->parent == nullptr);

    // Parenting an ancestor under its descendant: rejected.
    fed.setGroupParent(a, c);
    REQUIRE(fed.findGroupById(a)->parent == nullptr);
    REQUIRE(fed.findGroupById(c)->parent->id == b);

    // Valid reparent: move b up to root.
    fed.setGroupParent(b, QString());
    REQUIRE(fed.findGroupById(b)->parent == nullptr);
    REQUIRE(fed.findGroupById(c)->parent->id == b);  // c stays under b
    REQUIRE(fed.rootGroups().size() == 2);           // a + b at root
}

TEST_CASE("removeGroup reparents direct children + models up one level",
          "[federation][groups]") {
    ensureQApp();
    QTemporaryDir tmp;
    Federation fed;
    QString outer = fed.addGroup("Outer");
    QString mid_outer = fed.addGroup("MidOuter", outer);
    QString inner = fed.addGroup("Inner", mid_outer);

    QString m_outer = fed.addModel(writeStubFile(tmp.filePath("a.ifc")));
    QString m_mid   = fed.addModel(writeStubFile(tmp.filePath("b.ifc")));
    QString m_inner = fed.addModel(writeStubFile(tmp.filePath("c.ifc")));
    fed.setModelGroup(m_outer, outer);
    fed.setModelGroup(m_mid,   mid_outer);
    fed.setModelGroup(m_inner, inner);
    fed.markClean();

    QSignalSpy gc_spy(&fed, &Federation::groupChanged);
    QSignalSpy mg_spy(&fed, &Federation::modelGroupChanged);
    QSignalSpy gr_spy(&fed, &Federation::groupRemoved);

    // Remove the middle group: its child group (inner) and child model
    // (m_mid) should both move up to `outer`.
    fed.removeGroup(mid_outer);

    REQUIRE(fed.findGroupById(mid_outer) == nullptr);
    REQUIRE(fed.findGroupById(inner)->parent->id == outer);
    REQUIRE(fed.findById(m_mid)->group_id == outer);
    // Untouched siblings.
    REQUIRE(fed.findById(m_outer)->group_id == outer);
    REQUIRE(fed.findById(m_inner)->group_id == inner);
    REQUIRE(fed.isDirty());

    REQUIRE(gc_spy.count() == 1);
    REQUIRE(gc_spy.takeFirst().at(0).toString() == inner);
    REQUIRE(mg_spy.count() == 1);
    REQUIRE(mg_spy.takeFirst().at(0).toString() == m_mid);
    REQUIRE(gr_spy.count() == 1);
    REQUIRE(gr_spy.takeFirst().at(0).toString() == mid_outer);
}

TEST_CASE("groups + model.group_id round-trip through nested JSON save/load",
          "[federation][groups]") {
    ensureQApp();
    QTemporaryDir tmp;
    QString fed_path = tmp.filePath("p.ifcfed");

    QString site_id, bldg_id, m_root, m_bldg;
    {
        Federation src;
        site_id = src.addGroup("Site");
        bldg_id = src.addGroup("Building 1", site_id);
        m_root  = src.addModel(writeStubFile(tmp.filePath("root.ifc")));
        m_bldg  = src.addModel(writeStubFile(tmp.filePath("bldg.ifc")));
        src.setModelGroup(m_bldg, bldg_id);
        src.setGroupVisible(bldg_id, false);

        QString err;
        REQUIRE(src.save(fed_path, &err));
    }

    // Inspect raw JSON: groups should be nested under "groups" with no
    // parent_id field anywhere, and model.group_id is present only when set.
    {
        QJsonObject root = readJsonFile(fed_path);
        REQUIRE(root.contains("groups"));
        QJsonArray grps = root.value("groups").toArray();
        REQUIRE(grps.size() == 1);
        QJsonObject site = grps[0].toObject();
        REQUIRE(site.value("display_name").toString() == "Site");
        REQUIRE_FALSE(site.contains("parent_id"));

        QJsonArray site_children = site.value("groups").toArray();
        REQUIRE(site_children.size() == 1);
        QJsonObject bldg = site_children[0].toObject();
        REQUIRE(bldg.value("display_name").toString() == "Building 1");
        REQUIRE(bldg.value("visible").toBool() == false);
        REQUIRE_FALSE(bldg.contains("parent_id"));

        QJsonArray models = root.value("models").toArray();
        REQUIRE(models.size() == 2);
        // m_root is at root: no group_id key.
        REQUIRE_FALSE(models[0].toObject().contains("group_id"));
        // m_bldg is inside the building.
        REQUIRE(models[1].toObject().value("group_id").toString() == bldg_id);
    }

    {
        Federation dst;
        QStringList warnings;
        QString err;
        REQUIRE(dst.load(fed_path, &warnings, &err));
        REQUIRE(warnings.isEmpty());
        REQUIRE(dst.rootGroups().size() == 1);
        REQUIRE(dst.rootGroups()[0]->id == site_id);
        REQUIRE(dst.rootGroups()[0]->children.size() == 1);
        REQUIRE(dst.rootGroups()[0]->children[0]->id == bldg_id);
        REQUIRE_FALSE(dst.rootGroups()[0]->children[0]->visible);
        REQUIRE(dst.rootGroups()[0]->children[0]->parent != nullptr);
        REQUIRE(dst.rootGroups()[0]->children[0]->parent->id == site_id);

        REQUIRE(dst.findById(m_root)->group_id.isEmpty());
        REQUIRE(dst.findById(m_bldg)->group_id == bldg_id);
        REQUIRE_FALSE(dst.isModelEffectivelyVisible(m_bldg));
    }
}

TEST_CASE("composeModelTransformation with pivot=B keeps A landing on B",
          "[federation][compose]") {
    // A in ModelGlobal frame, federation in metres, identity CoordinateOperation.
    FederationConfig fed_cfg;       // METRE
    ModelUnits mu;                  // 1.0 / 1.0 (already in metres)
    Eigen::Matrix4d coord_op = Eigen::Matrix4d::Identity();

    ModelTransformation xf;
    xf.a_frame  = AFrame::ModelGlobal;
    xf.a        = Eigen::Vector3d(5.0, 0.0, 0.0);
    xf.b        = Eigen::Vector3d(100.0, 50.0, 10.0);
    xf.rxyz_deg = Eigen::Vector3d(0.0, 0.0, 30.0);
    xf.pivot    = xf.b;             // pivot at B preserves A->B regardless of rotation

    Eigen::Matrix4d M = composeModelTransformation(xf, fed_cfg, mu, coord_op);

    Eigen::Vector4d a(xf.a.x(), xf.a.y(), xf.a.z(), 1.0);
    Eigen::Vector4d r = M * a;
    REQUIRE(std::abs(r.x() - xf.b.x()) < 1e-9);
    REQUIRE(std::abs(r.y() - xf.b.y()) < 1e-9);
    REQUIRE(std::abs(r.z() - xf.b.z()) < 1e-9);
}
