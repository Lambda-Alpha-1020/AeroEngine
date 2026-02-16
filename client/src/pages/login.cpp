#include "login.h"
#include "ui_login.h"
#include "libs/libcurl/include/curl/curl.h"
#include <QLabel>
#include <QPushButton>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QPainter>
#include <QPixmap>
#include <QPainterPath>
#include <QFont>
#include <QStyleOption>
#include <QApplication>
#include <QMouseEvent>
#include <QResizeEvent>
#include <QLineEdit>
#include <QRandomGenerator>
#include <QMessageBox>
#include <QTimer>

login::login(QWidget *parent)
    : QWidget(parent), ui(new Ui::login)
{
    ui->setupUi(this);

    setWindowFlags(Qt::Window | Qt::FramelessWindowHint);
    setAttribute(Qt::WA_TranslucentBackground);

    // 创建一次性定时器（不用立即启动）
    countdownTimer = new QTimer();
    countdownTimer->setInterval(1000);
    connect(countdownTimer, &QTimer::timeout, this, &login::onCountdownTimeout);

    connectFunctions();
}

login::~login()
{
    delete ui;
}

void login::paintEvent(QPaintEvent *event)
{
    Q_UNUSED(event);
    QStyleOption opt;
    opt.initFrom(this);
    QPainter p(this);
    QLinearGradient g(rect().topLeft(), rect().bottomRight());
    g.setColorAt(0.0, QColor::fromRgb(244, 248, 255));
    g.setColorAt(0.5, QColor::fromRgb(250, 241, 252));
    g.setColorAt(1.0, QColor::fromRgb(240, 249, 255));
    p.fillRect(rect(), g);
    style()->drawPrimitive(QStyle::PE_Widget, &opt, &p, this);
}

void login::connectFunctions()
{
    connect(ui->closeBtn, &QPushButton::clicked, this, &QWidget::close);
    connect(ui->emailEdit, &QLineEdit::textChanged, this, &login::onEmailChanged);
    connect(ui->verifyCodeEdit, &QLineEdit::textChanged, this, &login::onVerifyCodeChanged);
    connect(ui->sendVerifyBtn, &QPushButton::clicked, this, &login::sendVerifyCode);
    connect(ui->loginBtn, &QPushButton::clicked, this, &login::isLogin);
}

// ======拖动窗口======
void login::mousePressEvent(QMouseEvent *event)
{
    if (event->button() == Qt::LeftButton)
    {
        dragPosition = event->globalPosition().toPoint() - frameGeometry().topLeft();
        grabMouse();
        event->accept();
    }
}
void login::mouseMoveEvent(QMouseEvent *event)
{
    if (underMouse())
    {
        if (!dragPosition.isNull())
        {
            move(event->globalPosition().toPoint() - dragPosition);
            event->accept();
        }
    }
}
void login::mouseReleaseEvent(QMouseEvent *event)
{
    if (event->button() == Qt::LeftButton)
    {
        dragPosition = QPoint();
        releaseMouse();
        event->accept();
    }
}

void login::onCountdownTimeout()
{
    remainingSeconds--;
    if (remainingSeconds > 0)
    {
        ui->sendVerifyBtn->setText(QString("%1s 后重发").arg(remainingSeconds));
    }
    else
    {
        countdownTimer->stop();
        ui->sendVerifyBtn->setText("发送验证码");
        ui->sendVerifyBtn->setEnabled(true);
    }
}
struct UploadStatus
{
    std::size_t bytes_read;
    std::string payload;
};
std::size_t payload_source(char *ptr, std::size_t size, std::size_t nmemb, void *userp)
{
    UploadStatus *upload_ctx = reinterpret_cast<UploadStatus *>(userp);
    const std::size_t buffer_size = size * nmemb;
    if (upload_ctx->bytes_read >= upload_ctx->payload.size())
        return 0;
    std::size_t copy_size = upload_ctx->payload.size() - upload_ctx->bytes_read;
    if (copy_size > buffer_size)
        copy_size = buffer_size;
    memcpy(ptr, upload_ctx->payload.c_str() + upload_ctx->bytes_read, copy_size);
    upload_ctx->bytes_read += copy_size;
    return copy_size;
}
void login::sendVerifyCode()
{
    if (ui->emailEdit->text() == "")
    {
        return;
    }
    // 生成验证码
    int code = QRandomGenerator::global()->bounded(100000, 1000000);
    verifyCode = QString::number(code).toUtf8().toStdString();

    // 构造邮件
    const char *smtp_url = "smtps://smtp.163.com:465";
    const char *username = "lambdaalpha@163.com";
    const char *password = "AWTeUEYjnypjM4Za";
    const char *from = "lambdaalpha@163.com";
    QByteArray toBytes = ui->emailEdit->text().toUtf8();
    const char *to = toBytes.constData();

    std::string payload =
        "To: " + toBytes.toStdString() + "\r\n"
                                         "From: lambdaalpha@163.com\r\n"
                                         "Subject: Verify Code\r\n"
                                         "\r\n"
                                         "Welcome to Residual Life Prediction of Aero Engines. \r\n"
                                         "This is your verify code: " +
        verifyCode;

    CURL *curl = curl_easy_init();
    CURLcode res = CURLE_OK;

    if (curl)
    {
        curl_easy_setopt(curl, CURLOPT_URL, smtp_url);      // 设置SMTP服务器地址
        curl_easy_setopt(curl, CURLOPT_USERNAME, username); // 设置SMTP用户名
        curl_easy_setopt(curl, CURLOPT_PASSWORD, password); // 设置SMTP密码（授权码）
        curl_easy_setopt(curl, CURLOPT_MAIL_FROM, from);    // 设置发件人邮箱
        struct curl_slist *recipients = nullptr;
        recipients = curl_slist_append(recipients, to);
        curl_easy_setopt(curl, CURLOPT_MAIL_RCPT, recipients); // 设置收件人邮箱
        curl_easy_setopt(curl, CURLOPT_SSL_VERIFYPEER, 0L);
        curl_easy_setopt(curl, CURLOPT_SSL_VERIFYHOST, 0L);
        curl_easy_setopt(curl, CURLOPT_USE_SSL, CURLUSESSL_ALL);     // 使用 SSL/TLS 加密连接
        curl_easy_setopt(curl, CURLOPT_VERBOSE, 1L);                 // 开启调试信息输出
        curl_easy_setopt(curl, CURLOPT_LOGIN_OPTIONS, "AUTH=login"); // 指定 login 认证方式

        UploadStatus upload_ctx = {0, payload};
        curl_easy_setopt(curl, CURLOPT_READFUNCTION, payload_source); // 设置回调函数，用于提供邮件内容
        curl_easy_setopt(curl, CURLOPT_READDATA, &upload_ctx);        // 设置回调函数的上下文数据，传递upload_ctx
        curl_easy_setopt(curl, CURLOPT_UPLOAD, 1L);                   // 设置为上传模式（即发邮件）
        res = curl_easy_perform(curl);                                // 正式执行SMTP流程（连接、认证、发信）。libcurl会自动完成所有SMTP细节

        if (res != CURLE_OK)
            qDebug() << "curl_easy_perform() failed : " << curl_easy_strerror(res);
        else
            qDebug() << "Email sent successfully! ";
        curl_slist_free_all(recipients);
        curl_easy_cleanup(curl);
    }
    // 1. 禁用按钮
    ui->sendVerifyBtn->setEnabled(false);
    // 2. 重置倒计时
    remainingSeconds = 60;
    // 3. 立即显示初始倒计时
    ui->sendVerifyBtn->setText(QString("%1s 后重发").arg(remainingSeconds));
    // 4. 启动定时器
    countdownTimer->start();
}

void login::isLogin()
{
    if (ui->emailEdit->text().isEmpty())
    {
        ui->emailErrorLabel->setVisible(true);
        ui->emailErrorLabel->setText("<span style='color:#f44336; font-size:12px;'>❗ 邮箱不可以为空</span>");
        ui->emailEdit->setStyleSheet("border: 1px solid #f44336; border-radius: 8px; padding: 8px;");
    }
    if (ui->verifyCodeEdit->text().isEmpty())
    {
        ui->verifyCodeErrorLabel->setVisible(true);
        ui->verifyCodeErrorLabel->setText("<span style='color:#f44336; font-size:12px;'>❗ 验证码不可以为空</span>");
        ui->verifyCodeEdit->setStyleSheet("border: 1px solid #f44336; border-radius: 8px; padding: 8px;");
    }
    if (!ui->emailEdit->text().isEmpty() || !ui->verifyCodeEdit->text().isEmpty() || ui->verifyCodeEdit->text().toUtf8().toStdString() != verifyCode)
    {
        QMessageBox::warning(this, "提示", "验证码或邮箱错误！");
    }
    else
    {
        return;
    }
}
bool isValidEmail(const QString &email)
{
    static const QRegularExpression emailRegex(R"(^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$)");
    return emailRegex.match(email).hasMatch();
}
void login::onEmailChanged()
{
    if (ui->emailEdit->text().isEmpty())
    {
        ui->emailErrorLabel->setVisible(true);
        ui->emailErrorLabel->setText("<span style='color:#f44336; font-size:12px;'>❗ 邮箱不可以为空</span>");
        ui->emailEdit->setStyleSheet("border: 1px solid #f44336; border-radius: 8px; padding: 8px;");
    }
    else if (!isValidEmail(ui->emailEdit->text()))
    {
        ui->emailErrorLabel->setVisible(true);
        ui->emailErrorLabel->setText("<span style='color:#f44336; font-size:12px;'>❗ 请输入有效的邮箱地址</span>");
        ui->emailEdit->setStyleSheet("border: 1px solid #f44336; border-radius: 8px; padding: 8px;");
    }
    else
    {
        ui->emailErrorLabel->setVisible(false);
        ui->emailEdit->setStyleSheet("");
    }
}

void login::onVerifyCodeChanged()
{
    if (ui->verifyCodeEdit->text().isEmpty())
    {
        ui->verifyCodeErrorLabel->setVisible(true);
        ui->verifyCodeErrorLabel->setText("<span style='color:#f44336; font-size:12px;'>❗ 验证码不可以为空</span>");
        ui->verifyCodeEdit->setStyleSheet("border: 1px solid #f44336; border-radius: 8px; padding: 8px;");
    }
    else
    {
        ui->verifyCodeErrorLabel->setVisible(false);
        ui->verifyCodeEdit->setStyleSheet("");
    }
}