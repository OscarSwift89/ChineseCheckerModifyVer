# ai/greedy_ai.py
import numpy as np
import random
from .move_utils import get_valid_moves, get_jump_moves, free_up_target_entry

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
        deep_target = self.get_deep_target()
        # 第一步：如果深层目标单元为空，尝试直接将某个棋子移动到深层目标上
        if board[deep_target] == 0:
            positions = [tuple(p) for p in np.argwhere(board == self.player_id)]
            for pos in positions:
                valid_moves = get_valid_moves(pos, board) + get_jump_moves(pos, board)
                if deep_target in valid_moves:
                    return (pos, deep_target)

        # 改进：只要目标区入口被己方棋子占据且入口外有己方棋子等待进入，就主动让路
        move_to_free = self.improved_free_up_target_entry(board)
        if move_to_free:
            return move_to_free

        # 第三步：正常的策略
        all_positions = [tuple(p) for p in np.argwhere(board == self.player_id)]
        outside_positions = [pos for pos in all_positions if not self.in_target_area(pos)]
        positions_to_consider = outside_positions if outside_positions else [pos for pos in all_positions if not self.in_stable_area(pos)]
        
        bonus = 50  # 提高进入目标区域的奖励
        if outside_positions and len(outside_positions) == 1:
            bonus = 200  # 提高最后一个棋子的奖励

        best_move = None
        best_improvement = -float('inf')
        fallback_move = None
        best_fallback = float('inf')
        random.shuffle(positions_to_consider)
        
        for pos in positions_to_consider:
            if self.in_target_area(pos) and self.in_stable_area(pos):
                continue
            candidate_moves = get_valid_moves(pos, board) + get_jump_moves(pos, board)
            if self.in_target_area(pos):
                candidate_moves = [m for m in candidate_moves if self.in_target_area(m)]
                candidate_moves.sort(key=lambda m: self.calculate_score(m))
            current_score = self.calculate_score(pos)
            for candidate in candidate_moves:
                new_score = self.calculate_score(candidate)
                improvement = current_score - new_score
                if not self.in_target_area(pos) and self.in_target_area(candidate):
                    improvement += bonus
                if not self.in_stable_area(pos) and self.in_stable_area(candidate):
                    improvement += bonus * 2
                if improvement > best_improvement:
                    best_improvement = improvement
                    best_move = (pos, candidate)
                if new_score < best_fallback:
                    best_fallback = new_score
                    fallback_move = (pos, candidate)
        return best_move if best_move is not None else fallback_move

    def improved_free_up_target_entry(self, board):
        # 只要目标区入口被己方棋子占据且入口外有己方棋子等待进入，就主动让路
        if self.player_id == 1:
            # 右下角入口
            entry_positions = [(8, 11), (9, 10), (10, 9), (11, 8)]
            waiting = [pos for pos in np.argwhere(board == 1) if not self.in_target_area(tuple(pos))]
            for entry in entry_positions:
                if board[entry] == 1:
                    # 尝试将入口棋子往更深处移动
                    candidates = []
                    for dx, dy in [(1,0),(0,1),(1,1)]:
                        nx, ny = entry[0]+dx, entry[1]+dy
                        if 0<=nx<12 and 0<=ny<12 and board[nx,ny]==0 and self.in_target_area((nx,ny)):
                            candidates.append((nx,ny))
                    if candidates and waiting:
                        best_candidate = min(candidates, key=lambda pos: abs(pos[0]-11)+abs(pos[1]-11))
                        return (entry, best_candidate)
            # 新增：目标区内棋子主动退出目标区
            if waiting:
                for pos in np.argwhere(board == 1):
                    pos = tuple(pos)
                    if self.in_target_area(pos):
                        for dx, dy in [(-1,0),(0,-1),(-1,-1)]:
                            nx, ny = pos[0]+dx, pos[1]+dy
                            if 0<=nx<12 and 0<=ny<12 and not self.in_target_area((nx,ny)) and board[nx,ny]==0:
                                return (pos, (nx,ny))
        elif self.player_id == 2:
            # 左上角入口
            entry_positions = [(3,0), (2,1), (1,2), (0,3)]
            waiting = [pos for pos in np.argwhere(board == 2) if not self.in_target_area(tuple(pos))]
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
            # 新增：目标区内棋子主动退出目标区
            if waiting:
                for pos in np.argwhere(board == 2):
                    pos = tuple(pos)
                    if self.in_target_area(pos):
                        for dx, dy in [(1,0),(0,1),(1,1)]:
                            nx, ny = pos[0]+dx, pos[1]+dy
                            if 0<=nx<12 and 0<=ny<12 and not self.in_target_area((nx,ny)) and board[nx,ny]==0:
                                return (pos, (nx,ny))
        return None
