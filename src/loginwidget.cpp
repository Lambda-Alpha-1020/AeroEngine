#include "loginwidget.h"
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

LoginWidget::LoginWidget(QWidget *parent)
    : QWidget(parent)
{
    // 设置窗口无边框（保留原有标志）
    setWindowFlags(windowFlags() | Qt::FramelessWindowHint);
    // 启用透明背景（让 paintEvent 的绘制生效）
    setAttribute(Qt::WA_TranslucentBackground);

    m_logo = new QLabel("AeroEngine", this);
    QFont logoFont;
    logoFont.setPointSize(40);
    logoFont.setBold(true);
    m_logo->setFont(logoFont);
    m_logo->setAlignment(Qt::AlignCenter);
    m_logo->setFixedHeight(80);
    m_logo->setStyleSheet("color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #7fc8ff, stop:1 #caa6ff); background:transparent;");

    m_avatar = new QLabel(this);
    int av = 120;
    m_avatar->setPixmap(createAvatar(av));
    m_avatar->setFixedSize(av, av);
    m_avatar->setAlignment(Qt::AlignCenter);

    m_name = new QLabel("Lambda-Alpha \u25BE", this); // small down arrow
    QFont nameFont;
    nameFont.setPointSize(14);
    m_name->setFont(nameFont);
    m_name->setAlignment(Qt::AlignCenter);
    m_name->setStyleSheet("color: #222; background: transparent;");

    m_loginBtn = new QPushButton(QString::fromUtf8("登录"), this);
    m_loginBtn->setFixedHeight(48);
    m_loginBtn->setStyleSheet(
        "QPushButton{ background-color: #0a84ff; color: white; border-radius: 8px; font-size:24px; padding:8px 16px; }"
        "QPushButton:pressed{ background-color: #066cd6; }");

    QLabel *bottomLinks = new QLabel(this);
    bottomLinks->setText(QString::fromUtf8("<a href=\"#\">账号登录</a> | <a href=\"#\">注册账号</a>"));
    bottomLinks->setTextFormat(Qt::RichText);
    bottomLinks->setTextInteractionFlags(Qt::TextBrowserInteraction);
    bottomLinks->setOpenExternalLinks(false);
    bottomLinks->setAlignment(Qt::AlignCenter);
    bottomLinks->setStyleSheet("color: #6b6b9a; background:transparent; font-size:24px;");

    QVBoxLayout *v = new QVBoxLayout(this);
    v->setContentsMargins(28, 24, 28, 20);
    v->setSpacing(100);
    v->addWidget(m_logo, 0, Qt::AlignHCenter);
    v->addSpacing(10);
    v->addWidget(m_avatar, 0, Qt::AlignHCenter);
    v->addWidget(m_name);
    v->addSpacing(8);
    v->addWidget(m_loginBtn);
    v->addStretch(1);
    v->addWidget(bottomLinks);
    setLayout(v);
}

void LoginWidget::paintEvent(QPaintEvent *event)
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

QPixmap LoginWidget::createAvatar(int size)
{
    QPixmap pix(size, size);
    pix.fill(Qt::transparent);
    QPainter p(&pix);
    p.setRenderHint(QPainter::Antialiasing, true);

    // outer circle (white)
    QRectF r(0, 0, size, size);
    QPainterPath path;
    path.addEllipse(r);
    p.fillPath(path, QBrush(Qt::white));

    // draw initials
    QFont f;
    f.setBold(true);
    f.setPointSize(size / 4);
    p.setFont(f);
    p.setPen(QColor(60, 60, 60));
    QString initials = "LA";
    QRectF tr = r;
    p.drawText(tr, Qt::AlignCenter, initials);

    // border
    QPen pen(QColor(220, 220, 225));
    pen.setWidth(4);
    p.setPen(pen);
    p.drawEllipse(r.adjusted(2, 2, -2, -2));

    return pix;
}

// 添加以下两个函数以支持点击任意位置拖动窗口
void LoginWidget::mousePressEvent(QMouseEvent *event)
{
    qDebug() << "Mouse pressed at:" << event->position()
             << "isWindow:" << isWindow()
             << "dragPos before:" << m_dragPosition;
    if (event->button() == Qt::LeftButton) {
        m_dragPosition = event->globalPosition().toPoint() - frameGeometry().topLeft();
        qDebug() << "Drag started, offset:" << m_dragPosition;
        grabMouse();
        event->accept();
    }
}

void LoginWidget::mouseMoveEvent(QMouseEvent *event)
{
    if (underMouse()) { // 确保是我们的窗口
        if (!m_dragPosition.isNull()) {
            move(event->globalPosition().toPoint() - m_dragPosition);
            event->accept();
        }
    }
}

void LoginWidget::mouseReleaseEvent(QMouseEvent *event)
{
    if (event->button() == Qt::LeftButton) {
        m_dragPosition = QPoint(); // 清空
        releaseMouse(); // 👈 释放鼠标捕获
        event->accept();
    }
}
