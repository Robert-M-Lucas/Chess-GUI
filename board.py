from copy import deepcopy


class Board:
    def __init__(self):
        self.board = [0]*64
        self.king_pos = [-1, -1]
        self.pieces = []
        self.turn = False
        self.castles = [True, True, True, True]
        self.setup_board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
        self.get_pieces(True)

    def decode(self, input):
        b = bin(input)
        b = "0" * (6 - (len(b) - 2)) + b[2:]
        return [int(b[:3], base=2), int(b[3:4], base=2), int(b[4:], base=2)]

    def encode(self, input):
        b_code = ""
        for i in [[input[0], 3], [input[1], 1], [input[2], 2]]:
            b = bin(i[0])
            b_code += "0" * (i[1] - (len(b) - 2)) + b[2:]
        int_code = int(b_code, base=2)
        return int_code

    def setup_board(self, fen):
        ranks = fen.split("/")
        pos = 0
        for count, rank in enumerate(ranks):
            pos = count * 8
            for piece in rank:
                if piece.isdigit():
                    pos += int(piece)
                else:
                    colour = 0
                    data = 0
                    if piece.islower():
                        colour = 1
                    p = piece.lower()
                    code = 7
                    if p == "p":
                        code = 1
                    elif p == "n":
                        code = 2
                    elif p == "b":
                        code = 3
                    elif p == "r":
                        code = 4
                    elif p == "q":
                        code = 5
                    elif p == "k":
                        code = 6
                        self.king_pos[colour] = pos

                    int_code = self.encode([code, colour, data])

                    self.board[pos] = int_code
                    pos += 1

    def get_pieces(self, moves=False, board=None, refining=False):
        _return = []
        check = None
        check_giver = -1
        for pos, i in enumerate(self.board):
            if i != 0:
                if moves:
                    legal_moves, _check = self.calculate_moves(pos, board=board, refining=refining)
                    if _check is not None:
                        check = _check
                        check_giver = pos
                else:
                    legal_moves = None
                _return += [self.decode(i) + [pos, legal_moves]]
            else:
                _return += [None]

        if not refining:
            self.pieces = _return
            self.refine_moves()
        return check, check_giver

    def u(self, counter, rank): return counter - 8
    def u_c(self, counter, rank): return counter < 0
    def d(self, counter, rank): return counter + 8
    def d_c(self, counter, rank): return counter >= 64
    def l(self, counter, rank): return counter - 1
    def lr_c(self, counter, rank):
        return int(counter/8) != rank
    def r(self, counter, rank): return counter + 1
    def ul(self, counter): return counter - 9
    def ul_c(self, counter, prev):
        return abs(prev % 8 - counter % 8) > 1
    def ur(self, counter): return counter -7
    def dl(self, counter):return counter + 7
    def dr(self, counter): return counter + 9

    def calculate_moves(self, pos, board=None, refining=False):
        _return = None
        if board is None:
            board = self.board

        if board[pos] == 0:
            return None, None
        else:
            data = self.decode(board[pos])
            possible_moves = []
            controllers = None
            king = False
            sliders = [False, False]
            # BISHOP
            if data[0] == 3:
                sliders[1] = True
            # ROOK
            if data[0] == 4:
                sliders[0] = True
            # QUEEN
            elif data[0] == 5:
                sliders = [True, True]
            # HORSE
            elif data[0] == 2:
                possible_moves_unchecked = [pos + 10, pos + 17, pos + 15, pos + 6, pos - 10, pos - 17, pos - 15, pos - 6]
                possible_moves = []
                for i in possible_moves_unchecked:
                    if i >= 64 or i < 0:
                        continue
                    if board[i] != 0 and self.decode(board[i])[1] == data[1]:
                        continue
                    if abs(pos % 8 - i % 8) > 2:
                        continue
                    possible_moves += [i]

                _return = possible_moves

            elif data[0] == 6:
                king = True
                sliders = [True, True]
                try:
                    if self.castles[int(not self.turn)*2] and board[pos-1] == 0 and board[pos-2] == 0 and board[pos-3] == 0:
                        possible_moves += [pos-2]
                    elif self.castles[(int(not self.turn)*2)+1] and board[pos+1] == 0 and board[pos+2] == 0:
                        possible_moves += [pos + 2]
                except:
                    pass

            elif data[0] == 1:
                possible_moves_unchecked = []
                possible_moves_unchecked_takes = []
                if data[1] == 0:
                    possible_moves_unchecked += [pos - 8]
                    possible_moves_unchecked_takes += [pos - 7, pos - 9]
                    if data[2] == 0 and 0 <= possible_moves_unchecked[0] < 64 and board[possible_moves_unchecked[0]] == 0:
                        possible_moves_unchecked += [pos - 16]
                else:
                    possible_moves_unchecked += [pos + 8]
                    possible_moves_unchecked_takes += [pos + 7, pos + 9]
                    if data[2] == 0 and 0 <= possible_moves_unchecked[0] < 64 and board[possible_moves_unchecked[0]] == 0:
                        possible_moves_unchecked += [pos + 16]
                possible_moves = []

                for i in possible_moves_unchecked:
                    if i >= 64 or i < 0:
                        continue
                    if board[i] != 0:
                        continue
                    possible_moves += [i]

                for i in possible_moves_unchecked_takes:
                    if i >= 64 or i < 0:
                        continue
                    if board[i] == 0 or self.decode(board[i])[1] == data[1]:
                        continue
                    if abs(pos % 8 - i % 8) > 1:
                        continue
                    possible_moves += [i]

                _return = possible_moves

            if sliders[0]:
                pos_rank = int(pos / 8)
                for i in [[self.u, self.u_c], [self.d, self.d_c], [self.l, self.lr_c], [self.r, self.lr_c]]:
                    _break = True
                    temp_pos = deepcopy(pos)
                    while _break:
                        if king:
                            _break = False
                        temp_pos = i[0](temp_pos, pos_rank)
                        if i[1](temp_pos, pos_rank):
                            break
                        if self.board[temp_pos] != 0:
                            target = self.decode(self.board[temp_pos])
                            if target[1] == data[1]:
                                _break = False
                                break
                            else:
                                _break = False
                        possible_moves += [temp_pos]

            if sliders[1]:
                for i in [[self.ul, self.ul_c], [self.ur, self.ul_c], [self.dl, self.ul_c], [self.dr, self.ul_c]]:
                    _break = True
                    temp_pos = deepcopy(pos)
                    while _break:
                        if king:
                            _break = False
                        prev_pos = deepcopy(temp_pos)
                        temp_pos = i[0](temp_pos)
                        if i[1](temp_pos, prev_pos) or temp_pos < 0 or temp_pos >= 64:
                            break
                        if self.board[temp_pos] != 0:
                            target = self.decode(self.board[temp_pos])
                            if target[1] == data[1]:
                                _break = False
                                break
                            else:
                                _break = False
                        possible_moves += [temp_pos]

            if sliders[0] or sliders[1]:
                _return = possible_moves

            if (self.king_pos[int(False)] in _return) and data[1] == int(True):
                check = False # Black gives check
            elif (self.king_pos[int(True)] in _return) and data[1] == int(False):
                check = True # White give check
            else:
                check = None

            return _return, check

    def move(self, before, after, check=None, board=None, refining=False):
        if board is None:
            board = self.board

        backup = deepcopy(self.board)

        moving = self.decode(board[before])

        if moving[0] == 6 and moving[2] == 0:
            if abs(before - after) == 2:
                if check == self.turn:
                    return [check, 1]
                else:
                    if after > before:
                        board[after-1] = board[after+1]
                        board[after+1] = 0
                    else:
                        board[after+1] = board[after-2]
                        board[after-2] = 0

        if moving[0] == 1 and (moving[1] == 0 and 0 <= after < 8) or (moving[1] == 1 and 56 <= after < 64):
            moving[0] = 5
            moving[2] = 0

        if moving[0] == 6:
            self.king_pos[moving[1]] = after

        board[before] = self.encode(moving)

        board[after] = board[before]

        board[before] = 0

        check, check_giver = self.get_pieces(True, board, refining=refining)

        if check is not None and check is self.turn:
            self.board = backup
            if moving[0] == 6:
                self.king_pos[moving[1]] = before
            if not refining:
                self.get_pieces(True)
            return [None, 0, check_giver]

        if (moving[0] == 1 or moving[0] == 4 or moving[0] == 6) and moving[2] == 0:
            moving[2] = 1
            if moving[0] == 4:
                if before == 0:
                    self.castles[2] = False
                elif before == 7:
                    self.castles[3] = False
                elif before == 56:
                    self.castles[0] = False
                elif before == 63:
                    self.castles[1] = False
            elif moving[0] == 6:
                if moving[1] == 0:
                    self.castles[0], self.castles[1] = False, False
                else:
                    self.castles[2], self.castles[3] = False, False

        self.turn = not self.turn
        return [check, -1, check_giver]

    def refine_moves(self):
        return
        backup = [deepcopy(self.board), deepcopy(self.king_pos), deepcopy(self.castles), deepcopy(self.turn)]

        for pos, piece in enumerate(self.pieces[:]):
            if piece is not None:
                for i in piece[4]:
                    if i != -1:
                        print(self.board, self.king_pos, self.castles, self.turn)
                        _return = self.move(pos, i, refining=True)
                        self.board, self.king_pos, self.castles, self.turn = deepcopy(backup[0]), deepcopy(backup[1]), deepcopy(backup[2]), deepcopy(backup[3])
                        if _return[1] != -1 or _return[0] != self.turn:
                            self.pieces[pos][4].remove(i)

        self.board, self.king_pos, self.castles, self.turn = backup[0].copy(), backup[1].copy(), backup[2].copy(), deepcopy(backup[3])