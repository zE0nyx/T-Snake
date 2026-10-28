import curses
import time
import random
from collections import deque
from itertools import islice

# Just some static game window measurements
WIDTH_P = 26
GH_MAX, GW_MAX = 25, 60
GH_MIN, GW_MIN = 15, 30

# typical game controls 
UP, DOWN, LEFT, RIGHT = (-1, 0), (1, 0), (0, -1), (0, 1)
OPPOSITES = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}
KEYS = {
    curses.KEY_UP: UP, ord("w"): UP, ord("W"): UP,
    curses.KEY_DOWN: DOWN, ord("s"): DOWN, ord("S"): DOWN,
    curses.KEY_LEFT: LEFT, ord("a"): LEFT, ord("A"): LEFT,
    curses.KEY_RIGHT: RIGHT, ord("d"): RIGHT, ord("D"): RIGHT,
}

SNAKE, FOOD, TITLE, DIM = 1,2,3,4


def make_windows(stdscr):
    t_height, t_width = stdscr.getmaxyx()
    g_height = min(GH_MAX, t_height - 2)
    g_width = min(GW_MAX, t_width - WIDTH_P - 3)

    if g_height < GH_MIN or g_width < GW_MIN:
        return None, None

    g_win = curses.newwin(g_height, g_width, 1, 1)
    p_win = curses.newwin(g_height, WIDTH_P, 1, 2 + g_width)
    return g_win, p_win


class Snake_Game:
    def __init__(self, height, width):
        self.h, self.w = height, width
        mid_y, mid_x = height // 2, width // 2
        self.body = deque([(mid_y, mid_x - i) for i in range(3)])
        self.direction = RIGHT
        self.next_direction = RIGHT
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
        if new_dir != OPPOSITES[self.direction]:
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

    def tick_seconds(self):
        return max(0.05, 0.15 - self.score * 0.005)

    def level(self):
        return 1 + self.score // 5


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

def make_panel(win, game, t_score):
    win.erase()
    win.box()
    win.addstr(0, 2, " STATS ")

    rows = [
        ("Time", time.strftime("%H:%M:%S")),
        ("Cur Score", str(game.score)),
        ("High Score", str(t_score)),
        ("Length", str(len(game.body))),
        ("Level", str(game.level()))
    ]
    for i, (label, value) in enumerate(rows):
        y = 2 + i
        win.addstr(y, 2, f"{label:<11}")
        win.addstr(y, 14, value)

    controls = [
        "Controls",
        "W A S D - Move",
        "P         pause",
        "R         restart",
        "Q         quit"
    ]

    start = 4 + len(rows)
    for i, line in enumerate(controls):
        win.addstr(start + i, 2, line)

    win.noutrefresh()


def main(stdscr):
    try:
        curses.curs_set(0)
    except curses.error:
        pass

    stdscr.refresh()

    gwin, pwin = make_windows(stdscr)
    if gwin is None:
        print("Terminal too small enlarge it to play the game")
        return

    gwin.keypad(True)
    h, w = gwin.getmaxyx()

    game = Snake_Game(h, w)
    score = 0
    paused = False
    n_step = time.monotonic()

    while True:
        wait_t = max(0, int((n_step - time.monotonic()) * 1000))
        gwin.timeout(wait_t)
        key = gwin.getch()

        if key in (ord("q"), ord("Q")):
            break
        elif key in (ord("p"), ord("P")) and game.alive():
            paused = not paused
        elif key in (ord("r"), ord("R")):
            game = Snake_Game(h, w)
            paused = False
        elif key in KEYS and not paused:
            game.turn(KEYS[key])

        if time.monotonic() >= n_step:
            if game.alive and not paused:
                game.step()
                score = max(score, game.score)

            make_game(gwin, game, paused)
            make_panel(pwin, game, score)
            curses.doupdate()

            n_step = time.monotonic() + game.tick_seconds()


if __name__ == "__main__":
    curses.wrapper(main)