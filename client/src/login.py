import math
import sys
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtGui import QPainter, QLinearGradient, QColor, QPaintEvent, QMouseEvent, QPen, QPainterPath, \
    QRadialGradient, QIcon
import random
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
import MessageBox

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # ===== 动画配置 =====
        self.animation_timer = QTimer()
        self.animation_timer.setInterval(16)  # 60 FPS
        self.animation_timer.timeout.connect(self.update_animation)

        # 动画状态
        self.turbine_angle = 0  # 涡轮旋转角度
        self.pulse_phase = 0  # 脉冲相位
        self.particle_offset = 0  # 粒子流动偏移

        # 颜色配置（科技蓝）
        self.colors = {
            'bg_dark': QColor(10, 15, 30),  # 深蓝背景
            'bg_light': QColor(20, 30, 60),  # 浅蓝背景
            'primary': QColor(0, 191, 255),  # 科技蓝
            'secondary': QColor(0, 255, 255),  # 青色
            'accent': QColor(100, 149, 237),  # 矢车菊蓝
            'glow': QColor(0, 191, 255, 100),  # 发光效果
            'warning': QColor(255, 100, 100),  # 警告红
        }

        # 粒子系统
        self.particles = []
        for i in range(50):
            self.particles.append({
                'x': 0,
                'y': 0,
                'speed': 0.5 + i * 0.02,
                'size': 1 + (i % 3),
                'alpha': 50 + (i % 100)
            })

        # 启动动画
        self.animation_timer.start()

        # ===== 窗口设置 =====
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(450, 550)
        self.setup_ui("login.ui")
        self.connect_ui()

        # 初始化定时器
        self.countdown_timer = QTimer()
        self.countdown_timer.setInterval(1000)  # 1秒
        self.countdown_timer.timeout.connect(self.on_countdown_timeout)

        self.drag_position = QPoint()
        self.email = ""
        self.verify_code = ""
        self.remaining_seconds = 60

    def setup_ui(self, ui_file):
        loader = QUiLoader()
        # 加载 UI 文件，self 作为父窗口
        self.ui = loader.load(ui_file, self)

    def update_animation(self):
        """更新动画状态"""
        self.turbine_angle = (self.turbine_angle + 2) % 360  # 涡轮旋转
        self.pulse_phase += 0.05  # 脉冲相位
        self.particle_offset += 1  # 粒子流动
        self.update()

    def draw_turbine(self, painter: QPainter, center: QPoint, radius: float):
        """绘制航空发动机涡轮"""
        painter.save()
        painter.translate(center)
        painter.rotate(self.turbine_angle)

        # 涡轮外环
        pen = QPen(self.colors['primary'], 2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPoint(0, 0), int(radius), int(radius))

        # 涡轮内环
        painter.setPen(QPen(self.colors['secondary'], 1))
        painter.drawEllipse(QPoint(0, 0), int(radius * 0.7), int(radius * 0.7))

        # 涡轮叶片（12 片）
        for i in range(12):
            painter.rotate(30)
            # 叶片
            path = QPainterPath()
            path.moveTo(0, -radius * 0.1)
            path.lineTo(radius * 0.8, -radius * 0.05)
            path.lineTo(radius * 0.8, radius * 0.05)
            path.lineTo(0, radius * 0.1)
            path.closeSubpath()

            # 叶片渐变
            gradient = QLinearGradient(0, -radius * 0.1, radius * 0.8, radius * 0.1)
            gradient.setColorAt(0, QColor(0, 191, 255, 150))
            gradient.setColorAt(1, QColor(0, 255, 255, 200))
            painter.setBrush(gradient)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPath(path)

        # 中心圆
        painter.setBrush(self.colors['primary'])
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPoint(0, 0), int(radius * 0.15), int(radius * 0.15))

        painter.restore()

    def draw_flow_lines(self, painter: QPainter):
        """绘制气流线条"""
        painter.save()

        pen = QPen(self.colors['glow'], 1)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        # 绘制多条流动曲线
        for i in range(8):
            y = 50 + i * 60
            points = []
            for x in range(0, self.width(), 20):
                offset = math.sin((x + self.particle_offset + i * 50) * 0.02) * 10
                points.append(QPoint(x, int(y + offset)))

            painter.drawPolyline(points)

        painter.restore()

    def draw_particles(self, painter: QPainter):
        """绘制粒子效果"""
        painter.save()

        for particle in self.particles:
            # 更新粒子位置
            particle['x'] = (particle['x'] + particle['speed'] * 2) % self.width()
            particle['y'] = (particle['y'] + math.sin(
                self.particle_offset * 0.05 + particle['speed']) * 0.5) % self.height()

            # 绘制粒子
            color = QColor(self.colors['secondary'])
            color.setAlpha(particle['alpha'])
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(
                QPoint(int(particle['x']), int(particle['y'])),
                particle['size'],
                particle['size']
            )

        painter.restore()

    def draw_grid(self, painter: QPainter):
        """绘制科技网格"""
        painter.save()

        pen = QPen(QColor(0, 191, 255, 30), 1)
        painter.setPen(pen)

        # 垂直线
        for x in range(0, self.width(), 40):
            painter.drawLine(x, 0, x, self.height())

        # 水平线
        for y in range(0, self.height(), 40):
            painter.drawLine(0, y, self.width(), y)

        painter.restore()

    def draw_engine_outline(self, painter: QPainter):
        """绘制发动机轮廓装饰"""
        painter.save()

        # 半透明轮廓
        pen = QPen(self.colors['accent'], 1)
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # 绘制装饰性圆环
        center = QPoint(self.width() // 2, 100)
        for i in range(3):
            radius = 60 + i * 20
            alpha = 100 - i * 30
            color = QColor(self.colors['primary'])
            color.setAlpha(alpha)
            painter.setPen(QPen(color, 1))
            painter.drawEllipse(center, radius, radius)

        painter.restore()

    def paintEvent(self, event: QPaintEvent) -> None:
        """绘制动画背景"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # ✅ 1. 创建圆角路径
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 15, 15)  # 15px 圆角
        # ✅ 2. 【关键】设置裁剪区域，只在圆角内绘制
        painter.setClipPath(path)
        # 1. 绘制背景渐变
        bg_gradient = QLinearGradient(0, 0, 0, self.height())
        bg_gradient.setColorAt(0.0, self.colors['bg_dark'])
        bg_gradient.setColorAt(0.5, self.colors['bg_light'])
        bg_gradient.setColorAt(1.0, self.colors['bg_dark'])
        painter.fillRect(self.rect(), bg_gradient)
        # 2. 绘制科技网格
        self.draw_grid(painter)
        # 3. 绘制气流线条
        self.draw_flow_lines(painter)
        # 4. 绘制粒子
        self.draw_particles(painter)
        # 5. 绘制发动机轮廓装饰（顶部）
        self.draw_engine_outline(painter)

        # 6. 绘制涡轮动画（右上角）
        turbine_center = QPoint(self.width() - 80, 80)
        self.draw_turbine(painter, turbine_center, 50)

        # 7. 绘制脉冲光晕
        pulse_alpha = int(50 + 50 * math.sin(self.pulse_phase))
        radial_gradient = QRadialGradient(self.width() // 2, self.height() // 2, 300)
        radial_gradient.setColorAt(0, QColor(0, 191, 255, pulse_alpha))
        radial_gradient.setColorAt(1, QColor(0, 191, 255, 0))
        painter.setBrush(radial_gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())

        # ✅ 6. 恢复裁剪 (可选，如果后面还要画东西)
        painter.setClipping(False)

        # 7. 绘制边框 (在圆角路径上描边)
        border_pen = QPen(self.colors['primary'], 2)
        painter.setPen(border_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

    def connect_ui(self):
        self.ui.closeBtn.clicked.connect(self.close)
        self.ui.sendVerifyBtn.clicked.connect(self.sendVerifyCode)
        self.ui.loginBtn.clicked.connect(self.verifyLogin)

    def showMessage(self, signal):
        messages = {
            0: ("错误", "邮箱错误", "error"),
            1: ("警告", "验证码错误", "warning"),
            2: ("验证失败", "验证码或邮箱错误！", "error"),
            201: ("成功", "登录成功！", "success")
        }

        if signal in messages:
            title, msg, m_type = messages[signal]

            # ✅ 创建并显示自定义对话框
            dialog = MessageBox.MessageBox(self, title=title, message=msg, msg_type=m_type)

            # 居中显示
            screen_geo = self.screen().geometry()
            x = (screen_geo.width() - dialog.width()) // 2
            y = (screen_geo.height() - dialog.height()) // 2
            dialog.move(x, y)

            dialog.exec()  # 模态显示，阻塞直到用户点击确定

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """当鼠标按下时，捕获鼠标的坐标"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.grabMouse()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.underMouse():
            if not self.drag_position.isNull():
                self.move(event.globalPosition().toPoint() - self.drag_position)
                event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = QPoint()
            self.releaseMouse()
            event.accept()

    def is_valid_email(self, email: str) -> bool:
        """验证邮箱格式"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def on_countdown_timeout(self) -> None:
        self.remaining_seconds -= 1
        if self.remaining_seconds > 0:
            self.ui.sendVerifyBtn.setText(f"{self.remaining_seconds}s 后重发")
        else:
            # 倒计时结束
            self.countdown_timer.stop()
            self.ui.sendVerifyBtn.setText("发送验证码")
            self.ui.sendVerifyBtn.setEnabled(True)
            self.verify_code = ""

    def sendVerifyCode(self) -> None:
        """发送验证码"""
        # 1. 验证邮箱
        email = self.ui.emailEdit.text().strip()
        if not self.is_valid_email(email):
            self.showMessage(0)
            return
        else:
            self.email = email
        # 2. 生成验证码（6位数字）
        code = random.randint(100000, 999999)
        self.verify_code = str(code)

        # 3. 构造邮件
        smtp_server = "smtp.163.com"
        smtp_port = 465
        sender = "lambdaalpha@163.com"
        password = "AWTeUEYjnypjM4Za"

        content = f"""
    <html>
    <body>
        <div style="font-family: Arial, sans-serif; padding: 20px;">
            <p>Dear User:</p>
            <p>Welcome to Residual Life Prediction of Aero Engines.</p>
            <div style="background: #fef0f0; border: 1px solid #f44336; 
                padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
                <p style="margin: 0; color: #666;">This is your verify code:</p>
                <p style="margin: 10px 0 0 0; color: #f44336; 
                    font-size: 32px; font-weight: bold; letter-spacing: 5px;">
                    <b>{self.verify_code}</b>
                </p>
                <p style="color: #666;">
                    Valid for 60 seconds.Do not disclose to others.
                </p>
            </div>
            <p style="color: #999; font-size: 12px; margin-top: 30px;">
                —— Sent automatically by the system.
            </p>
        </div>
    </body>
    </html>
    """

        msg = MIMEText(content, 'html', 'utf-8')
        msg['From'] = formataddr(("Aero Engine Prediction", sender))
        msg['To'] = Header(email, 'utf-8')
        msg['Subject'] = Header("Verify Code", 'utf-8')

        # 4. 发送邮件
        try:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
            server.set_debuglevel(1)
            server.login(sender, password)
            server.sendmail(sender, [email], msg.as_string())
        except Exception as e:
            print(f"Email send failed: {e}")
            self.showMessage(0)
            return
        finally:
            # server.quit()
            print("ok")

        # 5. 启动倒计时
        self.ui.sendVerifyBtn.setEnabled(False)
        self.remaining_seconds = 60
        self.ui.sendVerifyBtn.setText(f"{self.remaining_seconds}s 后重发")
        self.countdown_timer.start()

    def verifyLogin(self) -> None:
        # 1. 验证邮箱
        email = self.ui.emailEdit.text().strip()
        if not email:
            self.showMessage(0)
            return
        # 2. 验证验证码
        code_input = self.ui.verifyCodeEdit.text().strip()
        if not code_input:
            self.showMessage(1)
            return

        if code_input != self.verify_code or email != self.email:
            self.showMessage(2)
        else:
            self.showMessage(201)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('../logo.png'))
    window = MainWindow()
    window.setWindowIcon(QIcon('../logo.png'))
    window.show()
    sys.exit(app.exec())
