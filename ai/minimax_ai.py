# ai/minimax_ai.py
import numpy as np
import random
from .move_utils import get_all_moves, free_up_target_entry

class MinimaxAI:
    def __init__(self, player_id, depth=2):
        self.player_id = player_id
        self.depth = depth

    def choose_move(self, board):
        move_to_free = free_up_target_entry(board, self.player_id)
        if move_to_free:
            return move_to_free
        
        moves = get_all_moves(board, self.player_id)
        if not moves:
            return None
        best_val = -float('inf')
        best_move = None
        for move in moves:
            new_board = self.simulate_move(board, move)
            val = self.min_value(new_board, self.depth - 1, -float('inf'), float('inf'))
            if val > best_val:
                best_val = val
                best_move = move
        return best_move

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

    def min_value(self, board, depth, alpha, beta):
        # 为简化起见，固定选择一个对手（例如：如果自己不是 1 则对手用 1，否则用 2）
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

    def simulate_move(self, board, move):
        new_board = board.copy()
        from_pos, to_pos = move
        new_board[to_pos] = new_board[from_pos]
        new_board[from_pos] = 0
        return new_board

    def evaluate(self, board):
        if self.player_id == 1:
            my_target = (11, 11)
        elif self.player_id == 2:
            my_target = (0, 0)
        elif self.player_id == 3:
            my_target = (0, 11)
        elif self.player_id == 4:
            my_target = (11, 0)
            
        my_pieces = np.argwhere(board == self.player_id)
        score = 0
        
        # 计算每个棋子到目标的距离
        for piece in my_pieces:
            distance = abs(piece[0] - my_target[0]) + abs(piece[1] - my_target[1])
            score -= distance * 2  # 距离越近分数越高
            
            # 如果棋子在目标区域内，给予额外奖励
            if self.in_target_area(tuple(piece)):
                score += 50
                # 如果棋子在稳定区域内，给予更多奖励
                if self.in_stable_area(tuple(piece)):
                    score += 100
                    
        return score

    def in_target_area(self, pos):
        if self.player_id == 1:
            # 右下角三角形区域
            return (pos[0] >= 8 and pos[1] >= 8 and 
                   (pos[0] + pos[1] >= 16))  # 确保在三角形区域内
        elif self.player_id == 2:
            # 左上角三角形区域
            return (pos[0] <= 3 and pos[1] <= 3 and 
                   (pos[0] + pos[1] <= 6))  # 确保在三角形区域内
        elif self.player_id == 3:
            # 右上角三角形区域
            return (pos[0] <= 3 and pos[1] >= 8 and 
                   (pos[1] - pos[0] >= 5))  # 确保在三角形区域内
        elif self.player_id == 4:
            # 左下角三角形区域
            return (pos[0] >= 8 and pos[1] <= 3 and 
                   (pos[0] - pos[1] >= 5))  # 确保在三角形区域内
        return False

    def in_stable_area(self, pos):
        if self.player_id == 1:
            # 右下角三角形稳定区域
            return (pos[0] >= 9 and pos[1] >= 9 and 
                   (pos[0] + pos[1] >= 18))  # 确保在三角形区域内
        elif self.player_id == 2:
            # 左上角三角形稳定区域
            return (pos[0] <= 2 and pos[1] <= 2 and 
                   (pos[0] + pos[1] <= 4))  # 确保在三角形区域内
        elif self.player_id == 3:
            # 右上角三角形稳定区域
            return (pos[0] <= 2 and pos[1] >= 9 and 
                   (pos[1] - pos[0] >= 7))  # 确保在三角形区域内
        elif self.player_id == 4:
            # 左下角三角形稳定区域
            return (pos[0] >= 9 and pos[1] <= 2 and 
                   (pos[0] - pos[1] >= 7))  # 确保在三角形区域内
        return False

    def terminal(self, board):
        # 检查每个玩家的三角形目标区域是否填满
        p1_done = sum(1 for i in range(8, 12) for j in range(8, 12) 
                     if i + j >= 16 and board[i, j] == 1) == 10
        p2_done = sum(1 for i in range(0, 4) for j in range(0, 4) 
                     if i + j <= 6 and board[i, j] == 2) == 10
        p3_done = sum(1 for i in range(0, 4) for j in range(8, 12) 
                     if j - i >= 5 and board[i, j] == 3) == 10
        p4_done = sum(1 for i in range(8, 12) for j in range(0, 4) 
                     if i - j >= 5 and board[i, j] == 4) == 10
        return p1_done or p2_done or p3_done or p4_done
