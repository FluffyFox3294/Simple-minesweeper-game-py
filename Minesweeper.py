import tkinter as tk
from tkinter import messagebox
import numpy as np
import random
import time
import json
from datetime import datetime
import os
from functools import lru_cache

class Minesweeper:
    def __init__(self, master, height=10, width=10, mines=10, difficulty="Beginner"):
        # 初始化     
        
        # clear_cache()
        
        self.first_click = True
        self.first_click_row = None
        self.first_click_col = None
        self.master = master
        self.height = height
        self.width = width
        self.mines = mines
        self.difficulty = difficulty
        self.start_time = time.time()
        self.game_over = False
        self.board = np.zeros((height, width), dtype=int)
        self.revealed = np.full((height, width), False)
        self.flags = np.full((height, width), False)
        self.uncertain = np.full((height, width), False)
        self.buttons = [[None for _ in range(width)] for _ in range(height)]
        self.cheat_active = False
        self.place_mines()
        self.calculate_adjacent_mines()
        self.create_widgets()
        self.update_timer() 
        
        # 读取文件位置
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.rankings_file = os.path.join(script_dir, "rankings.json")
        
    # 重开
    def restart(self):
        self.master.destroy()
        main()
    
    #TODO: solve possible problems caused by cache   
    # @lru_cache(maxsize=128)
    # def cached_function(arg):
    #     # Function implementation
    #     return arg

    # def clear_cache():
    #     cached_function.cache_clear()

        # 地雷生成
    def place_mines(self, first_click_row=None, first_click_col=None):

        if first_click_row is None or first_click_col is None:# 初始生成
            for _ in range(self.mines):
                while True:
                    row = random.randint(0, self.height - 1)
                    col = random.randint(0, self.width - 1)
                    if self.board[row, col] != -1:
                        self.board[row, col] = -1
                        break
        else:
            for _ in range(self.mines): # 当首次点击到地雷时， 排除地雷并重新生成新的排序知道点在非地雷区域
                while True:
                    row = random.randint(0, self.height - 1)
                    col = random.randint(0, self.width - 1)
                    if (row != first_click_row or col != first_click_col) and self.board[row, col] != -1:
                        self.board[row, col] = -1
                        break

    # 计算非地雷格子周围有几个地雷
    def calculate_adjacent_mines(self):
        for row in range(self.height):
            for col in range(self.width):
                if self.board[row, col] == -1:
                    continue
                count = 0
                for i in range(max(0, row - 1), min(row + 2, self.height)):
                    for j in range(max(0, col - 1), min(col + 2, self.width)):
                        if self.board[i, j] == -1:
                            count += 1
                self.board[row, col] = count
    
    # 重置计时器和地雷数量显示
    def clear_timer_and_mine_count(self):
        self.timer_label.config(text="Time: 0")
        self.counter_label.config(text=f"Mines: 0/{self.mines}")
    
    # 创建雷区
    def create_widgets(self):
        self.show_restart_button()

        # 框架
        board_frame = tk.Frame(self.master)
        board_frame.grid(row=1, column=0, columnspan=self.width)

        # 计时器和地雷数量显示
        self.timer_label = tk.Label(self.master, text="Time: 0")
        self.timer_label.grid(row=0, column=0, columnspan=self.width // 2, sticky="w")

        self.counter_label = tk.Label(self.master, text=f"Mines: 0/{self.mines}")
        self.counter_label.grid(row=0, column=self.width // 2, columnspan=self.width // 2, sticky="e")

        button_width = 2 # 每格宽
        button_height = 1# 每格高
        custom_font = ("Courier", 8, "bold")
        
        for row in range(self.height):
            for col in range(self.width):
                
                # 上下留空
                pady_top = 5 if row == 0 else 0  
                pady_bottom = 20 if row == self.height - 1 else 0  
                
                button = tk.Button(
                    board_frame,  # 以棋盘框架为父类
                    text="", # 显示内容（F，*等）
                    width=button_width,
                    height=button_height,
                    command=lambda r=row, c=col: self.reveal(r, c),
                    relief=tk.RAISED,
                    bg="#c0c0c0",  # 浅灰色背景
                    activebackground="#a0a0a0",  # 暗灰色，按下时显示
                    bd=3,  # 可修改，边框宽
                    font=custom_font
                )
                button.bind("<Button-3>", lambda e, r=row, c=col: self.flag(r, c))
                button.bind("<Double-1>", lambda e, r=row, c=col: self.cheat_reveal(r, c, e))
                button.grid(row=row, column=col, pady=(pady_top, pady_bottom))
                self.buttons[row][col] = button

    def update_timer(self): # 计时器更新
        if self.game_over:
            return

        # 将时间格式化
        elapsed_time = int(time.time() - self.start_time) 
        hours = elapsed_time // 3600
        minutes = (elapsed_time % 3600) // 60
        seconds = elapsed_time % 60

        if elapsed_time < 60:
            time_str = f"Time: {seconds}"
        elif elapsed_time < 3600:
            time_str = f"Time: {minutes}:{seconds:02d}"
        else:
            time_str = f"Time: {hours}:{minutes:02d}:{seconds:02d}"

        self.timer_label.config(text=time_str)
        self.master.after(1000, self.update_timer)
    
    # 左键点击事件
    def reveal(self, row, col):
        # 首次点击如果不是空白就重新生成，保证每次游戏开始总能开启一片区域而不是一个数字格
        if self.first_click:
            while self.board[row][col] !=0:
                self.board = np.zeros((self.height, self.width), dtype=int)
                self.revealed = np.full((self.height, self.width), False)
                self.flags = np.full((self.height, self.width), False)
                self.uncertain = np.full((self.height, self.width), False)
                
                self.place_mines(first_click_row=row, first_click_col=col)
                self.calculate_adjacent_mines()
            self.first_click = False

        if self.game_over or self.flags[row, col]:  # 游戏结束后或者此格子已经被标记为地雷就忽略点击
            return

        if self.board[row, col] == -1:
            # 点到地雷，游戏结束
            self.show_all_mines() # 显示所有地雷
            self.game_over = True
            elapsed_time = int(time.time() - self.start_time) # 结算时间
            time_str = self.format_time(elapsed_time)
            self.add_ranking(elapsed_time, "Lose") # 记录本次游戏
            messagebox.showinfo("Game Over", f"You hit a mine! Time taken: {time_str}") # 弹出对话框
            self.show_restart_button() # 显示选项按键
            return

        self.flood_fill(row, col) # 显示周围空白格
        self.update_buttons()
        if self.check_win(): 
            # 游戏胜利
            self.game_over = True
            elapsed_time = int(time.time() - self.start_time)
            time_str = self.format_time(elapsed_time)
            self.add_ranking(elapsed_time, "Win")
            messagebox.showinfo("Congratulations", f"You win! Time taken: {time_str}")
            self.show_restart_button()

        # 点击后将颜色变为背景白色
        if not self.flags[row, col]:
            self.buttons[row][col].config(bg="white")

    def flag(self, row, col): # 右键插旗事件
        if self.revealed[row, col] or self.game_over:
            return

        if not self.flags[row, col] and not self.uncertain[row, col]:
            # M标记为地雷
            self.flags[row, col] = True
            self.buttons[row][col].config(text="F", bg="yellow")
        elif self.flags[row, col]:
            # 标记为疑问
            self.flags[row, col] = False
            self.uncertain[row, col] = True
            self.buttons[row][col].config(text="?", bg="lightblue")
        else:
            # 变为未翻开初始状态
            self.uncertain[row, col] = False
            self.buttons[row][col].config(text="", bg="#c0c0c0")

        self.update_counter() # 标记地雷后更新地雷数量显示
        if self.check_win():
            self.game_over = True
            elapsed_time = int(time.time() - self.start_time)
            time_str = self.format_time(elapsed_time)
            self.add_ranking(elapsed_time, "Win")
            messagebox.showinfo("Congratulations", f"You win! Time taken: {time_str}")
            self.show_restart_button()
    
    # 点击到空格将周围一片区全部显示
    def flood_fill(self, row, col):
        if not self.revealed[row, col] and self.board[row, col] != -1:
            self.revealed[row, col] = True
            self.buttons[row][col].config(bg="white")
            if self.board[row, col] == 0:
                for i in range(max(0, row - 1), min(row + 2, self.height)):
                    for j in range(max(0, col - 1), min(col + 2, self.width)):
                        if not self.revealed[i, j]:
                            self.flood_fill(i, j)

    # 胜利条件
    def check_win(self):
        if np.all((self.board == -1) | self.revealed): # 只剩地雷和已经翻开的区域则胜利
            return True
        return False

    def update_buttons(self): # 翻开功能实现
        color_map = {
            1:"",
        }
        for row in range(self.height):
            for col in range(self.width):
                if self.revealed[row, col]:
                    if self.board[row, col] == 0:
                        self.buttons[row][col].config(text="", state="disabled", relief="sunken")
                    else:
                        self.buttons[row][col].config(text=str(self.board[row][col]), state="disabled", relief="sunken")

    # 更新地雷数量显示
    def update_counter(self):
        marked_mines = np.sum(self.flags)
        self.counter_label.config(text=f"Mines: {marked_mines}/{self.mines}")

    def show_all_mines(self): # 将全部地雷显示
        for row in range(self.height):
            for col in range(self.width):
                if self.board[row, col] == -1:
                    self.buttons[row][col].config(text="*", bg="red", state="disabled")

    def hide_all_mines(self): # 将全部地雷隐藏
        for row in range(self.height):
            for col in range(self.width):
                if self.board[row, col] == -1 and not self.revealed[row, col]:
                    self.buttons[row][col].config(text="", bg="#c0c0c0", state="normal")

    # TODO: 完成内置作弊，也可以不完成
    def cheat_reveal(self, row, col, event):
        # return 
        if event.state & 0x0001:  # Check if Shift key is held down
            if self.cheat_active:
                self.hide_all_mines()
                self.cheat_active = False
            else:
                self.show_all_mines()
                self.cheat_active = True
        elif self.cheat_active and self.revealed[row, col] and self.board[row, col] == -1:
            self.buttons[row][col].config(text="", bg="SystemButtonFace", state="disabled")
            self.board[row, col] = 0
        elif self.cheat_active and not self.revealed[row, col] and event.num == 3:  # Right-click on unmarked cell
            pass  # Do nothing when cheating and right-clicking on unmarked cells
    
    # 时间格式化
    def format_time(self, elapsed_time):
        hours = elapsed_time // 3600
        minutes = (elapsed_time % 3600) // 60
        seconds = elapsed_time % 60
        if elapsed_time < 60:
            return f"{seconds} seconds"
        elif elapsed_time < 3600:
            return f"{minutes}:{seconds:02d}"
        else:
            return f"{hours}:{minutes:02d}:{seconds:02d}"

    # 游戏记录写入json文件
    def add_ranking(self, elapsed_time, result):
        # Add ranking entry to the file
        ranking = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "difficulty": self.difficulty,
            "height": self.height,
            "width": self.width,
            "mines": self.mines,
            "time": elapsed_time,
            "result": result
        }
        try:
            with open(self.rankings_file, "r") as file:
                rankings = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            rankings = []

        if result == "Lose":
            return 
        rankings.append(ranking)
        with open(self.rankings_file, "w") as file:
            json.dump(rankings, file, indent=4)

    # 读取并显示历史记录
    def show_rankings(self):
        if hasattr(self, "ranking_window") and self.ranking_window.winfo_exists():
            # 防止多开，已有窗口打开就将其移动至最前
            self.ranking_window.lift()
            return

        self.ranking_window = tk.Toplevel(self.master)
        self.ranking_window.title("Rankings")
        try:
            with open(self.rankings_file, "r") as file:
                rankings = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            rankings = []

        selected_rankings = [ranking for ranking in rankings if ranking["difficulty"] == self.difficulty]
        selected_rankings.sort(key=lambda x: (x["result"] == "Lose", x["time"]))  # 将胜利的记录显示在前
        top_10_rankings = selected_rankings[:10]  # 只显示历史最好的前10个记录

        if not top_10_rankings:
            tk.Label(self.ranking_window, text=f"No {self.difficulty} rankings yet.").pack() # 没有记录就显示无记录
        else:
            for ranking in top_10_rankings:
                details = f"{ranking['date']}: {ranking['difficulty']} - {ranking['result']} in {self.format_time(ranking['time'])}"
                if ranking["difficulty"] == "Custom":
                    details += f" ({ranking['height']}x{ranking['width']}, {ranking['mines']} mines)"
                tk.Label(self.ranking_window, text=details).pack()
    
    def show_restart_button(self):
        # 创建按钮对象
        restart_frame = tk.Frame(self.master)
        restart_frame.grid(row=2, column=0, columnspan=self.width)

        restart_button = tk.Button(restart_frame, text="Return to menu", command=self.restart)
        restart_button.pack(side=tk.LEFT, padx=5)

        retry_button = tk.Button(restart_frame, text="Retry Same Level", command=self.retry_level)
        retry_button.pack(side=tk.LEFT, padx=5)

        rankings_button = tk.Button(restart_frame, text="Rankings of current level", command=self.show_rankings)
        rankings_button.pack(side=tk.LEFT, padx=5)
        
    # 当前难度重新开始
    def retry_level(self):
        # Recreate the game instance with the same settings
        self.clear_timer_and_mine_count()
        self.__init__(self.master, height=self.height, width=self.width, mines=self.mines, difficulty=self.difficulty)
        self.master.title(f"Minesweeper - {self.height}x{self.width}, {self.mines} mines")

def main():
    # 主程序
    root = tk.Tk()
    root.title("Minesweeper")
    
    MAX_ROWS_COLS = 30
    MAX_MINES = 100

    def start_game():
        try:
            if selected_difficulty.get() == "Custom":
                # 获取输入
                height = int(rows_entry.get())
                width = int(cols_entry.get())
                mines = int(mines_entry.get())
                # 不合法输入就让用户重新输入
                if height <= 0 or width <= 0 or mines <= 0 or mines >= height * width:
                    raise ValueError("Invalid custom settings")
                if height > MAX_ROWS_COLS or width > MAX_ROWS_COLS or mines > MAX_MINES:
                    raise ValueError(f"Values cannot exceed {MAX_ROWS_COLS} for rows/columns and {MAX_MINES} for mines")
            else:
                # 键输入数据存入
                height, width, mines = difficulties[selected_difficulty.get()]

            # 关闭窗口
            settings_frame.pack_forget()

            # 游戏开始
            game = Minesweeper(root, height=height, width=width, mines=mines, difficulty=selected_difficulty.get())
            root.title(f"Minesweeper - {height}x{width}, {mines} mines")
            root.mainloop()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    settings_frame = tk.Frame(root)
    settings_frame.pack()

    # 预设难度等级
    difficulties = {
        "Beginner": (8, 8, 10),
        "Intermediate": (16, 16, 40),
        "Expert": (16, 30, 99),
        "Custom": None
    }

    # 难度的下拉选择框
    selected_difficulty = tk.StringVar()
    selected_difficulty.set("Beginner")  # Default difficulty
    difficulty_menu = tk.OptionMenu(settings_frame, selected_difficulty, *difficulties.keys())
    difficulty_menu.pack()

    # 显示不同难度的具体内容
    details_label = tk.Label(settings_frame, text="\n")
    details_label.pack()
    for difficulty, values in difficulties.items():
        if values is not None:
            height, width, mines = values
            details_label.config(text=details_label.cget("text") + f"{difficulty}: {height}x{width}, {mines} mines\n")

    # 自定义输入
    custom_frame = tk.Frame(settings_frame)
    tk.Label(custom_frame, text="Number of Rows (1-30):").grid(row=0, column=0)
    rows_entry = tk.Entry(custom_frame)
    rows_entry.grid(row=0, column=1)

    tk.Label(custom_frame, text="Number of Columns (1-30):").grid(row=1, column=0)
    cols_entry = tk.Entry(custom_frame)
    cols_entry.grid(row=1, column=1)

    tk.Label(custom_frame, text="Number of Mines (1-100):").grid(row=2, column=0)
    mines_entry = tk.Entry(custom_frame)
    mines_entry.grid(row=2, column=1)

    # 选择自定义是显示自定义
    def show_custom_options(*args):
        if selected_difficulty.get() == "Custom":
            custom_frame.pack()
        else:
            custom_frame.pack_forget()

    # 绑定功能
    selected_difficulty.trace("w", show_custom_options)

    # 开始按键
    tk.Button(settings_frame, text="Start Game", command=start_game).pack()

    # 设置窗口位置
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    screen_width = root.winfo_screenwidth() # 获取屏幕长宽
    screen_height = root.winfo_screenheight()
    offset = 150 # 可修改，窗口偏移多少
    x = (screen_width - width) // 2 - offset
    y = (screen_height - height) // 2 - offset
    root.geometry(f"+{x}+{y}")

    root.mainloop()

if __name__ == "__main__":
    main()