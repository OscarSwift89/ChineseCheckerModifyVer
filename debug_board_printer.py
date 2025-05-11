import numpy as np
import os

def print_board(board):
    symbols = {0: '.', 1: 'R', 2: 'B'}
    print("棋盘状态：")
    for row in board:
        print(' '.join([symbols[cell] for cell in row]))
    print()

def print_player_positions(board):
    for player in [1, 2]:
        positions = np.argwhere(board == player)
        print(f"玩家{player}棋子位置: {[tuple(pos) for pos in positions]}")

def save_board_to_file(board, step, folder="boards"):
    os.makedirs(folder, exist_ok=True)
    filename = os.path.join(folder, f"board_step_{step}.txt")
    with open(filename, 'w', encoding='utf-8') as f:
        symbols = {0: '.', 1: 'R', 2: 'B'}
        for row in board:
            f.write(' '.join([symbols[cell] for cell in row]) + '\n')

class MoveTracker:
    def __init__(self):
        self.tracks = {1: {}, 2: {}}  # {player: {起始位置: [轨迹列表]}}

    def update(self, board, prev_board):
        for player in [1, 2]:
            prev_positions = set(map(tuple, np.argwhere(prev_board == player)))
            curr_positions = set(map(tuple, np.argwhere(board == player)))
            # 检查每个棋子的移动
            for pos in curr_positions:
                if pos not in prev_positions:
                    # 新位置，找到最近的旧位置
                    if player not in self.tracks:
                        self.tracks[player] = {}
                    # 找到距离最近的旧位置
                    if prev_positions:
                        old_pos = min(prev_positions, key=lambda p: abs(p[0]-pos[0])+abs(p[1]-pos[1]))
                        self.tracks[player].setdefault(old_pos, [old_pos]).append(pos)
                    else:
                        self.tracks[player][pos] = [pos]

    def save_tracks(self, filename="move_tracks.txt"):
        with open(filename, 'w', encoding='utf-8') as f:
            for player in self.tracks:
                f.write(f"玩家{player}棋子移动轨迹：\n")
                for start, track in self.tracks[player].items():
                    f.write(f"  起点{start}: {track}\n")

if __name__ == "__main__":
    from board import Board
    b = Board()
    print_board(b.board)
    print_player_positions(b.board)
    save_board_to_file(b.board, 0)
    # 示例：模拟两步移动
    prev = b.board.copy()
    b.move_piece((0,0), (1,1))
    save_board_to_file(b.board, 1)
    tracker = MoveTracker()
    tracker.update(b.board, prev)
    tracker.save_tracks() 