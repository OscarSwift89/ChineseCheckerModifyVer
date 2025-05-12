import numpy as np
from colorama import Fore, Style

class Board:
    def __init__(self):
        # 初始化 12x12 棋盘，全为 0 表示空位
        self.board = np.zeros((12, 12), dtype=int)
        # 奖励点定义：钻石+3分，黄金+1分
        self.diamond_points = [(5,5), (6,6)]
        self.gold_points = [(5,6), (6,5)]
        self.init_pieces()

    def get_points_score(self, player_id):
        score = 0
        for pos in self.diamond_points:
            if self.board[pos] == player_id:
                score += 3
        for pos in self.gold_points:
            if self.board[pos] == player_id:
                score += 1
        return score


    def init_pieces(self):
        """
        两人中国跳棋起始布局：  
          - 玩家1起始区域：左上角三角形，目标区域：右下角三角形
          - 玩家2起始区域：右下角三角形，目标区域：左上角三角形
        """
        # 玩家1的棋子（编号1）放在左上角三角形
        # 第1层
        self.board[0, 0] = 1
        # 第2层
        self.board[0, 1] = 1
        self.board[1, 0] = 1
        # 第3层
        self.board[0, 2] = 1
        self.board[1, 1] = 1
        self.board[2, 0] = 1
        # 第4层
        self.board[0, 3] = 1
        self.board[1, 2] = 1
        self.board[2, 1] = 1
        self.board[3, 0] = 1

        # 玩家2的棋子（编号2）放在右下角三角形
        # 第1层
        self.board[11, 11] = 2
        # 第2层
        self.board[11, 10] = 2
        self.board[10, 11] = 2
        # 第3层
        self.board[11, 9] = 2
        self.board[10, 10] = 2
        self.board[9, 11] = 2
        # 第4层
        self.board[11, 8] = 2
        self.board[10, 9] = 2
        self.board[9, 10] = 2
        self.board[8, 11] = 2

    def move_piece(self, from_pos, to_pos):
        """移动棋子，如果目标位置为空则移动成功"""
        if self.board[to_pos] == 0:
            self.board[to_pos] = self.board[from_pos]
            self.board[from_pos] = 0
            return True
        return False

    def get_valid_moves(self, pos):
        """获取指定位置的所有基本（上下左右）合法移动"""
        x, y = pos
        moves = []
        directions = [(-1,0), (1,0), (0,-1), (0,1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 12 and 0 <= ny < 12 and self.board[nx, ny] == 0:
                moves.append((nx, ny))
        return moves

    def get_jump_moves(self, pos):
        """获取指定位置的所有跳跃移动（检查8个方向）"""
        x, y = pos
        jumps = []
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),           (0, 1),
                      (1, -1),  (1, 0),  (1, 1)]
        for dx, dy in directions:
            midx, midy = x + dx, y + dy
            landingx, landingy = x + 2*dx, y + 2*dy
            if (0 <= midx < 12 and 0 <= midy < 12 and self.board[midx, midy] != 0 and
                0 <= landingx < 12 and 0 <= landingy < 12 and self.board[landingx, landingy] == 0):
                jumps.append((landingx, landingy))
        return jumps

    def is_game_over(self):
        """
        胜利条件：当某一玩家的所有棋子都到达目标区域并且目标区域被填满时，返回 True
        """
        # 检查玩家1是否所有棋子都到达右下角三角形目标区域
        p1_target_positions = [
            (11, 11),  # 第1层
            (11, 10), (10, 11),  # 第2层
            (11, 9), (10, 10), (9, 11),  # 第3层
            (11, 8), (10, 9), (9, 10), (8, 11)  # 第4层
        ]
        p1_pieces = np.argwhere(self.board == 1)
        p1_all_in_target = all(self.in_target_area(tuple(pos)) for pos in p1_pieces)
        p1_target_filled = all(self.board[pos] == 1 for pos in p1_target_positions)

        # 检查玩家2是否所有棋子都到达左上角三角形目标区域
        p2_target_positions = [
            (0, 0),  # 第1层
            (0, 1), (1, 0),  # 第2层
            (0, 2), (1, 1), (2, 0),  # 第3层
            (0, 3), (1, 2), (2, 1), (3, 0)  # 第4层
        ]
        p2_pieces = np.argwhere(self.board == 2)
        p2_all_in_target = all(self.in_target_area(tuple(pos)) for pos in p2_pieces)
        p2_target_filled = all(self.board[pos] == 2 for pos in p2_target_positions)

        return (p1_all_in_target and p1_target_filled) or (p2_all_in_target and p2_target_filled)

    def in_target_area(self, pos):
        """检查位置是否在目标区域内"""
        x, y = pos
        # 玩家1的目标区域（右下角三角形）
        if self.board[pos] == 1:
            return (x >= 8 and y >= 8 and (x + y >= 16))
        # 玩家2的目标区域（左上角三角形）
        elif self.board[pos] == 2:
            return (x <= 3 and y <= 3 and (x + y <= 6))
        return False

    def render(self):
        """彩色渲染棋盘至终端"""
        symbols = {
            0: Fore.WHITE + '.' + Style.RESET_ALL,
            1: Fore.RED + '●' + Style.RESET_ALL,
            2: Fore.BLUE + '●' + Style.RESET_ALL
        }
        print("\n当前棋盘状态：")
        for row in self.board:
            print(' '.join([symbols[cell] for cell in row]))
        print("\n" + "=" * 33 + "\n")
