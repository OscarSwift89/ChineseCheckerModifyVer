#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import psutil
import os
import numpy as np
import random
import tracemalloc

# 为了加快模拟速度，取消 sleep 延时
time.sleep = lambda x: None

# 导入棋盘和 AI 模块（请确保路径和文件名正确）
from board import Board
from ai.greedy_ai import GreedyAI
from ai.astar_ai import AStarAI
from ai.minimax_ai import MinimaxAI

def simulate_game_with_stats(max_moves, agents):
    """
    模拟一局游戏：
      - max_moves: 最大走子步数（例如 1分钟=60步）
      - agents: 字典 {1: agent1, 2: agent2}
    游戏结束或达到最大步数后，统计目标区域中各玩家的棋子数，
    若全部为0则返回 winner = 0（表示平局），否则取得分最高者为胜者。
    同时记录每步决策的耗时和内存峰值。
    返回字典，格式：
      {'winner': winner, 'moves': 实际走步, 'stats': {p: {'times': [...], 'mems': [...]}}}
    """
    board_instance = Board()  # 初始棋盘（要求初始布局采用对角起始，使目标区域为空）
    current_player = 1
    moves_count = 0
    process = psutil.Process(os.getpid())
    
    # 初始化每个玩家决策统计
    stats = {1: {'times': [], 'mems': []},
             2: {'times': [], 'mems': []}}
    
    while moves_count < max_moves and not board_instance.is_game_over():
        agent = agents[current_player]
        tracemalloc.start()
        start_time = time.time()
        move = agent.choose_move(board_instance.board)
        step_time = time.time() - start_time
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        stats[current_player]['times'].append(step_time)
        stats[current_player]['mems'].append(peak)
        
        if move:
            from_pos, to_pos = move
            board_instance.move_piece(from_pos, to_pos)
        moves_count += 1
        current_player = 2 if current_player == 1 else 1

    board_arr = board_instance.board
    # 目标区域得分统计
    p1_score = np.count_nonzero(board_arr[9:12, 9:12] == 1)  # 玩家1目标区域：右下
    p2_score = np.count_nonzero(board_arr[0:3, 0:3] == 2)    # 玩家2目标区域：左上
    scores = {1: p1_score, 2: p2_score}
    # 如果所有玩家的得分都为 0，则返回 winner = 0 表示平局
    if all(score == 0 for score in scores.values()):
        winner = 0
    else:
        winner = max(scores, key=scores.get)
    
    return {'winner': winner, 'moves': moves_count, 'stats': stats}

def simulate_battles(time_limit_minutes, rounds=10):
    """
    针对指定游戏时长（分钟），进行 rounds 盘模拟。
    时长以走子步数表示（例如 1分钟=60步）。
    返回统计数据：包括每个玩家的胜局数、胜率、平均每步决策时间和平均每步内存使用（字节）。
    """
    max_moves = time_limit_minutes * 60
    print(f"\n开始模拟：游戏时长 {time_limit_minutes} 分钟（最多 {max_moves} 步），共 {rounds} 盘。")
    
    # 固定 Agent 分配：玩家1：Greedy，玩家2：A* 算法
    agents_template = {
        1: GreedyAI(1),
        2: AStarAI(2)
    }
    
    round_results = []
    for i in range(rounds):
        result = simulate_game_with_stats(max_moves, agents_template)
        round_results.append(result)
        # 输出每局结果
        if result['winner'] == 0:
            print(f"局 {i+1:2d}: 平局, Moves = {result['moves']}")
        else:
            print(f"局 {i+1:2d}: Winner = {result['winner']}, Moves = {result['moves']}")
    
    win_counts = {1: 0, 2: 0}
    total_times = {1: 0.0, 2: 0.0}
    total_mems = {1: 0, 2: 0}
    total_steps = {1: 0, 2: 0}
    
    # 统计所有局中各玩家的决策数据与胜局
    for res in round_results:
        # 如果为平局（winner=0）则不计入任何玩家胜局
        if res['winner'] in win_counts:
            win_counts[res['winner']] += 1
        stats = res['stats']
        for p in [1,2]:
            total_times[p] += sum(stats[p]['times'])
            total_mems[p] += sum(stats[p]['mems'])
            total_steps[p] += len(stats[p]['times'])
    
    avg_times = {p: (total_times[p] / total_steps[p] if total_steps[p]>0 else 0) for p in [1,2]}
    avg_mems = {p: (total_mems[p] / total_steps[p] if total_steps[p]>0 else 0) for p in [1,2]}
    win_rates = {p: (win_counts[p] / rounds * 100) for p in [1,2]}
    
    results = {
        'win_counts': win_counts,
        'win_rates': win_rates,
        'avg_times': avg_times,
        'avg_mems': avg_mems
    }
    return results

def print_results_table(time_limit, results):
    print("\n========================================")
    print(f"游戏时长：约 {time_limit} 分钟   (10 盘模拟)")
    print("------------------------------------------------")
    print(f"{'Algorithm':<12}{'Wins':>8}{'Win Rate':>10}{'Avg Time/Step(s)':>20}{'Avg Mem/Step(MB)':>22}")
    print("------------------------------------------------")
    # 固定对应：玩家1：Greedy, 玩家2：A* 算法
    algo_names = {1: "Greedy", 2: "A star"}
    for p in [1, 2]:
        wins = results['win_counts'][p]
        rate = results['win_rates'][p]
        avg_time = results['avg_times'][p]
        avg_mem = results['avg_mems'][p] / (1024*1024)  # 转为 MB
        print(f"{algo_names[p]:<12}{wins:8d}{rate:9.1f}%{avg_time:20.3f}{avg_mem:22.2f}")
    print("========================================\n")

if __name__ == '__main__':
    # 模拟不同游戏时长：1～5分钟分别进行 10 局模拟
    durations = [1, 2, 3, 4, 5]
    rounds = 10
    for t in durations:
        res = simulate_battles(t, rounds)
        print_results_table(t, res)
