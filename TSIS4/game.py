import pygame
import random
import json
from config import *


def load_settings():
    try:
        with open("settings.json") as f:
            return json.load(f)
    except Exception:
        return {"snake_color": list(GREEN), "grid": True, "sound": False}


def save_settings(s):
    with open("settings.json", "w") as f:
        json.dump(s, f, indent=4)


def random_cell(exclude=None):
    exclude = exclude or []
    while True:
        pos = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
        if pos not in exclude:
            return pos


class Food:
    def __init__(self, snake, obstacles):
        blocked = set(snake) | set(obstacles)
        self.pos = random_cell(blocked)
        self.weight = random.choice([1, 2, 3])
        self.lifetime = random.randint(5000, 10000)
        self.spawn_time = pygame.time.get_ticks()
        self.poisoned = (random.random() < 0.15)
        self.color = DARK_RED if self.poisoned else (
            RED if self.weight == 1 else ORANGE if self.weight == 2 else YELLOW
        )

    def is_expired(self):
        return pygame.time.get_ticks() - self.spawn_time > self.lifetime


class Bonus:
    TYPES = ["speed", "slow", "shield"]
    COLORS = {"speed": CYAN, "slow": BLUE, "shield": PURPLE}
    SYMBOLS = {"speed": "⚡", "slow": "🐢", "shield": "🛡"}

    def __init__(self, snake, obstacles):
        blocked = set(snake) | set(obstacles)
        self.btype = random.choice(self.TYPES)
        self.pos = random_cell(blocked)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 8000
        self.color = self.COLORS[self.btype]

    def is_expired(self):
        return pygame.time.get_ticks() - self.spawn_time > self.lifetime


class Game:
    def __init__(self, player_id, personal_best):
        self.player_id = player_id
        self.personal_best = personal_best
        self.settings = load_settings()
        self.snake_color = tuple(self.settings["snake_color"])
        self.show_grid = self.settings["grid"]

        self.reset()

    def reset(self):
        cx, cy = COLS // 2, ROWS // 2
        self.snake = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = (1, 0)
        self.next_dir = (1, 0)
        self.score = 0
        self.level = 1
        self.food_eaten = 0
        self.obstacles = []
        self.food = Food(self.snake, self.obstacles)
        self.bonus = None
        self.bonus_next = pygame.time.get_ticks() + random.randint(5000, 12000)
        self.shield_active = False
        self.active_effect = None
        self.effect_end = 0
        self.fps = FPS_BASE
        self.alive = True

    def _place_obstacles(self):
        new_obs = []
        head = self.snake[0]
        for _ in range(4 + self.level * 2):
            attempts = 0
            while attempts < 50:
                pos = random_cell(set(self.snake) | set(new_obs))
                dx = abs(pos[0] - head[0])
                dy = abs(pos[1] - head[1])
                if dx > 3 or dy > 3:
                    new_obs.append(pos)
                    break
                attempts += 1
        self.obstacles = new_obs

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            dirs = {
                pygame.K_UP:    (0, -1),
                pygame.K_DOWN:  (0,  1),
                pygame.K_LEFT:  (-1, 0),
                pygame.K_RIGHT: ( 1, 0),
                pygame.K_w:     (0, -1),
                pygame.K_s:     (0,  1),
                pygame.K_a:     (-1, 0),
                pygame.K_d:     ( 1, 0),
            }
            if event.key in dirs:
                nd = dirs[event.key]
                if (nd[0] + self.direction[0], nd[1] + self.direction[1]) != (0, 0):
                    self.next_dir = nd

    def update(self):
        if not self.alive:
            return

        now = pygame.time.get_ticks()

        # Apply effect
        self.direction = self.next_dir
        if self.active_effect and now > self.effect_end:
            self.active_effect = None
            self.fps = FPS_BASE + (self.level - 1) * 2

        head = (
            (self.snake[0][0] + self.direction[0]) % COLS,
            (self.snake[0][1] + self.direction[1]) % ROWS,
        )

        # Wall/self collision
        if head in self.snake[1:] or head in self.obstacles:
            if self.shield_active:
                self.shield_active = False
            else:
                self.alive = False
                return

        self.snake.insert(0, head)

        # Food
        if head == self.food.pos:
            if self.food.poisoned:
                # Remove 2 segments
                for _ in range(2):
                    if len(self.snake) > 1:
                        self.snake.pop()
                if len(self.snake) <= 1:
                    self.alive = False
                    return
            else:
                self.score += self.food.weight
                self.food_eaten += 1
                # Level up
                if self.food_eaten % LEVEL_UP_SCORE == 0:
                    self.level += 1
                    self.fps = FPS_BASE + (self.level - 1) * 2
                    if self.level >= 3:
                        self._place_obstacles()
            self.food = Food(self.snake, self.obstacles)
        else:
            self.snake.pop()

        # Food expiry
        if self.food.is_expired():
            self.food = Food(self.snake, self.obstacles)

        # Bonus spawn
        if self.bonus is None and now >= self.bonus_next:
            self.bonus = Bonus(self.snake, self.obstacles)

        # Bonus pick up or expiry
        if self.bonus:
            if self.bonus.is_expired():
                self.bonus = None
                self.bonus_next = now + random.randint(5000, 12000)
            elif head == self.bonus.pos:
                bt = self.bonus.btype
                if bt == "speed":
                    self.active_effect = "speed"
                    self.fps = self.fps + 5
                    self.effect_end = now + 5000
                elif bt == "slow":
                    self.active_effect = "slow"
                    self.fps = max(2, self.fps - 4)
                    self.effect_end = now + 5000
                elif bt == "shield":
                    self.shield_active = True
                    self.active_effect = "shield"
                    self.effect_end = now + 99999
                self.bonus = None
                self.bonus_next = now + random.randint(8000, 15000)

    def draw(self, surface, font_small, font_big):
        surface.fill(DARK)

        # Grid
        if self.show_grid:
            for x in range(0, SCREEN_W, CELL):
                pygame.draw.line(surface, (35, 35, 50), (x, 0), (x, SCREEN_H))
            for y in range(0, SCREEN_H, CELL):
                pygame.draw.line(surface, (35, 35, 50), (0, y), (SCREEN_W, y))

        # Obstacles
        for ox, oy in self.obstacles:
            pygame.draw.rect(surface, GRAY, (ox * CELL, oy * CELL, CELL, CELL))

        # Snake
        for i, (sx, sy) in enumerate(self.snake):
            c = self.snake_color if i > 0 else WHITE
            pygame.draw.rect(surface, c, (sx * CELL + 1, sy * CELL + 1, CELL - 2, CELL - 2))

        # Food
        fx, fy = self.food.pos
        pygame.draw.rect(surface, self.food.color, (fx * CELL + 2, fy * CELL + 2, CELL - 4, CELL - 4))
        pts = font_small.render(f"+{self.food.weight}", True, WHITE)
        surface.blit(pts, (fx * CELL, fy * CELL - 12))

        # Bonus
        if self.bonus:
            bx, by = self.bonus.pos
            pygame.draw.rect(surface, self.bonus.color, (bx * CELL, by * CELL, CELL, CELL))

        # HUD panel
        pygame.draw.rect(surface, PANEL, (0, 0, SCREEN_W, 30))
        hud = [
            f"Score: {self.score}",
            f"Level: {self.level}",
            f"PB: {self.personal_best}",
        ]
        if self.active_effect:
            hud.append(f"[{self.active_effect.upper()}]")
        if self.shield_active:
            hud.append("[SHIELD]")
        x = 8
        for txt in hud:
            s = font_small.render(txt, True, WHITE)
            surface.blit(s, (x, 7))
            x += s.get_width() + 20