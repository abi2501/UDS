import sys

import qdarktheme
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QApplication
from qt_material import apply_stylesheet

from lib.controller.app_screen import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    # qdarktheme.setup_theme("light")
    # apply_stylesheet(app, theme='dark_teal.xml')
    # app.setPalette(QPalette(QColor("#444444")))
    # main_window.show()
    main_window.setMinimumSize(1000, 700)
    main_window.show()
    # main_window.showNormal()
    # main_window.showMaximized()
    sys.exit(app.exec())