import logging
import math
import random
from PyQt6.QtWidgets import (
    QGraphicsPolygonItem, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsRectItem
)
from PyQt6.QtGui import QColor, QBrush, QPen, QPolygonF
from PyQt6.QtCore import QRectF, QPropertyAnimation, pyqtSignal
from PyQt6.QtCore import QPointF, Qt
import hex_logic
from peg_pieces import DICE_FACES, HEX_COLORS, HEX_RADIUS, BOARD_RADIUS, RAIN_COLOR, HOLE_RADIUS
from peg_game_state import GameState
from PyQt6.QtWidgets import QGraphicsScene
from peg_pieces import HexTile, Peg


class GameBoard(QGraphicsScene):
    """VIEW + CONTROLLER: The visual, interactive scene where users see and manipulate the GameState"""

    selection_mode_changed = pyqtSignal(str)
    user_selected_hex = pyqtSignal(tuple)  # (q, r)
    highlight_die_label = pyqtSignal(object)  # emit the Die instance

    def __init__(self, game_state: GameState, radius=BOARD_RADIUS, hex_size=HEX_RADIUS, x_center=400, y_center=300):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.game_state: GameState = game_state
        self.radius = radius
        self.hex_size = hex_size
        self.x_center = x_center
        self.y_center = y_center
        self.hexes = {}  # (q, r): HexTile instance
        self.hex_items = {}  # (q, r): {"hex": hex_item, "text": text_item}
        self.pegs = {}  # ((q1,r1),(q2,r2),?): Peg instance

        self.pointy_top = True
        self.sandbox_mode = False
        self.paint_color = None

        # User hex selection
        self.selection_mode = False
        self.valid_hexes = []
        self.highlight_items = {}

        self.build_hex_grid()
        self.draw_board()

    def build_hex_grid(self):
        self.hexes.clear()
        for q in range(-self.radius, self.radius + 1):
            r1 = max(-self.radius, -q - self.radius)
            r2 = min(self.radius, -q + self.radius)
            for r in range(r1, r2 + 1):
                color = random.choice(HEX_COLORS)
                number = random.choice(DICE_FACES)
                self.hexes[(q, r)] = HexTile(q, r, color, number)

    def hex_to_pixel(self, q, r):
        if self.pointy_top:
            x = self.hex_size * math.sqrt(3) * (q + r / 2)
            y = self.hex_size * 1.5 * r
        else:
            x = self.hex_size * 1.5 * q
            y = self.hex_size * math.sqrt(3) * (r + q / 2)
        return x + self.x_center, y + self.y_center

    def clear_board(self):
        self.logger.info(f'CLEAR BOARD')
        for peg in self.pegs.values():
            peg.remove_from_scene()
        for player in self.game_state.players.values():
            for die in player.get_dice():
                die.remove_from_scene()
        self.hex_items.clear()
        self.clear()

    def draw_board(self):
        self.clear_board()
        self.logger.info(f'REDRAWING BOARD')
        self.draw_hexes()

        # peg_pool_index = 0
        # for peg in self.pegs:
        #     point = peg.to_pixel(hex_size=self.hex_size, pointy_top=self.pointy_top)
        #     peg.add_to_scene
        #         q, r, peg_index = peg.position
        #         x, y = hex_logic.peg_to_pixel(q=q, r=r, peg_index=peg_index, hex_size=self.hex_size, point_top=self.pointy_top)
        #         peg.add_to_scene(self, x + self.x_center, y + self.y_center)
        #     else:
        #         # place in off-board pool
        #         x = 50 + peg_pool_index * 30
        #         y = 200  # arbitrary dice pool row
        #         peg.add_to_scene(self, x, y)

    def create_hex_polygon(self, x, y):
        points = []
        for i in range(6):
            angle_deg = 60 * i - (30 if self.pointy_top else 0)
            angle_rad = math.radians(angle_deg)
            px = x + self.hex_size * math.cos(angle_rad)
            py = y + self.hex_size * math.sin(angle_rad)
            points.append(QPointF(px, py))
        return QPolygonF(points)

    def draw_hex(self, q, r, hex_tile):
        self.logger.debug(f'DRAW {hex_tile.get_name()}')
        x, y = self.hex_to_pixel(q, r)

        hex_item = QGraphicsPolygonItem(self.create_hex_polygon(x, y))
        hex_item.setBrush(QBrush(QColor(hex_tile.color)))
        hex_item.setPen(QPen(Qt.GlobalColor.black))
        self.addItem(hex_item)
        hex_item.setZValue(-1)

        text_item = QGraphicsTextItem(str(hex_tile.number))
        text_item.setPos(x - 8, y - 10)
        self.addItem(text_item)

        # Draw dice count square (outline only)
        dice_count = len(hex_tile.dice)
        square_size = 16
        square_x = x + 15
        square_y = y - 20

        if dice_count > 0:
            self.logger.debug(f'HEX DICE = {dice_count}')

            dice_square = QGraphicsRectItem(0, 0, square_size, square_size)
            dice_square.setBrush(QBrush())  # transparent fill
            dice_square.setPen(QPen(Qt.GlobalColor.black))
            # dice_square.setPen(QPen(Qt.GlobalColor.white))
            dice_square.setZValue(10)
            dice_square.setPos(square_x, square_y)  # move square to pixel position
            self.addItem(dice_square)

            # Dice count text, centered inside the square
            dice_text = QGraphicsTextItem(str(dice_count))
            dice_text.setParentItem(dice_square)

            # Center text inside the square
            text_rect = dice_text.boundingRect()
            dice_text.setPos(
                (square_size - text_rect.width()) / 2,
                (square_size - text_rect.height()) / 2
            )
            # dice_text.setDefaultTextColor(Qt.GlobalColor.black)
            dice_text.setDefaultTextColor(Qt.GlobalColor.white)
            dice_text.setZValue(11)

        else:
            self.logger.debug(f'NO HEX DICE')
            dice_square = None
            dice_text = None

        # save graphics items for reference
        self.hex_items[(q, r)] = {
            'hex': hex_item,
            'text': text_item,
            'dice_square': dice_square,
            'dice_text': dice_text,
        }

        # for i, peg in enumerate(hex_tile.pegs):
        #     angle = math.radians(i * 120)
        #     px = x + self.hex_size * 0.5 * math.cos(angle)
        #     py = y + self.hex_size * 0.5 * math.sin(angle)
        #     peg_item = QGraphicsEllipseItem(px - 6, py - 6, 12, 12)
        #     peg_item.setBrush(QBrush(QColor(peg.player)))
        #     self.addItem(peg_item)
        # for i, die in enumerate(hex_tile.dice):
        #     die.add_to_scene(self, self.hex_to_pixel)

    def draw_hexes(self):
        for (q, r), hex_tile in self.hexes.items():
            self.draw_hex(q, r, hex_tile)
            self.draw_peg_holes(q, r)

    def draw_peg_hole(self, x, y, hole_radius=HOLE_RADIUS):
        hole = QGraphicsEllipseItem(x - hole_radius, y - hole_radius, 2 * hole_radius, 2 * hole_radius)
        # hole.setBrush(QBrush(QColor("#888888")))  # dark gray
        hole.setBrush(QBrush(QColor("#8b4513")))  # warm mahogany
        hole.setPen(QPen(Qt.GlobalColor.black))
        hole.setZValue(1)  # Above hexes (-1), below pegs (1, 2)
        self.addItem(hole)

    def draw_peg_holes(self, q, r, hole_radius=HOLE_RADIUS):
        """
        Draws peg hole visuals at all peg positions (0–11) for each hex in `hexes`.
        - `scene`: QGraphicsScene to draw on
        - `hexes`: iterable of (q, r) axial hex coordinates
        - `hex_size`: radius of hexagon
        - `hole_radius`: visual radius of the peg hole
        """
        self.logger.debug(f'DRAW peg holes (r={hole_radius}) around ({q}, {r})')
        for peg_index in range(12):
            x, y = hex_logic.peg_to_pixel(q, r, peg_index, hex_size=self.hex_size, point_top=self.pointy_top)
            x += self.x_center
            y += self.y_center
            self.draw_peg_hole(x, y, hole_radius=hole_radius)

    def enter_selection_mode(self, color, die, valid_hexes):
        self.logger.info(f'{color} SELECT FROM {valid_hexes}')
        self.selection_mode = True
        self.selection_mode_changed.emit(str(color))
        self.valid_hexes = valid_hexes
        self.highlight_valid_hexes(valid_hexes)
        self.highlight_die_label.emit(die)

    def highlight_valid_hexes(self, valid_hexes):
        """Draw semi-transparent halos on valid hexes for selection."""
        self.clear_highlights()
        self.highlight_items = {}

        for (q, r) in valid_hexes:
            self.logger.info(f'HIGHLIGHT HEX ({q},{r})')
            hex_tile = self.hexes.get((q, r))
            if not hex_tile:
                continue

            # Create halo (ellipse slightly larger than hex)
            hex_item = self.hex_items.get((q, r)).get("hex", None)
            if hex_item:
                rect = hex_item.boundingRect()
                halo = self.addEllipse(
                    rect.adjusted(-5, -5, 5, 5),
                    QPen(QColor(0, 200, 255, 200), 2),
                    QBrush(QColor(0, 200, 255, 90))
                )
                halo.setZValue(30)  # ensure it's above the board
                # halo.setParentItem(hex_item)
                self.highlight_items[(q, r)] = halo

            else:
                self.logger.error(f'CANNOT HIGHLIGHT HEX ({q},{r})')

    def clear_highlights(self):
        """Remove all highlight halos from the scene."""
        if not hasattr(self, "highlight_items"):
            return
        self.highlight_die_label.emit(None)
        self.highlight_items.clear()
        self.draw_board()

    def hex_at(self, scene_pos):
        """Return (q, r) of clicked hex, or None if no hex found."""
        for (q, r), items in self.hex_items.items():
            if items["hex"].contains(items["hex"].mapFromScene(scene_pos)):
                return (q, r)
        return None

    def mousePressEvent(self, event):
        self.logger.info(f'MOUSE PRESS EVENT')
        if self.selection_mode:
            clicked_hex = self.hex_at(event.scenePos())
            self.logger.debug(f'SELECTION MODE: CLICKED HEX = {clicked_hex}')
            if clicked_hex in self.valid_hexes:
                self.logger.debug(f'CLICKED HEX VALID, EMIT + EXIT SELECTION MODE')
                self.user_selected_hex.emit(clicked_hex)
                # self.exit_selection_mode()
        else:
            super().mousePressEvent(event)

    def exit_selection_mode(self, reason=None):
        self.logger.debug(f'EXIT SELECTION MODE: {reason if reason else ""}')
        self.selection_mode = False
        self.selection_mode_changed.emit('')
        self.clear_highlights()

    def mouseReleaseEvent(self, event):
        """Update HEX color in sandbox mode"""
        if not self.sandbox_mode:
            return
        clicked_point = event.scenePos()
        for (q, r), tile in self.hexes.items():
            x, y = self.hex_to_pixel(q, r)
            if math.hypot(clicked_point.x() - x, clicked_point.y() - y) < self.hex_size:
                if self.paint_color is not None:
                    tile.color = self.paint_color
                    self.draw_board()
                else:
                    self.logger.error(f'paint_color not set')
                break

    def wheelEvent(self, event):
        if not self.sandbox_mode:
            return
        event.scenePos()
        point = event.scenePos()
        for (q, r), tile in self.hexes.items():
            x, y = self.hex_to_pixel(q, r)
            if math.hypot(point.x() - x, point.y() - y) < self.hex_size:
                tile.number = (tile.number % 6) + 1
                self.draw_board()
                break

    def add_peg_to_board(self, peg: Peg, location):

        self.pegs[location] = peg
        self.addItem(peg.item)
        peg.item.setPos(peg.to_pixel(self.hex_size, self.pointy_top))

        # Add to all affected hex tiles
        for qr in peg.position:
            if qr in self.hexes:
                self.hexes[qr].pegs.append(peg)

        # Render if needed
        self.draw_board()
        return peg

    def remove_peg(self, peg: Peg):
        # Remove from scene
        peg.remove_from_scene()

        # Remove from GameBoard peg list
        if peg in self.pegs.values():
            self.pegs.pop(peg.position, None)

        # Remove from hex tile (if it's linked to one)
        for hex_tile in self.hexes_touching_peg(peg):
            hex_tile.pegs = [p for p in hex_tile.pegs if p is not peg]
        peg.position = None

    def hexes_touching_peg(self, peg: Peg):
        """Return all hexes touched by the peg's position."""
        # Example: vertex position between three hexes
        if peg.position:
            return [self.hexes[qr] for qr in peg.position if qr in self.hexes]
        return []
