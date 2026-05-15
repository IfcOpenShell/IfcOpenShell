// This file was generated with the assistance of an AI coding tool.
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

#include "Commands.h"

#include "AddModelDialog.h"
#include "SettingsDialog.h"

#include "../../ElementRegistry.h"
#include "../../SessionState.h"
#include "../../../ifcviewer/Federation.h"
#include "../../../ifcviewer/HeadlessSidecarBuilder.h"
#include "../../../ifcviewer/LodBuilder.h"
#include "../../../ifcviewer/SceneLoader.h"
#include "../../../ifcviewer/SidecarCache.h"
#include "../../../ifcviewer/ViewportWindow.h"
#include "../../../ifcgeom/Serializer.h"
#include "../../../serializers/document_serializer_plugin.h"

#include <QDebug>
#include <QDir>
#include <QDirIterator>
#include <QElapsedTimer>
#include <QFile>
#include <QFileDialog>
#include <QFileInfo>
#include <QInputDialog>
#include <QLineEdit>
#include <QListView>
#include <QMessageBox>
#include <QProgressDialog>
#include <QStandardPaths>
#include <QThread>
#include <QTreeView>
#include <QUuid>

#include <QtCore/private/qzipwriter_p.h>

#include <Eigen/Dense>

#include <memory>

namespace ifcviewerfull::modules::models::commands {

namespace {

QString formatElapsed(qint64 ms) {
    return (ms >= 1000)
        ? QString::number(ms / 1000.0, 'f', 2) + " s"
        : QString::number(ms) + " ms";
}

} // namespace

void toggleVisibility(SessionState& s, ItemKind kind, const QString& id) {
    Federation* fed = s.federation();
    if (kind == ItemKind::Group) {
        const Federation::Group* group = fed->findGroupById(id);
        if (!group) return;
        fed->setGroupVisible(id, !group->visible);
        s.notifyVisibilityChanged();
        s.setStatusMessage("Models", group->visible ? "Group hidden" : "Group shown");
    } else {
        const Federation::Model* model = fed->findById(id);
        if (!model) return;
        fed->setModelVisible(id, !model->visible);
        s.notifyVisibilityChanged();
        s.setStatusMessage("Models", model->visible ? "Model hidden" : "Model shown");
    }
}

void addGroup(SessionState& s, QWidget& host, const QString& parent_group_id) {
    bool ok = false;
    const QString name = QInputDialog::getText(
        &host, "New Group", "Group name:", QLineEdit::Normal, "Group", &ok);
    if (!ok) return;
    const QString trimmed = name.trimmed();
    if (trimmed.isEmpty()) return;

    s.federation()->addGroup(trimmed, parent_group_id);
    s.notifyFederationChanged();
    s.setStatusMessage("Models", "Group added");
}

void renameGroup(SessionState& s, QWidget& host, const QString& group_id) {
    const Federation::Group* group = s.federation()->findGroupById(group_id);
    if (!group) return;

    bool ok = false;
    const QString name = QInputDialog::getText(
        &host, "Rename Group", "Group name:", QLineEdit::Normal, group->display_name, &ok);
    if (!ok) return;
    const QString trimmed = name.trimmed();
    if (trimmed.isEmpty()) return;

    s.federation()->setGroupName(group_id, trimmed);
    s.notifyFederationChanged();
    s.setStatusMessage("Models", "Group renamed");
}

void moveGroup(SessionState& s, const QString& id, const QString& parent_group_id) {
    s.federation()->setGroupParent(id, parent_group_id);
    s.notifyFederationChanged();
    s.setStatusMessage("Models", parent_group_id.isEmpty() ? "Group moved to root" : "Group moved");
}

void moveModels(SessionState& s, const QStringList& ids, const QString& parent_group_id) {
    for (const auto& id : ids) {
        s.federation()->setModelGroup(id, parent_group_id);
    }
    s.notifyFederationChanged();
    s.setStatusMessage("Models", parent_group_id.isEmpty() ? "Model(s) moved to root" : "Model(s) moved");
}

void removeGroup(SessionState& s, QWidget& host, const QString& group_id) {
    const Federation::Group* group = s.federation()->findGroupById(group_id);
    if (!group) return;

    const auto choice = QMessageBox::question(
        &host, "Remove Group",
        QString("Remove group '%1'? Models inside it will move to the parent.").arg(group->display_name),
        QMessageBox::Yes | QMessageBox::No, QMessageBox::No);
    if (choice != QMessageBox::Yes) return;

    s.federation()->removeGroup(group_id);
    s.notifyFederationChanged();
    s.setStatusMessage("Models", "Group removed");
}

void removeModel(SessionState& s, ViewportWindow& vp, QWidget& host, const QString& fed_id) {
    const Federation::Model* model = s.federation()->findById(fed_id);
    const QString label = model ? model->display_name : fed_id;
    const auto choice = QMessageBox::question(
        &host, "Remove Model",
        QString("Remove model '%1' from the federation?").arg(label),
        QMessageBox::Yes | QMessageBox::No, QMessageBox::No);
    if (choice != QMessageBox::Yes) return;

    const uint32_t mid = s.modelIdForFedId(fed_id);
    if (mid == 0) {
        s.federation()->removeModel(fed_id);
        s.notifyFederationChanged();
        s.setStatusMessage("Models", "Model removed");
        return;
    }
    if (s.loader()->isLoadingModel(mid)) return;

    vp.setSelectedObjectId(0);
    s.setSelectedObjectId(0);
    s.federation()->removeModel(fed_id);
    vp.removeModel(mid);
    s.loader()->removeModel(mid);
    s.elementRegistry()->removeModel(mid);
    s.removeModelMappingByFedId(fed_id);
    s.notifySelectionChanged();
    s.notifyModelsChanged();
    s.setStatusMessage("Models", "Model removed");
}

namespace detail {

void loadModels(SessionState& s, const QStringList& paths, const QStringList& fed_ids) {
    if (paths.isEmpty()) return;

    const auto ids = s.loader()->addFiles(paths);
    for (int i = 0; i < paths.size() && i < static_cast<int>(ids.size()) && i < fed_ids.size(); ++i) {
        s.setModelMapping(fed_ids[i], ids[i]);
    }
}

} // namespace detail

void addModel(SessionState& s, QWidget& host) {
    AddModelDialog dialog(&host);
    if (dialog.exec() != QDialog::Accepted) return;

    QStringList paths;
    switch (dialog.selectedMode()) {
    case SourceMode::IfcFile: {
        QFileDialog file_dialog(&host, "Add IFC Files");
        file_dialog.setFileMode(QFileDialog::ExistingFiles);
        file_dialog.setNameFilter("IFC Files (*.ifc);;All Files (*)");
        file_dialog.setOption(QFileDialog::DontUseNativeDialog, true);
        if (file_dialog.exec() == QDialog::Accepted) {
            paths = file_dialog.selectedFiles();
        }
        break;
    }
    case SourceMode::IfcDatabase: {
        QFileDialog database_dialog(&host, "Add IFC Databases");
        database_dialog.setFileMode(QFileDialog::Directory);
        database_dialog.setOption(QFileDialog::ShowDirsOnly, true);
        database_dialog.setOption(QFileDialog::DontResolveSymlinks, true);
        database_dialog.setOption(QFileDialog::DontUseNativeDialog, true);
        if (auto* list = database_dialog.findChild<QListView*>("listView")) {
            list->setSelectionMode(QAbstractItemView::ExtendedSelection);
        }
        if (auto* tree = database_dialog.findChild<QTreeView*>()) {
            tree->setSelectionMode(QAbstractItemView::ExtendedSelection);
        }
        if (database_dialog.exec() == QDialog::Accepted) {
            paths = database_dialog.selectedFiles();
        }
        break;
    }
    case SourceMode::GeometryOnly: {
        QFileDialog file_dialog(&host, "Add Geometry Only");
        file_dialog.setFileMode(QFileDialog::ExistingFiles);
        file_dialog.setNameFilter("IFC Viewer Cache (*.ifcview);;All Files (*)");
        file_dialog.setOption(QFileDialog::DontUseNativeDialog, true);
        if (file_dialog.exec() == QDialog::Accepted) {
            paths = file_dialog.selectedFiles();
        }
        break;
    }
    case SourceMode::ConvertToDatabase:
        convertIfcToDatabase(s, host);
        return;
    case SourceMode::ExportGeometryDatabase:
        exportGeometryDatabase(s, host);
        return;
    case SourceMode::None:
        return;
    }

    QStringList accepted_paths;
    QStringList accepted_fed_ids;
    for (const auto& path : paths) {
        const QString fed_id = s.federation()->addModel(path);
        if (fed_id.isEmpty()) continue;
        accepted_paths << path;
        accepted_fed_ids << fed_id;
    }
    detail::loadModels(s, accepted_paths, accepted_fed_ids);
    s.notifyModelsChanged();
}

void convertIfcToDatabase(SessionState& s, QWidget& host) {
    QFileDialog input_dialog(&host, "Select IFC File to Convert");
    input_dialog.setFileMode(QFileDialog::ExistingFile);
    input_dialog.setNameFilter("IFC Files (*.ifc);;All Files (*)");
    input_dialog.setOption(QFileDialog::DontUseNativeDialog, true);
    if (input_dialog.exec() != QDialog::Accepted) return;
    const QStringList inputs = input_dialog.selectedFiles();
    if (inputs.isEmpty()) return;
    const QString input_path = inputs.first();

    const QFileInfo input_info(input_path);
    const QString default_output = input_info.absoluteDir().filePath(input_info.completeBaseName() + ".rdb");

    QFileDialog output_dialog(&host, "Save IFC Database As");
    output_dialog.setAcceptMode(QFileDialog::AcceptSave);
    output_dialog.setFileMode(QFileDialog::AnyFile);
    output_dialog.setNameFilter("IFC Database (*.rdb);;All Files (*)");
    output_dialog.setDefaultSuffix("rdb");
    output_dialog.selectFile(default_output);
    output_dialog.setOption(QFileDialog::DontUseNativeDialog, true);
    output_dialog.setOption(QFileDialog::DontConfirmOverwrite, true);
    if (output_dialog.exec() != QDialog::Accepted) return;
    const QStringList outputs = output_dialog.selectedFiles();
    if (outputs.isEmpty()) return;
    QString output_path = outputs.first();
    if (!output_path.endsWith(".rdb", Qt::CaseInsensitive)) {
        output_path += ".rdb";
    }

    const QFileInfo output_info(output_path);
    if (output_info.exists()) {
        const QString message = QString("'%1' already exists. Overwrite?").arg(output_info.fileName());
        if (QMessageBox::question(&host, "Convert IFC to Database", message,
                                  QMessageBox::Yes | QMessageBox::No, QMessageBox::No) != QMessageBox::Yes) {
            return;
        }
    }

    auto* progress = new QProgressDialog(&host);
    progress->setWindowTitle("Convert IFC to Database");
    progress->setLabelText(QString("Converting %1 to %2…")
                               .arg(QFileInfo(input_path).fileName(),
                                    QFileInfo(output_path).fileName()));
    progress->setRange(0, 0);
    progress->setCancelButton(nullptr);
    progress->setMinimumDuration(0);
    progress->setWindowModality(Qt::ApplicationModal);
    progress->setAutoClose(false);
    progress->setAutoReset(false);
    progress->show();

    s.setStatusMessage("Converting",
        QString("%1 → %2").arg(QFileInfo(input_path).fileName(), QFileInfo(output_path).fileName()));

    auto timer = std::make_shared<QElapsedTimer>();
    timer->start();
    auto error_message = std::make_shared<QString>();

    QThread* thread = QThread::create([input_path, output_path, error_message]() {
        try {
            ifcopenshell::serializers::document_serializer_context context;
            context.file = nullptr;
            context.input_filename = input_path.toStdString();
            context.output_filename = output_path.toStdString();
            context.stream = true;

            auto& registry = ifcopenshell::serializers::document_serializer_registry_instance();
            const auto* info = registry.find("rdb");
            if (!info) {
                throw ifcopenshell::exception(
                    "No 'rdb' document serializer is registered. The RocksDB serializer plugin may not be installed.");
            }
            if (!info->supports_input_filename) {
                throw ifcopenshell::exception("RDB serializer does not support streaming from an input filename");
            }

            boost::shared_ptr<Serializer> serializer = registry.create("rdb", context);
            serializer->finalize();
        } catch (const std::exception& e) {
            *error_message = QString::fromUtf8(e.what());
        } catch (...) {
            *error_message = "Unknown error during IFC to RDB conversion";
        }
    });

    QObject::connect(thread, &QThread::finished, &host,
            [&s, host_ptr = &host, thread, progress, timer, error_message, input_path, output_path]() {
        const qint64 elapsed = timer->elapsed();

        progress->close();
        progress->deleteLater();
        thread->deleteLater();

        if (!error_message->isEmpty()) {
            s.setStatusMessage("Error", *error_message);
            QMessageBox::warning(host_ptr, "Convert IFC to Database",
                                 QString("Conversion failed:\n%1").arg(*error_message));
            return;
        }

        s.setStatusMessage(
            "Converted",
            QString("%1 → %2 in %3")
                .arg(QFileInfo(input_path).fileName(),
                     QFileInfo(output_path).fileName(),
                     formatElapsed(elapsed)));
        QMessageBox::information(host_ptr, "Convert IFC to Database",
                                 QString("Database written to:\n%1").arg(output_path));
    });

    thread->start();
}

void exportGeometryDatabase(SessionState& s, QWidget& host) {
    QFileDialog input_dialog(&host, "Select IFC File to Export");
    input_dialog.setFileMode(QFileDialog::ExistingFile);
    input_dialog.setNameFilter("IFC Files (*.ifc);;All Files (*)");
    input_dialog.setOption(QFileDialog::DontUseNativeDialog, true);
    if (input_dialog.exec() != QDialog::Accepted) return;
    const QStringList inputs = input_dialog.selectedFiles();
    if (inputs.isEmpty()) return;
    const QString input_path = inputs.first();

    const QFileInfo input_info(input_path);
    const QString default_output = input_info.absoluteDir().filePath(input_info.completeBaseName() + ".rdbview");

    QFileDialog output_dialog(&host, "Save Geometry Database As");
    output_dialog.setAcceptMode(QFileDialog::AcceptSave);
    output_dialog.setFileMode(QFileDialog::AnyFile);
    output_dialog.setNameFilter("Geometry Database (*.rdbview);;All Files (*)");
    output_dialog.setDefaultSuffix("rdbview");
    output_dialog.selectFile(default_output);
    output_dialog.setOption(QFileDialog::DontUseNativeDialog, true);
    if (output_dialog.exec() != QDialog::Accepted) return;
    const QStringList outputs = output_dialog.selectedFiles();
    if (outputs.isEmpty()) return;
    QString output_path = outputs.first();
    if (!output_path.endsWith(".rdbview", Qt::CaseInsensitive)) {
        output_path += ".rdbview";
    }

    auto* progress = new QProgressDialog(&host);
    progress->setWindowTitle("Export Geometry Database");
    progress->setLabelText(QString("Exporting %1 to %2…")
                               .arg(QFileInfo(input_path).fileName(),
                                    QFileInfo(output_path).fileName()));
    progress->setRange(0, 0);
    progress->setCancelButton(nullptr);
    progress->setMinimumDuration(0);
    progress->setWindowModality(Qt::ApplicationModal);
    progress->setAutoClose(false);
    progress->setAutoReset(false);
    progress->show();

    s.setStatusMessage("Exporting",
        QString("%1 → %2").arg(QFileInfo(input_path).fileName(), QFileInfo(output_path).fileName()));

    auto timer = std::make_shared<QElapsedTimer>();
    timer->start();
    auto error_message = std::make_shared<QString>();

    QThread* thread = QThread::create([input_path, output_path, error_message]() {
        // Scratch dir holds the intermediate .ifcview and .rdb directory
        // until they're zipped into the .rdbview.  RAII-like cleanup at the
        // bottom of this lambda; on early exception we leak it (cheap
        // tradeoff to keep the failure log around for the user).
        const QString tmp_root = QDir(QStandardPaths::writableLocation(QStandardPaths::TempLocation))
                                     .filePath(QString("ifcviewer-export-%1")
                                                   .arg(QUuid::createUuid().toString(QUuid::Id128)));
        QDir().mkpath(tmp_root);

        const QString tmp_anchor   = QDir(tmp_root).filePath("model.ifc");
        const QString tmp_sidecar  = QDir(tmp_root).filePath("model.ifcview");
        const QString tmp_rdb_dir  = QDir(tmp_root).filePath("model.rdb");

        try {
            ifcopenshell::serializers::document_serializer_context context;
            context.file = nullptr;
            context.input_filename  = input_path.toStdString();
            context.output_filename = tmp_rdb_dir.toStdString();
            context.stream = true;
            context.skip_supertypes = { "IfcRepresentationItem" };

            auto& registry = ifcopenshell::serializers::document_serializer_registry_instance();
            const auto* info = registry.find("rdb");
            if (!info) {
                throw ifcopenshell::exception(
                    "No 'rdb' document serializer is registered. The RocksDB serializer plugin may not be installed.");
            }
            if (!info->supports_input_filename) {
                throw ifcopenshell::exception("RDB serializer does not support streaming from an input filename");
            }

            boost::shared_ptr<Serializer> serializer = registry.create("rdb", context);
            serializer->finalize();
            serializer.reset();

            HeadlessSidecarBuilder builder;
            if (!builder.build(input_path, tmp_anchor)) {
                throw ifcopenshell::exception(
                    ("Sidecar build failed: " + builder.lastError()).toStdString());
            }
            if (!QFileInfo::exists(tmp_sidecar)) {
                throw ifcopenshell::exception(
                    ("Sidecar build reported success but " + tmp_sidecar + " is missing").toStdString());
            }

            // Write to a sibling `.tmp` then rename so a partial file never
            // appears at the destination (matters for cloud-sync folders).
            const QString tmp_zip = output_path + ".tmp";
            QFile::remove(tmp_zip);
            {
                QZipWriter writer(tmp_zip);
                if (writer.status() != QZipWriter::NoError) {
                    throw ifcopenshell::exception(
                        ("Failed to open " + tmp_zip + " for writing").toStdString());
                }
                writer.setCompressionPolicy(QZipWriter::AutoCompress);

                {
                    QFile sf(tmp_sidecar);
                    if (!sf.open(QIODevice::ReadOnly)) {
                        throw ifcopenshell::exception(
                            ("Failed to read sidecar " + tmp_sidecar).toStdString());
                    }
                    writer.addFile("model.ifcview", sf.readAll());
                }

                QDirIterator it(tmp_rdb_dir, QDir::Files | QDir::NoDotAndDotDot,
                                QDirIterator::Subdirectories);
                const QDir rdb_root(tmp_rdb_dir);
                while (it.hasNext()) {
                    const QString file_path = it.next();
                    const QString rel = rdb_root.relativeFilePath(file_path);
                    QFile f(file_path);
                    if (!f.open(QIODevice::ReadOnly)) {
                        throw ifcopenshell::exception(
                            ("Failed to read " + file_path + " for zip").toStdString());
                    }
                    writer.addFile(QString("model.rdb/%1").arg(rel), f.readAll());
                }

                writer.close();
                if (writer.status() != QZipWriter::NoError) {
                    throw ifcopenshell::exception(
                        ("Failed to finalize " + tmp_zip).toStdString());
                }
            }

            QFile::remove(output_path);
            if (!QFile::rename(tmp_zip, output_path)) {
                QFile::remove(tmp_zip);
                throw ifcopenshell::exception(
                    ("Failed to move " + tmp_zip + " to " + output_path).toStdString());
            }
        } catch (const std::exception& e) {
            *error_message = QString::fromUtf8(e.what());
        } catch (...) {
            *error_message = "Unknown error during geometry database export";
        }

        QDir(tmp_root).removeRecursively();
    });

    QObject::connect(thread, &QThread::finished, &host,
            [&s, host_ptr = &host, thread, progress, timer, error_message, input_path, output_path]() {
        const qint64 elapsed = timer->elapsed();

        progress->close();
        progress->deleteLater();
        thread->deleteLater();

        if (!error_message->isEmpty()) {
            s.setStatusMessage("Error", *error_message);
            QMessageBox::warning(host_ptr, "Export Geometry Database",
                                 QString("Export failed:\n%1").arg(*error_message));
            return;
        }

        s.setStatusMessage(
            "Exported",
            QString("%1 → %2 in %3")
                .arg(QFileInfo(input_path).fileName(),
                     QFileInfo(output_path).fileName(),
                     formatElapsed(elapsed)));
        QMessageBox::information(host_ptr, "Export Geometry Database",
                                 QString("Geometry database written to:\n%1").arg(output_path));
    });

    thread->start();
}

void openSettings(SessionState& s, QWidget& host) {
    SettingsDialog dialog(&s, &host);
    dialog.exec();
}

void writeSidecarForLoadedModel(SessionState& s, ViewportWindow& vp, uint32_t mid) {
    SceneLoader* loader = s.loader();
    if (!loader) return;

    SidecarData sidecar_data;
    if (!vp.snapshotModel(mid, sidecar_data)) return;

    if (const ModelGeoref* georef = loader->modelGeoref(mid)) {
        sidecar_data.has_coordinate_operation = georef->has_coordinate_operation ? 1 : 0;
        Eigen::Map<Eigen::Matrix<double, 4, 4, Eigen::ColMajor>>(
            sidecar_data.coordinate_operation_meters) = georef->coordinate_operation_meters;
        sidecar_data.project_length_to_meters = georef->units.project_length_to_meters;
        sidecar_data.map_unit_to_meters = georef->units.map_unit_to_meters;
    }

    if (auto* element_registry = s.elementRegistry()) {
        for (const auto& info : element_registry->basicElementInfoForModel(mid)) {
            PackedElementInfo packed;
            packed.object_id = info.object_id;
            packed.model_id = info.model_id;
            packed.ifc_id = info.ifc_id;
            packed.parent_id = info.parent_id;

            const std::string guid = info.guid.toStdString();
            packed.guid_offset = static_cast<uint32_t>(sidecar_data.string_table.size());
            packed.guid_length = static_cast<uint32_t>(guid.size());
            sidecar_data.string_table += guid;

            const std::string name = info.name.toStdString();
            packed.name_offset = static_cast<uint32_t>(sidecar_data.string_table.size());
            packed.name_length = static_cast<uint32_t>(name.size());
            sidecar_data.string_table += name;

            const std::string type = info.type.toStdString();
            packed.type_offset = static_cast<uint32_t>(sidecar_data.string_table.size());
            packed.type_length = static_cast<uint32_t>(type.size());
            sidecar_data.string_table += type;

            sidecar_data.elements.push_back(packed);
        }
    }

    QElapsedTimer lod_timer;
    lod_timer.start();
    buildLods(sidecar_data);
    const LodStats lod_stats = summariseLods(sidecar_data);
    qDebug("  LOD build: %lld ms — %u/%u meshes got LOD1 "
           "(%u tris -> %u tris for those meshes)",
           lod_timer.elapsed(),
           lod_stats.meshes_with_lod1, lod_stats.meshes_total,
           lod_stats.tris_lod0_for_lod1, lod_stats.tris_lod1);

    vp.applyLodExtension(mid, sidecar_data);

    QElapsedTimer sidecar_timer;
    sidecar_timer.start();
    const bool ok = writeSidecar(loader->filePath(mid).toStdString(), sidecar_data);
    qDebug("  Sidecar write: %lld ms (%s)", sidecar_timer.elapsed(), ok ? "ok" : "FAILED");
}

} // namespace ifcviewerfull::modules::models::commands
