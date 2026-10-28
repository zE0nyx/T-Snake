import curses
import time
import random
from collections import deque
from itertools import islice

UP, DOWN, LEFT, RIGHT = (-1, 0), (1, 0), (0, -1), (0, 1)
OPPOSITE = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}

def game_window(m_height: int, m_width: int):
    win = curses.newwin(m_height, m_width, 1, 4)
    win.box()
    win.refresh()
    return win


def score_window(height, width, y, x):
    win = curses.newwin(height, width, y, x)
    win.box("-","-")
    win.refresh()
    return win


class Snake_Game:
    def __init__(self, height, width):
        self.h, self.w = height, width
        mid_y, mid_x = height // 2, width // 2
        self.body = deque([(mid_y, mid_x - i) for i in range(3)])
        self.direction = 0
        self.next_direction = 0
        self.score = 0
        self.alive = True
        self.food = self.place_food()
    
    def place_food(self):
        occupied = set(self.body)
        while True:
            pos = (random.randint(1, self.h - 2), random.randint(1, self.w - 2))
            if pos not in occupied:
                return pos
    
    def turn(self, new_dir):
        if new_dir != OPPOSITE[self.direction]:
            self.next_direction = new_dir
    
    def step(self):
        self.direction = self.next_direction
        dy, dx = self.direction
        hy, hx = self.body[0]
        new_head = (hy + dy, hx + dx)
        
        if not (1 <= new_head[0] <= self.h - 2 and 1 <= new_head[1] <= self.w - 2):
            self.alive = False
            return
        
        self.body.appendleft(new_head)
        if (new_head) == self.food:
            self.score += 1
            self.food = self.place_food()
        else:
            self.body.pop()
        
        if new_head in islice(self.body, 1, None):
            self.alive = False


def draw_centered(win, y, text, attr=0):
    _, w = win.getmaxyx()
    win.addstr(y, max(1, (w - len(text)) // 2), text, attr)


def make_game(win, game, paused):
    win.erase()
    win.box()
    win.addstr(0, 2, " SNAKE ")
    
    fy, fx = game.food
    win.addstr(fy, fx, "*")
    
    for i, (y, x) in enumerate(game.body):
        ch = "@" if i == 0 else "o"
        win.addstr(y, x, ch)
    
    mid = game.h // 2
    if not game.alive:
        draw_centered(win, mid - 1, " GAME OVER ")
        draw_centered(win, mid + 1, " R to restart, Q to quit ")
    elif paused:
        draw_centered(win, mid, " PAUSED ")
    
    win.noutrefresh()


def main(stdscr):
    curses.curs_set(0)
    stdscr.refresh()
    
    t_height, t_width = stdscr.getmaxyx()
    s_width = 30
    
    g_height = min(40, t_height - 1)
    g_width = min(80, t_width - 4 - s_width - 2)
    
    if g_width < 20 or g_height < 10:
        stdscr.addstr(0, 0, "Terminal too small, enlarge it and restart. Press any key.")
        stdscr.getch()
        return
    
    win_g = game_window(g_height, g_width)
    win_g.keypad(True)
    win_g.timeout(100)
    
    s_x = 4 + g_width + 2
    s_height = min(10, g_height)
    win_s = score_window(s_height, s_width, 1, s_x)
    s_width = min(30, t_width - s_x - 1)

    while True:
        current_time = time.strftime("%H:%M:%S")
        win_s.addstr(1, 2, f"{current_time}")
        win_s.refresh()
        
        key = win_g.getch()
        if key in (ord('q'), ord('Q')):
            break


curses.wrapper(main)