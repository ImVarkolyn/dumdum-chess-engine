import random
import time
import multiprocessing

# === AI config ===
set_depth = 5
max_time_per_move = 9.9  # Each move must be < 10s

# Positive values are good for white, negative for black
checkmate_points = 100000
stalemate_points = 0

piece_scores = {"P": 100, "N": 280, "B": 320, "R": 479, "Q": 929, "K": 60000}

piece_positions = {
    'wP': [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [78, 83, 86, 73, 102, 82, 85, 90],
        [7, 29, 21, 44, 40, 31, 44, 7],
        [-17, 16, -2, 15, 14, 0, 15, -13],
        [-26, 3, 10, 9, 6, 1, 0, -23],
        [-22, 9, 5, -11, -10, -2, 3, -19],
        [-31, 8, -7, -37, -36, -14, 3, -31],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ],

    'wN': [
        [-66, -53, -75, -75, -10, -55, -58, -70],
        [-3, -6, 100, -36, 4, 62, -4, -14],
        [10, 67, 1, 74, 73, 27, 62, -2],
        [24, 24, 45, 37, 33, 41, 25, 17],
        [-1, 5, 31, 21, 22, 35, 2, 0],
        [-18, 10, 13, 22, 18, 15, 11, -14],
        [-23, -15, 2, 0, 2, 0, -23, -20],
        [-74, -23, -26, -24, -19, -35, -22, -69]
    ],

    'wB': [
        [-59, -78, -82, -76, -23, -107, -37, -50],
        [-11, 20, 35, -42, -39, 31, 2, -22],
        [-9, 39, -32, 41, 52, -10, 28, -14],
        [25, 17, 20, 34, 26, 25, 15, 10],
        [13, 10, 17, 23, 17, 16, 0, 7],
        [14, 25, 24, 15, 8, 25, 20, 15],
        [19, 20, 11, 6, 7, 6, 20, 16],
        [-7, 2, -15, -12, -14, -15, -10, -10]
    ],

    'wR': [
        [35, 29, 33, 4, 37, 33, 56, 50],
        [55, 29, 56, 67, 55, 62, 34, 60],
        [19, 35, 28, 33, 45, 27, 25, 15],
        [0, 5, 16, 13, 18, -4, -9, -6],
        [-28, -35, -16, -21, -13, -29, -46, -30],
        [-42, -28, -42, -25, -25, -35, -26, -46],
        [-53, -38, -31, -26, -29, -43, -44, -53],
        [-30, -24, -18, 5, -2, -18, -31, -32]
    ],

    'wQ': [
        [6, 1, -8, -104, 69, 24, 88, 26],
        [14, 32, 60, -10, 20, 76, 57, 24],
        [-2, 43, 32, 60, 72, 63, 43, 2],
        [1, -16, 22, 17, 25, 20, -13, -6],
        [-14, -15, -2, -5, -1, -10, -20, -22],
        [-30, -6, -13, -11, -16, -11, -16, -27],
        [-36, -18, 0, -19, -15, -15, -21, -38],
        [-39, -30, -31, -13, -31, -36, -34, -42]
    ],

    'wK': [
        [4, 54, 47, -99, -99, 60, 83, -62],
        [-32, 10, 55, 56, 56, 55, 10, 3],
        [-62, 12, -57, 44, -67, 28, 37, -31],
        [-55, 50, 11, -4, -19, 13, 0, -49],
        [-55, -43, -52, -28, -51, -47, -8, -50],
        [-47, -42, -43, -79, -64, -32, -29, -32],
        [-4, 3, -14, -50, -57, -18, 13, 4],
        [17, 30, -3, -14, 6, -1, 40, 18]
    ],

    'bP': [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [-31, 8, -7, -37, -36, -14, 3, -31],
        [-22, 9, 5, -11, -10, -2, 3, -19],
        [-26, 3, 10, 9, 6, 1, 0, -23],
        [-17, 16, -2, 15, 14, 0, 15, -13],
        [7, 29, 21, 44, 40, 31, 44, 7],
        [78, 83, 86, 73, 102, 82, 85, 90],
        [0, 0, 0, 0, 0, 0, 0, 0]
    ],

    'bN': [
        [-74, -23, -26, -24, -19, -35, -22, -69],
        [-23, -15, 2, 0, 2, 0, -23, -20],
        [-18, 10, 13, 22, 18, 15, 11, -14],
        [-1, 5, 31, 21, 22, 35, 2, 0],
        [24, 24, 45, 37, 33, 41, 25, 17],
        [10, 67, 1, 74, 73, 27, 62, -2],
        [-3, -6, 100, -36, 4, 62, -4, -14],
        [-66, -53, -75, -75, -10, -55, -58, -70]
    ],

    'bB': [
        [-7, 2, -15, -12, -14, -15, -10, -10],
        [19, 20, 11, 6, 7, 6, 20, 16],
        [14, 25, 24, 15, 8, 25, 20, 15],
        [13, 10, 17, 23, 17, 16, 0, 7],
        [25, 17, 20, 34, 26, 25, 15, 10],
        [-9, 39, -32, 41, 52, -10, 28, -14],
        [-11, 20, 35, -42, -39, 31, 2, -22],
        [-59, -78, -82, -76, -23, -107, -37, -50]
    ],

    'bR': [
        [-30, -24, -18, 5, -2, -18, -31, -32],
        [-53, -38, -31, -26, -29, -43, -44, -53],
        [-42, -28, -42, -25, -25, -35, -26, -46],
        [-28, -35, -16, -21, -13, -29, -46, -30],
        [0, 5, 16, 13, 18, -4, -9, -6],
        [19, 35, 28, 33, 45, 27, 25, 15],
        [55, 29, 56, 67, 55, 62, 34, 60],
        [35, 29, 33, 4, 37, 33, 56, 50]
    ],

    'bQ': [
        [-39, -30, -31, -13, -31, -36, -34, -42],
        [-36, -18, 0, -19, -15, -15, -21, -38],
        [-30, -6, -13, -11, -16, -11, -16, -27],
        [-14, -15, -2, -5, -1, -10, -20, -22],
        [1, -16, 22, 17, 25, 20, -13, -6],
        [-2, 43, 32, 60, 72, 63, 43, 2],
        [14, 32, 60, -10, 20, 76, 57, 24],
        [6, 1, -8, -104, 69, 24, 88, 26]
    ],

    'bK': [
        [17, 30, -3, -14, 6, -1, 40, 18],
        [-4, 3, -14, -50, -57, -18, 13, 4],
        [-47, -42, -43, -79, -64, -32, -29, -32],
        [-55, -43, -52, -28, -51, -47, -8, -50],
        [-55, 50, 11, -4, -19, 13, 0, -49],
        [-62, 12, -57, 44, -67, 28, 37, -31],
        [-32, 10, 55, 56, 56, 55, 10, 3],
        [4, 54, 47, -99, -99, 60, 83, -62]
    ]

}

transposition_table = {}

def find_best_move(game_state, valid_moves, time_limit=max_time_per_move):
    global next_move
    next_move = None
    start = time.time()
    depth = 1
    last_depth = 0;
    while time.time() - start < time_limit and depth <= set_depth:
        find_negamax_move_alphabeta(game_state, valid_moves, depth, -checkmate_points, checkmate_points,
                                    1 if game_state.white_to_move else -1, start, time_limit)
        last_depth = depth
        depth += 1
    end = time.time()
    print(f"Move selected in {end - start:.2f} seconds at depth {last_depth}")
    return next_move

# def find_negamax_move_alphabeta(game_state, valid_moves, depth, alpha, beta, turn_multiplier, start_time, time_limit):
#     global next_move
#     if time.time() - start_time > time_limit:
#         return 0  # Abort if over time
#
#     board_key = str(game_state.board) + str(game_state.white_to_move)
#     if board_key in transposition_table and transposition_table[board_key]["depth"] >= depth:
#         return transposition_table[board_key]["score"]
#
#     if depth == 0:
#         return turn_multiplier * score_board(game_state)
#
#     max_score = -checkmate_points
#     ordered_moves = order_moves(valid_moves)
#     for move in ordered_moves:
#         game_state.make_move(move)
#         next_moves = game_state.get_valid_moves()
#         score = -find_negamax_move_alphabeta(game_state, next_moves, depth - 1, -beta, -alpha, -turn_multiplier,
#                                              start_time, time_limit)
#         game_state.undo_move()
#
#         if score > max_score:
#             max_score = score
#             if depth == set_depth:
#                 next_move = move
#
#         alpha = max(alpha, score)
#         if alpha >= beta:
#             break
#
#     transposition_table[board_key] = {"score": max_score, "depth": depth}
#     return max_score


# === NegaMax with Alpha-Beta + Transposition Table + Move Ordering ===
def find_negamax_move_alphabeta(game_state, valid_moves, depth, alpha, beta, turn_multiplier, start_time, time_limit):
    global next_move

    if time.time() - start_time > time_limit:
        return 0

    if depth == 0:
        return turn_multiplier * score_board(game_state)

    board_key = str(game_state.board) + str(game_state.white_to_move)
    if board_key in transposition_table and transposition_table[board_key]["depth"] >= depth:
        return transposition_table[board_key]["score"]

    # === Null Move Pruning ===
    if depth >= 3 and not game_state.in_check:
        null_state = game_state.clone()
        null_state.white_to_move = not null_state.white_to_move
        null_score = -find_negamax_move_alphabeta(
            null_state,
            null_state.get_valid_moves(),
            depth - 1 - 2,
            -beta,
            -beta + 1,
            -turn_multiplier,
            start_time,
            time_limit
        )
        if null_score >= beta:
            return beta

    max_score = -checkmate_points
    ordered_moves = order_moves(valid_moves)
    for move in ordered_moves:
        game_state.make_move(move)
        next_moves = game_state.get_valid_moves()
        score = -find_negamax_move_alphabeta(
            game_state, next_moves, depth - 1,
            -beta, -alpha, -turn_multiplier,
            start_time, time_limit
        )
        game_state.undo_move()

        if score > max_score:
            max_score = score
            if depth == set_depth:
                next_move = move

        alpha = max(alpha, score)
        if alpha >= beta:
            break

    transposition_table[board_key] = {"score": max_score, "depth": depth}
    return max_score




# === Move Ordering ===
def order_moves(moves):
    # Different from evaluation
    piece_order_values = {
        "P": 1,
        "N": 3,
        "B": 3,
        "R": 5,
        "Q": 9,
        "K": 0
    }

    def move_score(move):
        score = 0
        if move.piece_captured != "--":
            # MVV-LVA logic: 10 * victim value - attacker value
            victim_value = piece_order_values.get(move.piece_captured[1], 0)
            attacker_value = piece_order_values.get(move.piece_moved[1], 0)
            score += 10 * victim_value - attacker_value
        if move.is_promotion:
            score += 20  # Strong bonus for promotions
        return score

    return sorted(moves, key=move_score, reverse=True)



# === Evaluation Function ===
def score_board(game_state):
    if game_state.checkmate:
        return -checkmate_points if game_state.white_to_move else checkmate_points
    elif game_state.stalemate:
        return stalemate_points

    score = 0
    for row in range(len(game_state.board)):
        for col in range(len(game_state.board[row])):
            piece = game_state.board[row][col]
            if piece != "--":
                ps_key = piece
                if piece[0] == 'w':
                    score += piece_scores[piece[1]] + piece_positions[ps_key][row][col]
                else:
                    score -= piece_scores[piece[1]] + piece_positions[ps_key][row][col]
    return score


# === Utils ===
def find_random_move(valid_moves):
    return random.choice(valid_moves)


def get_piece_value(piece):
    return piece_scores.get(piece[1], 0)
