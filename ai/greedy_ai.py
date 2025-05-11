# ai/greedy_ai.py
import numpy as np
import random
from .move_utils import get_valid_moves, get_jump_moves, get_all_moves

class GreedyAI:
    def __init__(self, player_id):
        self.player_id = player_id

    def get_deep_target(self):
        if self.player_id == 1:
            return (11, 11)
        elif self.player_id == 2:
            return (0, 0)
        
        return None

    def in_target_area(self, pos):
        if self.player_id == 1:
            # 右下角三角形区域
            return (pos[0] >= 8 and pos[1] >= 8 and 
                   (pos[0] + pos[1] >= 16))  # 确保在三角形区域内
        elif self.player_id == 2:
            # 左上角三角形区域
            return (pos[0] <= 3 and pos[1] <= 3 and 
                   (pos[0] + pos[1] <= 6))  # 确保在三角形区域内

    def in_stable_area(self, pos):
        if self.player_id == 1:
            # 右下角三角形稳定区域
            return (pos[0] >= 9 and pos[1] >= 9 and 
                   (pos[0] + pos[1] >= 18))  # 确保在三角形区域内
        elif self.player_id == 2:
            # 左上角三角形稳定区域
            return (pos[0] <= 2 and pos[1] <= 2 and 
                   (pos[0] + pos[1] <= 4))  # 确保在三角形区域内
        
        return False

    def calculate_score(self, pos):
        # 曼哈顿距离作为评分，距离越短表示位置越理想
        deep_target = self.get_deep_target()
        return abs(pos[0] - deep_target[0]) + abs(pos[1] - deep_target[1])

    def choose_move(self, board):
        # —— 1. 让路 —— #
        all_positions = [tuple(p) for p in np.argwhere(board == self.player_id)]
        outside = [pos for pos in all_positions if not self.in_target_area(pos)]

        move = self.improved_free_up_target_entry(board)
        if move:
            return move

        # —— 2. 对“场外”棋子做贪心 —— #
        best_move, best_score = None, float('inf')
        random.shuffle(outside)
        for pos in outside:
            # 普通走 + 单跳 + 连续跳
            moves = get_valid_moves(pos, board) + get_jump_moves(pos, board)
            moves += self.get_all_jump_targets(pos, board)
            for dest in moves:
                score = self.heuristic(dest)
                if score < best_score:
                    best_score, best_move = score, (pos, dest)
        if best_move:
            return best_move

        # —— 3. 降级：考虑“目标区内”棋子 —— #
        for pos in all_positions:
            moves = get_valid_moves(pos, board) + get_jump_moves(pos, board)
            moves += self.get_all_jump_targets(pos, board)
            for dest in moves:
                score = self.heuristic(dest)
                if score < best_score:
                    best_score, best_move = score, (pos, dest)
        return best_move


    def heuristic(self, pos):
        if self.player_id == 1:
            target = (11, 11)
        else:
            target = (0, 0)
        return abs(pos[0] - target[0]) + abs(pos[1] - target[1])

    def get_all_jump_targets(self, pos, board):
        # 返回所有连续跳跃的终点
        from .move_utils import get_continuous_jump_moves
        jump_paths = get_continuous_jump_moves(pos, board)
        return [path[-1] for path in jump_paths if len(path) > 1]

    def improved_free_up_target_entry(self, board):
        # 让路逻辑同前
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
