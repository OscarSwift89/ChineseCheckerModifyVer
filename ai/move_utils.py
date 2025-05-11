# ai/move_utils.py
import numpy as np

def get_valid_moves(pos, board):
    x, y = pos
    moves = []
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < board.shape[0] and 0 <= ny < board.shape[1] and board[nx, ny] == 0:
            moves.append((nx, ny))
    return moves

def get_jump_moves(pos, board):
    x, y = pos
    moves = []
    directions = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1),           (0, 1),
                  (1, -1),  (1, 0),  (1, 1)]
    for dx, dy in directions:
        midx, midy = x + dx, y + dy
        landingx, landingy = x + 2 * dx, y + 2 * dy
        if (0 <= midx < board.shape[0] and 0 <= midy < board.shape[1] and board[midx, midy] != 0 and
            0 <= landingx < board.shape[0] and 0 <= landingy < board.shape[1] and board[landingx, landingy] == 0):
            moves.append((landingx, landingy))
    return moves

def get_continuous_jump_moves(pos, board, visited=None, max_depth=5):
    if visited is None:
        visited = set([pos])
    if max_depth <= 0:
        return []
    paths = []
    directions = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1),           (0, 1),
                  (1, -1),  (1, 0),  (1, 1)]
    for dx, dy in directions:
        midx, midy = pos[0] + dx, pos[1] + dy
        landingx, landingy = pos[0] + 2 * dx, pos[1] + 2 * dy
        if (0 <= midx < board.shape[0] and 0 <= midy < board.shape[1] and board[midx, midy] != 0 and
            0 <= landingx < board.shape[0] and 0 <= landingy < board.shape[1] and board[landingx, landingy] == 0):
            target = (landingx, landingy)
            if target not in visited:
                paths.append([pos, target])
                new_visited = set(visited)
                new_visited.add(target)
                further_paths = get_continuous_jump_moves(target, board, new_visited, max_depth-1)
                for fp in further_paths:
                    if fp[0] == pos:
                        continue
                    paths.append([pos] + fp[1:])
    return paths

def get_all_moves(board, player_id, only_from=None):
    moves = []
    positions = [tuple(p) for p in np.argwhere(board == player_id)]
    if only_from is not None:
        positions = [only_from]
    for pos in positions:
        # 普通移动
        for m in get_valid_moves(pos, board):
            moves.append((pos, m))
        # 跳跃
        for m in get_jump_moves(pos, board):
            moves.append((pos, m))
        # 连续跳跃
        jump_paths = get_continuous_jump_moves(pos, board)
        for path in jump_paths:
            if len(path) > 1:
                moves.append((pos, path[-1]))
    return moves

def free_up_target_entry(board, player_id):
    """
    当目标区域几乎填满，导致最后一个棋子无法进入时，
    尝试腾出目标入口位置，方法是将目标区域内处于入口边界的棋子向内部移动。
    
    四个玩家的目标区域和入口条件：
    - 玩家 1（目标：右下区域，即 row >= 9 且 col >= 9）：若棋子处于 row==9 或 col==9，
      尝试移动到 (row+1, col)、(row, col+1) 或 (row+1, col+1) 中空的单元。
    - 玩家 2（目标：左下区域，即 row >= 9 且 col < 3）：若棋子处于 row==9 或 col==2，
      尝试移动到 (row+1, col)、(row, col-1) 或 (row+1, col-1) 中空的单元。
    - 玩家 3（目标：右上区域，即 row < 3 且 col >= 9）：若棋子处于 row==2 或 col==9，
      尝试移动到 (row-1, col)、(row, col+1) 或 (row-1, col+1) 中空的单元。
    - 玩家 4（目标：左上区域，即 row < 3 且 col < 3）：若棋子处于 row==2 或 col==2，
      尝试移动到 (row-1, col)、(row, col-1) 或 (row-1, col-1) 中空的单元。
    """
    if player_id == 1:
        for row in range(9, 12):
            for col in range(9, 12):
                if board[row, col] == 1:
                    if row == 9 or col == 9:
                        candidates = []
                        if row + 1 < 12 and board[row+1, col] == 0:
                            candidates.append((row+1, col))
                        if col + 1 < 12 and board[row, col+1] == 0:
                            candidates.append((row, col+1))
                        if row + 1 < 12 and col + 1 < 12 and board[row+1, col+1] == 0:
                            candidates.append((row+1, col+1))
                        if candidates:
                            best_candidate = min(candidates, key=lambda pos: abs(pos[0]-11) + abs(pos[1]-11))
                            return ((row, col), best_candidate)
        return None
    elif player_id == 2:
        for row in range(9, 12):
            for col in range(0, 3):
                if board[row, col] == 2:
                    if row == 9 or col == 2:
                        candidates = []
                        if row + 1 < 12 and board[row+1, col] == 0:
                            candidates.append((row+1, col))
                        if col - 1 >= 0 and board[row, col-1] == 0:
                            candidates.append((row, col-1))
                        if row + 1 < 12 and col - 1 >= 0 and board[row+1, col-1] == 0:
                            candidates.append((row+1, col-1))
                        if candidates:
                            best_candidate = min(candidates, key=lambda pos: abs(pos[0]-11) + abs(pos[1]-0))
                            return ((row, col), best_candidate)
        return None
    elif player_id == 3:
        for row in range(0, 3):
            for col in range(9, 12):
                if board[row, col] == 3:
                    if row == 2 or col == 9:
                        candidates = []
                        if row - 1 >= 0 and board[row-1, col] == 0:
                            candidates.append((row-1, col))
                        if col + 1 < 12 and board[row, col+1] == 0:
                            candidates.append((row, col+1))
                        if row - 1 >= 0 and col + 1 < 12 and board[row-1, col+1] == 0:
                            candidates.append((row-1, col+1))
                        if candidates:
                            best_candidate = min(candidates, key=lambda pos: abs(pos[0]-0) + abs(pos[1]-11))
                            return ((row, col), best_candidate)
        return None
    elif player_id == 4:
        for row in range(0, 3):
            for col in range(0, 3):
                if board[row, col] == 4:
                    if row == 2 or col == 2:
                        candidates = []
                        if row - 1 >= 0 and board[row-1, col] == 0:
                            candidates.append((row-1, col))
                        if col - 1 >= 0 and board[row, col-1] == 0:
                            candidates.append((row, col-1))
                        if row - 1 >= 0 and col - 1 >= 0 and board[row-1, col-1] == 0:
                            candidates.append((row-1, col-1))
                        if candidates:
                            best_candidate = min(candidates, key=lambda pos: abs(pos[0]-0) + abs(pos[1]-0))
                            return ((row, col), best_candidate)
        return None
