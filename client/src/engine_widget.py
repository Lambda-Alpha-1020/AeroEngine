from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QTimer, QPoint, Qt
from PySide6.QtGui import QPainter, QColor, QPen, QPainterPath, QLinearGradient, QRadialGradient
import math


class EngineVisualizationWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(300)

        # 动画参数
        self.turbine_angle = 0
        self.flow_offset = 0
        self.pulse_phase = 0

        # 定时器
        self.anim_timer = QTimer()
        self.anim_timer.setInterval(30)  # 30 FPS
        self.anim_timer.timeout.connect(self.update_animation)
        self.anim_timer.start()

        # 颜色
        self.colors = {
            'blade': QColor(0, 191, 255),
            'blade_glow': QColor(0, 255, 255),
            'core': QColor(100, 149, 237),
            'flow': QColor(0, 191, 255, 80),
        }

    def update_animation(self):
        self.turbine_angle = (self.turbine_angle + 3) % 360
        self.flow_offset += 2
        self.pulse_phase += 0.05
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制背景
        self.draw_background(painter)

        # 绘制发动机主体
        center = QPoint(self.width() // 2, self.height() // 2)
        self.draw_engine_body(painter, center)

        # 绘制涡轮
        self.draw_turbine(painter, center, 80)

        # 绘制气流
        self.draw_airflow(painter, center)

    def draw_background(self, painter):
        """绘制背景网格"""
        pen = QPen(QColor(30, 50, 80, 100), 1)
        painter.setPen(pen)

        # 网格
        for x in range(0, self.width(), 30):
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), 30):
            painter.drawLine(0, y, self.width(), y)

    def draw_engine_body(self, painter, center):
        """绘制发动机主体轮廓"""
        # 外环
        pen = QPen(self.colors['core'], 2)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(center, 120, 120)

        # 内环
        pen = QPen(self.colors['blade'], 1)
        painter.setPen(pen)
        painter.drawEllipse(center, 90, 90)

        # 中心
        gradient = QRadialGradient(center, 40)
        gradient.setColorAt(0, self.colors['blade_glow'])
        gradient.setColorAt(1, self.colors['core'])
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, 40, 40)

    def draw_turbine(self, painter, center, radius):
        """绘制旋转涡轮"""
        painter.save()
        painter.translate(center)
        painter.rotate(self.turbine_angle)

        # 绘制叶片（12 片）
        for i in range(12):
            painter.rotate(30)

            path = QPainterPath()
            path.moveTo(0, -radius * 0.1)
            path.lineTo(radius * 0.8, -radius * 0.05)
            path.lineTo(radius * 0.8, radius * 0.05)
            path.lineTo(0, radius * 0.1)
            path.closeSubpath()

            gradient = QLinearGradient(0, -radius * 0.1, radius * 0.8, radius * 0.1)
            gradient.setColorAt(0, QColor(0, 191, 255, 150))
            gradient.setColorAt(1, QColor(0, 255, 255, 200))
            painter.setBrush(gradient)
            painter.setPen(Qt.NoPen)
            painter.drawPath(path)

        painter.restore()

    def draw_airflow(self, painter, center):
        """绘制气流效果"""
        pen = QPen(self.colors['flow'], 1)
        painter.setPen(pen)

        # 绘制波浪线
        for i in range(5):
            y_offset = i * 40 - 80
            points = []
            for x in range(0, self.width(), 10):
                y = center.y() + y_offset + math.sin((x + self.flow_offset + i * 30) * 0.03) * 15
                points.append(QPoint(x, int(y)))

            painter.drawPolyline(points)