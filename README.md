# PEG rulebook

## Overview

PEG (Plant, Eat, Grow) is a fast-paced, spatial strategy game where players compete to expand their network of pegs 
on a shared hexagonal board.

Each round, food is planted randomly across the map using dice. 
Players eat this food by pulling dice into their hands, 
then spend those dice to grow—either 
by placing new pegs or moving existing ones.

There's no scoreboard—instead, victory goes to the first player to place all of their pegs onto the board. 
PEG rewards smart positioning and adaptive strategy, 
but with enough luck involved, 
no one's ever fully out of the game.

## Components

![](https://t8575567.p.clickup-attachments.com/t8575567/14c1e714-b8cf-4720-aaa1-0d87e650683b/1000016727.jpg)

*   PEG board
*   Rain Dice (one blue D6 per player)
*   Food Dice (six D6s in each player color)
*   Pegs in player colors

## Setup

*   Configure board hexes for number of players and game style
*   Place 2 starting pegs per player
*   Roll to determine starting PEG order

## Game Phases

### P: PLANT Phase

(ALL)
*   Roll RAIN DIE (blue)
    * Face value = number of FOOD DICE to roll
*   Roll FOOD DICE (matching player color)
*   Place rolled dice onto board hex matching color and face value
    *   Players can choose between multiple options in some cases
    * Not all rain die face values have a place on the board
*   Push all unused dice against board to show they are not in play this round

### E: EAT Phase

(ALL)
* Pull dice from hexes which are uncontested (only one player has adjacent pegs) into that player's hand

Note:
* Players can pull dice of any color (not limited to eating own color)
* Do not change the face values when pulling dice off the board into hand

(IN PEG ORDER)
* Pull dice off of a single adjacent hex into hand
  * Hex must be adjacent to player's peg(s)
  * Dice limit per turn = number of pegs touching hex
* Continue until all reachable dice have been pulled by all players

(ALL)
*   Update PEG order based on dice in hand
    *   Least dice = first in PEG order
    *   Most dice = last in PEG order
    *   Same number of dice = maintain relative PEG order

### G: GROW Phase

(ALL) 
* Option to reroll any dice in hand once.

(IN ORDER)

* Choose one option:

  1. Spend matching dice to place new pegs on the board (see table below)
      * Pegs must be placed adjacent to existing pegs
  2.  Spend any number of dice to move pegs already on the board
      * Sum of die faces = movement range (number of peg holes)
      * Range can be shared between multiple pegs
      * Hopping over pegs is allowed, but costs a movement like a peg hole

| **DICE (6s = WILD)**                | **PEGS** |
|-------------------------------------|----------|
| Single 6 or Any Pair                | +1       |
| Pair of 6s or Any Triple            | +2       |
| Triple 6s or Any Quad (4-of-a-kind) | +3       |
| Quad 6s or Any Quint (5-of-a-kind)  | +4       |
| Quint 6s or Any Sext (6-of-a-kind)  | +5       |
| Sext 6s                             | +6       |

## Winning the Game

The first player to place all their pegs on the board wins!

## Optional Tweaks and Variants

### No hopping
* Players are not allowed to jump pegs over other pegs

### Free hopping
* Hopping over pegs costs no movement range

### Sized pegs
*   Pegs start at size = 1
*   Growth can either add a new peg of the same size or double the size of a peg
*   \[EAT\] Size determines the number of dice that can be pulled from a hex per turn
*   \[GROW\] Size determines peg range and pegs can only hop over other pegs of equal size or smaller.