# PEG — Map Maker and Simulator

**PEG** is a fast-paced, chaotic yet strategic board game where players compete to expand and evolve their population 
of pegs across a shared hexagonal world. This repository provides a fully editable **simulation GUI** 
to design maps, run PEG phases, test game balance, and playtest solo or with others.

> 🧠 PEG = **Play — Eat — Grow**, the three core phases of each round. 

---

## 🎮 Game Overview

- **PLAY**: Players place and move pegs on the hex grid of a shared PEG board
- **EAT**: Food dice are rolled and placed on their matching hex for the adjacent pegs
- **GROW**: Hexes with more than one die allow adjacent pegs to double in size or quantity
- Pegs are moved by pulling dice off of adjacent hexes
- The first player to grow and play all their pegs wins
- The game is a mix of **tactical movement**, **dice-based chaos**, and **territorial control**

---

## 🧩 Components

-  **PEG game board** with peg holes in a hexagonal grid
- 🟢🟡🔵**Hex markers** matching die color and faces
- 🟢🟡 **Pegs** in player colors, either stackable or sized (1, 2, 4, 8)
- 💧🎲 **Rain Dice**: decide food supply each round
- 🌽🎲 **Food Dice**: determine where food appears on the map
- 🌱🎲 **Growth Die** (variant): determines which food face allows pegs to grow

---

## 🎲 Setup

- Place PEG board within reach of all players
- Arrange hex markers around board to form the map
  - Map based on player count and balance preference
  - Center hex should be water/blue
- Agree on **number of available pegs** per player
- Agree on **win condition**
  - Simple: first player to play all of their pegs wins
- Each player places **TWO** pegs (size = 1) touching any hex matching their color
- Roll to determine initial PEG order (lower = first) and update board tracker

---

## 🔁 Phases of Play: “P.E.G.”

### P — PLAY Phase
- Each player: 
  - **ROLL** one rain die
  - **PLACE** # of **food dice** matching the rain die face into a **food dice pool** beside the board
  - **PLACE** the rain die onto its matching **water hex** (blue)
- *Variant: If two or more rain dice match, move them to the central water hex*
- In PEG order, each player may:
  - **PULL** one die adjacent to one of their pegs off the board to **MOVE** the peg
  - Peg must remain on corners (or edges) if starting from a corner (or edge)
  - Movement **range** is limited to the **peg size**
  - Can jump over pegs of equal size or smaller (i.e. cannot jump over bigger pegs)

### E — EAT Phase
- Each player:
  - **ROLL** all dice in the **food dice pool** created in the previous phase
  - **PLACE** each food die on the matching hex (based on color and face value)
- **EAT SCORE** = total number of dice touched by each player's pegs on the board
- **UPDATE** PEG order tracker: low EAT score (first) → high EAT score (last)
  - Roll to break ties (lower = first)

### G — GROW Phase

- In PEG order, each player may:
  - **GRAB** one peg adjacent to any growth hex:
    - A hex with more than one die on it
    - *Variant: A hex with a die face matching the growth die*
  - **CHOOSE** one growth type for the peg:
    - **2x SIZE**: replace with a peg double the size
    - **2x QUANTITY**: add another peg matching the peg pulled
  - **PLACE** the grown peg(s) **on top of** the growth hex, but not in the peg holes (yet)
    - Peg hole limit: If the hex is full (pegs around + on top of the hex = **12**), must choose **SIZE** growth
    - *Variant: no peg hole limit, pegs are removed when growth is resolved if there is not enough room*
- Once all eligible pegs have been pulled, in PEG order:
  - **PLACE** own peg on top of hex into any empty peg hole around the hex
  - *Note: the origin of the peg does not matter: a previous edge peg can be placed on a corner and vice versa.*

---

## 🎯 Victory Condition


- Standard: First to **place all their pegs on the board** wins the game
  - No traditional scoring — board presence is the only score
  - Players agree on the amount of pegs during setup
- Variants:
  - Reach certain **EAT score** (number of dice touched in the EAT phase)
  - Largest **EAT score** on round X
  - First player to touch every die on the board at the end of the EAT phase (max EAT score)

---

## 🛠️ Simulation GUI Features

This project includes a PyQt-based simulation interface to test and tune PEG:

### ✨ Core Features

- 🧱 **Editable hex map** with double-click to cycle colors and scroll to change numbers.
- 🔘 **Drag-and-drop pegs** in sandbox mode — fully editable layout and size.
- 📦 **Interactive dice pool** — food dice are placed visually on hexes.
- 🧠 **Phase Buttons** — run the full PEG loop with logic wired to the board state.
- 🧭 **corner/Edge Placement** — pegs snap to legal positions reflecting eaters/hunters.
- 📈 Future features include strategy testing, AI opponents, and statistical balance reports.

### 🧪 Developer Tools

- `sandbox_mode`: freely edit the board, move pieces, change die values, and test.
- Built-in `GameBoard`, `HexTile`, `Peg`, and `Die` classes for clear modularity.
- Easily extend PEG mechanics, GUI logic, or test hooks via plug-and-play architecture.

---

## 🤝 Design Philosophy

> PEG is designed to feel like an ecosystem: dynamic, unpredictable, and surprisingly competitive.

- 🎲 **Dice-driven chaos** with enough strategy to reward clever play.
- 🐦 **Ecosystem asymmetry** — grow big or spread wide, block or leap.
- 👨‍👩‍👧‍👦 **Bar-friendly fun** — low downtime, high replayability, lots of laughing at the rolls.

---

## 📸 Screenshots & Dev Notes

_coming soon!_

---

## 🧪 Getting Started (Developers)

```bash
pip install PyQt6
python peg_main.py
