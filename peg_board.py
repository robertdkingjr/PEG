import logging
import math
import random
from PyQt6.QtWidgets import (
    QGraphicsPolygonItem, QGraphicsEllipseItem, QGraphicsTextItem
)
from PyQt6.QtGui import QBrush, QPen, QColor, QPolygonF
from PyQt6.QtCore import QPointF, Qt
import hex_logic
from peg_pieces import DICE_FACES, HEX_COLORS, HEX_RADIUS, BOARD_RADIUS, RAIN_COLOR, HOLE_RADIUS
from peg_game_state import GameState
from PyQt6.QtWidgets import QGraphicsScene
from peg_pieces import HexTile, Peg


class GameBoard(QGraphicsScene):
    # todo consider how to allow peg sharing location? is that ever possible?

    def __init__(self, game_state: GameState, radius=BOARD_RADIUS, hex_size=HEX_RADIUS, x_center=400, y_center=300):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.game_state: GameState = game_state
        self.radius = radius
        self.hex_size = hex_size
        self.x_center = x_center
        self.y_center = y_center
        self.hexes = {}  # (q, r): HexTile instance
        self.pegs = {}  # ((q1,r1),(q2,r2),?): Peg instance
        self.dice = []  # Die instances

        self.pointy_top = True
        self.sandbox_mode = False
        self.paint_color = None

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

    def draw_hex(self, x, y, hex_tile):
        self.logger.debug(f'DRAW {hex_tile.get_name()}')

        hex_item = QGraphicsPolygonItem(self.create_hex_polygon(x, y))
        hex_item.setBrush(QBrush(QColor(hex_tile.color)))
        hex_item.setPen(QPen(Qt.GlobalColor.black))
        self.addItem(hex_item)
        hex_item.setZValue(-1)

        num_text = QGraphicsTextItem(str(hex_tile.number))
        num_text.setPos(x - 8, y - 10)
        self.addItem(num_text)

        # for i, peg in enumerate(hex_tile.pegs):
        #     angle = math.radians(i * 120)
        #     px = x + self.hex_size * 0.5 * math.cos(angle)
        #     py = y + self.hex_size * 0.5 * math.sin(angle)
        #     peg_item = QGraphicsEllipseItem(px - 6, py - 6, 12, 12)
        #     peg_item.setBrush(QBrush(QColor(peg.player)))
        #     self.addItem(peg_item)
        # for i, die in enumerate(hex_tile.dice):
        #     die.add_to_scene(self, self.hex_to_pixel)

    def scene(self):
        pass

    def draw_hexes(self):
        for (q, r), hex_tile in self.hexes.items():
            x, y = self.hex_to_pixel(q, r)
            self.draw_hex(x, y, hex_tile)
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

    def assign_rain_die_to_hex(self, die):
        for (q, r), hex_tile in self.hexes.items():
            if hex_tile.color == RAIN_COLOR and hex_tile.number == die.value:
                self.logger.info(f"ASSIGN {die.get_name()} TO {hex_tile.get_name()}")

                original_hex = self.hexes.get(die.position, None)
                if original_hex:
                    self.logger.debug(f"REMOVE {die.get_name()} FROM {original_hex.get_name()}")
                    original_hex.dice.remove(die)
                hex_tile.dice.append(die)
                die.position = (q, r)
                self.draw_board()
                return

        self.logger.info(f"ASSIGN {die.get_name()} to POOL")
        die.position = None

    def roll_rain_dice(self):
        for i, die in enumerate(self.dice):
            if die.color == RAIN_COLOR:
                self.logger.info(f'ROLL RAIN DIE {i}')
                die.reroll()

            self.logger.info(f'ASSIGN RAIN DIE {i}')
            self.assign_rain_die_to_hex(die=die)

        self.draw_board()  # ensure new roll is reflected

    def play_phase(self):
        from peg_rules import play_phase_logic
        play_phase_logic(self)

    def eat_phase(self):
        from peg_rules import eat_phase_logic
        eat_phase_logic(self)

    def grow_phase(self):
        from peg_rules import grow_phase_logic
        grow_phase_logic(self)
