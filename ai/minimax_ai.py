# ai/minimax_ai.py
import numpy as np
import random
from .move_utils import get_all_moves, get_valid_moves, get_jump_moves, get_continuous_jump_moves

class MinimaxAI:
    def __init__(self, player_id, depth=2):
        self.player_id = player_id
        self.depth = depth

    def in_target_area(self, pos):
        if self.player_id == 1:
            return (pos[0] >= 8 and pos[1] >= 8 and (pos[0] + pos[1] >= 16))
        elif self.player_id == 2:
            return (pos[0] <= 3 and pos[1] <= 3 and (pos[0] + pos[1] <= 6))
        return False

    def choose_move(self, board):
        # —— 1. 让路 —— #
        all_positions = [tuple(p) for p in np.argwhere(board == self.player_id)]
        outside = [pos for pos in all_positions if not self.in_target_area(pos)]

        move = self.improved_free_up_target_entry(board)
        if move:
            return move

        # —— 2. 收集“场外”所有可行走法 —— #
        moves = []
        for pos in outside:
            moves.extend(self.get_all_moves_from(pos, board))

        # —— 3. 降级到“全部棋子” —— #
        if not moves:
            moves = get_all_moves(board, self.player_id)
        if not moves:
            return None

        # —— 4. 带 α–β 剪枝的 Minimax —— #
        best_val, best_move = -float('inf'), None
        for mv in moves:
            new_board = self.simulate_move(board, mv)
            val = self.min_value(new_board, self.depth - 1, -float('inf'), float('inf'))
            if val > best_val:
                best_val, best_move = val, mv
        return best_move


    def get_all_moves_from(self, pos, board):
        moves = []
        for m in get_valid_moves(pos, board):
            moves.append((pos, m))
        for m in get_jump_moves(pos, board):
            moves.append((pos, m))
        jump_paths = get_continuous_jump_moves(pos, board)
        for path in jump_paths:
            if len(path) > 1:
                moves.append((pos, path[-1]))
        return moves

    def simulate_move(self, board, move):
        new_board = board.copy()
        from_pos, to_pos = move
        new_board[to_pos] = new_board[from_pos]
        new_board[from_pos] = 0
        return new_board

    def min_value(self, board, depth, alpha, beta):
        opp = 1 if self.player_id != 1 else 2
        if depth == 0 or self.terminal(board):
            return self.evaluate(board)
        value = float('inf')
        moves = get_all_moves(board, opp)
        if not moves:
            return self.evaluate(board)
        for move in moves:
            new_board = self.simulate_move(board, move)
            value = min(value, self.max_value(new_board, depth - 1, alpha, beta))
            if value <= alpha:
                return value
            beta = min(beta, value)
        return value

    def max_value(self, board, depth, alpha, beta):
        if depth == 0 or self.terminal(board):
            return self.evaluate(board)
        value = -float('inf')
        moves = get_all_moves(board, self.player_id)
        if not moves:
            return self.evaluate(board)
        for move in moves:
            new_board = self.simulate_move(board, move)
            value = max(value, self.min_value(new_board, depth - 1, alpha, beta))
            if value >= beta:
                return value
            alpha = max(alpha, value)
        return value

    def evaluate(self, board):
        if self.player_id == 1:
            my_target = (11, 11)
        else:
            my_target = (0, 0)
        my_pieces = np.argwhere(board == self.player_id)
        score = 0
        for piece in my_pieces:
            piece_pos = tuple(piece)
            if self.in_target_area(piece_pos):
                score -= 1000
                continue
            distance = abs(piece[0] - my_target[0]) + abs(piece[1] - my_target[1])
            score -= distance * 2
        return score

    def terminal(self, board):
        p1_done = sum(1 for i in range(8, 12) for j in range(8, 12) if i + j >= 16 and board[i, j] == 1) == 10
        p2_done = sum(1 for i in range(0, 4) for j in range(0, 4) if i + j <= 6 and board[i, j] == 2) == 10
        return p1_done or p2_done

    def improved_free_up_target_entry(self, board):
        # 让路逻辑同GreedyAI
        if self.player_id == 1:
            entry_positions = [(8, 11), (9, 10), (10, 9), (11, 8)]
            target_positions = [
                (11, 11), (11, 10), (10, 11),
                (11, 9), (10, 10), (9, 11),
                (11, 8), (10, 9), (9, 10), (8, 11)
            ]
            waiting = [pos for pos in np.argwhere(board == 1) if not self.in_target_area(tuple(pos))]
            in_target = [pos for pos in target_positions if board[pos] == 1]
            for entry in entry_positions:
                if board[entry] == 1:
                    candidates = []
                    for dx, dy in [(1,0),(0,1),(1,1)]:
                        nx, ny = entry[0]+dx, entry[1]+dy
                        if 0<=nx<12 and 0<=ny<12 and board[nx,ny]==0 and self.in_target_area((nx,ny)):
                            candidates.append((nx,ny))
                    if candidates and waiting:
                        best_candidate = min(candidates, key=lambda pos: abs(pos[0]-11)+abs(pos[1]-11))
                        return (entry, best_candidate)
            if len(in_target) >= 9 and waiting:
                for pos in np.argwhere(board == 1):
                    pos = tuple(pos)
                    if self.in_target_area(pos):
                        for dx, dy in [(-1,0),(0,-1),(-1,-1)]:
                            nx, ny = pos[0]+dx, pos[1]+dy
                            if 0<=nx<12 and 0<=ny<12 and not self.in_target_area((nx,ny)) and board[nx,ny]==0:
                                return (pos, (nx,ny))
        elif self.player_id == 2:
            entry_positions = [(3,0), (2,1), (1,2), (0,3)]
            target_positions = [
                (0, 0), (0, 1), (1, 0),
                (0, 2), (1, 1), (2, 0),
                (0, 3), (1, 2), (2, 1), (3, 0)
            ]
            waiting = [pos for pos in np.argwhere(board == 2) if not self.in_target_area(tuple(pos))]
            in_target = [pos for pos in target_positions if board[pos] == 2]
            for entry in entry_positions:
                if board[entry] == 2:
                    candidates = []
                    for dx, dy in [(-1,0),(0,-1),(-1,-1)]:
                        nx, ny = entry[0]+dx, entry[1]+dy
                        if 0<=nx<12 and 0<=ny<12 and board[nx,ny]==0 and self.in_target_area((nx,ny)):
                            candidates.append((nx,ny))
                    if candidates and waiting:
                        best_candidate = min(candidates, key=lambda pos: abs(pos[0]-0)+abs(pos[1]-0))
                        return (entry, best_candidate)
            if len(in_target) >= 9 and waiting:
                for pos in np.argwhere(board == 2):
                    pos = tuple(pos)
                    if self.in_target_area(pos):
                        for dx, dy in [(1,0),(0,1),(1,1)]:
                            nx, ny = pos[0]+dx, pos[1]+dy
                            if 0<=nx<12 and 0<=ny<12 and not self.in_target_area((nx,ny)) and board[nx,ny]==0:
                                return (pos, (nx,ny))
        return None
