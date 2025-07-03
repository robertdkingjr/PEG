import logging
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QGraphicsView, QMainWindow, QPushButton, QVBoxLayout,
    QWidget, QCheckBox, QComboBox,
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QDockWidget, QLabel, QPushButton, QComboBox, QListWidget,
    QGraphicsView, QGraphicsScene, QSizePolicy, QFrame
)
from PyQt6.QtGui import QIcon, QPixmap, QPainter
from peg_game_state import GameState
from peg_board import GameBoard
from peg_player_panel import PlayerDock
from peg_sandbox_panel import SandboxDock
import peg_pieces
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QGraphicsView
from PyQt6.QtGui import QWheelEvent
from PyQt6.QtCore import Qt


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

ZOOM_FACTOR = 1.02


class ZoomableGraphicsView(QGraphicsView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

    def wheelEvent(self, event: QWheelEvent):
        # If the user holds Ctrl or scrolls over empty space (not over a hex with a number)
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier or not self.itemAt(event.position().toPoint()):
            zoom_in = event.angleDelta().y() > 0
            factor = ZOOM_FACTOR if zoom_in else 1 / ZOOM_FACTOR
            self.scale(factor, factor)
        else:
            # Propagate event normally (for hex number cycling etc.)
            super().wheelEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.setWindowTitle("PEG Simulator")

        # === CENTRAL AREA (Game Board) ===
        central_widget = QWidget()
        central_layout = QVBoxLayout()
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

        self.game_state = GameState()
        self.board = GameBoard(game_state=self.game_state)
        self.game_state.board = self.board  # chicken/egg...

        # self.board_view = QGraphicsView()
        self.board_view = ZoomableGraphicsView()
        # self.board_scene = QGraphicsScene()
        self.board_view.setScene(self.board)
        self.board_view.setRenderHints(self.board_view.renderHints() | QPainter.RenderHint.Antialiasing)
        central_layout.addWidget(self.board_view)

        # === TOP PANEL (Dice & PEG Controls) ===
        top_bar = QHBoxLayout()

        # Dice Pool
        self.dice_pool_label = QLabel("🎲 Dice Pool:")
        top_bar.addWidget(self.dice_pool_label)

        # PEG Phase Buttons
        self.play_button = QPushButton("P (Play)")
        self.eat_button = QPushButton("E (Eat)")
        self.grow_button = QPushButton("G (Grow)")

        top_bar.addWidget(self.play_button)
        top_bar.addWidget(self.eat_button)
        top_bar.addWidget(self.grow_button)

        # Current Growth Die Display
        self.growth_label = QLabel("✖️ Growth Die: ?")
        top_bar.addWidget(self.growth_label)

        top_bar.addStretch()
        central_layout.insertLayout(0, top_bar)  # Insert above board

        # === RIGHT SIDEBAR (Player Info Panel) ===
        # self.player_dock = QDockWidget("Players", self)
        self.player_dock = PlayerDock(game_state=self.game_state, parent=self)
        self.player_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.player_dock)

        player_dock_toggle_button = QPushButton("Show Player Panel")
        player_dock_toggle_button.setCheckable(True)
        player_dock_toggle_button.setChecked(True)
        player_dock_toggle_button.toggled.connect(self.player_dock.setVisible)
        self.player_dock.visibilityChanged.connect(player_dock_toggle_button.setChecked)
        top_bar.addWidget(player_dock_toggle_button)

        # player_panel = QWidget()
        # player_layout = QVBoxLayout()
        # player_panel.setLayout(player_layout)
        #
        # for i in range(4):  # Placeholder for 4 players
        #     label = QLabel(f"🧍 Player {i+1}")
        #     label.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        #     player_layout.addWidget(label)
        #
        # self.player_dock.setWidget(player_panel)

        # === LEFT SIDEBAR (Sandbox / Editor Tools) ===
        # self.sandbox_dock = QDockWidget("Sandbox Tools", self)
        self.sandbox_dock = SandboxDock(main_window=self, parent=self)
        self.sandbox_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.sandbox_dock)

        sandbox_dock_toggle_button = QPushButton("Show Sandbox Panel")
        sandbox_dock_toggle_button.setCheckable(True)
        sandbox_dock_toggle_button.setChecked(True)
        sandbox_dock_toggle_button.toggled.connect(self.sandbox_dock.setVisible)
        self.sandbox_dock.visibilityChanged.connect(sandbox_dock_toggle_button.setChecked)
        top_bar.addWidget(sandbox_dock_toggle_button)

        # === BOTTOM PANEL (PEG Turn Order & Log) ===
        bottom_bar = QHBoxLayout()

        self.turn_order_label = QLabel("🔁 Phase Order: [PLAY → EAT → GROW]")
        bottom_bar.addWidget(self.turn_order_label)

        self.status_log = QListWidget()
        self.status_log.setMaximumHeight(100)
        central_layout.addLayout(bottom_bar)
        central_layout.addWidget(self.status_log)

        # === INIT STATE ===
        self.status_log.addItem("PEG Simulator Initialized.")

    def log(self, msg):
        self.logger.info(msg)
        self.status_log.addItem(msg)

    def update_all(self):
        """Redraw all elements"""
        self.log('Update player dock')
        self.player_dock.update_panel()
        self.log('Update game board')
        self.board.draw_board()
        # self.sandbox_dock.


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
