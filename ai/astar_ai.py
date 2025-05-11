# ai/astar_ai.py
import numpy as np
import heapq
import random
from .move_utils import get_valid_moves, get_jump_moves, get_all_moves, get_continuous_jump_moves

class AStarAI:
    def __init__(self, player_id):
        self.player_id = player_id

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

        # —— 2. 对“场外”棋子做 A* 路径规划 —— #
        best_move, best_score = None, float('inf')
        random.shuffle(outside)
        for pos in outside:
            path = self.a_star(pos, board)
            if path and len(path) >= 2:
                score = self.heuristic(path[1])
                if score < best_score:
                    best_score, best_move = score, (pos, path[1])
        if best_move:
            return best_move

        # —— 3. 降级到“全部棋子” —— #
        for pos in all_positions:
            path = self.a_star(pos, board)
            if path and len(path) >= 2:
                score = self.heuristic(path[1])
                if score < best_score:
                    best_score, best_move = score, (pos, path[1])
        return best_move


    def a_star(self, start, board):
        open_set = []
        heapq.heappush(open_set, (self.heuristic(start), start))
        came_from = {}
        g_score = {start: 0}
        while open_set:
            current_f, current = heapq.heappop(open_set)
            if self.in_target_area(current) and board[current] == 0:
                return self.reconstruct_path(came_from, current)
            for neighbor in self.get_neighbors(current, board):
                tentative_g = g_score[current] + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f = tentative_g + self.heuristic(neighbor)
                    heapq.heappush(open_set, (f, neighbor))
        return None

    def reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    def get_neighbors(self, pos, board):
        return get_valid_moves(pos, board) + get_jump_moves(pos, board) + self.get_all_jump_targets(pos, board)

    def heuristic(self, pos):
        if self.player_id == 1:
            target = (11, 11)
        else:
            target = (0, 0)
        return abs(pos[0] - target[0]) + abs(pos[1] - target[1])

    def get_all_jump_targets(self, pos, board):
        jump_paths = get_continuous_jump_moves(pos, board)
        return [path[-1] for path in jump_paths if len(path) > 1]

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
