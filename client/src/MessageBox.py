from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QWidget, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QFont, QIcon, QPainterPath, QPen
import math

class MessageBox(QDialog):
    def __init__(self, parent=None, title="提示", message="", msg_type="info"):
        super().__init__(parent)

        self.msg_type = msg_type  # 'info', 'warning', 'error', 'success'

        # === 窗口设置 ===
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(213, 160)  # 固定大小

        # === 布局 ===
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 内容容器 (用于绘制背景)
        self.content_widget = QWidget()
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)

        # 消息内容
        self.msg_label = QLabel(message)
        self.msg_label.setWordWrap(True)
        self.msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.msg_label.setStyleSheet("color: #FFFFFF; font-size: 14px; padding: 10px;")
        content_layout.addWidget(self.msg_label)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.ok_btn = QPushButton("确定")
        self.ok_btn.setFixedSize(80, 35)
        self.ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ok_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00BFFF, stop:1 #00FFFF);
                color: #0A0F1E;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00FFFF, stop:1 #6495ED);
            }
            QPushButton:pressed {
                background: #008B8B;
            }
        """)
        self.ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addStretch()
        content_layout.addLayout(btn_layout)

        layout.addWidget(self.content_widget)

        # === 动画 (淡入效果) ===
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.fade_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_anim.setDuration(300)
        self.fade_anim.setStartValue(0)
        self.fade_anim.setEndValue(1)
        self.fade_anim.setEasingCurve(QEasingCurve.InOutQuad)

        # === 状态配置 ===
        self.config_style()
        # 启动动画
        self.fade_anim.start()
        # 拖动变量
        self.drag_pos = QPoint()

    def config_style(self):
        """根据类型配置颜色和图标"""
        colors = {
            'info': '#00BFFF',  # 蓝
            'warning': '#FFA500',  # 橙
            'error': '#FF4D4F',  # 红
            'success': '#00FF00'  # 绿
        }
        icons = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'error': '❌',
            'success': '✅'
        }

        color = colors.get(self.msg_type, '#00BFFF')
        icon = icons.get(self.msg_type, 'ℹ️')

        # 在消息前加图标
        self.msg_label.setText(f"{icon}  {self.msg_label.text()}")

        # 存储颜色供 paintEvent 使用
        self.theme_color = QColor(color)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 1. 绘制圆角矩形背景 (半透明深蓝)
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 15, 15)
        painter.setClipPath(path)

        # 背景渐变
        bg_gradient = QLinearGradient(0, 0, 0, self.height())
        bg_gradient.setColorAt(0, QColor(10, 20, 40, 240))
        bg_gradient.setColorAt(1, QColor(5, 10, 20, 240))
        painter.fillRect(self.rect(), bg_gradient)

        # 2. 绘制发光边框
        border_pen = QPen(self.theme_color, 2)
        painter.setPen(border_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 14, 14)

    # === 鼠标拖动支持 ===
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and not self.drag_pos.isNull():
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()