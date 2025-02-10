import sys
from PyQt5.QtWidgets import QApplication
from ui import MainWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style as base
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
