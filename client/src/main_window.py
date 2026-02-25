import sys
import math
from datetime import datetime
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QFrame, QLabel, QPushButton, QScrollArea, QStackedWidget,
                               QGraphicsDropShadowEffect, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, QTimer, QPoint, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QColor, QLinearGradient, QPen, QPainterPath, QFont, QIcon

from src.engine_widget import EngineVisualizationWidget
import pyqtgraph as pg


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 窗口设置
        self.setWindowTitle("航空发动机寿命预测系统")
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)

        # 颜色配置（延续登录界面风格）
        self.colors = {
            'bg_dark': QColor(10, 15, 30),
            'bg_light': QColor(20, 30, 60),
            'primary': QColor(0, 191, 255),
            'secondary': QColor(0, 255, 255),
            'accent': QColor(100, 149, 237),
            'success': QColor(0, 255, 100),
            'warning': QColor(255, 165, 0),
            'danger': QColor(255, 77, 79),
            'text_main': QColor(255, 255, 255),
            'text_sub': QColor(150, 160, 180),
        }

        # 初始化 UI
        self.init_ui()

        # 启动动画
        self.start_animations()

    def init_ui(self):
        """初始化界面"""
        # 中央 widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("background-color: #0A0F1E;")

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. 顶部标题栏
        main_layout.addWidget(self.create_title_bar())

        # 2. 内容区域（侧边栏 + 主内容）
        content_frame = QFrame()
        content_frame.setStyleSheet("background-color: #0A0F1E;")
        content_layout = QHBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # 侧边栏
        content_layout.addWidget(self.create_sidebar(), 0)

        # 主内容
        content_layout.addWidget(self.create_main_content(), 1)

        main_layout.addWidget(content_frame)

        # 3. 底部状态栏
        main_layout.addWidget(self.create_status_bar())

    def create_title_bar(self):
        """创建顶部标题栏"""
        title_bar = QFrame()
        title_bar.setFixedHeight(60)
        title_bar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0A0F1E, stop:0.5 #141E30, stop:1 #0A0F1E);
                border-bottom: 1px solid #00BFFF;
            }
        """)

        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(20, 0, 20, 0)

        # Logo + 标题
        logo_label = QLabel("✈️")
        logo_label.setStyleSheet("font-size: 28px;")
        layout.addWidget(logo_label)

        title_label = QLabel("航空发动机寿命预测系统")
        title_label.setStyleSheet("""
            color: #00BFFF;
            font-size: 20px;
            font-weight: bold;
            letter-spacing: 2px;
            padding-left: 10px;
        """)
        layout.addWidget(title_label)

        layout.addStretch()

        # 用户信息
        user_btn = QPushButton("👤 管理员")
        user_btn.setStyleSheet(self.get_button_style('secondary'))
        layout.addWidget(user_btn)

        # 窗口控制按钮
        min_btn = QPushButton("─")
        min_btn.setFixedSize(40, 30)
        max_btn = QPushButton("□")
        max_btn.setFixedSize(40, 30)
        close_btn = QPushButton("×")
        close_btn.setFixedSize(40, 30)

        for btn in [min_btn, max_btn, close_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    color: #6495ED;
                    border: none;
                    border-radius: 4px;
                    font-size: 18px;
                }
                QPushButton:hover {
                    background-color: #00BFFF;
                    color: #0A0F1E;
                }
            """)
            layout.addWidget(btn)

        close_btn.clicked.connect(self.close)

        return title_bar

    def create_sidebar(self):
        """创建侧边导航栏"""
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #0D1525;
                border-right: 1px solid #1A2F4F;
            }
        """)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(5)

        # 导航菜单
        menu_items = [
            ("📊", "仪表盘", "dashboard"),
            ("📁", "数据管理", "data"),
            ("🔮", "预测分析", "prediction"),
            ("🧠", "模型管理", "model"),
            ("📜", "历史记录", "history"),
            ("⚙️", "系统设置", "settings"),
        ]

        self.nav_buttons = {}
        for icon, text, key in menu_items:
            btn = self.create_nav_button(icon, text)
            btn.clicked.connect(lambda checked, k=key: self.switch_page(k))
            layout.addWidget(btn)
            self.nav_buttons[key] = btn

        # 默认选中第一个
        self.nav_buttons['dashboard'].setChecked(True)

        layout.addStretch()

        # 底部版本信息
        version_label = QLabel("v2.3.1")
        version_label.setStyleSheet("color: #6495ED; font-size: 11px; padding: 10px;")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)

        return sidebar

    def create_nav_button(self, icon, text):
        """创建导航按钮"""
        btn = QPushButton(f"{icon}  {text}")
        btn.setFixedHeight(45)
        btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #96A0B4;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                padding-left: 20px;
                text-align: left;
            }
            QPushButton:hover {
                background: rgba(0, 191, 255, 0.1);
                color: #00BFFF;
            }
            QPushButton:checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 191, 255, 0.2), stop:1 transparent);
                color: #00BFFF;
                border-left: 3px solid #00BFFF;
            }
        """)
        btn.setCheckable(True)
        return btn

    def create_main_content(self):
        """创建主内容区域"""
        content_frame = QFrame()
        content_frame.setStyleSheet("background-color: #0A0F1E;")

        layout = QVBoxLayout(content_frame)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # 1. 关键指标卡片
        layout.addWidget(self.create_metrics_cards())

        # 2. 中间区域（模型可视化 + 参数面板）
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(20)

        # 左侧：发动机模型可视化
        middle_layout.addWidget(self.create_engine_visualization(), 2)

        # 右侧：预测参数
        middle_layout.addWidget(self.create_parameter_panel(), 1)

        layout.addLayout(middle_layout)

        # 3. 底部：趋势图表
        layout.addWidget(self.create_trend_chart())

        return content_frame

    def create_metrics_cards(self):
        """创建关键指标卡片"""
        frame = QFrame()
        frame.setFixedHeight(140)
        frame.setStyleSheet("background: transparent;")

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)

        # 指标卡片数据
        metrics = [
            ("剩余寿命", "15,280", "小时", "⬆️ 2.3%", self.colors['success']),
            ("健康度", "87.5", "%", "⬇️ 1.1%", self.colors['warning']),
            ("置信度", "94.2", "%", "⬆️ 0.5%", self.colors['primary']),
            ("故障概率", "2.8", "%", "⬇️ 0.3%", self.colors['danger']),
        ]

        for title, value, unit, trend, color in metrics:
            card = self.create_metric_card(title, value, unit, trend, color)
            layout.addWidget(card)

        return frame

    def create_metric_card(self, title, value, unit, trend, color):
        """创建单个指标卡片"""
        card = QFrame()
        card.setFixedWidth(280)
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #141E30, stop:1 #0D1525);
                border: 1px solid {color.name()};
                border-radius: 12px;
            }}
        """)

        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(color.red(), color.green(), color.blue(), 80))
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(5)

        # 标题
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {self.colors['text_sub'].name()}; font-size: 13px;")
        layout.addWidget(title_label)

        # 数值
        value_layout = QHBoxLayout()
        value_label = QLabel(f"{value}")
        value_label.setStyleSheet(f"""
            color: {color.name()};
            font-size: 32px;
            font-weight: bold;
        """)
        value_layout.addWidget(value_label)

        if unit:
            unit_label = QLabel(unit)
            unit_label.setStyleSheet(f"color: {color.name()}; font-size: 16px; padding-top: 10px;")
            value_layout.addWidget(unit_label)

        value_layout.addStretch()
        layout.addLayout(value_layout)

        # 趋势
        trend_label = QLabel(trend)
        trend_label.setStyleSheet(f"color: {color.name()}; font-size: 12px;")
        layout.addWidget(trend_label)

        return card

    def create_engine_visualization(self):
        """创建发动机可视化区域"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #141E30, stop:1 #0D1525);
                border: 1px solid #1A2F4F;
                border-radius: 12px;
            }
        """)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 标题
        title = QLabel("🔧 发动机实时状态")
        title.setStyleSheet("color: #00BFFF; font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        # 可视化画布
        self.engine_canvas = EngineVisualizationWidget()
        self.engine_canvas.setStyleSheet("background: transparent;")
        layout.addWidget(self.engine_canvas)

        # 控制按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        predict_btn = QPushButton("🔮 开始预测")
        predict_btn.setFixedSize(140, 45)
        predict_btn.setStyleSheet(self.get_button_style('primary'))
        predict_btn.clicked.connect(self.run_prediction)
        btn_layout.addWidget(predict_btn)

        upload_btn = QPushButton("📁 上传数据")
        upload_btn.setFixedSize(140, 45)
        upload_btn.setStyleSheet(self.get_button_style('secondary'))
        btn_layout.addWidget(upload_btn)

        layout.addLayout(btn_layout)

        return frame

    def create_parameter_panel(self):
        """创建预测参数面板"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #141E30, stop:1 #0D1525);
                border: 1px solid #1A2F4F;
                border-radius: 12px;
            }
        """)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 标题
        title = QLabel("📋 运行参数")
        title.setStyleSheet("color: #00BFFF; font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        # 参数列表
        parameters = [
            ("温度", "850", "°C", "#FF6B6B"),
            ("压力", "3.2", "MPa", "#4ECDC4"),
            ("转速", "12,000", "rpm", "#FFE66D"),
            ("振动", "0.15", "mm/s", "#95E1D3"),
            ("油耗", "2.8", "kg/h", "#F38181"),
        ]

        for name, value, unit, color in parameters:
            param_widget = self.create_parameter_row(name, value, unit, color)
            layout.addWidget(param_widget)

        layout.addStretch()

        # 导出按钮
        export_btn = QPushButton("📊 导出报告")
        export_btn.setFixedHeight(45)
        export_btn.setStyleSheet(self.get_button_style('success'))
        layout.addWidget(export_btn)

        return frame

    def create_parameter_row(self, name, value, unit, color):
        """创建参数行"""
        frame = QFrame()
        frame.setFixedHeight(50)
        frame.setStyleSheet(f"""
            QFrame {{
                background: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                border-left: 3px solid {color};
            }}
        """)

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(15, 0, 15, 0)

        name_label = QLabel(name)
        name_label.setStyleSheet("color: #96A0B4; font-size: 13px;")
        layout.addWidget(name_label)

        layout.addStretch()

        value_label = QLabel(f"{value} {unit}")
        value_label.setStyleSheet(f"color: {color}; font-size: 16px; font-weight: bold;")
        layout.addWidget(value_label)

        return frame

    def create_trend_chart(self):
        """创建趋势图表"""
        frame = QFrame()
        frame.setFixedHeight(250)
        frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #141E30, stop:1 #0D1525);
                border: 1px solid #1A2F4F;
                border-radius: 12px;
            }
        """)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # 标题
        title_layout = QHBoxLayout()
        title = QLabel("📉 寿命衰减趋势")
        title.setStyleSheet("color: #00BFFF; font-size: 16px; font-weight: bold;")
        title_layout.addWidget(title)
        title_layout.addStretch()

        date_label = QLabel("📅 2026-01 ~ 2026-02")
        date_label.setStyleSheet("color: #6495ED; font-size: 12px;")
        title_layout.addWidget(date_label)

        layout.addLayout(title_layout)

        # 图表区域
        self.chart_view = self.create_chart()
        layout.addWidget(self.chart_view)

        return frame

    def create_chart(self):
        """使用 PyQtGraph 创建趋势图表"""
        # 创建图表组件
        graph_widget = pg.PlotWidget()
        graph_widget.setMinimumHeight(180)
        graph_widget.setStyleSheet("background: transparent;")

        # 设置背景透明
        graph_widget.setBackground('transparent')

        # 显示网格
        graph_widget.showGrid(x=True, y=True, alpha=0.3)

        # 禁用鼠标交互
        graph_widget.setMouseEnabled(x=False, y=False)

        # 设置轴标签和颜色
        styles = {'color': '#96A0B4', 'font-size': '12px'}
        graph_widget.setLabel('bottom', '时间（天）', **styles)
        graph_widget.setLabel('left', '健康度', **styles)

        # 设置轴线颜色
        graph_widget.getAxis('bottom').setPen(QColor(30, 50, 80))
        graph_widget.getAxis('left').setPen(QColor(30, 50, 80))

        # 设置范围
        graph_widget.setXRange(0, 100)
        graph_widget.setYRange(0, 100)

        # 绘制数据
        x_data = list(range(0, 101, 10))
        y_data = [100, 95, 92, 88, 85, 82, 78, 75, 72, 68, 65]

        # 创建线条样式
        pen = pg.mkPen(color=(0, 191, 255), width=2)
        graph_widget.plot(x_data, y_data, pen=pen, symbol='o',
                          symbolBrush=(0, 191, 255), symbolSize=6)

        return graph_widget

    def create_status_bar(self):
        """创建底部状态栏"""
        status_bar = QFrame()
        status_bar.setFixedHeight(35)
        status_bar.setStyleSheet("""
            QFrame {
                background-color: #0D1525;
                border-top: 1px solid #1A2F4F;
            }
        """)

        layout = QHBoxLayout(status_bar)
        layout.setContentsMargins(20, 0, 20, 0)

        status_label = QLabel("● 系统就绪")
        status_label.setStyleSheet("color: #00FF00; font-size: 12px;")
        layout.addWidget(status_label)

        layout.addWidget(QLabel("│"))

        model_label = QLabel("模型版本：v2.3.1")
        model_label.setStyleSheet("color: #6495ED; font-size: 12px;")
        layout.addWidget(model_label)

        layout.addWidget(QLabel("│"))

        update_label = QLabel(f"最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        update_label.setStyleSheet("color: #6495ED; font-size: 12px;")
        layout.addWidget(update_label)

        layout.addStretch()

        return status_bar

    def get_button_style(self, type='primary'):
        """获取按钮样式"""
        styles = {
            'primary': """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #00BFFF, stop:1 #00FFFF);
                    color: #0A0F1E;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #00FFFF, stop:1 #6495ED);
                }
            """,
            'secondary': """
                QPushButton {
                    background: transparent;
                    color: #00BFFF;
                    border: 1px solid #00BFFF;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: rgba(0, 191, 255, 0.1);
                }
            """,
            'success': """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #00FF66, stop:1 #00CC52);
                    color: #0A0F1E;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #00CC52, stop:1 #009933);
                }
            """
        }
        return styles.get(type, styles['primary'])

    def switch_page(self, page_key):
        """切换页面"""
        # 更新按钮状态
        for key, btn in self.nav_buttons.items():
            btn.setChecked(key == page_key)

        # 这里可以添加页面切换逻辑
        print(f"切换到页面：{page_key}")

    def run_prediction(self):
        """运行预测"""
        print("开始预测...")
        # 调用深度学习模型进行预测

    def start_animations(self):
        """启动动画"""
        # 可以添加页面加载动画等
        pass

    # === 鼠标拖动支持 ===
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and not self.drag_pos.isNull():
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()