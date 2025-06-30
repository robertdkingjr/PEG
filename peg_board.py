import logging
import math
import random
from collections import defaultdict
from PyQt6.QtWidgets import (
    QGraphicsScene, QGraphicsPolygonItem, QGraphicsEllipseItem, QGraphicsTextItem
)
from PyQt6.QtGui import QBrush, QPen, QColor, QPolygonF
from PyQt6.QtCore import QPointF, Qt

import hex_logic
from peg_pieces import HexTile, Peg, Die, DICE_FACES, HEX_COLORS, HEX_RADIUS, BOARD_RADIUS, RAIN_COLOR, HOLE_RADIUS


class GameBoard(QGraphicsScene):

    def __init__(self, radius=BOARD_RADIUS, hex_size=HEX_RADIUS, x_center=400, y_center=300):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.radius = radius
        self.hex_size = hex_size
        self.x_center = x_center
        self.y_center = y_center
        self.hexes = {}
        self.players = ['Yellow', 'Green']
        self.food_dice_pile = {'yellow': [], 'green': []}
        self.rain_dice = []
        self.eat_scores = defaultdict(int)
        self.growth_die = random.choice(DICE_FACES)
        self.pointy_top = True
        self.sandbox_mode = False
        self.paint_color = None
        self.pegs = []
        self.peg_holes = []
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
        for rain_die in self.rain_dice:
            rain_die.remove_from_scene(self)
        for peg in self.pegs:
            peg.remove_from_scene()
        self.clear()

    def draw_board(self):
        self.clear_board()
        self.logger.info(f'REDRAWING BOARD')
        for (q, r), hex_tile in self.hexes.items():
            x, y = self.hex_to_pixel(q, r)
            self.draw_hex(x, y, hex_tile)
            self.logger.info(f'DRAW {hex_tile.get_name()}')
        self.draw_peg_holes()
        rain_die_pool_index = 0
        for rain_die in self.rain_dice:
            if rain_die.qr_location is None:
                self.logger.info(f'DRAW {rain_die.get_name()} in POOL index {rain_die_pool_index}')
                rain_die.add_to_scene(self, self.hex_to_pixel, pool_index=rain_die_pool_index)
                rain_die_pool_index += 1
        peg_pool_index = 0
        for peg in self.pegs:
            if peg.position:
                q, r, peg_index = peg.position
                x, y = hex_logic.peg_to_pixel(q=q, r=r, peg_index=peg_index, hex_size=self.hex_size)
                peg.add_to_scene(self, x + self.x_center, y + self.y_center)
            else:
                # place in off-board pool
                x = 50 + peg_pool_index * 30
                y = 200  # arbitrary dice pool row
                peg.add_to_scene(self, x, y)

    def draw_hex(self, x, y, hex_tile):
        hex_item = QGraphicsPolygonItem(self.create_hex_polygon(x, y))
        hex_item.setBrush(QBrush(QColor(hex_tile.color)))
        hex_item.setPen(QPen(Qt.GlobalColor.black))
        self.addItem(hex_item)
        hex_item.setZValue(-1)

        num_text = QGraphicsTextItem(str(hex_tile.number))
        num_text.setPos(x - 8, y - 10)
        self.addItem(num_text)

        for i, peg in enumerate(hex_tile.pegs):
            angle = math.radians(i * 120)
            px = x + self.hex_size * 0.5 * math.cos(angle)
            py = y + self.hex_size * 0.5 * math.sin(angle)
            peg_item = QGraphicsEllipseItem(px - 6, py - 6, 12, 12)
            peg_item.setBrush(QBrush(QColor(peg.player)))
            self.addItem(peg_item)

        for i, die in enumerate(hex_tile.dice):
            die.add_to_scene(self, self.hex_to_pixel)

    def draw_peg_holes(self, hole_radius=HOLE_RADIUS):
        """
        Draws peg hole visuals at all peg positions (0–11) for each hex in `hexes`.
        - `scene`: QGraphicsScene to draw on
        - `hexes`: iterable of (q, r) axial hex coordinates
        - `hex_size`: radius of hexagon
        - `hole_radius`: visual radius of the peg hole
        """
        for (q, r), hex_tile in self.hexes.items():
            for peg_index in range(12):
                x, y = hex_logic.peg_to_pixel(q, r, peg_index, hex_size=self.hex_size)
                x += self.x_center
                y += self.y_center
                hole = QGraphicsEllipseItem(x - hole_radius, y - hole_radius, 2 * hole_radius, 2 * hole_radius)
                # hole.setBrush(QBrush(QColor("#888888")))  # dark gray
                hole.setBrush(QBrush(QColor("#8b4513")))  # warm mahogany
                hole.setPen(QPen(Qt.GlobalColor.black))
                hole.setZValue(1)  # Above hexes (-1), below pegs (1, 2)
                self.addItem(hole)

    def create_hex_polygon(self, x, y):
        points = []
        for i in range(6):
            angle_deg = 60 * i - (30 if self.pointy_top else 0)
            angle_rad = math.radians(angle_deg)
            px = x + self.hex_size * math.cos(angle_rad)
            py = y + self.hex_size * math.sin(angle_rad)
            points.append(QPointF(px, py))
        return QPolygonF(points)

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

    def add_random_peg(self, player_color=None, size=1):
        hex_tile = random.choice(list(self.hexes.values()))
        if player_color is None:
            player_color = random.choice(self.players)
        peg_index = random.randint(0, 11)
        self.add_peg(q=hex_tile.q, r=hex_tile.r, peg_index=peg_index, player_color=player_color, size=size)

    def add_peg(self, q, r, peg_index, player_color, size=1):

        peg = Peg(player_color=player_color, size=size, position=(q, r, peg_index))
        self.pegs.append(peg)

        # Add to all affected hex tiles
        for qr in peg.position:
            if qr in self.hexes:
                self.hexes[qr].pegs.append(peg)

        # Render if needed
        self.draw_board()
        return peg

    def remove_peg(self, peg_to_remove: Peg):
        # Remove from scene
        peg_to_remove.remove_from_scene()

        # Remove from GameBoard peg list
        if peg_to_remove in self.pegs:
            self.pegs.remove(peg_to_remove)

        # Remove from hex tile (if it's linked to one)
        if peg_to_remove.position:
            affected_hexes = self.hexes_touching_peg(peg_to_remove)
            for hex_tile in affected_hexes:
                hex_tile.pegs = [peg for peg in hex_tile.pegs if peg is not peg_to_remove]

    def hexes_touching_peg(self, peg: Peg):
        """Return all hexes touched by the peg's position."""
        # Example: vertex position between three hexes
        if peg.position:
            return [self.hexes[qr] for qr in peg.position if qr in self.hexes]
        return []

    def assign_rain_die_to_hex(self, die):
        for (q, r), hex_tile in self.hexes.items():
            if hex_tile.color == RAIN_COLOR and hex_tile.number == die.value:
                self.logger.info(f"ASSIGN {die.get_name()} to {hex_tile.get_name()}")
                hex_tile.dice.append(die)
                die.qr_location = (q, r)
                self.draw_board()
                return

        self.logger.info(f"ASSIGN {die.get_name()} to POOL")
        die.qr_location = None

    def add_rain_die(self):
        new_rain_die = Die(color='blue', value=1)
        new_rain_die.roll()
        self.rain_dice.append(new_rain_die)
        self.assign_rain_die_to_hex(die=new_rain_die)
        self.draw_board()

    def roll_rain_dice(self):
        for i, die in enumerate(self.rain_dice):
            self.logger.info(f'ROLL RAIN DIE {i}')
            die.roll()

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
