# from typing import Optional
# from peg_board import GameBoard
from peg_pieces import Peg, Die
import logging


class Player:
    def __init__(self, board, color, name=None, n_pegs=0, n_rain_dice=1, n_food_dice=6):
        self.board = board
        self.color = color
        self.name = name
        self.pegs = [Peg(color=color, size=1, position=None, board=self.board)] * n_pegs
        self.food_dice = [Die(color=self.color, board=self.board)] * n_food_dice
        self.rain_dice = [Die(color='blue', board=self.board)] * n_rain_dice
        self.eat_score = 0    # Most recent EAT score

    def get_dice(self):
        return [*self.rain_dice, *self.food_dice]

    def get_pegs(self):
        return self.pegs


class GameState:

    PHASE_SANDBOX = 'sandbox'
    PHASE_PLAY = 'play'
    PHASE_EAT = 'eat'
    PHASE_GROW = 'grow'

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.board = None
        self.players = {}  # {'color': Player instance}
        self.current_round = 0
        self.phase = self.PHASE_SANDBOX
        self.growth_die = None
        # more game state fields...

    def add_player(self, color, name=None):
        if color in self.players:
            self.logger.error(f'IGNORING PLAYER COLOR ALREADY ACTIVE: {color}')
            player = None
        else:
            self.logger.info(f'ADD PLAYER ({color})')
            player = Player(board=self.board, color=color, name=name)
            self.players[color] = player
        return player

    def remove_player(self, color):
        player = self.players.pop(color, None)
        self.logger.info(f'REMOVED PLAYER {player}')
        return player
