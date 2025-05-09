## Dumdum Chess Engine

## Project demo link: https://drive.google.com/file/d/1K8flc4QPWI9jAfE0_y3jHPiUFyr07mBW/view?usp=drive_web

## Overview
This personal project is a fully functional chess engine written in Python with graphical user interface. The engine is capable of playing legal chess games in standard format, supports rules such as castling, en passant and promotions.
The engine’s core functions are divided across three modules:
- ChessMain.py: Handles the game loop, user input and renders user interface
- ChessEngine.py: Manages the game state, generates valid moves for all pieces, accounting for pins, checks and special moves.
- ChessAI.py: Implements algorithms to evaluate positions and select moves for the AI.

## Progress and Features
- Graphical User Interface: Pygame library was used to provide a user-friendly interface with chess board and move log table.
- Side selection: From the start menu, you can choose to play as white (the AI will play as black) or as black (the AI will play as white).
  ![image](https://github.com/user-attachments/assets/84f95201-ae3a-4c66-949a-90d9a666b449)
- Standard Chess Rules: The engine handles all standard chess moves, including special moves such as castling, en passant and pawn promotion. It tracks game state (check, checkmate, stalemate, castle rights) and maintains move history

AI Move Selection: The AI, implemented in ChessAI.py, uses advanced algorithms to select moves within a 10s time limit:
- Negamax with Alpha-Beta Pruning: The core search algorithm which explores the game tree to a specified depth. Alpha-beta pruning reduces the number of nodes evaluated by cutting off branches that won’t affect the final decision.
- Move Ordering + MVV-LVA (Most Valuable Victim, Least Valuable Attacker): Prioritizes captures of high-value pieces by low-value attackers.
- Transposition Table: Stores previously evaluated positions to avoid redundant calculations
- Null Move Pruning: Reduces search depth in non-critical positions by assuming the opponent can skip a move
- Evaluation Function: Combines material balance with piece-square tables to favor strategic piece placement.

## Notes
- Press `r` to restart the game.

## Improvements to be made
- Improve board representation from 2D to bitboards for faster move generation.
- Add opening book to reduce unecessary search time for the first few moves
- Further optimize AI's search and evaluation functions



