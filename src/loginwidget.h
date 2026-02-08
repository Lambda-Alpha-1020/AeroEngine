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

private:
    QLabel *m_logo;
    QLabel *m_avatar;
    QLabel *m_name;
    QPushButton *m_loginBtn;
    QPixmap createAvatar(int size);
    QPoint m_dragPosition;
};

#endif
