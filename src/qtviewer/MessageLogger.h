#ifndef MESSAGELOGGER_H
#define MESSAGELOGGER_H

#include <QObject>
#include <string>

// SINGLETON
class MessageLogger : public QObject
{
    Q_OBJECT

signals:
    void logMessage(const QString& message);

public:
    static MessageLogger& getInstance()
    {
        static MessageLogger instance;
        return instance;
    }

    // Convenience function to log a message
    static void log(const std::string& message)
    {
        getInstance().emitMessage(message);
    }

private slots:
    void emitMessage(const std::string& message)
    {
        emit logMessage(QString::fromStdString(message));
    }

private:
    MessageLogger() {}
    ~MessageLogger() {}

    // Disable copy constructor for MessageLogger
    MessageLogger(const MessageLogger&) = delete;

    // Disable copy assignment operator for MessageLogger
    MessageLogger& operator=(const MessageLogger&) = delete;
};

#endif // MESSAGELOGGER_H
