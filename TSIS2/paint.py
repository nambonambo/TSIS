import pygame
import sys
from datetime import datetime
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

# Инструменты: 1-7 фигуры, 8-0/- новые
TOOLS = {
    pygame.K_1: "rect",
    pygame.K_2: "circle",
    pygame.K_3: "eraser",
    pygame.K_4: "square",
    pygame.K_5: "righttri",
    pygame.K_6: "equitri",
    pygame.K_7: "rhombus",
    pygame.K_8: "pencil",
    pygame.K_9: "line",
    pygame.K_0: "fill",
    pygame.K_MINUS: "text",
}

NAMES = {
    "rect":     "1-Прямоугольник",
    "circle":   "2-Круг",
    "eraser":   "3-Ластик",
    "square":   "4-Квадрат",
    "righttri": "5-Прям.треуг",
    "equitri":  "6-Равност.треуг",
    "rhombus":  "7-Ромб",
    "pencil":   "8-Карандаш",
    "line":     "9-Линия",
    "fill":     "0-Заливка",
    "text":     "Текст",
}

# Размер кисти
BRUSH_SIZES = {pygame.K_LEFTBRACKET: 2, pygame.K_RIGHTBRACKET: 5, pygame.K_BACKSLASH: 10}
brush_size = 2

# Состояние текста
text_active = False
text_pos = (0, 0)
text_input = ""
text_font = pygame.font.SysFont("Arial", 20)

# Состояние карандаша
prev_pos = None

COLOR = (255, 0, 0)
tool = "rect"
drawing = False
start = (0, 0)
snapshot = None
CANVAS_Y = SWATCH + 14

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            # Текстовый инструмент
            if text_active:
                if event.key == pygame.K_RETURN:
                    txt_surf = text_font.render(text_input, True, COLOR)
                    canvas.blit(txt_surf, text_pos)
                    text_active = False
                    text_input = ""
                elif event.key == pygame.K_ESCAPE:
                    text_active = False
                    text_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    text_input = text_input[:-1]
                else:
                    text_input += event.unicode
            else:
                if event.key in TOOLS:
                    tool = TOOLS[event.key]
                if event.key in BRUSH_SIZES:
                    brush_size = BRUSH_SIZES[event.key]
                if event.key == pygame.K_c:
                    canvas.fill((255, 255, 255))
                # сохранялка
                if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    fname = datetime.now().strftime("canvas_%Y%m%d_%H%M%S.png")
                    pygame.image.save(canvas, fname)

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            for i, col in enumerate(PALETTE):
                sx = 10 + i * (SWATCH + 4)
                if sx <= mx <= sx + SWATCH and PALETTE_Y <= my <= PALETTE_Y + SWATCH:
                    COLOR = col
                    break
            else:
                if my >= CANVAS_Y:
                    cy = my - CANVAS_Y
                    if tool == "fill":
                        flood_fill(canvas, mx, cy, COLOR)
                    elif tool == "text":
                        text_active = True
                        text_pos = (mx, cy)
                        text_input = ""
                    else:
                        drawing = True
                        start = (mx, cy)
                        snapshot = canvas.copy()

        if event.type == pygame.MOUSEMOTION and drawing:
            mx, my = event.pos
            cy = my - CANVAS_Y
            x0, y0 = start
            if tool == "eraser":
                draw_eraser(canvas, mx, cy)
            elif tool == "pencil":
                if prev_pos:
                    draw_pencil(canvas, COLOR, prev_pos[0], prev_pos[1], mx, cy, brush_size)
                prev_pos = (mx, cy)
            else:
                canvas.blit(snapshot, (0, 0))

        if event.type == pygame.MOUSEBUTTONUP and drawing:
            drawing = False
            mx, my = event.pos
            x0, y0 = start
            x1, y1 = mx, my - CANVAS_Y
            prev_pos_ref = None
            if tool == "rect":       draw_rectangle(canvas, COLOR, x0, y0, x1, y1)
            elif tool == "circle":   draw_circle(canvas, COLOR, x0, y0, x1, y1)
            elif tool == "square":   draw_square(canvas, COLOR, x0, y0, x1, y1)
            elif tool == "righttri": draw_right_triangle(canvas, COLOR, x0, y0, x1, y1)
            elif tool == "equitri":  draw_equilateral_triangle(canvas, COLOR, x0, y0, x1, y1)
            elif tool == "rhombus":  draw_rhombus(canvas, COLOR, x0, y0, x1, y1)
            elif tool == "line":     draw_line(canvas, COLOR, x0, y0, x1, y1, brush_size)

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

    # Текст в процессе ввода
    if text_active:
        preview = canvas.copy()
        txt_surf = text_font.render(text_input + "|", True, COLOR)
        preview.blit(txt_surf, text_pos)
        screen.blit(preview, (0, CANVAS_Y))

    # Линия
    if drawing and tool == "line":
        mx, my = pygame.mouse.get_pos()
        x0, y0 = start
        pygame.draw.line(screen, COLOR, (x0, y0 + CANVAS_Y), (mx, my), brush_size)

    # Подсказки снизу
    line1 = "1-Прямоугольник  2-Круг  3-Ластик  4-Квадрат  5-Прям.треуг  6-Равност.треуг  7-Ромб"
    line2 = f"8-Карандаш  9-Линия  0-Заливка  --Текст  | кисть: [/]/\\ ({brush_size}px)  | C-очистить  Ctrl+S-сохранить  | Сейчас: {NAMES[tool]}"
    screen.blit(font.render(line1, True, (60, 60, 60)), (10, HEIGHT - 36))
    screen.blit(font.render(line2, True, (60, 60, 60)), (10, HEIGHT - 18))

    pygame.display.flip()
    clock.tick(60)