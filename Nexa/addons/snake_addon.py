# snake_wasd_q.py
import tkinter as tk
import random

CELL = 20
GRID_W, GRID_H = 28, 20
SPEED_MS = 110

# directions (dx, dy)
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class SnakeGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Snake (W/A/S/D + Q = Quit)")
        self.resizable(False, False)

        self.canvas = tk.Canvas(self, width=GRID_W * CELL, height=GRID_H * CELL, bg="#202020", highlightthickness=0)
        self.canvas.pack()

        self.status = tk.Label(self, text="Score: 0", font=("Arial", 12))
        self.status.pack(pady=(2, 6))

        self.running = True
        self.after_id = None
        self.score = 0
        self.dir = RIGHT
        self.next_dir = RIGHT
        self.snake = [(5, 5), (4, 5), (3, 5)]
        self.food = self._random_empty_cell()

        self.bind_all("<Key>", self.on_key)

        self.draw()
        self.tick()

    def on_key(self, e):
        k = e.keysym.lower()
        if k in ("w", "a", "s", "d"):
            nd = {"w": UP, "a": LEFT, "s": DOWN, "d": RIGHT}[k]
            if (nd[0], nd[1]) != (-self.dir[0], -self.dir[1]):
                self.next_dir = nd
        elif k == "r":
            self.restart()
        elif k == "q":
            self.destroy()  # Q = quit

    def tick(self):
        if not self.running:
            return
        self.dir = self.next_dir
        head = self.snake[0]
        nx = (head[0] + self.dir[0]) % GRID_W
        ny = (head[1] + self.dir[1]) % GRID_H
        new_head = (nx, ny)

        if new_head in self.snake:
            self.game_over()
            return

        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.score += 1
            self.status.config(text=f"Score: {self.score}")
            self.food = self._random_empty_cell()
        else:
            self.snake.pop()

        self.draw()
        self.after_id = self.after(SPEED_MS, self.tick)

    def draw(self):
        c = self.canvas
        c.delete("all")

        fx, fy = self.food
        c.create_oval(fx*CELL+3, fy*CELL+3, fx*CELL+CELL-3, fy*CELL+CELL-3, fill="#e74c3c", outline="")

        for i, (x, y) in enumerate(self.snake):
            x0, y0 = x * CELL, y * CELL
            x1, y1 = x0 + CELL, y0 + CELL
            c.create_rectangle(x0, y0, x1, y1, fill="#2ecc71" if i == 0 else "#27ae60", outline="")

    def _random_empty_cell(self):
        while True:
            pos = (random.randint(0, GRID_W - 1), random.randint(0, GRID_H - 1))
            if pos not in self.snake:
                return pos

    def game_over(self):
        self.running = False
        if self.after_id:
            self.after_cancel(self.after_id)
        self.canvas.create_text(GRID_W*CELL//2, GRID_H*CELL//2 - 10,
                                text="GAME OVER", fill="white", font=("Arial", 24, "bold"))
        self.canvas.create_text(GRID_W*CELL//2, GRID_H*CELL//2 + 18,
                                text="R = restart   Q = quit", fill="#cccccc", font=("Arial", 12))

    def restart(self):
        if self.after_id:
            self.after_cancel(self.after_id)
        self.running = True
        self.score = 0
        self.status.config(text="Score: 0")
        self.dir = RIGHT
        self.next_dir = RIGHT
        self.snake = [(5, 5), (4, 5), (3, 5)]
        self.food = self._random_empty_cell()
        self.draw()
        self.tick()

if __name__ == "__main__":
    SnakeGame().mainloop()
