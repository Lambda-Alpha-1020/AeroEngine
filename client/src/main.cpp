#include "./pages/login.h"
#include <QApplication>
#pragma comment(lib, "user32.lib")

int main(int argc, char *argv[])
{
    qDebug() << " ok ";
    QApplication app(argc, argv);
    login w;
    w.show();
    return app.exec();
}