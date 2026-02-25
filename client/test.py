# main_window.py
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import sys


class ArknightsStyleWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("明日方舟风格界面")
        self.setFixedSize(1280, 720)
        self.setup_ui()
        self.apply_stylesheet()

    def setup_ui(self):
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 顶部栏
        self.top_bar = self.create_top_bar()
        main_layout.addWidget(self.top_bar)

        # 内容区域
        self.content_area = self.create_content_area()
        main_layout.addWidget(self.content_area, 1)

        # 底部栏
        self.bottom_bar = self.create_bottom_bar()
        main_layout.addWidget(self.bottom_bar)

    def create_top_bar(self):
        """创建顶部状态栏"""
        top_bar = QFrame()
        top_bar.setObjectName("TopBar")
        top_bar.setFixedHeight(60)

        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(20, 10, 20, 10)

        # 等级显示
        self.level_label = QLabel("LV.120")
        self.level_label.setObjectName("LevelLabel")

        # 资源显示
        self.resource_label = QLabel("💎 12800  📦 256")
        self.resource_label.setObjectName("ResourceLabel")

        layout.addWidget(self.level_label)
        layout.addStretch()
        layout.addWidget(self.resource_label)

        return top_bar

    def create_content_area(self):
        """创建主内容区域"""
        content = QFrame()
        content.setObjectName("ContentArea")
        layout = QHBoxLayout(content)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # 左侧菜单
        self.left_menu = self.create_left_menu()
        layout.addWidget(self.left_menu, 0)

        # 主内容
        self.main_content = self.create_main_content()
        layout.addWidget(self.main_content, 1)

        return content

    def create_left_menu(self):
        """创建左侧导航菜单"""
        menu = QFrame()
        menu.setObjectName("LeftMenu")
        menu.setFixedWidth(200)
        layout = QVBoxLayout(menu)
        layout.setSpacing(10)

        menu_items = ["作战", "干员", "基建", "采购", "活动"]
        for item in menu_items:
            btn = QPushButton(item)
            btn.setObjectName("MenuButton")
            btn.setFixedHeight(50)
            btn.setCursor(Qt.PointingHandCursor)
            layout.addWidget(btn)

        layout.addStretch()
        return menu

    def create_main_content(self):
        """创建主内容区域"""
        content = QFrame()
        content.setObjectName("MainContent")
        layout = QVBoxLayout(content)

        # 标题
        title = QLabel("作战选择")
        title.setObjectName("ContentTitle")
        layout.addWidget(title)

        # 关卡列表
        self.stage_list = self.create_stage_list()
        layout.addWidget(self.stage_list)

        return content

    def create_stage_list(self):
        """创建关卡列表"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("StageScroll")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(15)

        stages = [
            ("1-1", "主题曲 第一章", "0/18"),
            ("1-2", "主题曲 第一章", "0/18"),
            ("1-3", "主题曲 第一章", "0/18"),
            ("1-4", "主题曲 第一章", "0/18"),
            ("1-5", "主题曲 第一章", "0/18"),
        ]

        for stage_id, stage_name, progress in stages:
            card = self.create_stage_card(stage_id, stage_name, progress)
            layout.addWidget(card)

        layout.addStretch()
        scroll.setWidget(container)
        return scroll

    def create_stage_card(self, stage_id, stage_name, progress):
        """创建关卡卡片"""
        card = QFrame()
        card.setObjectName("StageCard")
        card.setFixedHeight(80)
        card.setCursor(Qt.PointingHandCursor)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)

        # 关卡编号
        id_label = QLabel(stage_id)
        id_label.setObjectName("StageId")

        # 关卡信息
        info_layout = QVBoxLayout()
        name_label = QLabel(stage_name)
        name_label.setObjectName("StageName")
        prog_label = QLabel(progress)
        prog_label.setObjectName("StageProgress")
        info_layout.addWidget(name_label)
        info_layout.addWidget(prog_label)

        # 开始按钮
        start_btn = QPushButton("开始行动")
        start_btn.setObjectName("StartButton")
        start_btn.setFixedWidth(120)

        layout.addWidget(id_label)
        layout.addLayout(info_layout, 1)
        layout.addWidget(start_btn)

        return card

    def create_bottom_bar(self):
        """创建底部栏"""
        bottom_bar = QFrame()
        bottom_bar.setObjectName("BottomBar")
        bottom_bar.setFixedHeight(50)

        layout = QHBoxLayout(bottom_bar)
        layout.setContentsMargins(20, 5, 20, 5)

        friend_btn = QPushButton("好友")
        friend_btn.setObjectName("BottomButton")

        mail_btn = QPushButton("邮件")
        mail_btn.setObjectName("BottomButton")

        layout.addWidget(friend_btn)
        layout.addStretch()
        layout.addWidget(mail_btn)

        return bottom_bar

    def apply_stylesheet(self):
        """应用明日方舟风格样式表"""
        self.setStyleSheet("""
            /* 全局样式 */
            QMainWindow {
                background-color: #1a1a1a;
            }

            QWidget {
                font-family: "Microsoft YaHei", "思源黑体", sans-serif;
                color: #ffffff;
            }

            /* 顶部栏 */
            #TopBar {
                background-color: #2d2d2d;
                border-bottom: 2px solid #c9a959;
            }

            #LevelLabel {
                font-size: 18px;
                font-weight: bold;
                color: #c9a959;
                padding: 5px 15px;
                background-color: #1a1a1a;
                border-radius: 3px;
            }

            #ResourceLabel {
                font-size: 16px;
                color: #ffffff;
                padding: 5px 15px;
            }

            /* 内容区域 */
            #ContentArea {
                background-color: #1a1a1a;
            }

            #LeftMenu {
                background-color: #252525;
                border-right: 1px solid #3d3d3d;
                border-radius: 5px;
            }

            #MenuButton {
                background-color: transparent;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                font-size: 16px;
                color: #ffffff;
                padding: 10px;
            }

            #MenuButton:hover {
                background-color: #c9a959;
                color: #1a1a1a;
                border-color: #c9a959;
            }

            #MenuButton:pressed {
                background-color: #a88845;
            }

            /* 主内容 */
            #MainContent {
                background-color: #252525;
                border-radius: 5px;
                padding: 20px;
            }

            #ContentTitle {
                font-size: 24px;
                font-weight: bold;
                color: #c9a959;
                padding-bottom: 20px;
            }

            /* 滚动区域 */
            #StageScroll {
                background-color: transparent;
                border: none;
            }

            #StageScroll QScrollBar:vertical {
                background-color: #1a1a1a;
                width: 8px;
                border-radius: 4px;
            }

            #StageScroll QScrollBar::handle:vertical {
                background-color: #3d3d3d;
                border-radius: 4px;
                min-height: 30px;
            }

            #StageScroll QScrollBar::handle:vertical:hover {
                background-color: #c9a959;
            }

            /* 关卡卡片 */
            #StageCard {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
            }

            #StageCard:hover {
                border-color: #c9a959;
                background-color: #353535;
            }

            #StageId {
                font-size: 32px;
                font-weight: bold;
                color: #c9a959;
                min-width: 80px;
            }

            #StageName {
                font-size: 16px;
                color: #ffffff;
            }

            #StageProgress {
                font-size: 12px;
                color: #888888;
            }

            #StartButton {
                background-color: #c9a959;
                color: #1a1a1a;
                border: none;
                border-radius: 3px;
                font-size: 14px;
                font-weight: bold;
            }

            #StartButton:hover {
                background-color: #d4b56a;
            }

            #StartButton:pressed {
                background-color: #a88845;
            }

            /* 底部栏 */
            #BottomBar {
                background-color: #2d2d2d;
                border-top: 1px solid #3d3d3d;
            }

            #BottomButton {
                background-color: transparent;
                border: 1px solid #3d3d3d;
                border-radius: 3px;
                color: #ffffff;
                padding: 5px 20px;
            }

            #BottomButton:hover {
                border-color: #c9a959;
                color: #c9a959;
            }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 设置应用程序风格
    app.setStyle("Fusion")

    window = ArknightsStyleWindow()
    window.show()

    sys.exit(app.exec())