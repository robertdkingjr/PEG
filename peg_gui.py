import logging
from PyQt6.QtWidgets import (
    QGraphicsView, QMainWindow, QPushButton, QVBoxLayout,
    QWidget, QCheckBox, QComboBox
)
from PyQt6.QtGui import QIcon, QPixmap
from peg_board import GameBoard
import peg_pieces
from PyQt6.QtGui import QPalette, QColor


# Define all colors as hex strings
COLOR_BG = "#2b2b2b"  # Main background
COLOR_TEXT = "#f0f0f0"  # General text (soft white)
# COLOR_TEXT = "#404040"
COLOR_BASE = "#1e1e1e"  # Base input background
# COLOR_BUTTON_BG = "#1e1e1e"  # Button background
COLOR_BUTTON_BG = COLOR_BG
# COLOR_BUTTON_TEXT = "#000000"  # Black
COLOR_BUTTON_TEXT = COLOR_TEXT
COLOR_TOOLTIP_BG = "#f0f0f0"
COLOR_TOOLTIP_TEXT = "#2b2b2b"
COLOR_BRIGHT_TEXT = "#ff0000"  # Error text
COLOR_HIGHLIGHT = "#2a82da"  # Selection/active
COLOR_HIGHLIGHT_TEXT = "#000000"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.setWindowTitle("PEG Simulator")
        self.resize(1000, 800)

        self.view = QGraphicsView()
        self.board = GameBoard()
        self.view.setScene(self.board)

        btn_p = QPushButton("P - Play")
        btn_p.clicked.connect(self.board.play_phase)

        btn_e = QPushButton("E - Eat")
        btn_e.clicked.connect(self.board.eat_phase)

        btn_g = QPushButton("G - Grow")
        btn_g.clicked.connect(self.board.grow_phase)

        self.hex_orientation_toggle = QCheckBox("Pointy-Topped Hexes")
        self.hex_orientation_toggle.setChecked(True)
        self.hex_orientation_toggle.stateChanged.connect(self.toggle_orientation)

        self.sandbox_toggle = QCheckBox("Sandbox Mode")
        self.sandbox_toggle.stateChanged.connect(self.toggle_sandbox)

        self.color_dropdown = self.get_color_dropdown()
        self.color_dropdown.currentTextChanged.connect(self.set_board_paint_color)
        self.set_board_paint_color()

        self.add_peg_button = QPushButton("Add Peg")
        self.add_peg_button.clicked.connect(self.board.add_random_peg)

        self.add_rain_die_button = QPushButton("Add Rain Die")
        self.add_rain_die_button.clicked.connect(self.board.add_rain_die)

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addWidget(btn_p)
        layout.addWidget(btn_e)
        layout.addWidget(btn_g)
        layout.addWidget(self.hex_orientation_toggle)
        layout.addWidget(self.sandbox_toggle)
        layout.addWidget(self.color_dropdown)
        layout.addWidget(self.add_peg_button)
        layout.addWidget(self.add_rain_die_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def get_color_dropdown(self):
        """
        Creates a QComboBox with color swatches.

        Returns:
            QComboBox: The dropdown widget.
        """

        combo = QComboBox()
        for color in peg_pieces.HEX_COLORS:
            pixmap = QPixmap(20, 20)
            pixmap.fill(QColor(color))
            icon = QIcon(pixmap)
            combo.addItem(icon, str(color).upper())

        return combo

    def set_board_paint_color(self):
        self.board.paint_color = self.color_dropdown.currentText()

    def toggle_orientation(self):
        self.board.pointy_top = self.hex_orientation_toggle.isChecked()
        self.board.draw_board()

    def toggle_sandbox(self):
        self.board.sandbox_mode = self.sandbox_toggle.isChecked()
        print(f"Sandbox Mode: {self.board.sandbox_mode}")


def apply_dark_palette(app):

    dark_palette = QPalette()

    # Use QColor from hex string
    dark_palette.setColor(QPalette.ColorRole.Window,           QColor(COLOR_BG))
    dark_palette.setColor(QPalette.ColorRole.WindowText,       QColor(COLOR_TEXT))
    dark_palette.setColor(QPalette.ColorRole.Base,             QColor(COLOR_BASE))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase,    QColor(COLOR_BG))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase,      QColor(COLOR_TOOLTIP_BG))
    dark_palette.setColor(QPalette.ColorRole.ToolTipText,      QColor(COLOR_TOOLTIP_TEXT))
    dark_palette.setColor(QPalette.ColorRole.Text,             QColor(COLOR_TEXT))
    dark_palette.setColor(QPalette.ColorRole.Button,           QColor(COLOR_BUTTON_BG))
    dark_palette.setColor(QPalette.ColorRole.ButtonText,       QColor(COLOR_BUTTON_TEXT))
    dark_palette.setColor(QPalette.ColorRole.BrightText,       QColor(COLOR_BRIGHT_TEXT))
    dark_palette.setColor(QPalette.ColorRole.Highlight,        QColor(COLOR_HIGHLIGHT))
    dark_palette.setColor(QPalette.ColorRole.HighlightedText,  QColor(COLOR_HIGHLIGHT_TEXT))

    app.setPalette(dark_palette)
