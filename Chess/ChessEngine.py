from Chess import ChessMain


class GameState:

    def __init__(self):
        # === BOARD REPRESENTATION ===
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bP'] * 8,
            ['--'] * 8,
            ['--'] * 8,
            ['--'] * 8,
            ['--'] * 8,
            ['wP'] * 8,
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
        ]
        self.move_functions = {'P': self.get_pawn_moves, 'R': self.get_rook_moves, 'N': self.get_knight_moves,
                               'B': self.get_bishop_moves, 'Q': self.get_queen_moves, 'K': self.get_king_moves}
        self.white_to_move = True
        self.move_log = []
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.in_check = False
        self.pins = []
        self.checks = []

        # En passant
        self.en_passant_possible = ()  # Coordinates for square where en passant possible
        self.en_passant_possible_log = [self.en_passant_possible]

        # Castling
        self.white_castle_king_side = True
        self.white_castle_queen_side = True
        self.black_castle_king_side = True
        self.black_castle_queen_side = True
        self.castle_rights_log = [CastleRights(self.white_castle_king_side, self.black_castle_king_side,
                                               self.white_castle_queen_side, self.black_castle_queen_side)]

    def make_move(self, move):
        """Takes a move as a parameter, executes it, and updates move log"""
        global promoted_piece

        self.board[move.start_row][move.start_col] = '--'  # When a piece is moved, the square it leaves is blank
        self.board[move.end_row][move.end_col] = move.piece_moved  # Moves piece to new location
        self.move_log.append(move)  # Logs move

        if move.piece_moved == 'wK':
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == 'bK':
            self.black_king_location = (move.end_row, move.end_col)

        # Pawn promotion
        if move.is_promotion:

            # Player turn
            if (self.white_to_move and ChessMain.player_one) or (not self.white_to_move and ChessMain.player_two):
                promoted_piece = input('Promote to Q(ueen), R(ook), B(ishop), or (k)N(ight):').upper()

            else:  # AI turn
                promoted_piece = 'Q'

            self.board[move.end_row][move.end_col] = move.piece_moved[0] + promoted_piece

        # En passant
        if move.is_en_passant:
            self.board[move.start_row][move.end_col] = '--'  # Capturing the pawn

        # Updates the en_passant_possible variable
        if move.piece_moved[1] == 'P' and abs(move.start_row - move.end_row) == 2:  # Only valid for 2 square pawn moves
            self.en_passant_possible = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            self.en_passant_possible = ()

        self.en_passant_possible_log.append(self.en_passant_possible)

        # Castling
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:  # King side castle
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][
                    move.end_col + 1]  # Moves rook
                self.board[move.end_row][move.end_col + 1] = '--'  # Erases old rook
            else:  # Queen side castle
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][
                    move.end_col - 2]  # Moves rook
                self.board[move.end_row][move.end_col - 2] = '--'  # Erases old rook

        # Updates castling rights
        self.update_castle_rights(move)
        self.castle_rights_log.append(CastleRights(self.white_castle_king_side, self.black_castle_king_side,
                                                   self.white_castle_queen_side, self.black_castle_queen_side))

        self.white_to_move = not self.white_to_move  # Switches turns

    def undo_move(self):
        """Undos last move made"""
        if len(self.move_log) != 0:  # Makes sure that there is a move to undo
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move  # Switches turn back

            # Updates king positions
            if move.piece_moved == 'wK':
                self.white_king_location = (move.start_row, move.start_col)
            elif move.piece_moved == 'bK':
                self.black_king_location = (move.start_row, move.start_col)

            # En passant
            if move.is_en_passant:
                self.board[move.end_row][move.end_col] = '--'  # Leaves landing square blank
                self.board[move.start_row][move.end_col] = move.piece_captured  # Allows en passant on the next move
            self.en_passant_possible_log.pop()
            self.en_passant_possible = self.en_passant_possible_log[-1]

            # Castling rights
            self.castle_rights_log.pop()  # Gets rid of new castle rights from move undoing
            castle_rights = self.castle_rights_log[-1]
            self.white_castle_king_side = castle_rights.white_king_side
            self.black_castle_king_side = castle_rights.black_king_side
            self.white_castle_queen_side = castle_rights.white_queen_side
            self.black_castle_queen_side = castle_rights.black_queen_side

            # Castling
            if move.is_castle_move:
                if move.end_col - move.start_col == 2:  # King side
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                    self.board[move.end_row][move.end_col - 1] = '--'
                else:  # Queen side
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = '--'

            self.checkmate = False
            self.stalemate = False

    def get_valid_moves(self):
        """Gets all moves considering checks"""
        valid_moves = []
        self.in_check, self.pins, self.checks = self.check_for_pins_and_checks()

        # Updates king locations
        if self.white_to_move:
            king_row, king_col = self.white_king_location[0], self.white_king_location[1]
        else:
            king_row, king_col = self.black_king_location[0], self.black_king_location[1]

        if self.in_check:
            if len(self.checks) == 1:  # Only 1 check: block check or move king
                valid_moves = self.get_all_possible_moves()
                check = self.checks[0]
                check_row, check_col = check[0], check[1]
                piece_checking = self.board[check_row][check_col]  # Enemy piece causing check
                valid_squares = []
                if piece_checking == 'N':
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, len(self.board)):
                        valid_square = (king_row + check[2] * i, king_col + check[3] * i)  # 2 & 3 = check directions
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col:
                            break
                for i in range(len(valid_moves) - 1, -1, -1):  # Gets rid of move not blocking, checking, or moving king
                    if valid_moves[i].piece_moved[1] != 'K':
                        if not (valid_moves[i].end_row, valid_moves[i].end_col) in valid_squares:
                            valid_moves.remove(valid_moves[i])
            else:  # Double check, king must move
                self.get_king_moves(king_row, king_col, valid_moves)
        else:  # Not in check
            valid_moves = self.get_all_possible_moves()

        if len(valid_moves) == 0:  # Either checkmate or stalemate
            if self.in_check:
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        return valid_moves

    def get_all_possible_moves(self):
        """Gets all moves without considering checks"""
        moves = []
        for row in range(len(self.board)):  # Number of rows
            for col in range(len(self.board[row])):  # Number of cols in each row
                turn = self.board[row][col][0]
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[row][col][1]
                    self.move_functions[piece](row, col, moves)  # Calls move function based on piece type
        return moves

    def get_pawn_moves(self, row, col, moves):
        """Gets all pawn moves for the pawn located at (row, col) and adds moves to move log"""
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.white_to_move:
            move_amount = -1
            start_row = 6
            back_row = 0
            opponent = 'b'
            king_row, king_col = self.white_king_location
        else:
            move_amount = 1
            start_row = 1
            back_row = 7
            opponent = 'w'
            king_row, king_col = self.black_king_location
        pawn_promotion = False

        if self.board[row + move_amount][col] == '--':  # 1 square move
            if not piece_pinned or pin_direction == (move_amount, 0):
                if row + move_amount == back_row:  # If piece gets to back rank, it is a pawn promotion
                    pawn_promotion = True
                moves.append(
                    Move((row, col), (row + move_amount, col), self.board, pawn_promotion=pawn_promotion))
                if row == start_row and self.board[row + 2 * move_amount][col] == '--':  # 2 square advance
                    moves.append(Move((row, col), (row + 2 * move_amount, col), self.board))
        if col - 1 >= 0:  # Captures left
            if not piece_pinned or pin_direction == (move_amount, -1):
                if self.board[row + move_amount][col - 1][0] == opponent:
                    if (row + move_amount == 0 and self.white_to_move) or (row + move_amount == 7 and not self.white_to_move):  # If piece gets to back rank, it is a pawn promotion
                        pawn_promotion = True
                    moves.append(Move((row, col), (row + move_amount, col - 1),
                                      self.board, pawn_promotion=pawn_promotion))
                if (row + move_amount, col - 1) == self.en_passant_possible:
                    attacking_piece = blocking_piece = False
                    if king_row == row:
                        if king_col < col:  # King is left of pawn
                            # inside_range between king and pawn; outside_range between pawn and border
                            inside_range = range(king_col + 1, col - 1)
                            outside_range = range(col + 1, len(self.board))
                        else:  # King is right of pawn
                            inside_range = range(king_col - 1, col, -1)
                            outside_range = range(col - 2, -1, -1)
                        for i in inside_range:
                            if self.board[row][i] != '--':
                                blocking_piece = True
                        for i in outside_range:
                            square = self.board[row][i]
                            if square[0] == opponent and (square[1] == 'R' or square[1] == 'Q'):
                                attacking_piece = True
                            elif square != '--':
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((row, col), (row + move_amount, col - 1), self.board, en_passant=True))
        if col + 1 <= len(self.board) - 1:  # Captures right
            if not piece_pinned or pin_direction == (move_amount, 1):
                if self.board[row + move_amount][col + 1][0] == opponent:
                    if row + move_amount == back_row:  # If piece gets to back rank, it is a pawn promotion
                        pawn_promotion = True
                    moves.append(Move((row, col), (row + move_amount, col + 1),
                                      self.board, pawn_promotion=pawn_promotion))
                if (row + move_amount, col + 1) == self.en_passant_possible:
                    attacking_piece = blocking_piece = False
                    if king_row == row:
                        if king_col < col:  # King is left of pawn
                            # inside_range between king and pawn; outside_range between pawn and border
                            inside_range = range(king_col + 1, col)
                            outside_range = range(col + 2, len(self.board))
                        else:  # King is right of pawn
                            inside_range = range(king_col - 1, col + 1, -1)
                            outside_range = range(col - 1, -1, -1)
                        for i in inside_range:
                            if self.board[row][i] != '--':
                                blocking_piece = True
                        for i in outside_range:
                            square = self.board[row][i]
                            if square[0] == opponent and (square[1] == 'R' or square[1] == 'Q'):
                                attacking_piece = True
                            elif square != '--':
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((row, col), (row + move_amount, col + 1), self.board, en_passant=True))

    def get_rook_moves(self, row, col, moves):
        """Gets all rook moves for the rook located at (row, col) and adds moves to move log"""
        opponent = 'b' if self.white_to_move else 'w'

        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[row][col][1] != 'Q':  # Can't remove queen from pin on rook moves (only bishop moves)
                    self.pins.remove(self.pins[i])
                break

        directions = [(-1, 0), (0, -1), (1, 0), (0, 1)]  # Tuples indicate (row, col) movements possible
        for d in directions:
            for i in range(1, len(self.board)):
                end_row = row + d[0] * i  # Potentially moves up/down to 7 rows
                end_col = col + d[1] * i  # Potentially moves up/down to 7 cols
                if 0 <= end_row < len(self.board) and 0 <= end_col < len(self.board):  # Makes sure on the board
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == '--':  # Valid move to empty space
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                        elif end_piece[0] == opponent:  # Valid move to capture
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                            break
                        else:  # Cannot take friendly piece
                            break
                else:  # Cannot move off board
                    break

    def get_knight_moves(self, row, col, moves):
        """Gets all knight moves for the knight located at (row, col) and adds moves to move log"""
        opponent = 'b' if self.white_to_move else 'w'

        piece_pinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break

        # Tuples indicate (row, col) movements possible
        directions = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]

        for d in directions:
            end_row = row + d[0]
            end_col = col + d[1]
            if 0 <= end_row < len(self.board) and 0 <= end_col < len(self.board):  # Makes sure on the board
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == opponent:  # Valid move to capture
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                    elif end_piece == '--':  # Valid move to empty space
                        moves.append(Move((row, col), (end_row, end_col), self.board))

    def get_bishop_moves(self, row, col, moves):
        """Gets all bishop moves for the bishop located at (row, col) and adds moves to move log"""
        opponent = 'b' if self.white_to_move else 'w'

        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = [(-1, -1), (-1, 1), (1, 1), (1, -1)]  # Tuples indicate (row, col) movements possible
        for d in directions:
            for i in range(1, len(self.board)):

                # See get_rook_moves for explanation; same here but for diagonals
                end_row = row + d[0] * i
                end_col = col + d[1] * i

                if 0 <= end_row < len(self.board) and 0 <= end_col < len(self.board):  # Makes sure on the board
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == '--':  # Valid move to empty space
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                        elif end_piece[0] == opponent:  # Valid move to capture
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                            break
                        else:  # Cannot take friendly piece
                            break
                else:  # Cannot move off board
                    break

    def get_queen_moves(self, row, col, moves):
        """Gets all queen moves for the queen located at (row, col) and adds moves to move log"""
        self.get_bishop_moves(row, col, moves)
        self.get_rook_moves(row, col, moves)

    def get_king_moves(self, row, col, moves):
        """Gets all king moves for the king located at (row, col) and adds moves to move log"""
        ally = 'w' if self.white_to_move else 'b'
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        for i in range(len(self.board)):
            end_row = row + row_moves[i]
            end_col = col + col_moves[i]
            if 0 <= end_row < len(self.board) and 0 <= end_col < len(self.board):  # Makes sure on the board
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally:  # Empty or enemy piece

                    # Places king on end square and checks for checks
                    if ally == 'w':
                        self.white_king_location = (end_row, end_col)
                    else:
                        self.black_king_location = (end_row, end_col)
                    in_check, pins, checks = self.check_for_pins_and_checks()
                    if not in_check:
                        moves.append(Move((row, col), (end_row, end_col), self.board))

                    # Places king back on original location
                    if ally == 'w':
                        self.white_king_location = (row, col)
                    else:
                        self.black_king_location = (row, col)
        self.get_castle_moves(row, col, moves, ally)

    def get_castle_moves(self, row, col, moves, ally):
        """
        Generates all valid castle moves for the king at (row, col).
        Adds valid castle moves to the list of moves.
        """
        if self.square_under_attack(row, col, ally):
            return  # Can't castle while in check
        if (self.white_to_move and self.white_castle_king_side) or \
                (not self.white_to_move and self.black_castle_king_side):
            self.get_king_side_castle_moves(row, col, moves, ally)
        if (self.white_to_move and self.white_castle_queen_side) or \
                (not self.white_to_move and self.black_castle_queen_side):
            self.get_queen_side_castle_moves(row, col, moves, ally)

    def get_king_side_castle_moves(self, row, col, moves, ally):
        if self.board[row][col + 1] == '--' and self.board[row][col + 2] == '--' and \
                not self.square_under_attack(row, col + 1, ally) and not self.square_under_attack(row, col + 2,
                                                                                                     ally):
            moves.append(Move((row, col), (row, col + 2), self.board, castle=True))

    def get_queen_side_castle_moves(self, row, col, moves, ally):
        if self.board[row][col - 1] == '--' and self.board[row][col - 2] == '--' and \
                self.board[row][col - 3] == '--' and not self.square_under_attack(row, col - 1, ally) and \
                not self.square_under_attack(row, col - 2, ally):
            moves.append(Move((row, col), (row, col - 2), self.board, castle=True))

    def update_castle_rights(self, move):
        """Updates castle rights given the move"""

        # If king or rook moved
        if move.piece_moved == 'wK':
            self.white_castle_queen_side = False
            self.white_castle_king_side = False
        elif move.piece_moved == 'bK':
            self.black_castle_queen_side = False
            self.black_castle_king_side = False
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 7:
                    self.white_castle_king_side = False
                elif move.start_col == 0:
                    self.white_castle_queen_side = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 7:
                    self.black_castle_king_side = False
                elif move.start_col == 0:
                    self.black_castle_queen_side = False

        # If rook is captured
        if move.piece_captured == 'wR':
            if move.end_row == 7:
                if move.end_col == 0:
                    self.white_castle_queen_side = False
                elif move.end_col == 7:
                    self.white_castle_king_side = False
        elif move.piece_captured == 'bR':
            if move.end_row == 0:
                if move.end_col == 0:
                    self.black_castle_queen_side = False
                elif move.end_col == 7:
                    self.black_castle_king_side = False

    def square_under_attack(self, row, col, ally):
        """Checks outward from a square to see if it is being attacked, thus invalidating castling"""
        opponent = 'b' if self.white_to_move else 'w'
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            for i in range(1, len(self.board)):
                end_row = row + d[0] * i
                end_col = col + d[1] * i
                if 0 <= end_row < len(self.board) and 0 <= end_col < len(self.board):
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally:  # no attack from that direction
                        break
                    elif end_piece[0] == opponent:
                        piece_type = end_piece[1]
                        if (0 <= j <= 3 and piece_type == 'R') or (4 <= j <= 7 and piece_type == 'B') or \
                                (i == 1 and piece_type == 'P' and ((opponent == 'w' and 6 <= j <= 7)
                                                                   or (opponent == 'b' and 4 <= j <= 5))) or \
                                (piece_type == 'Q') or (i == 1 and piece_type == 'K'):
                            return True
                        else:  # Enemy piece but not applying check
                            break
                else:  # Off board
                    break
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for move in knight_moves:
            end_row = row + move[0]
            end_col = col + move[1]
            if 0 <= end_row < len(self.board) and 0 <= end_col < len(self.board):
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == opponent and end_piece[1] == 'N':
                    return True
        return False

    def check_for_pins_and_checks(self):
        """Returns if the player is in check, a list of pins, and a list of checks"""
        pins = []
        checks = []
        in_check = False

        if self.white_to_move:
            opponent = 'b'
            ally = 'w'
            start_row, start_col = self.white_king_location[0], self.white_king_location[1]
        else:
            opponent = 'w'
            ally = 'b'
            start_row, start_col = self.black_king_location[0], self.black_king_location[1]

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possible_pin = ()  # Resets possible pins
            for i in range(1, len(self.board)):
                end_row = start_row + d[0] * i
                end_col = start_col + d[1] * i
                if 0 <= end_row < len(self.board) and 0 <= end_col < len(self.board):
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally and end_piece[1] != 'K':
                        if possible_pin == ():  # 1st ally piece can be pinned
                            possible_pin = (end_row, end_col, d[0], d[1])
                        else:  # 2nd ally piece, so no pin or check possible
                            break
                    elif end_piece[0] == opponent:
                        piece_type = end_piece[1]
                        if (0 <= j <= 3 and piece_type == 'R') or (4 <= j <= 7 and piece_type == 'B') or \
                                (i == 1 and piece_type == 'P' and ((opponent == 'w' and 6 <= j <= 7)
                                                                   or (opponent == 'b' and 4 <= j <= 5))) or \
                                (piece_type == 'Q') or (i == 1 and piece_type == 'K'):
                            if possible_pin == ():  # no piece blocking, so check
                                in_check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else:  # Piece blocking, so pin
                                pins.append(possible_pin)
                                break
                        else:  # Enemy piece but not applying check
                            break
                else:  # Off board
                    break

        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for move in knight_moves:
            end_row = start_row + move[0]
            end_col = start_col + move[1]
            if 0 <= end_row < len(self.board) and 0 <= end_col < len(self.board):
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == opponent and end_piece[1] == 'N':
                    in_check = True
                    checks.append((end_row, end_col, move[0], move[1]))

        return in_check, pins, checks


class CastleRights:
    """Data storage of current states of castling rights"""

    def __init__(self, white_king_side, black_king_side, white_queen_side, black_queen_side):
        self.white_king_side = white_king_side
        self.black_king_side = black_king_side
        self.white_queen_side = white_queen_side
        self.black_queen_side = black_queen_side


class Move:
    ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4,
                     '5': 3, '6': 2, '7': 1, '8': 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3,
                        'e': 4, 'f': 5, 'g': 6, 'h': 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_square, end_square, board, en_passant=False, pawn_promotion=False, castle=False):
        self.start_row, self.start_col = start_square[0], start_square[1]
        self.end_row, self.end_col = end_square[0], end_square[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.is_promotion = pawn_promotion

        # En passant
        self.is_en_passant = en_passant
        if self.is_en_passant:
            self.piece_captured = 'wP' if self.piece_moved == 'bP' else 'bP'

        self.is_castle_move = castle
        self.is_capture = self.piece_captured != '--'
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    def __eq__(self, other):
        """Overrides the equals method because a Class is used"""
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def get_chess_notation(self):
        """Creates a rank and file chess notation"""
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, rank, col):
        return self.cols_to_files[col] + self.rows_to_ranks[rank]

    def __str__(self):
        """
        Overrides string function to improve chess notation.
        Does not 1) specify checks, 2) checkmate, or 3) when
        multiple same-type pieces can capture the same square.
        """
        # Castling
        if self.is_castle_move:
            return 'O-O' if self.end_col == 6 else 'O-O-O'

        end_square = self.get_rank_file(self.end_row, self.end_col)

        # Pawn moves
        if self.piece_moved[1] == 'P':
            if self.is_capture and self.is_promotion:  # Pawn promotion
                return f'{end_square}={promoted_piece}'
            elif self.is_capture and not self.is_promotion:  # Capture move
                return f'{self.cols_to_files[self.start_col]}x{end_square}'
            else:  # Normal movement
                return end_square

        # Other piece moves
        move_string = self.piece_moved[1]
        if self.is_capture:
            move_string += 'x'

        return f'{move_string}{end_square}'

'''
Test
'''
from Chess import ChessMain


# class GameState:
#     def __init__(self):
#         self.board = [
#             ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
#             ['bP'] * 8,
#             ['--'] * 8,
#             ['--'] * 8,
#             ['--'] * 8,
#             ['--'] * 8,
#             ['wP'] * 8,
#             ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
#         ]
#         self.white_to_move = True
#         self.move_log = []
#         self.white_king_location = (7, 4)
#         self.black_king_location = (0, 4)
#         self.checkmate = False
#         self.stalemate = False
#         self.en_passant_possible = ()
#         self.castling_rights = {
#             'wks': True, 'wqs': True,
#             'bks': True, 'bqs': True
#         }
#
#     def make_move(self, move):
#         self.board[move.start_row][move.start_col] = '--'
#         piece = move.piece_moved[0] + move.promotion_choice if move.is_promotion else move.piece_moved
#         self.board[move.end_row][move.end_col] = piece
#         self.move_log.append(move)
#         self.white_to_move = not self.white_to_move
#
#         if piece[1] == 'K':
#             if piece[0] == 'w':
#                 self.white_king_location = (move.end_row, move.end_col)
#                 self.castling_rights['wks'] = False
#                 self.castling_rights['wqs'] = False
#             else:
#                 self.black_king_location = (move.end_row, move.end_col)
#                 self.castling_rights['bks'] = False
#                 self.castling_rights['bqs'] = False
#
#         if move.piece_moved[1] == 'P' and abs(move.start_row - move.end_row) == 2:
#             self.en_passant_possible = ((move.start_row + move.end_row) // 2, move.start_col)
#         else:
#             self.en_passant_possible = ()
#
#         if move.is_en_passant:
#             self.board[move.start_row][move.end_col] = '--'
#
#         if move.is_castle:
#             if move.end_col - move.start_col == 2:
#                 self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1]
#                 self.board[move.end_row][move.end_col + 1] = '--'
#             else:
#                 self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2]
#                 self.board[move.end_row][move.end_col - 2] = '--'
#
#     def undo_move(self):
#         if self.move_log:
#             move = self.move_log.pop()
#             self.board[move.start_row][move.start_col] = move.piece_moved
#             self.board[move.end_row][move.end_col] = move.piece_captured
#             self.white_to_move = not self.white_to_move
#
#             if move.piece_moved[1] == 'K':
#                 if move.piece_moved[0] == 'w':
#                     self.white_king_location = (move.start_row, move.start_col)
#                 else:
#                     self.black_king_location = (move.start_row, move.start_col)
#
#             if move.is_en_passant:
#                 self.board[move.end_row][move.end_col] = '--'
#                 self.board[move.start_row][move.end_col] = 'bP' if self.white_to_move else 'wP'
#
#             if move.is_castle:
#                 if move.end_col - move.start_col == 2:
#                     self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
#                     self.board[move.end_row][move.end_col - 1] = '--'
#                 else:
#                     self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
#                     self.board[move.end_row][move.end_col + 1] = '--'
#
#     def get_valid_moves(self):
#         return [m for m in self.get_all_possible_moves() if not self.causes_check(m)]
#
#     def causes_check(self, move):
#         self.make_move(move)
#         in_check = self.square_under_attack(
#             *self.white_king_location if self.white_to_move else self.black_king_location,
#             'b' if self.white_to_move else 'w')
#         self.undo_move()
#         return in_check
#
#     def get_all_possible_moves(self):
#         moves = []
#         for r in range(8):
#             for c in range(8):
#                 turn = self.board[r][c][0]
#                 if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
#                     piece_type = self.board[r][c][1]
#                     self.get_piece_moves(r, c, piece_type, moves)
#         return moves
#
#     def get_piece_moves(self, r, c, piece, moves):
#         if piece == 'P':
#             self.get_pawn_moves(r, c, moves)
#         elif piece == 'R':
#             self.get_rook_moves(r, c, moves)
#         elif piece == 'N':
#             self.get_knight_moves(r, c, moves)
#         elif piece == 'B':
#             self.get_bishop_moves(r, c, moves)
#         elif piece == 'Q':
#             self.get_queen_moves(r, c, moves)
#         elif piece == 'K':
#             self.get_king_moves(r, c, moves)
#
#     def get_pawn_moves(self, r, c, moves):
#         direction = -1 if self.white_to_move else 1
#         start_row = 6 if self.white_to_move else 1
#         enemy = 'b' if self.white_to_move else 'w'
#         end_row = r + direction
#
#         if self.board[end_row][c] == '--':
#             is_promotion = (end_row == 0 or end_row == 7)
#             moves.append(Move((r, c), (end_row, c), self.board, promotion=is_promotion))
#             if r == start_row and self.board[r + 2 * direction][c] == '--':
#                 moves.append(Move((r, c), (r + 2 * direction, c), self.board))
#
#         for dc in [-1, 1]:
#             col = c + dc
#             if 0 <= col < 8:
#                 if self.board[end_row][col][0] == enemy:
#                     is_promotion = (end_row == 0 or end_row == 7)
#                     moves.append(Move((r, c), (end_row, col), self.board, promotion=is_promotion))
#                 elif (end_row, col) == self.en_passant_possible:
#                     moves.append(Move((r, c), (end_row, col), self.board, en_passant=True))
#
#     def get_rook_moves(self, r, c, moves):
#         directions = [(-1, 0), (0, -1), (1, 0), (0, 1)]
#         enemy = 'b' if self.white_to_move else 'w'
#         for d in directions:
#             for i in range(1, 8):
#                 end_row, end_col = r + d[0]*i, c + d[1]*i
#                 if 0 <= end_row < 8 and 0 <= end_col < 8:
#                     target = self.board[end_row][end_col]
#                     if target == '--':
#                         moves.append(Move((r, c), (end_row, end_col), self.board))
#                     elif target[0] == enemy:
#                         moves.append(Move((r, c), (end_row, end_col), self.board))
#                         break
#                     else:
#                         break
#                 else:
#                     break
#
#     def get_knight_moves(self, r, c, moves):
#         directions = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
#         ally = 'w' if self.white_to_move else 'b'
#         for d in directions:
#             end_row, end_col = r + d[0], c + d[1]
#             if 0 <= end_row < 8 and 0 <= end_col < 8:
#                 target = self.board[end_row][end_col]
#                 if target[0] != ally:
#                     moves.append(Move((r, c), (end_row, end_col), self.board))
#
#     def get_bishop_moves(self, r, c, moves):
#         directions = [(-1, -1), (-1, 1), (1, 1), (1, -1)]
#         enemy = 'b' if self.white_to_move else 'w'
#         for d in directions:
#             for i in range(1, 8):
#                 end_row, end_col = r + d[0]*i, c + d[1]*i
#                 if 0 <= end_row < 8 and 0 <= end_col < 8:
#                     target = self.board[end_row][end_col]
#                     if target == '--':
#                         moves.append(Move((r, c), (end_row, end_col), self.board))
#                     elif target[0] == enemy:
#                         moves.append(Move((r, c), (end_row, end_col), self.board))
#                         break
#                     else:
#                         break
#                 else:
#                     break
#
#     def get_queen_moves(self, r, c, moves):
#         self.get_rook_moves(r, c, moves)
#         self.get_bishop_moves(r, c, moves)
#
#     def get_king_moves(self, r, c, moves):
#         directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
#         ally = 'w' if self.white_to_move else 'b'
#         for d in directions:
#             end_row, end_col = r + d[0], c + d[1]
#             if 0 <= end_row < 8 and 0 <= end_col < 8:
#                 target = self.board[end_row][end_col]
#                 if target[0] != ally:
#                     moves.append(Move((r, c), (end_row, end_col), self.board))
#
#         # Castling
#         if self.white_to_move:
#             if self.castling_rights['wks']:
#                 if self.board[7][5] == self.board[7][6] == '--' and not self.square_under_attack(7, 4, 'b') and not self.square_under_attack(7, 5, 'b') and not self.square_under_attack(7, 6, 'b'):
#                     moves.append(Move((7, 4), (7, 6), self.board, castle=True))
#             if self.castling_rights['wqs']:
#                 if self.board[7][1] == self.board[7][2] == self.board[7][3] == '--' and not self.square_under_attack(7, 4, 'b') and not self.square_under_attack(7, 2, 'b') and not self.square_under_attack(7, 3, 'b'):
#                     moves.append(Move((7, 4), (7, 2), self.board, castle=True))
#         else:
#             if self.castling_rights['bks']:
#                 if self.board[0][5] == self.board[0][6] == '--' and not self.square_under_attack(0, 4, 'w') and not self.square_under_attack(0, 5, 'w') and not self.square_under_attack(0, 6, 'w'):
#                     moves.append(Move((0, 4), (0, 6), self.board, castle=True))
#             if self.castling_rights['bqs']:
#                 if self.board[0][1] == self.board[0][2] == self.board[0][3] == '--' and not self.square_under_attack(0, 4, 'w') and not self.square_under_attack(0, 2, 'w') and not self.square_under_attack(0, 3, 'w'):
#                     moves.append(Move((0, 4), (0, 2), self.board, castle=True))
#
#     def square_under_attack(self, row, col, opponent):
#         temp_white_to_move = self.white_to_move
#         self.white_to_move = (opponent == 'w')
#         opp_moves = self.get_all_possible_moves()
#         self.white_to_move = temp_white_to_move
#         for move in opp_moves:
#             if move.end_row == row and move.end_col == col:
#                 return True
#         return False
#
#
# class Move:
#     ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
#     rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
#     files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
#     cols_to_files = {v: k for k, v in files_to_cols.items()}
#
#     def __init__(self, start_sq, end_sq, board, promotion=False, en_passant=False, castle=False):
#         self.start_row, self.start_col = start_sq
#         self.end_row, self.end_col = end_sq
#         self.piece_moved = board[self.start_row][self.start_col]
#         self.piece_captured = board[self.end_row][self.end_col] if not en_passant else ('bP' if self.piece_moved[0] == 'w' else 'wP')
#         self.is_promotion = promotion
#         self.promotion_choice = 'Q' if promotion else ''
#         self.is_en_passant = en_passant
#         self.is_castle = castle
#         self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col
#
#     def __eq__(self, other):
#         return isinstance(other, Move) and self.move_id == other.move_id
#
#     def __str__(self):
#         return self.get_chess_notation()
#
#     def get_chess_notation(self):
#         return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)
#
#     def get_rank_file(self, r, c):
#         return self.cols_to_files[c] + self.rows_to_ranks[r]
