import numpy as np
from collections import deque

class DebugAgentWrapper:
    def __init__(self, agent, player_id, max_repeat=20, board_history_len=10):
        self.agent = agent
        self.player_id = player_id
        self.last_moves = deque(maxlen=max_repeat)
        self.last_boards = deque(maxlen=board_history_len)
        self.max_repeat = max_repeat
        self.board_history_len = board_history_len

    def choose_move(self, board):
        move = self.agent.choose_move(board)
        if move:
            self.last_moves.append(move)
            # 检查是否一直在移动同一个棋子
            from_positions = [m[0] for m in self.last_moves]
            if len(set(from_positions)) == 1 and len(self.last_moves) == self.max_repeat:
                print(f"[Debug] 警告：玩家{self.player_id}连续{self.max_repeat}步只移动棋子{from_positions[0]}，可能卡死！")
        # 检查棋盘状态是否长时间未变
        board_hash = hash(board.tobytes())
        self.last_boards.append(board_hash)
        if len(set(self.last_boards)) == 1 and len(self.last_boards) == self.board_history_len:
            print(f"[Debug] 警告：玩家{self.player_id}最近{self.board_history_len}步棋盘状态未变，可能卡死！")
        return move 