import logging
import random
from collections import defaultdict
from peg_board import GameBoard


LOGGER = logging.getLogger(__name__)


def play_phase_logic(board: GameBoard):
    LOGGER.info("PLAY phase triggered.")
    # for tile in board.hexes.values():
    #     if tile.dice:
    #         tile.dice.pop(0)

    # todo movement
    board.roll_rain_dice()


def eat_phase_logic(board):
    LOGGER.info("EAT phase triggered.")
    board.eat_scores = defaultdict(int)
    for color, dice_list in board.food_dice_pile.items():
        for face in dice_list:
            candidates = [tile for tile in board.hexes.values()
                          if tile.color == color and tile.number == face]
            if candidates:
                chosen = random.choice(candidates)
                chosen.dice.append(face)
    for tile in board.hexes.values():
        for peg in tile.pegs:
            for die in tile.dice:
                if tile.color in ['yellow', 'green'] and die == tile.number:
                    board.eat_scores[peg.player] += peg.size
    LOGGER.info("EAT scores:", dict(board.eat_scores))
    board.draw_board()

def grow_phase_logic(board):
    LOGGER.info("GROW phase triggered.")
    board.growth_die = random.randint(1, 6)
    LOGGER.info("Growth Die:", board.growth_die)
    for tile in board.hexes.values():
        die_counts = defaultdict(int)
        for die in tile.dice:
            die_counts[die] += 1
        for peg in tile.pegs:
            grew = False
            for die, count in die_counts.items():
                if count > 1 or die == board.growth_die:
                    if peg.size < 8:
                        peg.size *= 2
                    grew = True
                    break
            if grew:
                LOGGER.info(f"{peg.player} peg grew to size {peg.size} at {tile.coords()}")
    board.draw_board()