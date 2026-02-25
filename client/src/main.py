import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont, QIcon
from main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 设置全局字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)
    app.setWindowIcon(QIcon('../logo.png'))
    # 创建主窗口
    window = MainWindow()
    window.setWindowIcon(QIcon('../logo.png'))
    window.show()

    sys.exit(app.exec())