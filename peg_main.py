import sys
from peg_gui import MainWindow, apply_dark_palette
from PyQt6.QtWidgets import QApplication
import logging


# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(name)s - %(levelname)s: %(message)s',
    handlers=[logging.StreamHandler(stream=sys.stdout)]
)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    apply_dark_palette(app)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
