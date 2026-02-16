#pragma once
#include "ui_login.h"
#include <QWidget>
#include <QPoint>
#include <QLineEdit>
#include <QPushButton>
#include <QVBoxLayout>
#include <qlabel.h>

class QLabel;
class QPushButton;

namespace Ui { class login; }  // 前向声明
class login : public QWidget
{
    Q_OBJECT

public:
    login(QWidget *parent = nullptr);
    ~login();

protected:
    void paintEvent(QPaintEvent *event) override;
    void connectFunctions();
    void mousePressEvent(QMouseEvent *event) override;
    void mouseMoveEvent(QMouseEvent *event) override;
    void mouseReleaseEvent(QMouseEvent *event);
    void onCountdownTimeout();
    void sendVerifyCode();
    void isLogin();
    void onEmailChanged();
    void onVerifyCodeChanged();

private:
    Ui::login *ui;
    QWidget *loginPage = nullptr;
    QVBoxLayout *loginLayout = nullptr;
    QWidget *titleBar = nullptr;
    QPushButton *closeBtn = nullptr;
    QLabel *title = nullptr;
    QPushButton *loginBtn = nullptr;
    QPushButton *sendVerifyBtn = nullptr;
    QLineEdit *emailEdit = nullptr;
    QLabel *emailErrorLabel = nullptr;
    QLineEdit *verifyCodeEdit = nullptr;
    QLabel *verifyCodeErrorLabel = nullptr;
    std::string verifyCode = "";
    QPoint dragPosition;
    QHBoxLayout *codeLayout = nullptr;
    QTimer *countdownTimer;
    int remainingSeconds = 60;
};
