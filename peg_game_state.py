# from typing import Optional
# from peg_board import GameBoard
from peg_pieces import Peg, Die, HEX_COLORS, RAIN_COLOR
import logging
from functools import partial


class Player:
    def __init__(self, board, color, name=None, n_pegs=20, n_rain_dice=1, n_food_dice=6):
        self.board = board
        self.color = color
        self.name = name
        self.pegs = [Peg(color=color, size=1, position=None, board=self.board) for _ in range(n_pegs)]
        self.food_dice = [Die(color=self.color, board=self.board) for _ in range(n_food_dice)]
        self.rain_dice = [Die(color='blue', board=self.board) for _ in range(n_rain_dice)]
        self.eat_score = 0    # Most recent EAT score

    def get_dice(self):
        return [*self.rain_dice, *self.food_dice]

    def get_pegs(self):
        return self.pegs


class GameState:
    """MODEL: The authoritative source of truth for what is happening in the game"""

    PHASE_SETUP = 'setup'
    PHASE_PLANT = 'plant'
    PHASE_EAT = 'eat'
    PHASE_GROW = 'grow'

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.board = None
        self.players = {}  # {'color': Player instance}
        self.current_round = 0
        self.phase = self.PHASE_SETUP
        self._plant_selection_queue = []  # (color, die, valid_hexes)

    def add_all_players(self):
        for color in HEX_COLORS:
            if color != RAIN_COLOR:
                self.add_player(color=color)

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

    def place_die(self, die, position):

        original_position = die.position
        if original_position is not None:
            original_hex_tile = self.board.hexes[original_position]
            original_hex_tile.dice.remove(die)

        die.position = position

        if position is not None:
            target_hex_tile = self.board.hexes[position]
            target_hex_tile.dice.append(die)

    def clear_dice_off_board(self):
        for color, player in self.players.items():
            for die in player.get_dice():
                self.place_die(die=die, position=None)

    def run_plant_phase(self):
        """Roll rain & food dice, place dice that have 0 or 1 valid spot immediately,
           queue dice with multiple valid spots for interactive placement (one-by-one)."""
        self.logger.info('RUN PLANT PHASE')
        self.phase = self.PHASE_PLANT

        # We'll gather ambiguous dice across all players and then start interactive placement.
        self.clear_dice_off_board()
        selection_queue = []  # list of tuples: (player_color, die, valid_hexes)

        for color, player in self.players.items():
            self.logger.debug(f'PLAYER {color}')
            dice_to_place_on_board = []

            # --- Rain dice (roll & append) ---
            n_food_dice = 0
            for rain_die in player.rain_dice:
                self.logger.debug(f'{color} ROLLING RAIN DIE...')
                rain_die.reroll()
                value = rain_die.value
                self.logger.info(f'{color} RAIN DIE = {value}')
                n_food_dice += value
                dice_to_place_on_board.append(rain_die)

            # --- Food dice (roll as allowed, else put out of play) ---
            for n, food_die in enumerate(player.food_dice):
                if n < n_food_dice:
                    self.logger.debug(f'{color} ROLLING FOOD DIE...')
                    food_die.reroll()
                    self.logger.info(f'{color} FOOD DIE = {food_die.value}')
                    dice_to_place_on_board.append(food_die)
                else:
                    self.logger.debug(f'{color} SETTING FOOD DIE OUT OF PLAY')
                    food_die.position = None

            # --- Evaluate placement options for this player's dice ---
            for die in dice_to_place_on_board:
                # compute valid hexes for this die
                valid_hexes = []
                for (q, r), hex_tile in self.board.hexes.items():
                    if (str(die.color).upper() == str(hex_tile.color).upper() and
                            int(die.value) == int(hex_tile.number)):
                        valid_hexes.append((q, r))

                self.logger.info(f'{color} VALID HEXES for {die}: {len(valid_hexes)}')

                if not valid_hexes:
                    # no place — mark out of play
                    self.logger.info(f'{color} - NO SPOT FOR {die}')
                    self.place_die(die=die, position=None)
                    die.value = 'X'

                elif len(valid_hexes) == 1:
                    # deterministic placement
                    self.logger.debug(f'{color} - PLACING {die} on {die.position}')
                    self.place_die(die=die, position=valid_hexes[0])
                    self.logger.info(f'{color} PLACED {die} on {die.position}')

                else:
                    # ambiguous: queue for interactive placement (do NOT enter selection mode here)
                    self.logger.info(f'{color} - MULTIPLE OPTIONS for {die}, QUEUING FOR SELECTION')
                    selection_queue.append((color, die, valid_hexes))

        # If any dice need selection, start the interactive sequence (one-by-one).
        if selection_queue:
            # store queue state on self so handlers can advance it
            self._plant_selection_queue = selection_queue
            self._start_next_plant_selection()
        else:
            self.logger.info('PLANT PHASE complete: no interactive placements required.')

    def _start_next_plant_selection(self):
        """Internal helper to begin selection for the next queued die (if any)."""
        if not hasattr(self, "_plant_selection_queue"):
            self.logger.debug(f'No _plant_selection_queue, skipping plant selection.')
            return

        if len(self._plant_selection_queue) == 0:
            # done
            self.logger.info('PLANT SELECTION QUEUE COMPLETE')
            # ensure board clears selection/highlights
            try:
                self.board.exit_selection_mode('QUEUE COMPLETE')
            except Exception:
                pass

            return

        # use pop to take out of list
        color, die, valid_hexes = self._plant_selection_queue.pop(0)
        self.logger.info(f'Waiting for user to place {die} (player {color}) — options: {valid_hexes}')

        # # Ensure board shows only this die's possible hexes
        # # Clear previous highlights/selections first
        # try:
        #     self.board.exit_selection_mode('EXIT BEFORE ENTERING')
        # except Exception:
        #     pass

        self.board.enter_selection_mode(color, die, valid_hexes)

        # Disconnect any existing slot so we don't stack handlers
        try:
            self.board.user_selected_hex.disconnect()
        except Exception:
            # disconnect may raise if nothing connected; ignore
            pass

        # Connect a handler bound to this die. When the user clicks, _on_plant_hex_selected will run.
        self.board.user_selected_hex.connect(partial(self._on_plant_hex_selected, die))

    def _on_plant_hex_selected(self, die, hex_pos):
        """Signal handler called when user selects a hex for the currently-active die."""
        self.logger.info(f'User selected {hex_pos} for {die}')
        # Put the die on the board
        self.place_die(die=die, position=hex_pos)
        self.logger.info(f'Placed {die} on {die.position}')

        # Clear this die's highlights and disconnect this handler
        try:
            self.board.exit_selection_mode('EXIT AFTER SELECTION')
        except Exception:
            pass

        try:
            self.board.user_selected_hex.disconnect()
        except Exception:
            pass

        # Advance to the next queued die (if any)
        self._start_next_plant_selection()

    def on_die_placement_selected(self, die, hex_pos):
        die.position = hex_pos
        self.board.draw_board()

    def run_eat_phase(self):
        self.logger.info(f'RUN EAT PHASE')
        pass

    def run_grow_phase(self):
        self.logger.info(f'RUN GROW PHASE')
        pass
