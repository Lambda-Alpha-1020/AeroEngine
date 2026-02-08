#ifndef LOGINWIDGET_H
#define LOGINWIDGET_H

#include <QWidget>
#include <QPoint>

class QLabel;
class QPushButton;

class LoginWidget : public QWidget
{
    Q_OBJECT
public:
    explicit LoginWidget(QWidget *parent = nullptr);

protected:
    void paintEvent(QPaintEvent *event) override;
    void mousePressEvent(QMouseEvent *event) override;
    void mouseMoveEvent(QMouseEvent *event) override;
    void mouseReleaseEvent(QMouseEvent *event);
    void resizeEvent(QResizeEvent *event);

private:
    QWidget *titleBar = nullptr;
    QPushButton *closeBtn = nullptr;
    QLabel *m_logo = nullptr;
    QLabel *m_avatar = nullptr;
    QLabel *m_name = nullptr;
    QPushButton *m_loginBtn = nullptr;
    QPixmap createAvatar(int size);
    QPoint m_dragPosition;
};

#endif
