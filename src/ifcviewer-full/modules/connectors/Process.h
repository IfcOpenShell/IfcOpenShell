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

#ifndef IFCINTERFACE_MODULES_CONNECTORS_PROCESS_H
#define IFCINTERFACE_MODULES_CONNECTORS_PROCESS_H

#include "Discovery.h"

#include <QByteArray>
#include <QHash>
#include <QJsonValue>
#include <QObject>
#include <QProcess>
#include <QString>
#include <functional>

namespace ifcviewerfull::modules::connectors {

// One running connector subprocess. Owns the QProcess, frames stdio as
// newline-delimited JSON-RPC 2.0, and routes responses back to per-call
// callbacks. Per the protocol, one process per session: launch lazily on
// first call(), keep alive until shutdown().
class ConnectorProcess : public QObject {
    Q_OBJECT
public:
    using ResultHandler = std::function<void(const QJsonValue& result)>;
    using ErrorHandler  = std::function<void(int code, const QString& message)>;

    explicit ConnectorProcess(ConnectorManifest manifest, QObject* parent = nullptr);
    ~ConnectorProcess() override;

    const ConnectorManifest& manifest() const { return manifest_; }
    bool isRunning() const;
    QString lastError() const { return last_error_; }

    // Lazy-launches the underlying process. Returns false on launch failure;
    // the user-facing reason is in lastError().
    bool ensureStarted();

    // Async JSON-RPC 2.0 call. Exactly one of on_result / on_error fires
    // exactly once, on the same thread (queued). Launch failure synthesizes
    // an immediate on_error via singleShot so callers see consistent
    // async ordering.
    void call(const QString& method,
              const QJsonValue& params,
              ResultHandler on_result,
              ErrorHandler on_error);

    // Closes stdin and waits a few seconds for clean exit; SIGKILLs on
    // timeout. Any in-flight calls fail via on_error. Safe to call when
    // not running.
    void shutdown();

signals:
    // Process exited unexpectedly (not via shutdown()). In-flight calls have
    // already been failed via on_error before this fires.
    void crashed(const QString& message);

private:
    void onReadyReadStdout();
    void onProcessFinished(int exit_code, QProcess::ExitStatus status);
    void dispatchLine(const QByteArray& line);
    void failPendingAndClear(int code, const QString& message);

    ConnectorManifest manifest_;
    QProcess* process_ = nullptr;
    QByteArray buffer_;
    QString last_error_;
    bool shutting_down_ = false;
    quint64 next_request_id_ = 0;

    struct Pending {
        ResultHandler on_result;
        ErrorHandler on_error;
    };
    QHash<QString, Pending> pending_;
};

} // namespace ifcviewerfull::modules::connectors

#endif
