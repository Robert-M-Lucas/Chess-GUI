import time
from copy import deepcopy

import pygame
from board import Board

import win32gui, win32con

TEXT_PIECES = False

# INNITs
pygame.font.init()
display = 80*8

def innits(width=None):
    global myfont
    global myfontbig
    global screen
    global chess_font
    global scale
    global r_piece_names
    global check_text
    global turn_text
    global error_texts
    global colours
    global restart_text
    global restart_text_rect

    scale = int(display/8)
    myfont = pygame.font.SysFont('Ariel', int(scale*0.7))
    myfontbig = pygame.font.SysFont('Ariel', int(scale*1.5))
    if TEXT_PIECES:
        chess_font = myfont
    else:
        chess_font = pygame.font.Font("CASEFONT.TTF", int(scale*0.8))

    if width is None:
        width = int(display * 1.5)
    screen = pygame.display.set_mode((width, display), pygame.RESIZABLE)

    # TEXT GENERATION
    if TEXT_PIECES:
        piece_names = [["p", "n", "b", "r", "q", "k"], ["o", "m", "v", "t", "w", "l"]]
    else:
        piece_names = [["o", "m", "v", "t", "w", "l"], ["o", "m", "v", "t", "w", "l"]]
    if TEXT_PIECES:
        r_piece_names = [[], []]
        for i in range(2):
            colour = black_pieces
            if i == 1:
                colour = white_pieces
            for j in piece_names[i]:
                r_piece_names[i] += [chess_font.render(j, True, colour)]
    else:
        r_piece_names = [[], []]
        colours = [white_pieces, black_pieces]
        for i in range(2):
            colour = colours[i]
            for j in piece_names[i]:
                r_piece_names[i] += [chess_font.render(j, True, colour)]
    check_text = [myfontbig.render("CHECK", True, board_white), myfont.render("Black gives", True, board_white),
                  myfont.render("White gives", True, board_white)]
    turn_text = [myfont.render("Turn: White", True, board_white), myfont.render("Turn: Black", True, board_white)]
    error_texts = [[myfont.render("Can't put king", True, board_white), myfont.render("in check", True, board_white)],
                   [myfont.render("Can't castle", True, board_white),
                    myfont.render("while in check", True, board_white)]]
    restart_text = myfontbig.render("Restart", True, board_white)
    restart_text_rect = restart_text.get_rect(center=(display*1.25, (display/8)*7))


board_white = (227, 208, 141)
board_black = (66, 35, 10)
black = (0, 0, 0)
black_pieces = (0, 0, 0)
white_pieces = (255, 255, 255)
check_colour = (255, 0, 0)
capture_colour = (255, 115, 0)
selected_colour = (38, 125, 255)
innits()


# BOARD INNIT
board = Board()


def pos_to_coords(pos):
    return [int((pos % 8) * (display / 8)), int(int(pos / 8) * (display / 8))]


# LESSER INNITs
def lesser_innits():
    global pos_selected
    global possible_moves
    global check
    global check_giver
    global error

    pos_selected = None
    possible_moves = []
    check = None
    check_giver = -1
    error = -1
lesser_innits()

screen.fill(board_black)
hwnd = win32gui.GetForegroundWindow()
win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
# MAIN LOOP
while True:
    screen.fill(board_black)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit(0)

        elif event.type == pygame.VIDEORESIZE:
            display = event.h
            if event.w < int(1.5*event.h):
                width = int(1.5*event.h)
            else:
                width = event.w
            innits(width=width)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos[0] > display:
                pos_selected = None
                possible_moves = []
                if restart_text_rect.center[0] - (restart_text_rect.w/2) < mouse_pos[0] < restart_text_rect.center[0] + (restart_text_rect.w/2) and restart_text_rect.center[1] - (restart_text_rect.h/2) < mouse_pos[1] < restart_text_rect.center[1] + (restart_text_rect.h/2):
                    board.__init__()
                    lesser_innits()
                continue
            x, y = int((mouse_pos[0] / display) * 8), int((mouse_pos[1] / display) * 8)
            temp_pos = (y * 8) + x
            if pos_selected == temp_pos:
                pos_selected = None
                possible_moves = []
            else:
                if temp_pos in possible_moves or pygame.mouse.get_pressed()[2]:
                    returned = board.move(pos_selected, temp_pos, check)
                    if returned[1] == -1:
                        check = returned[0]
                        error = -1
                    else:
                        error = returned[1]
                    if check is not None:
                        if len(returned) == 3:
                            check_giver = returned[2]
                    else:
                        check_giver = -1
                    pos_selected = None
                    possible_moves = []
                else:
                    pos_selected = (y * 8) + x

                    moves = board.pieces[pos_selected]

                    if moves is not None and moves[4] is not None and moves[1] == int(board.turn):
                        possible_moves = moves[4]
                    else:
                        possible_moves = []

    in_square_offset = int((display / 8) / 8)
    for i in range(64):
        colour = board_white
        draw = True
        if i == pos_selected:
            colour = selected_colour
        elif i == check_giver:
            colour = check_colour
        elif (int(i / 8) * 8) % 16:
            if i % 2:
                draw = False
        else:
            if not (i % 2):
                draw = False
        if draw:
            pygame.draw.rect(screen, colour, pos_to_coords(i) + [int(display / 8), int(display / 8)])

        pos_coords_no_mod = pos_to_coords(i)
        pos_coords = deepcopy(pos_coords_no_mod)
        pos_coords[0] += display/16
        pos_coords[1] += display / 16

        if i in possible_moves:
            if board.board[i] == 0:
                pygame.draw.circle(screen, selected_colour, pos_coords, scale * 0.2)
            else:
                pygame.draw.rect(screen, capture_colour, pos_to_coords(i) + [int(display / 8), int(display / 8)])

        if board.pieces[i] is not None:
            pygame.draw.rect(screen, colours[int(not bool(board.pieces[i][1]))], (pos_coords_no_mod[0] + in_square_offset, pos_coords_no_mod[1] + in_square_offset,
                                                                                  int(display / 8) - in_square_offset*2, int(display / 8) - in_square_offset*2))
            text = r_piece_names[board.pieces[i][1]][board.pieces[i][0]-1]
            text_rect = text.get_rect(center=pos_coords)
            screen.blit(text, text_rect)

    if check is not None:
        text_rect = check_text[0].get_rect(center=(display*1.25, display/6))
        screen.blit(check_text[0], text_rect)
        screen.blit(check_text[int(check)+1], check_text[int(check)+1].get_rect(center=(display*1.25, (display/16))))

    if error >= 0:
        selected = error_texts[error]
        if error == 0 or error == 1:
            for j, i in enumerate(selected):
                screen.blit(i, i.get_rect(center=(display * 1.25, (display / 13)*(6+j))))

    screen.blit(turn_text[int(board.turn)], turn_text[int(board.turn)].get_rect(center=(display*1.25, (display/8)*6)))

    screen.blit(restart_text, restart_text_rect)

    pygame.display.update()
