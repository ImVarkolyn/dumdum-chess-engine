import pygame as p
import os
from Chess import ChessEngine, ChessAI

p.init()

# === Config ===
board_width = board_height = 512
dimension = 8
sq_size = board_height // dimension
max_fps = 15
images = {}
white_sq = (238, 210, 183)
black_sq = (184, 135, 98)
colors = [p.Color(white_sq), p.Color(black_sq)]
move_log_panel_width = 200
move_log_panel_height = board_height
window_width = board_width + move_log_panel_width
window_height = board_height

# === Game state ===
player_one = True  # White by default
player_two = False  # Black by default

def load_images():
    pieces = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR', 'bP',
              'wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR', 'wP']
    for piece in pieces:
        images[piece] = p.transform.smoothscale(p.image.load(os.path.join('images', f'{piece}.png')), (sq_size, sq_size))

def starting_menu(screen):
    font = p.font.SysFont('Helvetica', 32, True, False)
    small_font = p.font.SysFont('Helvetica', 24, False, False)
    clock = p.time.Clock()
    background = p.transform.scale(p.image.load(os.path.join('images', 'background2.png')), (window_width, window_height))

    # Buttons
    button_width = 200
    button_height = 50
    white_button = p.Rect((window_width // 2) - button_width // 2, 200, button_width, button_height)
    black_button = p.Rect((window_width // 2) - button_width // 2, 300, button_width, button_height)

    while True:
        screen.blit(background, (0, 0))
        title = font.render('Choose Your Side', True, p.Color('black'))
        screen.blit(title, (window_width // 2 - title.get_width() // 2, 100))

        mouse_pos = p.mouse.get_pos()

        # Draw buttons with hover effect
        if white_button.collidepoint(mouse_pos):
            p.draw.rect(screen, p.Color('lightblue'), white_button)
        else:
            p.draw.rect(screen, p.Color('lightgray'), white_button)

        if black_button.collidepoint(mouse_pos):
            p.draw.rect(screen, p.Color('lightblue'), black_button)
        else:
            p.draw.rect(screen, p.Color('lightgray'), black_button)

        white_text = small_font.render('Play as White', True, p.Color('black'))
        black_text = small_font.render('Play as Black', True, p.Color('black'))
        screen.blit(white_text, (white_button.x + (button_width - white_text.get_width()) // 2, white_button.y + (button_height - white_text.get_height()) // 2))
        screen.blit(black_text, (black_button.x + (button_width - black_text.get_width()) // 2, black_button.y + (button_height - black_text.get_height()) // 2))

        p.display.flip()
        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                exit()
            if event.type == p.MOUSEBUTTONDOWN:
                if white_button.collidepoint(event.pos):
                    return True, False
                elif black_button.collidepoint(event.pos):
                    return False, True
        clock.tick(15)

# === MAIN ===
def main():
    global player_one, player_two
    screen = p.display.set_mode((board_width + move_log_panel_width, board_height))
    p.display.set_caption("Dumdum Chess Engine")
    logo = p.image.load(os.path.join('images', 'logo.png'))
    p.display.set_icon(logo)

    player_one, player_two = starting_menu(screen)

    clock = p.time.Clock()
    screen.fill(p.Color('white'))
    move_log_font = p.font.SysFont('Arial', 14, False, False)
    game_state = ChessEngine.GameState()
    valid_moves = game_state.get_valid_moves()
    move_made = False
    animate = False
    load_images()
    running = True
    square_selected = ()
    player_clicks = []
    game_over = False

    while running:
        human_turn = (game_state.white_to_move and player_one) or (not game_state.white_to_move and player_two)

        for event in p.event.get():
            if event.type == p.QUIT:
                running = False
            elif event.type == p.MOUSEBUTTONDOWN:
                if not game_over and human_turn:
                    location = p.mouse.get_pos()
                    column = location[0] // sq_size
                    row = location[1] // sq_size
                    if column >= dimension:
                        continue
                    if square_selected == (row, column):
                        square_selected = ()
                        player_clicks = []
                    else:
                        square_selected = (row, column)
                        player_clicks.append(square_selected)
                    if len(player_clicks) == 2:
                        move = ChessEngine.Move(player_clicks[0], player_clicks[1], game_state.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                game_state.make_move(valid_moves[i])
                                move_made = True
                                animate = True
                                square_selected = ()
                                player_clicks = []
                        if not move_made:
                            player_clicks = [square_selected]
            elif event.type == p.KEYDOWN:
                if event.key == p.K_z:
                    game_state.undo_move()
                    move_made = True
                    animate = False
                    game_over = False
                if event.key == p.K_r:
                    game_state = ChessEngine.GameState()
                    valid_moves = game_state.get_valid_moves()
                    square_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False

        if not game_over and not human_turn:
            AI_move = ChessAI.find_best_move(game_state, valid_moves, time_limit=9.9)
            if AI_move is None:
                AI_move = ChessAI.find_random_move(valid_moves)
            game_state.make_move(AI_move)
            move_made = True
            animate = True

        if move_made:
            if animate:
                animate_move(game_state.move_log[-1], screen, game_state.board, clock)
            valid_moves = game_state.get_valid_moves()
            move_made = False
            animate = False

        draw_game_state(screen, game_state, square_selected, move_log_font)

        if game_state.checkmate or game_state.stalemate:
            game_over = True
            text = 'Stalemate' if game_state.stalemate else ('Black wins by checkmate' if game_state.white_to_move else 'White wins by checkmate')
            draw_endgame_text(screen, text)

        clock.tick(max_fps)
        p.display.flip()

def draw_game_state(screen, game_state, square_selected, move_log_font):
    draw_board(screen)
    highlight_squares(screen, game_state, square_selected)
    draw_pieces(screen, game_state.board)
    draw_move_log(screen, game_state, move_log_font)

def draw_board(screen):
    for row in range(dimension):
        for column in range(dimension):
            color = colors[((row + column) % 2)]
            p.draw.rect(screen, color, p.Rect(column * sq_size, row * sq_size, sq_size, sq_size))

def highlight_squares(screen, game_state, square_selected):
    if square_selected != ():
        row, column = square_selected
        if game_state.board[row][column][0] == ('w' if game_state.white_to_move else 'b'):
            s = p.Surface((sq_size, sq_size))
            s.set_alpha(70)
            s.fill(p.Color('yellow'))
            screen.blit(s, (column * sq_size, row * sq_size))
    if len(game_state.move_log) != 0:
        last_move = game_state.move_log[-1]
        start_row, start_col = last_move.start_row, last_move.start_col
        end_row, end_col = last_move.end_row, last_move.end_col
        s = p.Surface((sq_size, sq_size))
        s.set_alpha(70)
        s.fill(p.Color('yellow'))
        screen.blit(s, (start_col * sq_size, start_row * sq_size))
        screen.blit(s, (end_col * sq_size, end_row * sq_size))

def draw_pieces(screen, board):
    for row in range(dimension):
        for column in range(dimension):
            piece = board[row][column]
            if piece != '--':
                screen.blit(images[piece], p.Rect(column * sq_size, row * sq_size, sq_size, sq_size))

def draw_move_log(screen, game_state, font):
    move_log_area = p.Rect(board_width, 0, move_log_panel_width, move_log_panel_height)
    p.draw.rect(screen, p.Color('#2d2d2e'), move_log_area)
    move_log = game_state.move_log
    move_texts = []
    for i in range(0, len(move_log), 2):
        move_string = f'{i // 2 + 1}. {str(move_log[i])} '
        if i + 1 < len(move_log):
            move_string += f'{str(move_log[i + 1])} '
        move_texts.append(move_string)

    move_per_row = 2
    padding = 5
    line_spacing = 2
    text_y = padding
    for i in range(0, len(move_texts), move_per_row):
        text = ''
        for j in range(move_per_row):
            if i + j < len(move_texts):
                text += move_texts[i + j]
        text_object = font.render(text, True, p.Color('whitesmoke'))
        text_location = move_log_area.move(padding, text_y)
        screen.blit(text_object, text_location)
        text_y += text_object.get_height() + line_spacing

def animate_move(move, screen, board, clock):
    delta_row = move.end_row - move.start_row
    delta_column = move.end_col - move.start_col
    frames_per_square = 5
    frame_count = (abs(delta_row) + abs(delta_column)) * frames_per_square

    for frame in range(frame_count + 1):
        row, column = (move.start_row + delta_row * frame / frame_count, move.start_col + delta_column * frame / frame_count)
        draw_board(screen)
        draw_pieces(screen, board)
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(move.end_col * sq_size, move.end_row * sq_size, sq_size, sq_size)
        p.draw.rect(screen, color, end_square)
        if move.piece_captured != '--':
            if move.is_en_passant:
                en_passant_row = move.end_row + 1 if move.piece_captured[0] == 'b' else move.end_row - 1
                end_square = p.Rect(move.end_col * sq_size, en_passant_row * sq_size, sq_size, sq_size)
            screen.blit(images[move.piece_captured], end_square)
        screen.blit(images[move.piece_moved], p.Rect(column * sq_size, row * sq_size, sq_size, sq_size))
        p.display.flip()
        clock.tick(60)

def draw_endgame_text(screen, text):
    font = p.font.SysFont('Helvetica', 32, True, False)
    text_object = font.render(text, True, p.Color('gray'), p.Color('mintcream'))
    text_location = p.Rect(0, 0, board_width, board_height).move(board_width / 2 - text_object.get_width() / 2, board_height / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, True, p.Color('black'))
    screen.blit(text_object, text_location.move(2, 2))

if __name__ == '__main__':
    main()
