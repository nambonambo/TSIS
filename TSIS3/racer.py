import pygame, sys, random
 
W, H = 480, 640
LANES = 4
RL, RR = 80, 400
LW = (RR - RL) // LANES
FPS = 60
 
def lx(l): return RL + l * LW + LW // 2
 
pygame.init()
sc = pygame.display.set_mode((W, H))
pygame.display.set_caption("Racer v1")
ck = pygame.time.Clock()
 
lane = 1
px = lx(lane)
py = H - 100
road_off = 0
spd = 3.5
enemies = []
t_enemy = 0
over = False
font = pygame.font.SysFont(None, 48)
 
while True:
    dt = ck.tick(FPS) / 1000.0
 
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
        if ev.type == pygame.KEYDOWN and not over:
            if ev.key in (pygame.K_LEFT, pygame.K_a): lane = max(0, lane - 1); px = lx(lane)
            if ev.key in (pygame.K_RIGHT, pygame.K_d): lane = min(LANES-1, lane + 1); px = lx(lane)
        if ev.type == pygame.KEYDOWN and over and ev.key == pygame.K_r:
            lane=1; px=lx(lane); enemies=[]; t_enemy=0; over=False
 
    if not over:
        road_off = (road_off + spd) % 60
        t_enemy += dt
        if t_enemy > 1.2:
            t_enemy = 0
            l = random.randint(0, LANES-1)
            enemies.append([lx(l), -60, spd])
 
        for e in enemies: e[1] += e[2]
        enemies = [e for e in enemies if e[1] < H + 60]
 
        pr = pygame.Rect(px-18, py-30, 36, 60)
        for e in enemies:
            if pr.colliderect(pygame.Rect(e[0]-18, e[1]-30, 36, 60)):
                over = True
 
    # draw
    sc.fill((40, 40, 40))
    pygame.draw.rect(sc, (70, 70, 70), (RL, 0, RR-RL, H))
    for i in range(1, LANES):
        x = RL + i * LW
        for y in range(int(-60 + road_off), H, 60):
            pygame.draw.rect(sc, (200, 200, 100), (x-2, y, 4, 30))
    pygame.draw.rect(sc, (220, 180, 30), (RL-4, 0, 4, H))
    pygame.draw.rect(sc, (220, 180, 30), (RR, 0, 4, H))
 
    for e in enemies:
        pygame.draw.rect(sc, (180, 60, 60), (e[0]-18, e[1]-30, 36, 60))
 
    pygame.draw.rect(sc, (220, 50, 50), (px-18, py-30, 36, 60))
 
    if over:
        t = font.render("GAME OVER  R=restart", True, (255, 80, 80))
        sc.blit(t, (W//2 - t.get_width()//2, H//2 - 24))
 
    pygame.display.flip()