import logging

from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsRectItem
from PyQt6.QtGui import QBrush, QColor, QPen
from PyQt6.QtCore import Qt

import random

import hex_logic

BOARD_RADIUS = 3
HEX_RADIUS = 40
HOLE_RADIUS = 5
DIE_RADIUS = 10
HEX_COLORS = [
    'blue',
    'orange',
    'green',
    'darkGreen',
    # 'darkOrange',
    'grey',
    'purple',
    'darkBlue',
    'olive',
    # 'chartreuse',
    'yellowGreen',
    # 'lime',
    'seaGreen',
    'brown'
]
RAIN_COLOR = 'blue'
DICE_FACES = [1, 2, 3, 4, 5, 6]


class HexTile:
    def __init__(self, q, r, color='yellow', number=1):
        self.q = q
        self.r = r
        self.color = color
        self.number = number
        self.pegs = []
        self.dice = []

    def coords(self):
        return self.q, self.r

    def get_name(self):
        return f'HEX-{self.color.upper()}{self.number} at ({self.q},{self.r})'


class Peg:
    def __init__(self, player_color: str, size: int = 1, position=None):
        self.player_color = player_color  # e.g., 'Red', 'Blue'
        self.size = size  # 1, 2, 4, etc.

        self.position = position  # (q, r, peg_index)
        self.touches = None
        self.graphics_item = None
        self.text_item = None
        self.scene = None

    def get_touched_hexes(self):
        if self.position is not None:
            q, r, peg_index = self.position
            hexes = hex_logic.get_hexes_for_peg(q, r, peg_index)
        else:
            hexes = []

        return hexes

    def add_to_scene(self, scene, x, y):
        """Draws the peg at (x, y) on the given scene."""
        self.remove_from_scene()  # If already drawn, remove first.

        radius = 10 + 2 * self.size
        self.graphics_item = QGraphicsEllipseItem(x - radius / 2, y - radius / 2, radius, radius)
        self.graphics_item.setBrush(QBrush(QColor(self.player_color)))
        self.graphics_item.setZValue(1)
        scene.addItem(self.graphics_item)

        # Size label
        self.text_item = QGraphicsTextItem(str(self.size))
        self.text_item.setPos(x - 5, y - 8)
        self.text_item.setZValue(2)
        scene.addItem(self.text_item)

        self.scene = scene

    def remove_from_scene(self):
        """Removes the peg’s graphics from the scene."""
        if self.scene:
            if self.graphics_item:
                self.scene.removeItem(self.graphics_item)
            if self.text_item:
                self.scene.removeItem(self.text_item)
        self.graphics_item = None
        self.text_item = None
        self.scene = None

    def update_position(self, x, y):
        """Repositions graphics without redrawing from scratch."""
        if self.graphics_item:
            self.graphics_item.setRect(x - self.graphics_item.rect().width() / 2,
                                       y - self.graphics_item.rect().height() / 2,
                                       self.graphics_item.rect().width(),
                                       self.graphics_item.rect().height())
        if self.text_item:
            self.text_item.setPos(x - 5, y - 8)

    def set_draggable(self, is_draggable: bool):

        for item in [self.graphics_item, self.text_item]:
            if item:
                flags = item.flags()
                if is_draggable:
                    flags |= QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable
                    flags |= QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable
                else:
                    flags &= ~QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable
                    flags &= ~QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable
                item.setFlags(flags)


class Die:
    def __init__(self, color='yellow', value=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.color = color
        self.value = value if value is not None else random.randint(1, 6)
        self.graphics_item = None
        self.text_item = None
        self.qr_location = None  # optional (q, r) to track die placement on hex

    def get_name(self):
        if self.qr_location is None:
            location = 'OFF-GRID'
        else:
            q, r = self.qr_location
            location = f'({q},{r})'
        return f"DIE-{self.color.upper()}{self.value} at {location}"

    def roll(self):
        new_roll = random.randint(1, 6)
        self.logger.info(f'ROLL {self.get_name()} -> {new_roll}')
        self.value = new_roll
        self.update_text()

    def add_to_scene(self, scene, hex_to_pixel=None, pool_index=0):
        radius = DIE_RADIUS
        color_map = {'yellow': '#f7e159', 'green': '#74c365', 'blue': '#6ec3f0'}
        brush = QBrush(QColor(color_map.get(self.color, 'white')))
        pen = QPen(Qt.GlobalColor.black)

        if self.qr_location and hex_to_pixel:
            q, r = self.qr_location
            x, y = hex_to_pixel(q, r)
            x += 0  # adjust x-offset on hex if needed
            y += HEX_RADIUS * 0.6  # stack dice slightly below hex center
        else:
            # place in off-board dice pool using pool_index for layout
            x = 50 + pool_index * 30
            y = 100  # arbitrary dice pool row
            self.qr_location = None

        # self.graphics_item = QGraphicsEllipseItem(x - radius, y - radius, radius * 2, radius * 2)
        self.graphics_item = QGraphicsRectItem(x - radius, y - radius, radius * 2, radius * 2)
        self.graphics_item.setBrush(brush)
        self.graphics_item.setPen(pen)
        scene.addItem(self.graphics_item)

        self.text_item = QGraphicsTextItem(str(self.value))
        self.text_item.setPos(x - 6, y - 10)
        self.text_item.setDefaultTextColor(Qt.GlobalColor.black)
        scene.addItem(self.text_item)

    def update_text(self):
        if self.text_item:
            self.text_item.setPlainText(str(self.value))

    def remove_from_scene(self, scene):
        if self.graphics_item:
            scene.removeItem(self.graphics_item)
            self.graphics_item = None
        if self.text_item:
            scene.removeItem(self.text_item)
            self.text_item = None
