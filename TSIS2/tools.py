import pygame
import math


def draw_rectangle(surface, color, x0, y0, x1, y1):
    w, h = x1 - x0, y1 - y0
    pygame.draw.rect(surface, color, (x0, y0, w, h), 2)


def draw_circle(surface, color, x0, y0, x1, y1):
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    r = int(math.hypot(x1 - x0, y1 - y0) // 2)
    pygame.draw.circle(surface, color, (cx, cy), r, 2)


def draw_eraser(surface, x, y):
    pygame.draw.rect(surface, (255, 255, 255), (x - 15, y - 15, 30, 30))


def draw_square(surface, color, x0, y0, x1, y1):
    side = min(abs(x1 - x0), abs(y1 - y0))
    pygame.draw.rect(surface, color, (x0, y0, side, side), 2)


def draw_right_triangle(surface, color, x0, y0, x1, y1):
    pts = [(x0, y0), (x0, y1), (x1, y1)]
    pygame.draw.polygon(surface, color, pts, 2)


def draw_equilateral_triangle(surface, color, x0, y0, x1, y1):
    side = abs(x1 - x0)
    h = int(side * math.sqrt(3) / 2)
    pts = [(x0, y0 + h), (x0 - side // 2, y0), (x0 + side // 2, y0)]
    pygame.draw.polygon(surface, color, pts, 2)


def draw_rhombus(surface, color, x0, y0, x1, y1):
    dx, dy = x1 - x0, y1 - y0
    pts = [
        (x0 + dx // 2, y0),
        (x1, y0 + dy // 2),
        (x0 + dx // 2, y1),
        (x0, y0 + dy // 2),
    ]
    pygame.draw.polygon(surface, color, pts, 2)


def draw_pencil(surface, color, x0, y0, x1, y1, width):
    pygame.draw.line(surface, color, (x0, y0), (x1, y1), width)


def draw_line(surface, color, x0, y0, x1, y1, width):
    pygame.draw.line(surface, color, (x0, y0), (x1, y1), width)


def flood_fill(surface, x, y, new_color):
    old_color = surface.get_at((x, y))[:3]
    if old_color == new_color:
        return
    stack = [(x, y)]
    w, h = surface.get_size()
    while stack:
        cx, cy = stack.pop()
        if cx < 0 or cx >= w or cy < 0 or cy >= h:
            continue
        if surface.get_at((cx, cy))[:3] != old_color:
            continue
        surface.set_at((cx, cy), new_color)
        stack += [(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)]