import pygame
import sys
from tools import *
 
pygame.init()
 
WIDTH, HEIGHT = 800, 620
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")
 
font = pygame.font.SysFont("Arial", 14)
 
# Палитра цветов вверху
PALETTE = [
    (0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 200, 0),
    (0, 0, 255), (255, 255, 0), (255, 140, 0), (160, 0, 200),
    (0, 200, 200), (255, 105, 180), (139, 69, 19), (128, 128, 128),
]
PALETTE_Y = 5
SWATCH = 24  # размер квадратика
 
canvas = pygame.Surface((WIDTH, HEIGHT - SWATCH - 14))
canvas.fill((255, 255, 255))
 
# Инструменты: клавиши 1-7
TOOLS = {
    pygame.K_1: "rect",
    pygame.K_2: "circle",
    pygame.K_3: "eraser",
    pygame.K_4: "square",
    pygame.K_5: "righttri",
    pygame.K_6: "equitri",
    pygame.K_7: "rhombus",
}
 
NAMES = {
    "rect":     "1-Прямоугольник",
    "circle":   "2-Круг",
    "eraser":   "3-Ластик",
    "square":   "4-Квадрат",
    "righttri": "5-Прям.треуг",
    "equitri":  "6-Равност.треуг",
    "rhombus":  "7-Ромб",
}
 
COLOR = (255, 0, 0)
tool = "rect"
drawing = False
start = (0, 0)
snapshot = None
CANVAS_Y = SWATCH + 14  # холст начинается ниже палитры
 
clock = pygame.time.Clock()
 
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
 
        if event.type == pygame.KEYDOWN:
            if event.key in TOOLS:
                tool = TOOLS[event.key]
            if event.key == pygame.K_c:
                canvas.fill((255, 255, 255))
 
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            # Клик по палитре
            for i, col in enumerate(PALETTE):
                sx = 10 + i * (SWATCH + 4)
                if sx <= mx <= sx + SWATCH and PALETTE_Y <= my <= PALETTE_Y + SWATCH:
                    COLOR = col
                    break
            else:
                # Клик по холсту
                if my >= CANVAS_Y:
                    drawing = True
                    start = (mx, my - CANVAS_Y)
                    snapshot = canvas.copy()
 
        if event.type == pygame.MOUSEMOTION and drawing:
            mx, my = event.pos
            cy = my - CANVAS_Y
            x0, y0 = start
            if tool == "eraser":
                draw_eraser(canvas, mx, cy)
            else:
                canvas.blit(snapshot, (0, 0))
 
        if event.type == pygame.MOUSEBUTTONUP and drawing:
            drawing = False
            mx, my = event.pos
            x0, y0 = start
            x1, y1 = mx, my - CANVAS_Y
            if tool == "rect":       draw_rectangle(canvas, COLOR, x0, y0, x1, y1)
            elif tool == "circle":   draw_circle(canvas, COLOR, x0, y0, x1, y1)
            elif tool == "square":   draw_square(canvas, COLOR, x0, y0, x1, y1)
            elif tool == "righttri": draw_right_triangle(canvas, COLOR, x0, y0, x1, y1)
            elif tool == "equitri":  draw_equilateral_triangle(canvas, COLOR, x0, y0, x1, y1)
            elif tool == "rhombus":  draw_rhombus(canvas, COLOR, x0, y0, x1, y1)
 
    # Отрисовка
    screen.fill((220, 220, 220))
 
    # Палитра
    for i, col in enumerate(PALETTE):
        sx = 10 + i * (SWATCH + 4)
        pygame.draw.rect(screen, col, (sx, PALETTE_Y, SWATCH, SWATCH))
        pygame.draw.rect(screen, (80, 80, 80), (sx, PALETTE_Y, SWATCH, SWATCH), 1)
 
    # Текущий цвет
    cx_start = 10 + len(PALETTE) * (SWATCH + 4) + 10
    pygame.draw.rect(screen, COLOR, (cx_start, PALETTE_Y, SWATCH + 10, SWATCH))
    pygame.draw.rect(screen, (0, 0, 0), (cx_start, PALETTE_Y, SWATCH + 10, SWATCH), 2)
 
    # Холст
    screen.blit(canvas, (0, CANVAS_Y))
 
    # Подсказка внизу
    hint = font.render(
        f"Инструмент: {NAMES[tool]}   |   C - очистить",
        True, (60, 60, 60)
    )
    screen.blit(hint, (10, HEIGHT - 20))
 
    pygame.display.flip()
    clock.tick(60)