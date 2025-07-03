import logging
from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsRectItem
from PyQt6.QtGui import QBrush, QColor, QPen
from PyQt6.QtCore import Qt, QPointF
import random
import math

BOARD_RADIUS = 3
HEX_RADIUS = 40
HOLE_RADIUS = 5
DIE_RADIUS = 10
HEX_COLORS = [
    'blue',
    'orange',
    'green',
    # 'darkGreen',
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


# hex_tile_item.py
from PyQt6.QtWidgets import QGraphicsPolygonItem, QGraphicsTextItem
from PyQt6.QtGui import QBrush, QPen, QColor, QPolygonF
from PyQt6.QtCore import QPointF, Qt
import math


class HexTileItem(QGraphicsPolygonItem):
    def __init__(self, tile: "HexTile", hex_size: float, pointy_top: bool = True):
        super().__init__()
        self.tile = tile
        self.hex_size = hex_size
        self.pointy_top = pointy_top
        self.setZValue(-1)  # Background

        self.setAcceptHoverEvents(True)
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable)

        self.text_item = QGraphicsTextItem("", self)
        self.text_item.setDefaultTextColor(Qt.GlobalColor.black)
        self.text_item.setZValue(1)

        self.update_polygon()
        self.update_appearance()
        self.update_label()

    def update_polygon(self):
        q, r = self.tile.q, self.tile.r
        center = self.axial_to_pixel(q, r)
        self.setPolygon(self.create_hexagon(center))

    def axial_to_pixel(self, q, r):
        s = self.hex_size
        if self.pointy_top:
            x = s * math.sqrt(3) * (q + r/2)
            y = s * 3/2 * r
        else:
            x = s * 3/2 * q
            y = s * math.sqrt(3) * (r + q/2)
        return QPointF(x, y)

    def create_hexagon(self, center: QPointF) -> QPolygonF:
        s = self.hex_size
        points = []
        angle_offset = 30 if self.pointy_top else 0
        for i in range(6):
            angle_deg = 60 * i + angle_offset
            angle_rad = math.radians(angle_deg)
            x = center.x() + s * math.cos(angle_rad)
            y = center.y() + s * math.sin(angle_rad)
            points.append(QPointF(x, y))
        return QPolygonF(points)

    def update_appearance(self):
        color_map = {
            "green": QColor(102, 204, 102),
            "yellow": QColor(255, 255, 153),
            "blue": QColor(102, 178, 255),
            "gray": QColor(200, 200, 200),
        }
        fill = color_map.get(self.tile.color, QColor("white"))
        self.setBrush(QBrush(fill))
        self.setPen(QPen(Qt.GlobalColor.black, 1))

    def update_label(self):
        self.text_item.setPlainText(str(self.tile.number))
        bounds = self.polygon().boundingRect()
        self.text_item.setPos(
            bounds.center().x() - self.text_item.boundingRect().width() / 2,
            bounds.center().y() - self.text_item.boundingRect().height() / 2,
        )

    def mouseDoubleClickEvent(self, event):
        if hasattr(self.scene(), "on_hex_double_click"):
            self.scene().on_hex_double_click(self.tile)
        super().mouseDoubleClickEvent(event)

    def wheelEvent(self, event):
        if hasattr(self.scene(), "on_hex_wheel_scroll"):
            self.scene().on_hex_wheel_scroll(self.tile, event.angleDelta().y())
        super().wheelEvent(event)


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
        return f'HEX-{self.color.upper()}{self.number} at ({self.q}, {self.r})'

    def to_pixel(self, hex_size, pointy_top, x_center, y_center):
        if pointy_top:
            x = hex_size * math.sqrt(3) * (self.q + self.r / 2)
            y = hex_size * 1.5 * self.r
        else:
            x = hex_size * 1.5 * self.q
            y = hex_size * math.sqrt(3) * (self.r + self.q / 2)
        return x + x_center, y + y_center


class PegItem(QGraphicsEllipseItem):
    def __init__(self, peg, radius=10):
        super().__init__()
        self.peg = peg  # back-reference
        self.radius = radius

        self.setRect(QRectF(-radius, -radius, 2*radius, 2*radius))
        self.setBrush(QBrush(QColor(peg.color)))
        self.setPen(QPen(Qt.GlobalColor.black, 1))
        self.setZValue(10)  # ensure it's above the board
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable, peg.board.sandbox_mode)
        self.setFlag(self.GraphicsItemFlag.ItemSendsScenePositionChanges)

        # Tooltip
        self.setToolTip(f"Peg: Player {peg.color}, Size {peg.size}")

    def update_visual(self):
        self.setBrush(QBrush(QColor(self.peg.color)))
        self.setToolTip(f"Peg: Player {self.peg.color}, Size {self.peg.size}")

    def itemChange(self, change, value):
        if change == self.GraphicsItemChange.ItemPositionHasChanged:
            if self.peg.board.sandbox_mode:
                self.peg.update_from_position(value)
        return super().itemChange(change, value)


class Peg:
    def __init__(self, color, size, position, board):
        """
        Parameters:
            color (str): Player color
            size (int): Peg size (1, 2, 4, 8, etc.)
            position (tuple): tuple(sorted((q, r) coordinates))
            board (GameBoard): Reference to the game board
        """
        self.color = color
        self.size = size
        self.position = position  # canonical hex position: tuple(sorted([(q, r), ...]))
        self.board = board

        # GUI item
        self.item = PegItem(self)

    def grow(self):
        """Double the size (max size can be enforced elsewhere)."""
        self.size = min(self.size * 2, 8)
        self.item.update_visual()

    def move_to(self, new_position):
        """Update logic position and redraw the peg."""
        self.position = new_position
        self.item.setPos(self.to_pixel(self.board.hex_size, self.board.pointy_top))

    def to_pixel(self, hex_size, pointy_top):
        """Convert self.position (canonicalized hexes) into a screen coordinate for drawing."""
        if not self.position:
            return QPointF(0, 0)

        # Get average pixel center of all touched hexes
        centers = [self.board.hex_to_pixel(q, r, hex_size, pointy_top) for (q, r) in self.position]
        avg_x = sum(pt.x() for pt in centers) / len(centers)
        avg_y = sum(pt.y() for pt in centers) / len(centers)
        return QPointF(avg_x, avg_y)

    def remove_from_scene(self):
        """Remove peg visual from scene."""
        if self.item.scene():
            self.board.removeItem(self.item)

# class Peg:
#     def __init__(self, color: str, size: int = 1, position=None):
#         self.color = color  # e.g., 'Red', 'Blue'
#         self.size = size  # 1, 2, 4, etc.
#
#         self.position = position  # ((q1, r1),(q2, r2),?)
#         self.graphics_item = None
#         self.text_item = None
#         self.scene = None
#
#     def to_pixel(self, x_center, y_center, hex_size, pointy_top) -> QPointF:
#         """
#         Compute the average pixel position of the hexes this peg touches.
#         The peg's position is stored as a tuple of (q, r) hexes (sorted and unique).
#         """
#         if not self.position:
#             return QPointF(0, 0)  # Default fallback
#
#         hexes = self.position  # canonical tuple of (q, r) tuples
#         total_x, total_y = 0.0, 0.0
#
#         for q, r in hexes:
#             if pointy_top:
#                 # Pointy-topped hex axial to pixel
#                 x = hex_size * math.sqrt(3) * (q + r / 2)
#                 y = hex_size * 1.5 * r
#             else:
#                 # Flat-topped hex axial to pixel
#                 x = hex_size * 1.5 * q
#                 y = hex_size * math.sqrt(3) * (r + q / 2)
#
#             total_x += x
#             total_y += y
#
#         count = len(hexes)
#         return QPointF(total_x / count, total_y / count)
#
#     def add_to_scene(self, scene, hex_size, pointy_top, x_center, y_center, z=2):
#         """Draws the peg at (x, y) on the given scene."""
#         self.remove_from_scene()  # If already drawn, remove first.
#
#         pixel_pos = self.to_pixel(x_center=x_center, y_center=y_center, hex_size=hex_size, pointy_top=pointy_top)
#         radius = 10 + 2 * self.size
#         self.graphics_item = QGraphicsEllipseItem(x - radius / 2, y - radius / 2, radius, radius)
#         self.graphics_item.setPos(pixel_pos)
#         self.graphics_item.setBrush(QBrush(QColor(self.color)))
#         self.graphics_item.setZValue(1)
#         scene.addItem(self.graphics_item)
#
#         # Size label
#         self.text_item = QGraphicsTextItem(str(self.size))
#         self.text_item.setPos(x - 5, y - 8)
#         self.text_item.setZValue(z)
#         scene.addItem(self.text_item)
#
#         self.scene = scene
#
#     def remove_from_scene(self):
#         """Removes the peg’s graphics from the scene."""
#         if self.scene:
#             if self.graphics_item:
#                 self.scene.removeItem(self.graphics_item)
#             if self.text_item:
#                 self.scene.removeItem(self.text_item)
#         self.graphics_item = None
#         self.text_item = None
#         self.scene = None
#
#     def update_position(self, x, y):
#         """Repositions graphics without redrawing from scratch."""
#         if self.graphics_item:
#             self.graphics_item.setRect(x - self.graphics_item.rect().width() / 2,
#                                        y - self.graphics_item.rect().height() / 2,
#                                        self.graphics_item.rect().width(),
#                                        self.graphics_item.rect().height())
#         if self.text_item:
#             self.text_item.setPos(x - 5, y - 8)
#
#     def set_draggable(self, is_draggable: bool):
#
#         for item in [self.graphics_item, self.text_item]:
#             if item:
#                 flags = item.flags()
#                 if is_draggable:
#                     flags |= QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable
#                     flags |= QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable
#                 else:
#                     flags &= ~QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable
#                     flags &= ~QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable
#                 item.setFlags(flags)


from PyQt6.QtWidgets import QGraphicsRectItem, QGraphicsTextItem
from PyQt6.QtGui import QBrush, QPen, QColor, QFont
from PyQt6.QtCore import QRectF, Qt


class DieItem(QGraphicsRectItem):
    def __init__(self, die, size=20):
        super().__init__()
        self.die = die  # back-reference
        self.size = size

        self.setRect(QRectF(-size/2, -size/2, size, size))
        self.setBrush(QBrush(QColor(die.color)))
        self.setPen(QPen(Qt.GlobalColor.black, 1))
        self.setZValue(5)

        # Text label
        self.label = QGraphicsTextItem(str(die.value), self)
        self.label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.label.setDefaultTextColor(Qt.GlobalColor.black)
        self.label.setZValue(6)
        self.label.setPos(-size/4, -size/3)

        self.setToolTip(f"Die: {die.color} {die.value}")

    def update_visual(self):
        self.setBrush(QBrush(QColor(self.die.color)))
        self.label.setPlainText(self.die.value)
        self.setToolTip(f"Die: {self.die.color} {self.die.value}")


class Die:
    def __init__(self, color, value=None, board=None, position=None):
        """
        Parameters:
            color (str): Die color (e.g. 'yellow', 'green')
            value (str/int): Face value
            board (GameBoard): Reference to board
            position (tuple): (q, r) hex position or None if in dice pool
        """
        self.color = color
        self.value = value
        self.board = board
        self.position = position  # None = dice pool, else (q, r)

        # GUI item
        self.item = DieItem(self)

    def reroll(self):
        """Change to a random new face value."""
        self.value = random.randint(1, 6)  # or use custom face set
        self.item.update_visual()

    def move_to(self, position):
        """Update hex position and redraw."""
        self.position = position
        if position:
            pos = self.board.hex_to_pixel(*position, self.board.hex_size, self.board.pointy_top)
            self.item.setPos(pos)
        else:
            # Off-board pool — you may define a grid/pool position logic
            self.item.setPos(self.board.get_pool_position(self))

    def remove_from_scene(self):
        """Remove die from board's scene."""
        if self.item.scene():
            self.board.removeItem(self.item)


# class Die:
#     def __init__(self, color='yellow', value=None, player=None):
#         self.logger = logging.getLogger(self.__class__.__name__)
#         self.color = color
#         self.value = value if value is not None else random.randint(1, 6)
#         self.graphics_item = None
#         self.text_item = None
#         self.qr_position = None  # optional (q, r) to track die placement on hex
#         self.player = player
#
#     def get_name(self):
#         if self.qr_position is None:
#             position = 'OFF-GRID'
#         else:
#             q, r = self.qr_position
#             position = f'({q}, {r})'
#         return f"DIE-{self.color.upper()}{self.value} at {position}"
#
#     def roll(self):
#         new_roll = random.randint(1, 6)
#         self.logger.info(f'ROLL {self.get_name()} -> {new_roll}')
#         self.value = new_roll
#         self.update_text()
#
#     def add_to_scene(self, scene, hex_to_pixel=None, pool_index=0):
#         radius = DIE_RADIUS
#         color_map = {'yellow': '#f7e159', 'green': '#74c365', 'blue': '#6ec3f0'}
#         brush = QBrush(QColor(color_map.get(self.color, 'white')))
#         pen = QPen(Qt.GlobalColor.black)
#
#         if self.qr_position and hex_to_pixel:
#             q, r = self.qr_position
#             x, y = hex_to_pixel(q, r)
#             x += 0  # adjust x-offset on hex if needed
#             y += HEX_RADIUS * 0.6  # stack dice slightly below hex center
#         else:
#             # place in off-board dice pool using pool_index for layout
#             x = 50 + pool_index * 30
#             y = 100  # arbitrary dice pool row
#             self.qr_position = None
#
#         # self.graphics_item = QGraphicsEllipseItem(x - radius, y - radius, radius * 2, radius * 2)
#         self.graphics_item = QGraphicsRectItem(x - radius, y - radius, radius * 2, radius * 2)
#         self.graphics_item.setBrush(brush)
#         self.graphics_item.setPen(pen)
#         scene.addItem(self.graphics_item)
#
#         self.text_item = QGraphicsTextItem(str(self.value))
#         self.text_item.setPos(x - 6, y - 10)
#         self.text_item.setDefaultTextColor(Qt.GlobalColor.black)
#         scene.addItem(self.text_item)
#
#     def update_text(self):
#         if self.text_item:
#             self.text_item.setPlainText(str(self.value))
#
#     def remove_from_scene(self, scene):
#         if self.graphics_item:
#             scene.removeItem(self.graphics_item)
#             self.graphics_item = None
#         if self.text_item:
#             scene.removeItem(self.text_item)
#             self.text_item = None
