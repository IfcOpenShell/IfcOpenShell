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
#include "Unit.h"

#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <QSaveFile>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonValue>
#include <QUuid>

#include <algorithm>
#include <cmath>
#include <functional>

namespace {
constexpr const char* kSchema = "ifcfed/1";

constexpr double kPi       = 3.14159265358979323846;
constexpr double kDegToRad = kPi / 180.0;

Eigen::Matrix4d translation4(const Eigen::Vector3d& t) {
    Eigen::Matrix4d M = Eigen::Matrix4d::Identity();
    M(0, 3) = t.x();
    M(1, 3) = t.y();
    M(2, 3) = t.z();
    return M;
}

// Intrinsic XYZ Euler: R = R_z · R_y · R_x.
Eigen::Matrix4d eulerXYZ(const Eigen::Vector3d& rxyz_rad) {
    const Eigen::Matrix3d R3 =
        (Eigen::AngleAxisd(rxyz_rad.z(), Eigen::Vector3d::UnitZ()) *
         Eigen::AngleAxisd(rxyz_rad.y(), Eigen::Vector3d::UnitY()) *
         Eigen::AngleAxisd(rxyz_rad.x(), Eigen::Vector3d::UnitX())).matrix();
    Eigen::Matrix4d R = Eigen::Matrix4d::Identity();
    R.block<3, 3>(0, 0) = R3;
    return R;
}

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

// === Stage-3/4 compose helpers ===

double federationUnitToMeters(const FederationConfig& cfg) {
    return convert(1.0, cfg.unit_prefix, cfg.unit_name, "", "METRE");
}

Eigen::Matrix4d composeFederatedFalseOrigin(const FederatedFalseOrigin& origin,
                                            const FederationConfig& cfg) {
    const double u = federationUnitToMeters(cfg);
    const Eigen::Vector3d xyz_m = origin.xyz * u;
    const double rz_rad = origin.rz_deg * kDegToRad;
    const Eigen::Matrix3d Rz =
        Eigen::AngleAxisd(rz_rad, Eigen::Vector3d::UnitZ()).matrix();
    Eigen::Matrix4d Rz4 = Eigen::Matrix4d::Identity();
    Rz4.block<3, 3>(0, 0) = Rz;
    return Rz4 * translation4(-xyz_m);
}

ModelGeoref computeModelGeoref(ifcopenshell::file* ifc_file) {
    ModelGeoref out;
    if (!ifc_file) return out;

    out.units.project_length_to_meters =
        calculateUnitScale(ifc_file, "LENGTHUNIT");

    if (auto map_unit = getMapUnit(ifc_file)) {
        if (auto s = siScaleFromNamedUnit(*map_unit)) {
            out.units.map_unit_to_meters = *s;
        } else {
            out.units.map_unit_to_meters = out.units.project_length_to_meters;
        }
    } else {
        // No MapUnit on the IfcProjectedCRS — fall back to project length unit.
        out.units.map_unit_to_meters = out.units.project_length_to_meters;
    }

    auto params = getHelmertTransformationParameters(ifc_file);
    if (!params) return out;

    Eigen::Matrix4d helmert =
        helmertMetersFromParameters(*params, out.units.map_unit_to_meters);

    if (auto wcs = getWcs(ifc_file)) {
        // getWcs returns the WCS in project units (translation in project
        // length units).  Convert translation to metres before inverting.
        Eigen::Matrix4d wcs_m = *wcs;
        wcs_m(0, 3) *= out.units.project_length_to_meters;
        wcs_m(1, 3) *= out.units.project_length_to_meters;
        wcs_m(2, 3) *= out.units.project_length_to_meters;
        out.coordinate_operation_meters = helmert * wcs_m.inverse();
    } else {
        out.coordinate_operation_meters = helmert;
    }
    out.has_coordinate_operation = true;
    return out;
}

FederatedFalseOrigin
guessFederatedFalseOrigin(const Eigen::Matrix4d& first_placement_meters,
                          const ModelGeoref& georef,
                          const FederationConfig& fed_cfg) {
    Eigen::Vector3d t_m = first_placement_meters.block<3, 1>(0, 3);

    const bool use_coord_op = georef.has_coordinate_operation;
    if (use_coord_op) {
        const Eigen::Vector4d th(t_m.x(), t_m.y(), t_m.z(), 1.0);
        t_m = (georef.coordinate_operation_meters * th).head<3>();
    }

    const double u_fed = federationUnitToMeters(fed_cfg);
    const double u_fed_inv = (u_fed != 0.0) ? (1.0 / u_fed) : 1.0;

    FederatedFalseOrigin out;
    out.xyz = t_m * u_fed_inv;

    // Rotation: helmert grid-north baked into coordinate_operation_meters.
    // helmertMetersFromParameters built that block as R_z(theta)·diag(fx,fy,fz)
    // with theta = atan2(xao, xaa); xaxis2angle is `-theta` in degrees.
    if (use_coord_op) {
        const Eigen::Matrix4d& M = georef.coordinate_operation_meters;
        out.rz_deg = xaxis2angleDeg(M(0, 0), M(1, 0));
    }
    return out;
}

Eigen::Matrix4d composeModelTransformation(const ModelTransformation& xf,
                                           const FederationConfig& fed_cfg,
                                           const ModelUnits& model_units,
                                           const Eigen::Matrix4d& coordinate_operation_meters) {
    const double u_fed = federationUnitToMeters(fed_cfg);

    Eigen::Vector3d A_m;
    if (xf.a_frame == AFrame::ModelLocal) {
        // a is in the model's project length unit, expressed in the
        // pre-CoordinateOperation frame.  Convert to metres, then lift
        // through the CoordinateOperation.
        const Eigen::Vector4d a_h(
            xf.a.x() * model_units.project_length_to_meters,
            xf.a.y() * model_units.project_length_to_meters,
            xf.a.z() * model_units.project_length_to_meters,
            1.0);
        A_m = (coordinate_operation_meters * a_h).head<3>();
    } else {
        // a is in the model's map unit, expressed in the
        // post-CoordinateOperation frame.
        A_m = xf.a * model_units.map_unit_to_meters;
    }

    const Eigen::Vector3d B_m     = xf.b     * u_fed;
    const Eigen::Vector3d pivot_m = xf.pivot * u_fed;

    const Eigen::Matrix4d R_local = eulerXYZ(xf.rxyz_deg * kDegToRad);
    const Eigen::Matrix4d R_at_pivot =
        translation4(pivot_m) * R_local * translation4(-pivot_m);

    const Eigen::Vector4d Ah(A_m.x(), A_m.y(), A_m.z(), 1.0);
    const Eigen::Vector3d RA = (R_at_pivot * Ah).head<3>();
    const Eigen::Matrix4d T  = translation4(B_m - RA);

    return T * R_at_pivot;
}

// === Federation class ===

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
    root_groups_.clear();
    config_                 = FederationConfig{};
    federated_false_origin_ = FederatedFalseOrigin{};
    has_home_view_ = false;
    home_view_ = HomeView{};
    setDirty(false);
}

void Federation::setConfig(const FederationConfig& c) {
    if (config_.unit_name == c.unit_name && config_.unit_prefix == c.unit_prefix)
        return;
    config_ = c;
    setDirty(true);
    emit configChanged();
}

void Federation::setFederatedFalseOrigin(const FederatedFalseOrigin& o) {
    if (federated_false_origin_.xyz == o.xyz &&
        federated_false_origin_.rz_deg == o.rz_deg) return;
    federated_false_origin_ = o;
    setDirty(true);
    emit federatedFalseOriginChanged();
}

void Federation::setModelTransformation(const QString& fed_id,
                                        const ModelTransformation& xf) {
    for (auto& m : models_) {
        if (m.id != fed_id) continue;
        m.model_transformation = xf;
        setDirty(true);
        emit modelTransformationChanged(fed_id);
        return;
    }
}

void Federation::setModelVisible(const QString& fed_id, bool visible) {
    for (auto& m : models_) {
        if (m.id != fed_id) continue;
        if (m.visible == visible) return;
        m.visible = visible;
        setDirty(true);
        emit modelVisibilityChanged(fed_id, visible);
        return;
    }
}

void Federation::setModelGroup(const QString& fed_id, const QString& group_id) {
    if (!group_id.isEmpty() && findGroupById(group_id) == nullptr) return;
    for (auto& m : models_) {
        if (m.id != fed_id) continue;
        if (m.group_id == group_id) return;
        m.group_id = group_id;
        setDirty(true);
        emit modelGroupChanged(fed_id, group_id);
        return;
    }
}

QString Federation::addGroup(const QString& display_name,
                              const QString& parent_id) {
    Group* parent = nullptr;
    if (!parent_id.isEmpty()) {
        parent = findGroupByIdMutable(parent_id);
        if (!parent) return {};
    }

    auto g = std::make_unique<Group>();
    g->id = generateId();
    g->display_name = display_name.isEmpty() ? QString("Group") : display_name;
    g->parent = parent;
    const QString new_id = g->id;

    if (parent) parent->children.push_back(std::move(g));
    else        root_groups_.push_back(std::move(g));

    setDirty(true);
    emit groupAdded(new_id);
    return new_id;
}

void Federation::removeGroup(const QString& group_id) {
    Group* group = findGroupByIdMutable(group_id);
    if (!group) return;

    Group* new_parent = group->parent;
    const QString new_parent_id = new_parent ? new_parent->id : QString();
    auto& target_children = new_parent ? new_parent->children : root_groups_;

    // Move out of the to-be-removed group.  Splice into target_children
    // *before* the removed group's slot when possible to keep stable
    // visual order.  We don't bother with the precise position — append
    // is fine and simpler.
    std::vector<QString> moved_child_ids;
    moved_child_ids.reserve(group->children.size());
    for (auto& child : group->children) {
        moved_child_ids.push_back(child->id);
        child->parent = new_parent;
        target_children.push_back(std::move(child));
    }
    group->children.clear();

    // Reparent direct child models up one level.
    std::vector<QString> moved_model_ids;
    for (auto& m : models_) {
        if (m.group_id == group_id) {
            m.group_id = new_parent_id;
            moved_model_ids.push_back(m.id);
        }
    }

    // Detach + drop the now-empty group.
    auto owned = detachGroup(group);
    owned.reset();

    setDirty(true);
    for (const auto& cid : moved_child_ids) emit groupChanged(cid);
    for (const auto& mid : moved_model_ids) emit modelGroupChanged(mid, new_parent_id);
    emit groupRemoved(group_id);
}

void Federation::setGroupName(const QString& group_id,
                              const QString& display_name) {
    Group* g = findGroupByIdMutable(group_id);
    if (!g) return;
    if (g->display_name == display_name) return;
    g->display_name = display_name;
    setDirty(true);
    emit groupChanged(group_id);
}

void Federation::setGroupParent(const QString& group_id,
                                 const QString& parent_id) {
    if (group_id.isEmpty()) return;
    if (parent_id == group_id) return;

    Group* group = findGroupByIdMutable(group_id);
    if (!group) return;

    Group* new_parent = nullptr;
    if (!parent_id.isEmpty()) {
        new_parent = findGroupByIdMutable(parent_id);
        if (!new_parent) return;
        if (isDescendantOrSelf(group, new_parent)) return;
    }

    if (group->parent == new_parent) return;

    auto owned = detachGroup(group);
    if (!owned) return;
    owned->parent = new_parent;
    if (new_parent) new_parent->children.push_back(std::move(owned));
    else            root_groups_.push_back(std::move(owned));

    setDirty(true);
    emit groupChanged(group_id);
}

void Federation::setGroupVisible(const QString& group_id, bool visible) {
    Group* g = findGroupByIdMutable(group_id);
    if (!g) return;
    if (g->visible == visible) return;
    g->visible = visible;
    setDirty(true);
    emit groupVisibilityChanged(group_id, visible);
}

const Federation::Group* Federation::findGroupById(const QString& group_id) const {
    return const_cast<Federation*>(this)->findGroupByIdMutable(group_id);
}

Federation::Group* Federation::findGroupByIdMutable(const QString& group_id) {
    if (group_id.isEmpty()) return nullptr;
    std::vector<Group*> stack;
    for (auto& g : root_groups_) stack.push_back(g.get());
    while (!stack.empty()) {
        Group* g = stack.back();
        stack.pop_back();
        if (g->id == group_id) return g;
        for (auto& c : g->children) stack.push_back(c.get());
    }
    return nullptr;
}

std::vector<const Federation::Group*> Federation::allGroups() const {
    std::vector<const Group*> out;
    for (const auto& g : root_groups_) appendDfs(g.get(), out);
    return out;
}

void Federation::appendDfs(const Group* g, std::vector<const Group*>& out) {
    if (!g) return;
    out.push_back(g);
    for (const auto& c : g->children) appendDfs(c.get(), out);
}

std::unique_ptr<Federation::Group> Federation::detachGroup(Group* group) {
    if (!group) return nullptr;
    auto& siblings = group->parent ? group->parent->children : root_groups_;
    auto it = std::find_if(siblings.begin(), siblings.end(),
        [group](const std::unique_ptr<Group>& up) { return up.get() == group; });
    if (it == siblings.end()) return nullptr;
    std::unique_ptr<Group> owned = std::move(*it);
    siblings.erase(it);
    return owned;
}

bool Federation::isDescendantOrSelf(const Group* group,
                                     const Group* candidate_descendant) {
    if (!group || !candidate_descendant) return false;
    if (group == candidate_descendant) return true;
    for (const auto& c : group->children) {
        if (isDescendantOrSelf(c.get(), candidate_descendant)) return true;
    }
    return false;
}

bool Federation::isGroupChainVisible(const QString& group_id) const {
    if (group_id.isEmpty()) return true;
    const Group* g = findGroupById(group_id);
    while (g != nullptr) {
        if (!g->visible) return false;
        g = g->parent;
    }
    return true;
}

bool Federation::isModelEffectivelyVisible(const QString& fed_id) const {
    const Model* m = findById(fed_id);
    if (!m) return false;
    if (!m->visible) return false;
    return isGroupChainVisible(m->group_id);
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

    if (QJsonValue cv = root.value("config"); cv.isObject()) {
        QJsonObject co = cv.toObject();
        QJsonObject uo = co.value("unit").toObject();
        config_.unit_name   = uo.value("name").toString("METRE").toStdString();
        config_.unit_prefix = uo.value("prefix").toString("").toStdString();
    }

    if (QJsonValue ov = root.value("federated_false_origin"); ov.isObject()) {
        QJsonObject oo = ov.toObject();
        QJsonArray xyz = oo.value("xyz").toArray();
        if (xyz.size() == 3) {
            federated_false_origin_.xyz = Eigen::Vector3d(
                xyz[0].toDouble(), xyz[1].toDouble(), xyz[2].toDouble());
        }
        federated_false_origin_.rz_deg = oo.value("rz_deg").toDouble(0.0);
    }

    // Groups load before models so model.group_id can be validated.
    {
        // Recursive descend over the nested "groups" array.  Each entry is
        // {id, display_name, visible?, groups?: [...]}.  Children inherit
        // their parent pointer at construction time.
        std::function<void(const QJsonArray&,
                           std::vector<std::unique_ptr<Group>>&,
                           Group*)> load_groups;
        load_groups = [&](const QJsonArray& arr,
                          std::vector<std::unique_ptr<Group>>& sink,
                          Group* parent) {
            for (int i = 0; i < arr.size(); ++i) {
                if (!arr[i].isObject()) {
                    if (warnings)
                        *warnings << QString("groups: entry %1 is not an object; skipping.").arg(i);
                    continue;
                }
                QJsonObject go = arr[i].toObject();
                auto g = std::make_unique<Group>();
                g->id = go.value("id").toString();
                if (g->id.isEmpty()) g->id = generateId();
                g->display_name = go.value("display_name").toString();
                if (QJsonValue vv = go.value("visible"); vv.isBool())
                    g->visible = vv.toBool();
                g->parent = parent;

                if (QJsonValue cv = go.value("groups"); cv.isArray()) {
                    load_groups(cv.toArray(), g->children, g.get());
                }
                sink.push_back(std::move(g));
            }
        };
        load_groups(root.value("groups").toArray(), root_groups_, nullptr);
    }

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

        if (QJsonValue tv = mo.value("model_transformation"); tv.isObject()) {
            QJsonObject to = tv.toObject();
            const QString af = to.value("a_frame").toString("ModelGlobal");
            m.model_transformation.a_frame =
                (af == "ModelLocal") ? AFrame::ModelLocal : AFrame::ModelGlobal;
            auto readVec3 = [](QJsonArray ja) {
                if (ja.size() != 3) return Eigen::Vector3d::Zero().eval();
                return Eigen::Vector3d(
                    ja[0].toDouble(), ja[1].toDouble(), ja[2].toDouble());
            };
            m.model_transformation.a        = readVec3(to.value("a").toArray());
            m.model_transformation.b        = readVec3(to.value("b").toArray());
            m.model_transformation.rxyz_deg = readVec3(to.value("rxyz_deg").toArray());
            m.model_transformation.pivot    = readVec3(to.value("pivot").toArray());
        }

        QJsonValue vv = mo.value("visible");
        if (vv.isBool()) m.visible = vv.toBool();

        m.group_id = mo.value("group_id").toString();
        if (!m.group_id.isEmpty() && findGroupById(m.group_id) == nullptr) {
            if (warnings)
                *warnings << QString("models[%1]: unknown group_id '%2'; moved to root.")
                                 .arg(i).arg(m.group_id);
            m.group_id.clear();
        }

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

    {
        QJsonObject co, uo;
        uo["name"]   = QString::fromStdString(config_.unit_name);
        uo["prefix"] = QString::fromStdString(config_.unit_prefix);
        co["unit"]   = uo;
        root["config"] = co;
    }
    {
        QJsonObject oo;
        QJsonArray xyz;
        xyz.append(federated_false_origin_.xyz.x());
        xyz.append(federated_false_origin_.xyz.y());
        xyz.append(federated_false_origin_.xyz.z());
        oo["xyz"]    = xyz;
        oo["rz_deg"] = federated_false_origin_.rz_deg;
        root["federated_false_origin"] = oo;
    }

    if (!root_groups_.empty()) {
        std::function<QJsonArray(const std::vector<std::unique_ptr<Group>>&)> dump;
        dump = [&](const std::vector<std::unique_ptr<Group>>& src) {
            QJsonArray out;
            for (const auto& g : src) {
                QJsonObject go;
                go["id"]           = g->id;
                go["display_name"] = g->display_name;
                if (!g->visible)   go["visible"] = false;
                if (!g->children.empty()) go["groups"] = dump(g->children);
                out.append(go);
            }
            return out;
        };
        root["groups"] = dump(root_groups_);
    }

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

        // Skip model_transformation when it's at defaults (identity placement).
        const ModelTransformation def;
        const ModelTransformation& xf = m.model_transformation;
        const bool xf_is_default =
            xf.a_frame == def.a_frame && xf.a == def.a && xf.b == def.b &&
            xf.rxyz_deg == def.rxyz_deg && xf.pivot == def.pivot;
        if (!xf_is_default) {
            QJsonObject to;
            to["a_frame"] = (xf.a_frame == AFrame::ModelLocal)
                ? "ModelLocal" : "ModelGlobal";
            auto writeVec3 = [](const Eigen::Vector3d& v) {
                QJsonArray a;
                a.append(v.x()); a.append(v.y()); a.append(v.z());
                return a;
            };
            to["a"]        = writeVec3(xf.a);
            to["b"]        = writeVec3(xf.b);
            to["rxyz_deg"] = writeVec3(xf.rxyz_deg);
            to["pivot"]    = writeVec3(xf.pivot);
            mo["model_transformation"] = to;
        }

        if (!m.visible) mo["visible"] = false;
        if (!m.group_id.isEmpty()) mo["group_id"] = m.group_id;

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
