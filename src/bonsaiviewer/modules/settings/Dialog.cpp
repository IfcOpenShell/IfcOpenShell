// This file was generated with the assistance of an AI coding tool.
/********************************************************************************
 *                                                                              *
 * This file is part of Bonsai.                                                 *
 *                                                                              *
 * Bonsai is free software: you can redistribute it and/or modify               *
 * it under the terms of the GNU General Public License as published by         *
 * the Free Software Foundation, either version 3.0 of the License, or          *
 * (at your option) any later version.                                          *
 *                                                                              *
 * Bonsai is distributed in the hope that it will be useful,                    *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
 * GNU General Public License for more details.                                 *
 *                                                                              *
 * You should have received a copy of the GNU General Public License            *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.         *
 *                                                                              *
 ********************************************************************************/

#include "Dialog.h"

#include "../../SessionState.h"
#include "../../ViewerSettings.h"
#include "../../../ifcviewer/AppSettings.h"
#include "../../components/Dialog.h"
#include "../../components/Section.h"
#include "../../components/SvgIcon.h"
#include "../../components/Style.h"
#include "../connectors/Process.h"
#include "../connectors/Registry.h"

#include <QCheckBox>
#include <QColorDialog>
#include <QComboBox>
#include <QDialogButtonBox>
#include <QDoubleSpinBox>
#include <QFrame>
#include <QFormLayout>
#include <QGridLayout>
#include <QHBoxLayout>
#include <QLabel>
#include <QLineEdit>
#include <QMessageBox>
#include <QPointer>
#include <QPushButton>
#include <QShowEvent>
#include <QSpinBox>
#include <QToolButton>
#include <QVBoxLayout>

namespace bonsaiviewer::modules::settings {

SettingsDialog::SettingsDialog(bonsaiviewer::SessionState* session_state, QWidget* parent)
    : components::TabbedDialog(parent)
    , session_state_(session_state)
{
    setObjectName("appDialog");
    setWindowTitle("Settings");
    setModal(true);
    resize(520, 420);
    setupUi();
}

void SettingsDialog::showEvent(QShowEvent* event) {
    syncFromSettings();
    QDialog::showEvent(event);
}

void SettingsDialog::setupUi() {
    auto* graphics_tab = new QWidget(this);
    auto* graphics_layout = new QVBoxLayout(graphics_tab);
    graphics_layout->setContentsMargins(0, 0, 0, 0);
    graphics_layout->setSpacing(components::style::metrics::padding);
    graphics_layout->setAlignment(Qt::AlignTop);

    auto* general_section = new components::Section("General", components::SectionHeaderMode::Visible, graphics_tab);
    auto* general_body = new QWidget(general_section);
    auto* general_form = new QFormLayout(general_body);
    general_form->setContentsMargins(0, 0, 0, 0);
    general_form->setHorizontalSpacing(16);
    general_form->setVerticalSpacing(10);

    geometry_library_edit_ = new QLineEdit(general_body);
    geometry_library_edit_->setMinimumWidth(300);
    general_form->addRow("Geometry Library", geometry_library_edit_);

    show_stats_check_ = new QCheckBox(general_body);
    general_form->addRow("Show Performance Stats", show_stats_check_);

    backface_culling_check_ = new QCheckBox(general_body);
    backface_culling_check_->setToolTip(
        "Skip triangles facing away from the camera. Big FPS win on closed solids; "
        "disable if you see holes in open geometry.");
    general_form->addRow("Backface Culling", backface_culling_check_);

    general_section->addBodyWidget(general_body);

    auto* loading_section = new components::Section("Loading", components::SectionHeaderMode::Visible, graphics_tab);
    auto* loading_body = new QWidget(loading_section);
    auto* loading_form = new QFormLayout(loading_body);
    loading_form->setContentsMargins(0, 0, 0, 0);
    loading_form->setHorizontalSpacing(16);
    loading_form->setVerticalSpacing(10);

    void_limit_spin_ = new QSpinBox(loading_body);
    void_limit_spin_->setRange(0, 100000);
    loading_form->addRow("Void Limit", void_limit_spin_);

    deflection_tolerance_spin_ = new QDoubleSpinBox(loading_body);
    deflection_tolerance_spin_->setRange(0.000001, 1000.0);
    deflection_tolerance_spin_->setDecimals(6);
    deflection_tolerance_spin_->setSingleStep(0.001);
    loading_form->addRow("Deflection Tolerance", deflection_tolerance_spin_);

    angular_tolerance_spin_ = new QDoubleSpinBox(loading_body);
    angular_tolerance_spin_->setRange(0.000001, 3.141592);
    angular_tolerance_spin_->setDecimals(6);
    angular_tolerance_spin_->setSingleStep(0.05);
    loading_form->addRow("Angular Tolerance", angular_tolerance_spin_);

    min_pixel_radius_spin_ = new QDoubleSpinBox(loading_body);
    min_pixel_radius_spin_->setRange(0.0, 100.0);
    min_pixel_radius_spin_->setDecimals(2);
    min_pixel_radius_spin_->setSingleStep(0.5);
    min_pixel_radius_spin_->setToolTip(
        "Minimum projected sphere radius (in pixels) for an instance to "
        "be drawn. Bigger = faster but more pop-in on small detail.");
    loading_form->addRow("Min Pixel Radius", min_pixel_radius_spin_);

    motion_min_pixel_radius_spin_ = new QDoubleSpinBox(loading_body);
    motion_min_pixel_radius_spin_->setRange(0.0, 100.0);
    motion_min_pixel_radius_spin_->setDecimals(2);
    motion_min_pixel_radius_spin_->setSingleStep(1.0);
    motion_min_pixel_radius_spin_->setToolTip(
        "Aggressive cull threshold while the camera is moving. 0 = no "
        "motion boost (motion uses the same threshold as still frames).");
    loading_form->addRow("Motion Min Pixel Radius", motion_min_pixel_radius_spin_);

    lod1_pixel_threshold_spin_ = new QDoubleSpinBox(loading_body);
    lod1_pixel_threshold_spin_->setRange(0.0, 1000.0);
    lod1_pixel_threshold_spin_->setDecimals(1);
    lod1_pixel_threshold_spin_->setSingleStep(1.0);
    lod1_pixel_threshold_spin_->setToolTip(
        "Pixel radius below which an instance switches to its LOD1 "
        "representation. 0 disables LOD1 entirely.");
    loading_form->addRow("LOD1 Pixel Threshold", lod1_pixel_threshold_spin_);

    hiz_enabled_check_ = new QCheckBox(loading_body);
    hiz_enabled_check_->setToolTip(
        "Enable HiZ (hierarchical Z) occlusion culling. Hides geometry "
        "behind opaque blockers based on a downsampled depth pyramid.");
    loading_form->addRow("HiZ Occlusion", hiz_enabled_check_);

    hiz_resolution_spin_ = new QSpinBox(loading_body);
    hiz_resolution_spin_->setRange(64, 4096);
    hiz_resolution_spin_->setSingleStep(64);
    hiz_resolution_spin_->setToolTip(
        "Base HiZ pyramid width in texels (height tracks aspect). "
        "Changes take effect on next viewport reinitialization.");
    loading_form->addRow("HiZ Resolution", hiz_resolution_spin_);

    loading_section->addBodyWidget(loading_body);
    graphics_layout->addWidget(general_section);
    graphics_layout->addWidget(loading_section);
    graphics_layout->addStretch(1);

    // Navigation tab: orbit / pan presets.  Selection always stays on
    // LMB so click + box-select keep working regardless of preset.
    auto* interface_tab = new QWidget(this);
    {
        auto* layout = new QVBoxLayout(interface_tab);
        layout->setContentsMargins(0, 0, 0, 0);
        layout->setSpacing(components::style::metrics::padding);
        layout->setAlignment(Qt::AlignTop);

        auto* section = new components::Section(
            "Navigation", components::SectionHeaderMode::Visible, interface_tab);
        auto* body = new QWidget(section);
        auto* form = new QFormLayout(body);
        form->setContentsMargins(0, 0, 0, 0);
        form->setHorizontalSpacing(16);
        form->setVerticalSpacing(10);

        nav_preset_combo_ = new QComboBox(body);
        // Order must match AppSettings::NavPreset enum ordering — index
        // is what we read back via currentIndex / setCurrentIndex.
        nav_preset_combo_->addItem("Blender (Orbit MMB, Pan Shift+MMB)");
        nav_preset_combo_->addItem("Rhino (Orbit RMB, Pan Shift+RMB)");
        nav_preset_combo_->addItem("Revit (Orbit Shift+MMB, Pan MMB)");
        nav_preset_combo_->addItem("Web (Orbit LMB, Pan MMB, Select RMB)");
        nav_preset_combo_->setToolTip(
            "Mouse-button mapping for orbit, pan, and selection.  Selection is "
            "on the left mouse button for Blender/Rhino/Revit and on the right "
            "for Web; click + box-select use whichever the preset assigns.");
        form->addRow("Preset", nav_preset_combo_);

        section->addBodyWidget(body);
        layout->addWidget(section);

        auto* theme_section = new components::Section(
            "Theme", components::SectionHeaderMode::Visible, interface_tab);
        auto* theme_body = new QWidget(theme_section);
        auto* theme_layout = new QVBoxLayout(theme_body);
        theme_layout->setContentsMargins(0, 0, 0, 0);
        theme_layout->setSpacing(components::style::metrics::padding);

        auto* theme_form = new QFormLayout();
        theme_form->setContentsMargins(0, 0, 0, 0);
        theme_form->setHorizontalSpacing(16);
        theme_form->setVerticalSpacing(10);

        theme_mode_combo_ = new QComboBox(theme_body);
        theme_mode_combo_->addItem("Dark", static_cast<int>(bonsaiviewer::ViewerSettings::ThemeMode::Dark));
        theme_mode_combo_->addItem("Light", static_cast<int>(bonsaiviewer::ViewerSettings::ThemeMode::Light));
        theme_mode_combo_->addItem("Custom", static_cast<int>(bonsaiviewer::ViewerSettings::ThemeMode::Custom));
        theme_form->addRow("Preset", theme_mode_combo_);

        theme_custom_body_ = new QWidget(theme_body);
        auto* custom_grid = new QGridLayout(theme_custom_body_);
        custom_grid->setContentsMargins(0, 0, 0, 0);
        custom_grid->setHorizontalSpacing(12);
        custom_grid->setVerticalSpacing(8);

        int row = 0;
        for (const auto& spec : bonsaiviewer::ViewerSettings::themeColorSpecs()) {
            auto* label = new QLabel(QString::fromUtf8(spec.label), theme_custom_body_);
            auto* edit = new QLineEdit(theme_custom_body_);
            edit->setPlaceholderText("#000000");
            auto* pick = new QPushButton("Pick", theme_custom_body_);
            connect(pick, &QPushButton::clicked, this, [this, edit]() { pickThemeColor(edit); });
            custom_grid->addWidget(label, row, 0);
            custom_grid->addWidget(edit, row, 1);
            custom_grid->addWidget(pick, row, 2);
            theme_color_editors_.push_back({QString::fromUtf8(spec.key), edit});
            ++row;
        }

        auto* theme_form_widget = new QWidget(theme_body);
        theme_form_widget->setLayout(theme_form);
        theme_layout->addWidget(theme_form_widget);
        theme_layout->addWidget(theme_custom_body_);
        theme_section->addBodyWidget(theme_body);
        layout->addWidget(theme_section);

        connect(theme_mode_combo_, &QComboBox::currentIndexChanged, this, [this](int) {
            updateThemeEditorEnabled();
        });
    }

    auto make_placeholder_tab = [this](const QString& title, const QString& detail) {
        auto* tab = new QWidget(this);
        auto* layout = new QVBoxLayout(tab);
        layout->setContentsMargins(0, 0, 0, 0);
        layout->setSpacing(components::style::metrics::padding);
        layout->setAlignment(Qt::AlignTop);

        auto* section = new components::Section(title, components::SectionHeaderMode::Visible, tab);
        auto* body = new QWidget(section);
        auto* body_layout = new QVBoxLayout(body);
        body_layout->setContentsMargins(0, 0, 0, 0);
        body_layout->setSpacing(8);

        auto* heading = new QLabel(title, body);
        auto* content = new QLabel(detail, body);
        content->setProperty("textRole", "secondary");
        content->setWordWrap(true);

        body_layout->addWidget(heading);
        body_layout->addWidget(content);
        section->addBodyWidget(body);
        layout->addWidget(section);
        layout->addStretch(1);
        return tab;
    };

    addTab("Interface", interface_tab);
    addTab("Keybindings", make_placeholder_tab("Keybindings", "Shortcut presets and command bindings will live here."));
    addTab("Graphics", graphics_tab);
    addTab("Connectors", buildConnectorsTab());
    addTab("About", make_placeholder_tab("About", "Version, credits, and environment information will live here."));

    auto* buttons = new QDialogButtonBox(QDialogButtonBox::Ok | QDialogButtonBox::Cancel, this);
    if (auto* ok = buttons->button(QDialogButtonBox::Ok)) {
        ok->setText("OK");
        ok->setIcon(components::icons::makeSvgIcon(":/icons/check.svg"));
    }
    if (auto* cancel = buttons->button(QDialogButtonBox::Cancel)) {
        cancel->setText("Cancel");
        cancel->setIcon(components::icons::makeSvgIcon(":/icons/xmark-circle.svg"));
    }
    connect(buttons, &QDialogButtonBox::accepted, this, &SettingsDialog::onAccepted);
    connect(buttons, &QDialogButtonBox::rejected, this, &QDialog::reject);

    addFooterWidget(buttons);
}

void SettingsDialog::syncFromSettings() {
    geometry_library_edit_->setText(AppSettings::instance().geometryLibrary());
    show_stats_check_->setChecked(AppSettings::instance().showStats());
    backface_culling_check_->setChecked(AppSettings::instance().backfaceCulling());
    void_limit_spin_->setValue(AppSettings::instance().voidLimit());
    deflection_tolerance_spin_->setValue(AppSettings::instance().deflectionTolerance());
    angular_tolerance_spin_->setValue(AppSettings::instance().angularTolerance());
    min_pixel_radius_spin_->setValue(AppSettings::instance().minPixelRadius());
    motion_min_pixel_radius_spin_->setValue(AppSettings::instance().motionMinPixelRadius());
    lod1_pixel_threshold_spin_->setValue(AppSettings::instance().lod1PixelThreshold());
    hiz_enabled_check_->setChecked(AppSettings::instance().hizEnabled());
    hiz_resolution_spin_->setValue(AppSettings::instance().hizResolution());
    nav_preset_combo_->setCurrentIndex(static_cast<int>(AppSettings::instance().navPreset()));
    syncThemeSettings();
}

void SettingsDialog::syncThemeSettings() {
    const auto& settings = bonsaiviewer::ViewerSettings::instance();
    const int idx = theme_mode_combo_->findData(static_cast<int>(settings.themeMode()));
    theme_mode_combo_->setCurrentIndex(idx >= 0 ? idx : 0);
    for (auto& editor : theme_color_editors_) {
        editor.edit->setText(settings.customColor(editor.key));
    }
    updateThemeEditorEnabled();
}

void SettingsDialog::updateThemeEditorEnabled() {
    if (!theme_mode_combo_ || !theme_custom_body_) return;
    const auto mode =
        static_cast<bonsaiviewer::ViewerSettings::ThemeMode>(theme_mode_combo_->currentData().toInt());
    const bool is_custom = mode == bonsaiviewer::ViewerSettings::ThemeMode::Custom;
    theme_custom_body_->setVisible(is_custom);
    theme_custom_body_->setEnabled(is_custom);
}

void SettingsDialog::pickThemeColor(QLineEdit* edit) {
    QColorDialog dialog(QColor(edit->text()), this);
    dialog.setObjectName("appDialog");
    dialog.setWindowTitle("Choose Color");
    dialog.setOption(QColorDialog::DontUseNativeDialog, true);
    if (dialog.exec() != QDialog::Accepted) return;
    const QColor color = dialog.selectedColor();
    if (!color.isValid()) return;
    edit->setText(color.name(QColor::HexRgb));
}

void SettingsDialog::onAccepted() {
    AppSettings::instance().setGeometryLibrary(geometry_library_edit_->text());
    AppSettings::instance().setShowStats(show_stats_check_->isChecked());
    AppSettings::instance().setBackfaceCulling(backface_culling_check_->isChecked());
    AppSettings::instance().setVoidLimit(void_limit_spin_->value());
    AppSettings::instance().setDeflectionTolerance(deflection_tolerance_spin_->value());
    AppSettings::instance().setAngularTolerance(angular_tolerance_spin_->value());
    AppSettings::instance().setMinPixelRadius(min_pixel_radius_spin_->value());
    AppSettings::instance().setMotionMinPixelRadius(motion_min_pixel_radius_spin_->value());
    AppSettings::instance().setLod1PixelThreshold(lod1_pixel_threshold_spin_->value());
    AppSettings::instance().setHizEnabled(hiz_enabled_check_->isChecked());
    AppSettings::instance().setHizResolution(hiz_resolution_spin_->value());
    AppSettings::instance().setNavPreset(
        static_cast<AppSettings::NavPreset>(nav_preset_combo_->currentIndex()));
    auto& interface_settings = bonsaiviewer::ViewerSettings::instance();
    interface_settings.setThemeMode(
        static_cast<bonsaiviewer::ViewerSettings::ThemeMode>(theme_mode_combo_->currentData().toInt()));
    for (const auto& editor : theme_color_editors_) {
        interface_settings.setCustomColor(editor.key, editor.edit->text());
    }
    accept();
}

QWidget* SettingsDialog::buildConnectorsTab() {
    auto* tab = new QWidget(this);
    auto* layout = new QVBoxLayout(tab);
    layout->setContentsMargins(0, 0, 0, 0);
    layout->setSpacing(components::style::metrics::padding);
    layout->setAlignment(Qt::AlignTop);

    auto* section = new components::Section(
        "Installed Connectors", components::SectionHeaderMode::Visible, tab);
    auto* body = new QWidget(section);
    auto* body_layout = new QVBoxLayout(body);
    body_layout->setContentsMargins(0, 0, 0, 0);
    body_layout->setSpacing(8);

    const auto& manifests = session_state_
        ? session_state_->connectorRegistry()->available()
        : std::vector<connectors::ConnectorManifest>{};

    if (manifests.empty()) {
        auto* empty = new QLabel(
            "No connectors found. Install one under your user connectors directory.",
            body);
        empty->setProperty("textRole", "secondary");
        empty->setWordWrap(true);
        body_layout->addWidget(empty);
    }

    for (const auto& manifest : manifests) {
        auto* row = new QWidget(body);
        auto* row_layout = new QHBoxLayout(row);
        row_layout->setContentsMargins(0, 0, 0, 0);
        row_layout->setSpacing(8);

        auto* name = new QLabel(manifest.name, row);
        auto* version = new QLabel(
            manifest.version.isEmpty() ? QString() : QString("v%1").arg(manifest.version), row);
        version->setProperty("textRole", "secondary");

        auto* settings_button = new QPushButton("Settings…", row);
        settings_button->setIcon(components::icons::makeSvgIcon(":/icons/settings.svg"));
        const QString connector_id = manifest.id;
        connect(settings_button, &QPushButton::clicked, this,
                [this, connector_id, settings_button]() {
            if (!session_state_) return;
            auto* proc = session_state_->connectorRegistry()->get(connector_id);
            if (!proc) {
                QMessageBox::warning(this, "Connector",
                    QString("Could not launch connector '%1':\n%2")
                        .arg(connector_id,
                             session_state_->connectorRegistry()->lastError()));
                return;
            }
            settings_button->setEnabled(false);
            QPointer<QPushButton> guard(settings_button);
            QPointer<SettingsDialog> self(this);
            proc->call("open_settings", QJsonValue(),
                [guard](const QJsonValue&) {
                    if (guard) guard->setEnabled(true);
                },
                [self, guard, connector_id](int code, const QString& message) {
                    if (guard) guard->setEnabled(true);
                    if (!self) return;
                    // -32601 = JSON-RPC "Method not found": connector opted
                    // out of the optional open_settings handler per spec.
                    if (code == -32601) {
                        QMessageBox::information(self, "Connector",
                            "Settings not available.");
                    } else {
                        QMessageBox::warning(self, "Connector",
                            QString("Connector '%1' failed to open settings:\n%2")
                                .arg(connector_id, message));
                    }
                });
        });

        row_layout->addWidget(name);
        row_layout->addWidget(version);
        row_layout->addStretch(1);
        row_layout->addWidget(settings_button);
        body_layout->addWidget(row);
    }

    section->addBodyWidget(body);
    layout->addWidget(section);
    layout->addStretch(1);
    return tab;
}

} // namespace bonsaiviewer::modules::settings
