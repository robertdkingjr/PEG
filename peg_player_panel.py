from PyQt6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QSizePolicy
)
from PyQt6.QtGui import QColor, QPixmap, QPainter
from PyQt6.QtCore import Qt, QSize
import logging


class PlayerDock(QDockWidget):
    def __init__(self, game_state, parent=None):
        super().__init__("Players", parent)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.game_state = game_state
        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetClosable | QDockWidget.DockWidgetFeature.DockWidgetMovable)

        self.widget = QWidget()
        self.layout = QVBoxLayout(self.widget)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(10)

        self.setWidget(self.widget)

        self.die_label_map = {}  # key = Die object: value = QLabel object

    def update_panel(self):
        self.logger.debug(f'update_panel')

        # Clear existing
        for i in reversed(range(self.layout.count())):
            item = self.layout.itemAt(i).widget()
            if item:
                item.setParent(None)

        for player in self.game_state.players.values():
            self.layout.addWidget(self.create_player_row(player))

    def create_player_row(self, player) -> QFrame:
        self.logger.debug(f'create_player_row')

        row = QFrame()
        row.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(row)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(4)

        # Player color block
        color_box = QLabel()
        color_box.setFixedSize(20, 20)
        pix = QPixmap(20, 20)
        pix.fill(QColor(player.color))
        painter = QPainter(pix)
        painter.setPen(Qt.GlobalColor.black)
        painter.drawText(pix.rect(), Qt.AlignmentFlag.AlignCenter, ':)')
        painter.end()
        color_box.setPixmap(pix)
        layout.addWidget(color_box)

        # Show remaining pegs
        layout.addWidget(self.make_n_pegs_icon(color=player.color, n_pegs=len(player.pegs)))

        # Rain Dice
        for die in player.rain_dice:
            layout.addWidget(self.make_die_icon(die))

        # Food Dice
        for die in player.food_dice:
            layout.addWidget(self.make_die_icon(die))

        # # Pegs
        # for peg in player.pegs:
        #     layout.addWidget(self.make_peg_icon(peg))

        return row

    def highlight_die_label(self, die):
        self.update_panel()
        label = self.die_label_map.get(die)
        if label:
            label.setStyleSheet("""
                    border: 2px solid #00C8FF;
                    padding: 0px;
                    background-color: rgba(0, 200, 255, 30);
                """)
        else:
            # Clear existing highlights first
            for label in self.die_label_map.values():
                label.setStyleSheet("")  # reset style

    def make_die_icon(self, die) -> QLabel:
        size = 40
        pix = QPixmap(size, size)
        pix.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pix)
        color = QColor(die.color).darker(120)
        if die.position is None:
            color = color.darker(255)
            color.setAlpha(100)
        else:
            color = color.darker(150)
        painter.setBrush(color)
        painter.setPen(Qt.GlobalColor.black)
        painter.drawRect(0, 0, size, size)
        painter.setPen(Qt.GlobalColor.white)
        painter.drawText(pix.rect(), Qt.AlignmentFlag.AlignCenter, str(die.value or '?'))
        painter.end()

        label = QLabel()
        label.setPixmap(pix)
        label.setFixedSize(QSize(size + 2, size + 2))
        label.setToolTip(f"Die: {die.color} {die.value}")
        self.die_label_map[die] = label
        return label

    def make_n_pegs_icon(self, color, n_pegs):
        size = 30
        pix = QPixmap(size, size)
        pix.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pix)
        color = QColor(color).lighter(150)
        painter.setBrush(color)
        painter.setPen(Qt.GlobalColor.black)
        painter.drawEllipse(2, 2, size - 4, size - 4)
        painter.drawText(pix.rect(), Qt.AlignmentFlag.AlignCenter, str(n_pegs))
        painter.end()

        label = QLabel()
        label.setPixmap(pix)
        label.setFixedSize(QSize(size + 2, size + 2))
        label.setToolTip(f"Remaining pegs: {n_pegs}")
        return label

    def make_peg_icon(self, peg):
        size = 20
        pix = QPixmap(size, size)
        pix.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pix)
        color = QColor(peg.color)
        if peg.position is not None:
            color.setAlpha(100)  # Greyed out if placed
        painter.setBrush(color)
        painter.setPen(Qt.GlobalColor.black)
        painter.drawEllipse(2, 2, size - 4, size - 4)
        painter.drawText(pix.rect(), Qt.AlignmentFlag.AlignCenter, str(peg.size))
        painter.end()

        label = QLabel()
        label.setPixmap(pix)
        label.setFixedSize(QSize(size + 2, size + 2))
        label.setToolTip(f"Peg: {peg.color} size {peg.size}")
        return label
