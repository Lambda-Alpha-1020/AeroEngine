// 使用 Qt 实现的跨平台 GUI 示例（带中文注释）
#include <QApplication>
#include <QFontDatabase>
#include "loginwidget.h"
#include <QScreen>
#include <QRect>

static void setChineseFriendlyFont(QApplication &app)
{
    // Try a list of common CJK fonts and pick the first available
    const QStringList candidates = {
        "Noto Sans CJK SC",
        "Noto Sans SC",
        "WenQuanYi Micro Hei",
        "WenQuanYi Zen Hei",
        "Source Han Sans SC",
        "Microsoft YaHei",
        "SimHei",
        "Arial Unicode MS"};

    QFontDatabase db;
    for (const QString &fam : candidates)
    {
        if (db.families().contains(fam))
        {
            QFont f(fam);
            app.setFont(f);
            return;
        }
    }
    // no preferred font found — leave system default
}

int main(int argc, char *argv[])
{

    QApplication app(argc, argv);

    setChineseFriendlyFont(app);

    QFont font;
    font.setPointSize(40);

    LoginWidget w;
    // 获取主屏幕
    QScreen *screen = QGuiApplication::primaryScreen();
    w.setWindowTitle(QString::fromUtf8("AeroEngine - 登录"));
    if (!screen)
    {
        // 安全兜底
        w.resize(420, 620);
    }
    else
    {
        QRect screenGeometry = screen->geometry(); // 获取完整屏幕区域
        int width = screenGeometry.width() * 0.175;   // 屏幕宽度的 40%
        int height = screenGeometry.height() * 0.45; // 屏幕高度的 60%
        w.resize(width, height);
        w.move(screenGeometry.center() - QPoint(w.width()/2, w.height()/2)); // 自动居中
    }
    w.show();
    return app.exec();
}
