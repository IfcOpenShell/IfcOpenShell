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

#include "Process.h"

#include <QDebug>
#include <QJsonDocument>
#include <QJsonObject>
#include <QStringList>
#include <QTimer>

namespace ifcviewerfull::modules::connectors {

namespace {

constexpr int kStartTimeoutMs = 5000;
constexpr int kShutdownTimeoutMs = 3000;

// Reserved out-of-band error codes used by the host (not by the connector).
// JSON-RPC reserves -32000..-32099 for "implementation-defined server
// errors"; we co-opt three for transport failures.
constexpr int kErrLaunchFailed   = -32000;
constexpr int kErrShutdown       = -32001;
constexpr int kErrProcessExited  = -32002;

} // namespace

ConnectorProcess::ConnectorProcess(ConnectorManifest manifest, QObject* parent)
    : QObject(parent)
    , manifest_(std::move(manifest))
{
}

ConnectorProcess::~ConnectorProcess() {
    shutdown();
}

bool ConnectorProcess::isRunning() const {
    return process_ && process_->state() != QProcess::NotRunning;
}

bool ConnectorProcess::ensureStarted() {
    if (isRunning()) return true;
    if (manifest_.exec_path.isEmpty()) {
        last_error_ = QString("Connector '%1' has no executable configured.")
                          .arg(manifest_.id);
        return false;
    }

    process_ = new QProcess(this);
    process_->setWorkingDirectory(manifest_.folder);
    process_->setProcessChannelMode(QProcess::SeparateChannels);
    connect(process_, &QProcess::readyReadStandardOutput,
            this, &ConnectorProcess::onReadyReadStdout);
    connect(process_, &QProcess::finished,
            this, &ConnectorProcess::onProcessFinished);

    process_->start(manifest_.exec_path, QStringList{});
    if (!process_->waitForStarted(kStartTimeoutMs)) {
        last_error_ = QString("Failed to launch connector '%1': %2")
                          .arg(manifest_.id, process_->errorString());
        process_->deleteLater();
        process_ = nullptr;
        return false;
    }
    last_error_.clear();
    shutting_down_ = false;
    return true;
}

void ConnectorProcess::call(const QString& method,
                            const QJsonValue& params,
                            ResultHandler on_result,
                            ErrorHandler on_error) {
    if (!ensureStarted()) {
        const QString err = last_error_;
        // Queue rather than invoke inline so callers see uniform async order
        // regardless of whether the launch succeeded.
        QTimer::singleShot(0, this, [on_error = std::move(on_error), err]() {
            if (on_error) on_error(kErrLaunchFailed, err);
        });
        return;
    }

    const QString id = QString::number(next_request_id_++);
    pending_.insert(id, Pending{std::move(on_result), std::move(on_error)});

    QJsonObject msg;
    msg["jsonrpc"] = "2.0";
    msg["id"] = id;
    msg["method"] = method;
    if (!params.isUndefined() && !params.isNull()) {
        msg["params"] = params;
    }
    const QByteArray line = QJsonDocument(msg).toJson(QJsonDocument::Compact) + '\n';
    process_->write(line);
}

void ConnectorProcess::shutdown() {
    if (!process_) return;
    shutting_down_ = true;
    if (process_->state() == QProcess::Running) {
        process_->closeWriteChannel();
        if (!process_->waitForFinished(kShutdownTimeoutMs)) {
            qWarning() << "ifcviewer connectors:" << manifest_.id
                       << "did not exit within" << kShutdownTimeoutMs
                       << "ms after stdin close; killing.";
            process_->kill();
            process_->waitForFinished(1000);
        }
    }
    failPendingAndClear(kErrShutdown,
        QString("Connector '%1' was shut down.").arg(manifest_.id));
    process_->deleteLater();
    process_ = nullptr;
}

void ConnectorProcess::onReadyReadStdout() {
    if (!process_) return;
    buffer_.append(process_->readAllStandardOutput());
    int newline = buffer_.indexOf('\n');
    while (newline >= 0) {
        const QByteArray line = buffer_.left(newline);
        buffer_.remove(0, newline + 1);
        if (!line.isEmpty()) dispatchLine(line);
        newline = buffer_.indexOf('\n');
    }
}

void ConnectorProcess::onProcessFinished(int exit_code, QProcess::ExitStatus status) {
    const bool unexpected = !shutting_down_;
    const QString reason = (status == QProcess::CrashExit)
        ? QString("Connector '%1' crashed (exit %2).").arg(manifest_.id).arg(exit_code)
        : QString("Connector '%1' exited (code %2).").arg(manifest_.id).arg(exit_code);
    failPendingAndClear(kErrProcessExited, reason);
    if (unexpected) emit crashed(reason);
}

void ConnectorProcess::dispatchLine(const QByteArray& line) {
    QJsonParseError err{};
    const QJsonDocument doc = QJsonDocument::fromJson(line, &err);
    if (doc.isNull() || !doc.isObject()) {
        qWarning() << "ifcviewer connectors:" << manifest_.id
                   << "emitted non-JSON line:" << line << err.errorString();
        return;
    }
    const QJsonObject obj = doc.object();
    if (obj.value("jsonrpc").toString() != "2.0") {
        qWarning() << "ifcviewer connectors:" << manifest_.id
                   << "ignored message missing jsonrpc=2.0:" << line;
        return;
    }
    // Connector echoes our id verbatim (we always send strings), but accept
    // numeric ids too in case a connector parses our "0" as an int.
    const QString id = obj.value("id").toVariant().toString();
    if (!pending_.contains(id)) {
        qWarning() << "ifcviewer connectors:" << manifest_.id
                   << "ignored response with unknown id:" << id;
        return;
    }
    Pending pending = pending_.take(id);
    if (obj.contains("error")) {
        const QJsonObject err_obj = obj.value("error").toObject();
        const int code = err_obj.value("code").toInt();
        const QString message = err_obj.value("message").toString();
        if (pending.on_error) pending.on_error(code, message);
    } else {
        if (pending.on_result) pending.on_result(obj.value("result"));
    }
}

void ConnectorProcess::failPendingAndClear(int code, const QString& message) {
    QHash<QString, Pending> snapshot;
    snapshot.swap(pending_);
    for (const auto& p : snapshot) {
        if (p.on_error) p.on_error(code, message);
    }
}

} // namespace ifcviewerfull::modules::connectors
