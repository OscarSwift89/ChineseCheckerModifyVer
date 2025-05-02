import tkinter as tk
from tkinter import ttk
import time
import tracemalloc
import psutil
import os
import numpy as np
from PIL import Image, ImageTk

from game import Game
from ai.greedy_ai import GreedyAI
from ai.astar_ai import AStarAI

class GameGUI:
    def __init__(self, root, p1_ai, p2_ai, game_duration):
        self.root = root
        self.game_duration = game_duration  # 游戏总时长（秒）
        
        # 保存各个 agent 实例，确保正确显示算法名称
        self.agents = {1: p1_ai, 2: p2_ai}
        
        # 创建游戏实例
        self.game = Game(p1_ai, p2_ai)
        
        # 定义棋子颜色与目标区域颜色的映射
        self.piece_colors = {1: "#FF4444", 2: "#4444FF"}  # 更鲜艳的颜色
        self.target_colors = {1: "#FFCCCC", 2: "#CCCCFF"}  # 更柔和的颜色
        self.highlight_color = "#FFFF00"  # 高亮颜色
        self.valid_move_color = "#00FF00"  # 有效移动颜色
        
        # 定义颜色名称映射
        self.color_names = {1: "红色", 2: "蓝色"}
        
        # 创建 Canvas 绘制棋盘
        self.canvas = tk.Canvas(root, width=600, height=600, bg="#F0F0F0", highlightthickness=0)
        self.canvas.grid(row=0, column=0, padx=10, pady=10)
        
        # 创建右侧信息面板，并放入滚动区域
        self.info_frame = tk.Frame(root, bg="#F0F0F0")
        self.info_frame.grid(row=0, column=1, sticky="n", padx=10, pady=10)
        self.create_scrollable_info_panel()
        
        self.cell_size = 600 // 12
        
        # 记录每个玩家决策统计数据
        self.stats = {i: {'decision_time': 0.0, 'cumulative_time': 0.0, 'decision_count': 0, 'latest_mem': 0} for i in range(1,3)}
        self.start_time = time.perf_counter()
        self.process = psutil.Process(os.getpid())
        
        # 动画相关变量
        self.animation_in_progress = False
        self.animation_speed = 10  # 动画速度（像素/帧）
        self.animation_delay = 20  # 动画延迟（毫秒）
        
        self.update_board()
        self.root.after(1000, self.game_step)

    def create_scrollable_info_panel(self):
        # 创建一个 canvas 实现滚动效果
        self.info_canvas = tk.Canvas(self.info_frame, width=300, height=600, bg="#F0F0F0", highlightthickness=0)
        self.info_scrollbar = tk.Scrollbar(self.info_frame, orient="vertical", command=self.info_canvas.yview)
        self.info_canvas.configure(yscrollcommand=self.info_scrollbar.set)
        self.info_scrollbar.pack(side="right", fill="y")
        self.info_canvas.pack(side="left", fill="both", expand=True)
        self.inner_info_frame = tk.Frame(self.info_canvas, bg="#F0F0F0")
        self.inner_info_frame.bind("<Configure>", lambda e: self.info_canvas.configure(scrollregion=self.info_canvas.bbox("all")))
        self.info_canvas.create_window((0,0), window=self.inner_info_frame, anchor="nw")
        
        self.create_info_panel()

    def create_info_panel(self):
        # 每个玩家一块显示区域
        self.info_labels = {}
        self.player_frames = {}
        for player in range(1, 3):
            frame = tk.Frame(self.inner_info_frame, bd=2, relief="groove", padx=5, pady=5, bg="#FFFFFF")
            frame.pack(fill="x", pady=5)
            self.player_frames[player] = frame
            
            # 第一行动态显示【玩家号：算法 - 棋子颜色】
            header_text = f"玩家 {player}: {self.agents[player].__class__.__name__} - {self.color_names[player]}"
            header_label = tk.Label(frame, text=header_text, font=("Arial", 12, "bold"), bg="#FFFFFF", fg=self.piece_colors[player])
            header_label.pack(anchor="w")
            
            stat_labels = {}
            stat_labels['current_time'] = tk.Label(frame, text="当前决策耗时: -", bg="#FFFFFF")
            stat_labels['current_time'].pack(anchor="w")
            stat_labels['cumulative_time'] = tk.Label(frame, text="累计决策耗时: -", bg="#FFFFFF")
            stat_labels['cumulative_time'].pack(anchor="w")
            stat_labels['decision_count'] = tk.Label(frame, text="决策次数: -", bg="#FFFFFF")
            stat_labels['decision_count'].pack(anchor="w")
            stat_labels['latest_mem'] = tk.Label(frame, text="最新决策内存: -", bg="#FFFFFF")
            stat_labels['latest_mem'].pack(anchor="w")
            self.info_labels[player] = stat_labels
        
        # 整体信息
        self.total_mem_label = tk.Label(self.inner_info_frame, text="总内存消耗: -", bg="#FFFFFF")
        self.total_mem_label.pack(anchor="w", pady=(10,0))
        self.elapsed_label = tk.Label(self.inner_info_frame, text="游戏运行时间: -", bg="#FFFFFF")
        self.elapsed_label.pack(anchor="w", pady=(0,10))
        self.score_label = tk.Label(self.inner_info_frame, text="分数：\n玩家1: 0\n玩家2: 0", 
                                  font=("Arial", 12, "bold"), bg="#FFFFFF")
        self.score_label.pack(anchor="w", pady=(10,0))

    def animate_piece_movement(self, from_pos, to_pos, player):
        if self.animation_in_progress:
            return
            
        self.animation_in_progress = True
        from_x, from_y = from_pos
        to_x, to_y = to_pos
        
        # 计算起始和结束的像素坐标
        start_x = from_y * self.cell_size + self.cell_size // 2
        start_y = from_x * self.cell_size + self.cell_size // 2
        end_x = to_y * self.cell_size + self.cell_size // 2
        end_y = to_x * self.cell_size + self.cell_size // 2
        
        # 创建移动的棋子
        piece = self.canvas.create_oval(
            start_x - self.cell_size//3,
            start_y - self.cell_size//3,
            start_x + self.cell_size//3,
            start_y + self.cell_size//3,
            fill=self.piece_colors[player],
            outline="black",
            width=2
        )
        
        def move_piece():
            current_x = self.canvas.coords(piece)[0] + self.cell_size//3
            current_y = self.canvas.coords(piece)[1] + self.cell_size//3
            
            if abs(current_x - end_x) < self.animation_speed and abs(current_y - end_y) < self.animation_speed:
                self.canvas.delete(piece)
                self.animation_in_progress = False
                self.update_board()
                return
                
            dx = (end_x - current_x) * self.animation_speed / 100
            dy = (end_y - current_y) * self.animation_speed / 100
            
            self.canvas.move(piece, dx, dy)
            self.root.after(self.animation_delay, move_piece)
            
        move_piece()

    def highlight_valid_moves(self, position):
        # 清除之前的高亮
        self.canvas.delete("highlight")
        
        # 获取所有有效移动
        valid_moves = self.game.board.get_valid_moves(position)
        
        # 高亮显示有效移动
        for move in valid_moves:
            x, y = move
            self.canvas.create_rectangle(
                y * self.cell_size,
                x * self.cell_size,
                (y + 1) * self.cell_size,
                (x + 1) * self.cell_size,
                fill=self.valid_move_color,
                stipple="gray50",
                tags="highlight"
            )

    def update_info_panel(self, elapsed, total_mem):
        for player in range(1, 3):
            cur = self.stats[player]
            self.info_labels[player]['current_time'].config(text=f"当前决策耗时: {cur['decision_time']*1000:.1f} ms")
            self.info_labels[player]['cumulative_time'].config(text=f"累计决策耗时: {cur['cumulative_time']:.2f} s")
            self.info_labels[player]['decision_count'].config(text=f"决策次数: {cur['decision_count']}")
            self.info_labels[player]['latest_mem'].config(text=f"最新决策内存: {cur['latest_mem'] / 1024:.1f} KB")
        self.total_mem_label.config(text=f"总内存消耗: {total_mem / (1024*1024):.1f} MB")
        self.elapsed_label.config(text=f"游戏运行时间: {elapsed:.1f} s")
        
        board = self.game.board.board
        # 计算玩家1在右下角三角形区域的得分
        p1_target_positions = [
            (11, 11),  # 第1层
            (11, 10), (10, 11),  # 第2层
            (11, 9), (10, 10), (9, 11),  # 第3层
            (11, 8), (10, 9), (9, 10), (8, 11)  # 第4层
        ]
        p1_score = sum(1 for pos in p1_target_positions if board[pos] == 1)

        # 计算玩家2在左上角三角形区域的得分
        p2_target_positions = [
            (0, 0),  # 第1层
            (0, 1), (1, 0),  # 第2层
            (0, 2), (1, 1), (2, 0),  # 第3层
            (0, 3), (1, 2), (2, 1), (3, 0)  # 第4层
        ]
        p2_score = sum(1 for pos in p2_target_positions if board[pos] == 2)

        score_text = f"分数：\n玩家1: {p1_score}\n玩家2: {p2_score}"
        self.score_label.config(text=score_text)

    def update_board(self):
        self.canvas.delete("all")
        board = self.game.board.board
        
        # 绘制棋盘背景
        for i in range(12):
            for j in range(12):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                # 检查是否在玩家1的目标区域（右下角三角形）
                if ((i == 11 and j == 11) or
                    (i == 11 and j == 10) or (i == 10 and j == 11) or
                    (i == 11 and j == 9) or (i == 10 and j == 10) or (i == 9 and j == 11) or
                    (i == 11 and j == 8) or (i == 10 and j == 9) or (i == 9 and j == 10) or (i == 8 and j == 11)):
                    fill_color = self.target_colors[1]
                # 检查是否在玩家2的目标区域（左上角三角形）
                elif ((i == 0 and j == 0) or
                      (i == 0 and j == 1) or (i == 1 and j == 0) or
                      (i == 0 and j == 2) or (i == 1 and j == 1) or (i == 2 and j == 0) or
                      (i == 0 and j == 3) or (i == 1 and j == 2) or (i == 2 and j == 1) or (i == 3 and j == 0)):
                    fill_color = self.target_colors[2]
                else:
                    fill_color = "white"
                
                # 绘制格子
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black", width=1)
                
                # 绘制棋子
                if board[i, j] == 1:
                    self.canvas.create_oval(
                        x1 + 5, y1 + 5,
                        x2 - 5, y2 - 5,
                        fill=self.piece_colors[1],
                        outline="black",
                        width=2
                    )
                elif board[i, j] == 2:
                    self.canvas.create_oval(
                        x1 + 5, y1 + 5,
                        x2 - 5, y2 - 5,
                        fill=self.piece_colors[2],
                        outline="black",
                        width=2
                    )

    def game_step(self):
        elapsed = time.perf_counter() - self.start_time
        total_mem = self.process.memory_info().rss
        
        if elapsed >= self.game_duration:
            board = self.game.board.board
            # 计算玩家1在右下角三角形区域的得分
            p1_target_positions = [
                (11, 11),  # 第1层
                (11, 10), (10, 11),  # 第2层
                (11, 9), (10, 10), (9, 11),  # 第3层
                (11, 8), (10, 9), (9, 10), (8, 11)  # 第4层
            ]
            p1_score = sum(1 for pos in p1_target_positions if board[pos] == 1)

            # 计算玩家2在左上角三角形区域的得分
            p2_target_positions = [
                (0, 0),  # 第1层
                (0, 1), (1, 0),  # 第2层
                (0, 2), (1, 1), (2, 0),  # 第3层
                (0, 3), (1, 2), (2, 1), (3, 0)  # 第4层
            ]
            p2_score = sum(1 for pos in p2_target_positions if board[pos] == 2)

            scores = {1: p1_score, 2: p2_score}
            winner = max(scores, key=scores.get)
            
            # 创建胜利动画
            victory_text = f"玩家 {winner} ({self.color_names[winner]}) 胜利！"
            print(victory_text)  # 在终端也打印胜利信息
            
            self.canvas.create_text(
                300, 300,
                text=victory_text,
                font=("Arial", 36, "bold"),
                fill=self.piece_colors[winner],
                tags="victory"
            )
            
            # 添加闪烁效果
            def blink_text():
                if not hasattr(self, '_blink_count'):
                    self._blink_count = 0
                if self._blink_count < 10:  # 闪烁5次（10次颜色变化）
                    current_color = self.canvas.itemcget("victory", "fill")
                    new_color = "white" if current_color == self.piece_colors[winner] else self.piece_colors[winner]
                    self.canvas.itemconfig("victory", fill=new_color)
                    self._blink_count += 1
                    self.root.after(500, blink_text)
            
            blink_text()
            return
        
        if self.animation_in_progress:
            self.root.after(100, self.game_step)
            return
            
        current_player = self.game.current_player
        current_ai = self.game.players[current_player]
        
        tracemalloc.start()
        start_decision = time.perf_counter()
        move = current_ai.choose_move(self.game.board.board)
        decision_time = time.perf_counter() - start_decision
        current_mem, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        self.stats[current_player]['decision_time'] = decision_time
        self.stats[current_player]['cumulative_time'] += decision_time
        self.stats[current_player]['decision_count'] += 1
        self.stats[current_player]['latest_mem'] = peak_mem
        
        if move:
            from_pos, to_pos = move
            self.animate_piece_movement(from_pos, to_pos, current_player)
            self.game.board.move_piece(from_pos, to_pos)
        else:
            print(f"玩家 {current_player} 没有合法移动！")
        
        self.update_info_panel(elapsed, total_mem)
        self.game.current_player = 2 if self.game.current_player == 1 else 1
        self.root.after(100, self.game_step)

def create_styled_button(parent, text, command, width=20):
    """创建一个现代风格的按钮"""
    btn = tk.Button(parent, text=text, command=command, width=width,
                    font=("Arial", 11),
                    bg="#4a90e2", fg="white",
                    activebackground="#357abd", activeforeground="white",
                    relief=tk.FLAT, padx=20, pady=8)
    btn.bind("<Enter>", lambda e: e.widget.config(bg="#357abd"))
    btn.bind("<Leave>", lambda e: e.widget.config(bg="#4a90e2"))
    return btn

def create_styled_combobox(parent, values, width=18):
    """创建一个现代风格的下拉框"""
    combo = ttk.Combobox(parent, values=values, width=width, state="readonly",
                        font=("Arial", 11))
    combo.set(values[0])  # 设置默认值
    return combo

def create_selection_ui(root):
    """创建美化后的选择界面"""
    # 创建主样式
    style = ttk.Style()
    style.configure("TCombobox", padding=5)
    style.configure("TLabel", font=("Arial", 11))
    
    # 创建一个Frame作为背景
    selection_frame = tk.Frame(root, bg="#f5f6f7", padx=30, pady=20)
    selection_frame.pack(expand=True, fill="both")
    
    # 添加标题
    title_label = tk.Label(selection_frame,
                          text="中国跳棋 AI 对战",
                          font=("Arial", 24, "bold"),
                          bg="#f5f6f7",
                          fg="#2c3e50",
                          pady=20)
    title_label.pack()
    
    # 创建内容框架
    content_frame = tk.Frame(selection_frame, bg="#f5f6f7", pady=10)
    content_frame.pack()
    
    # 玩家选择区域
    players_frame = tk.LabelFrame(content_frame, text="选择对战双方",
                                font=("Arial", 12, "bold"),
                                bg="#f5f6f7", fg="#2c3e50",
                                padx=20, pady=15)
    players_frame.pack(pady=10)
    
    # 玩家1选择
    p1_frame = tk.Frame(players_frame, bg="#f5f6f7")
    p1_frame.pack(pady=5)
    p1_label = tk.Label(p1_frame, text="玩家 1 (红方):",
                        font=("Arial", 11),
                        bg="#f5f6f7", fg="#e74c3c",
                        width=12, anchor="w")
    p1_label.pack(side=tk.LEFT, padx=5)
    p1_var = tk.StringVar(value="Greedy")
    p1_menu = create_styled_combobox(p1_frame, ["Greedy", "A* 算法"])
    p1_menu.pack(side=tk.LEFT, padx=5)
    
    # 玩家2选择
    p2_frame = tk.Frame(players_frame, bg="#f5f6f7")
    p2_frame.pack(pady=5)
    p2_label = tk.Label(p2_frame, text="玩家 2 (蓝方):",
                        font=("Arial", 11),
                        bg="#f5f6f7", fg="#3498db",
                        width=12, anchor="w")
    p2_label.pack(side=tk.LEFT, padx=5)
    p2_var = tk.StringVar(value="Greedy")
    p2_menu = create_styled_combobox(p2_frame, ["Greedy", "A* 算法"])
    p2_menu.pack(side=tk.LEFT, padx=5)
    
    # 游戏设置区域
    settings_frame = tk.LabelFrame(content_frame, text="游戏设置",
                                 font=("Arial", 12, "bold"),
                                 bg="#f5f6f7", fg="#2c3e50",
                                 padx=20, pady=15)
    settings_frame.pack(pady=10)
    
    # 时间选择
    time_frame = tk.Frame(settings_frame, bg="#f5f6f7")
    time_frame.pack(pady=5)
    time_label = tk.Label(time_frame, text="游戏时长:",
                         font=("Arial", 11),
                         bg="#f5f6f7", fg="#2c3e50",
                         width=12, anchor="w")
    time_label.pack(side=tk.LEFT, padx=5)
    time_var = tk.StringVar(value="1分钟")
    time_menu = create_styled_combobox(time_frame, ["1分钟", "2分钟", "3分钟", "4分钟", "5分钟"])
    time_menu.pack(side=tk.LEFT, padx=5)
    
    # 开始游戏按钮
    start_button = create_styled_button(
        selection_frame,
        "开始游戏",
        lambda: start_game(p1_menu.get(), p2_menu.get(),
                         int(time_menu.get()[0]) * 60,
                         root, selection_frame)
    )
    start_button.pack(pady=20)
    
    # 添加说明文字
    info_text = """
游戏说明：
• 红方和蓝方轮流移动棋子
• 每方需要将棋子移动到对方起始区域
• 比赛时间结束时，目标区域内棋子最多的一方获胜
"""
    info_label = tk.Label(selection_frame, text=info_text,
                         font=("Arial", 10),
                         bg="#f5f6f7", fg="#7f8c8d",
                         justify=tk.LEFT)
    info_label.pack(pady=10)
    
    return selection_frame

def start_game(p1_type, p2_type, game_duration, root, selection_frame):
    """开始游戏的函数"""
    # 创建AI实例
    p1_ai = GreedyAI(1) if p1_type == "Greedy" else AStarAI(1)
    p2_ai = GreedyAI(2) if p2_type == "Greedy" else AStarAI(2)
    
    # 销毁选择界面
    selection_frame.destroy()
    
    # 创建游戏界面
    GameGUI(root, p1_ai, p2_ai, game_duration)

# 主程序入口
if __name__ == "__main__":
    root = tk.Tk()
    root.title("中国跳棋 AI 对战")
    
    # 设置窗口图标（如果有的话）
    try:
        root.iconbitmap("chess_icon.ico")
    except:
        pass
    
    # 设置窗口大小和位置
    window_width = 800
    window_height = 600
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # 创建选择界面
    create_selection_ui(root)
    
    root.mainloop()
