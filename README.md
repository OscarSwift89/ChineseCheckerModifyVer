以下是一个详细的 `README.md` 文件，适合在 GitHub 中使用。它涵盖了项目的描述、安装步骤、使用方法、代码结构、贡献指南等内容。

---

# **中国跳棋AI对战项目**

![GitHub](https://img.shields.io/badge/Python-3.8%2B-blue)
![GitHub](https://img.shields.io/badge/License-MIT-green)

本项目是一个基于 Python 的中国跳棋游戏，支持 2 人 AI 对战。通过实现不同的 AI 算法（如贪心算法、A*算法、A*算法等），可以在可视化界面中观察 AI 代理之间的对抗。当前版本已移除奖励点与奖励分数，积分即为每个玩家棋子总数，右下角显示积分统计。

---

## **项目特点**

- **棋盘生成**：使用 12x12 的二维数组表示棋盘，支持棋子的初始化和渲染。
- **移动规则**：实现棋子的基础移动和跳跃移动规则。
- **AI 对战**：支持多种 AI 算法（如贪心算法、A*算法等）之间的对抗。
- **可视化界面**：基于 tkinter，支持实时棋盘显示和信息面板。
- **积分统计**：右下角显示每个玩家的积分（即棋子总数）。
- **可扩展性**：易于添加新的 AI 算法或扩展游戏规则。

---

## **安装与运行**

### **1. 克隆项目**

```bash
git clone https://github.com/your-username/chinese-checkers-ai.git
cd chinese-checkers-ai
```

### **2. 安装依赖**

确保已安装 Python 3.8 或更高版本，然后安装依赖：

```bash
pip install numpy colorama
```

### **3. 运行游戏**

运行 `main.py` 启动游戏：

```bash
python main.py
```

---

## **使用方法**

1. **选择 AI 代理**：
   - 游戏启动后，选择两个 AI 代理进行对战。
   - 支持的 AI 代理：
     - **1. 贪心算法**：选择当前最优的移动。
     - **2. A*算法**：使用 A*算法搜索最优路径。

2. **观察对战**：
   - 游戏会在窗口中实时显示棋盘状态。
   - 每个 AI 代理轮流移动棋子，直到游戏结束。

3. **游戏结束**：
   - 当某一玩家的棋子全部到达目标区域或达到胜利条件时，游戏结束并宣布胜利者。

4. **积分显示**：
   - 右下角信息面板实时显示每个玩家的积分（即棋子总数）。

---

## **代码结构**

```
chinese-checkers-ai/
├── board.py               # 棋盘与棋子逻辑
├── ai/
│   ├── greedy_ai.py       # 贪心算法AI
│   ├── astar_ai.py        # A*算法AI

├── game.py                # 游戏主逻辑与终端渲染
├── main.py                # 程序入口
├── README.md              # 项目说明文档
└── requirements.txt       # 依赖列表
```

---

## **AI 算法介绍**

### **1. 贪心算法**
- 每次选择当前最优的移动（如距离目标最近的棋子）。
- 使用曼哈顿距离作为评估函数。

### **2. A*算法**
- 使用 A*算法搜索从当前位置到目标区域的最短路径。
- 启发函数为曼哈顿距离。

---

## **贡献指南**

欢迎贡献代码！以下是贡献步骤：

1. **Fork 项目**：
   - 点击右上角的 `Fork` 按钮，将项目复制到你的 GitHub 账户。

2. **克隆你的 Fork**：
   ```bash
   git clone https://github.com/your-username/chinese-checkers-ai.git
   cd chinese-checkers-ai
   ```

3. **创建新分支**：
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **提交更改**：
   - 修改代码后，提交更改：
     ```bash
     git add .
     git commit -m "描述你的更改"
     ```

5. **推送分支**：
   ```bash
   git push origin feature/your-feature-name
   ```

6. **创建 Pull Request**：
   - 在你的 GitHub 仓库页面，点击 `New Pull Request`，选择你的分支并提交。

---

## **许可证**

本项目基于 [MIT 许可证](LICENSE) 开源。

---

## **联系作者**

如有问题或建议，请联系：

- **作者**：抒阳
- **邮箱**：your-email@example.com
- **GitHub**：[your-username](https://github.com/your-username)

---

## **致谢**

- 感谢 [numpy](https://numpy.org/) 和 [colorama](https://pypi.org/project/colorama/) 库的支持。
- 感谢所有贡献者和用户的支持与反馈！

---

**Happy Coding!** 🎮
