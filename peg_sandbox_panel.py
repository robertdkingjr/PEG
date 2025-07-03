from PyQt6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout,
    QPushButton, QCheckBox, QComboBox,
)
from PyQt6.QtGui import QIcon, QPixmap, QColor
from PyQt6.QtCore import Qt
import peg_pieces
import logging


class SandboxDock(QDockWidget):
    def __init__(self, main_window: "MainWindow", parent=None):
        super().__init__("Sandbox", parent)
        self.logger = logging.getLogger(self.__class__.__name__)

        self.main_window = main_window
        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable)

        #
        #
        #
        # ORIGINAL
        sandbox_panel = QWidget()
        sandbox_layout = QVBoxLayout()
        sandbox_panel.setLayout(sandbox_layout)

        self.sandbox_toggle = QCheckBox("Sandbox Mode")
        self.sandbox_toggle.stateChanged.connect(self.toggle_sandbox)

        self.color_dropdown = self.get_color_dropdown()
        self.color_dropdown.currentTextChanged.connect(self.set_board_paint_color)
        self.set_board_paint_color()

        self.hex_orientation_toggle = QCheckBox("Pointy-Topped Hexes")
        self.hex_orientation_toggle.setChecked(True)
        self.hex_orientation_toggle.stateChanged.connect(self.toggle_orientation)

        # sandbox_layout.addWidget(self.sandbox_toggle)
        # sandbox_layout.addWidget(self.hex_orientation_toggle)
        # sandbox_layout.addWidget(self.color_dropdown)
        # self.sandbox_dock.setWidget(sandbox_panel)

        #
        #
        # NEW
        self.widget = QWidget()
        layout = QVBoxLayout(self.widget)

        # Add Player Button
        add_btn = QPushButton("Add Player")
        add_btn.clicked.connect(self.add_player)
        layout.addWidget(add_btn)

        # Remove Player Button
        remove_btn = QPushButton("Remove Player")
        remove_btn.clicked.connect(self.remove_player)
        layout.addWidget(remove_btn)

        layout.addWidget(self.sandbox_toggle)
        layout.addWidget(self.hex_orientation_toggle)
        layout.addWidget(self.color_dropdown)

        layout.addStretch()
        self.setWidget(self.widget)

    def set_board_paint_color(self):
        color = self.color_dropdown.currentText()
        self.logger.info(f'SET PAINT COLOR = {color}')
        self.main_window.board.paint_color = color

    def toggle_orientation(self):
        self.main_window.board.pointy_top = self.hex_orientation_toggle.isChecked()
        self.main_window.board.draw_board()

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

    def toggle_sandbox(self):
        self.main_window.board.sandbox_mode = self.sandbox_toggle.isChecked()
        self.logger.info(f"Sandbox Mode: {self.main_window.board.sandbox_mode}")

    def add_player(self, color=None):
        if not color:
            color = self.color_dropdown.currentText()

        self.logger.info(f'ADD PLAYER ({color})')
        self.main_window.game_state.add_player(color=color)  # custom logic in GameState
        self.logger.info(f'UPDATE MAIN WINDOW')
        self.main_window.update_all()

    def remove_player(self, color=None):
        if not color:
            color = self.color_dropdown.currentText()

        self.logger.info(f'REMOVE PLAYER ({color})')
        self.main_window.game_state.remove_player(color=color)
        self.main_window.update_all()
