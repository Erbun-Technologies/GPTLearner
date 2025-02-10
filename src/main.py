import sys
import logging
from PyQt5.QtWidgets import QApplication
from ui import MainWindow

# Configure root logger
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style as base
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
