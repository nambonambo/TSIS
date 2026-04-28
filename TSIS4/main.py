import pygame, sys, random
pygame.init()

W, H, C = 600, 600, 20
COLS, ROWS = W//C, H//C
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()
F  = pygame.font.SysFont("monospace", 16)
FB = pygame.font.SysFont("monospace", 44, bold=True)
FM = pygame.font.SysFont("monospace", 24)

BLK=(0,0,0); WHT=(255,255,255); GRN=(0,200,0)
RED=(200,0,0); GRY=(80,80,80); DRK=(20,20,30); PNL=(30,30,45)

def rnd(exc):
    while True:
        p = (random.randint(0,COLS-1), random.randint(0,ROWS-1))
        if p not in exc: return p

def btn(label, r, hover=False):
    pygame.draw.rect(screen, (70,70,110) if hover else PNL, r, border_radius=5)
    pygame.draw.rect(screen, GRY, r, 1, border_radius=5)
    t = FM.render(label, True, WHT)
    screen.blit(t, (r.x+(r.w-t.get_width())//2, r.y+(r.h-t.get_height())//2))

def screen_menu():
    while True:
        mx, my = pygame.mouse.get_pos()
        r_play = pygame.Rect(W//2-100, 280, 200, 44)
        r_quit = pygame.Rect(W//2-100, 340, 200, 44)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if r_play.collidepoint(mx,my): return
                if r_quit.collidepoint(mx,my): pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN: return
        screen.fill(DRK)
        t = FB.render("SNAKE", True, GRN)
        screen.blit(t, (W//2-t.get_width()//2, 160))
        btn("Play", r_play, r_play.collidepoint(mx,my))
        btn("Quit", r_quit, r_quit.collidepoint(mx,my))
        pygame.display.flip(); clock.tick(60)

def screen_gameover(score, level):
    r_btn = pygame.Rect(W//2-110, 340, 200, 44)
    m_btn = pygame.Rect(W//2-110, 395, 200, 44)
    while True:
        mx, my = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if r_btn.collidepoint(mx,my): return "retry"
                if m_btn.collidepoint(mx,my): return "menu"
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r: return "retry"
                if e.key == pygame.K_ESCAPE: return "menu"
        screen.fill(DRK)
        for text, y in [(FB.render("GAME OVER", True, RED), 180),
                        (FM.render(f"Score: {score}", True, WHT), 270),
                        (FM.render(f"Level: {level}", True, WHT), 305)]:
            screen.blit(text, (W//2-text.get_width()//2, y))
        btn("Retry [R]", r_btn, r_btn.collidepoint(mx,my))
        btn("Menu [Esc]", m_btn, m_btn.collidepoint(mx,my))
        pygame.display.flip(); clock.tick(60)

def run_game():
    snake = [(COLS//2, ROWS//2), (COLS//2-1, ROWS//2), (COLS//2-2, ROWS//2)]
    d = (1,0); nd = (1,0)
    food = rnd(set(snake))
    score = 0; level = 1; eaten = 0; fps = 10

    while True:
        clock.tick(fps)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                dirs = {pygame.K_UP:(0,-1), pygame.K_DOWN:(0,1),
                        pygame.K_LEFT:(-1,0), pygame.K_RIGHT:(1,0),
                        pygame.K_w:(0,-1), pygame.K_s:(0,1),
                        pygame.K_a:(-1,0), pygame.K_d:(1,0)}
                if e.key in dirs:
                    nd2 = dirs[e.key]
                    if (nd2[0]+d[0], nd2[1]+d[1]) != (0,0): nd = nd2

        d = nd
        head = (snake[0][0]+d[0], snake[0][1]+d[1])

        if head[0]<0 or head[0]>=COLS or head[1]<0 or head[1]>=ROWS: return score, level
        if head in snake: return score, level

        snake.insert(0, head)
        if head == food:
            score += 1; eaten += 1
            food = rnd(set(snake))
            if eaten % 5 == 0:
                level += 1; fps += 2
        else:
            snake.pop()

        screen.fill(DRK)
        pygame.draw.rect(screen, RED, (food[0]*C+2, food[1]*C+2, C-4, C-4))
        for i,(sx,sy) in enumerate(snake):
            pygame.draw.rect(screen, WHT if i==0 else GRN, (sx*C+1, sy*C+1, C-2, C-2))
        pygame.draw.rect(screen, PNL, (0,0,W,26))
        screen.blit(F.render(f"Score:{score}  Level:{level}", True, WHT), (6,5))
        pygame.display.flip()

def main():
    while True:
        screen_menu()
        while True:
            score, level = run_game()
            action = screen_gameover(score, level)
            if action == "menu": break

main()