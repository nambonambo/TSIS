import pygame, sys, random

W, H = 480, 640
LANES = 4
RL, RR = 80, 400
LW = (RR - RL) // LANES
FPS = 60

def lx(l): return RL + l * LW + LW // 2

def draw_car(sc, x, y, color):
    pygame.draw.rect(sc, color, (x-18, y-30, 36, 60), border_radius=6)
    pygame.draw.rect(sc, (255, 255, 255), (x-18, y-30, 36, 60), 2, border_radius=6)
    pygame.draw.rect(sc, (150, 220, 255), (x-12, y-22, 24, 14), border_radius=3)
    pygame.draw.rect(sc, (150, 220, 255), (x-12, y+6, 24, 10), border_radius=2)
    pygame.draw.rect(sc, (255, 220, 50), (x-18, y-30, 8, 6), border_radius=2)
    pygame.draw.rect(sc, (255, 220, 50), (x+10, y-30, 8, 6), border_radius=2)
    pygame.draw.rect(sc, (200, 50, 50), (x-18, y+22, 8, 6), border_radius=2)
    pygame.draw.rect(sc, (200, 50, 50), (x+10, y+22, 8, 6), border_radius=2)

pygame.init()
sc = pygame.display.set_mode((W, H))
pygame.display.set_caption("Racer v2")
ck = pygame.time.Clock()

lane = 1; px = lx(lane); py = H - 100
road_off = 0; base_spd = 3.5; spd = base_spd
enemies = []; coins = []
t_enemy = t_coin = 0
coin_count = 0; score = 0
over = False
font = pygame.font.SysFont(None, 36)

COIN_DATA = {"b": (1, (180,100,40)), "s": (3, (190,190,190)), "g": (10, (240,200,30))}

while True:
    dt = ck.tick(FPS) / 1000.0

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
        if ev.type == pygame.KEYDOWN and not over:
            if ev.key in (pygame.K_LEFT, pygame.K_a): lane=max(0,lane-1); px=lx(lane)
            if ev.key in (pygame.K_RIGHT, pygame.K_d): lane=min(LANES-1,lane+1); px=lx(lane)
        if ev.type == pygame.KEYDOWN and over and ev.key == pygame.K_r:
            lane=1; px=lx(lane); enemies=[]; coins=[]; t_enemy=t_coin=0
            coin_count=0; score=0; spd=base_spd; over=False

    if not over:
        road_off = (road_off + spd) % 60

        t_enemy += dt
        if t_enemy > 1.2:
            t_enemy = 0; l = random.randint(0, LANES-1)
            enemies.append({"x":lx(l),"y":-60,"spd":spd,"col":random.choice([(180,60,60),(60,60,180),(60,160,60)])})

        t_coin += dt
        if t_coin > 1.0:
            t_coin = 0
            for l in random.sample(range(LANES), 2):
                k = random.choices(["b","s","g"], weights=[10,6,2])[0]
                v, c = COIN_DATA[k]
                coins.append({"x":lx(l),"y":-20,"spd":spd*0.8,"val":v,"col":c})

        for e in enemies: e["y"] += e["spd"]
        for c in coins:   c["y"] += c["spd"]
        enemies = [e for e in enemies if e["y"] < H+80]
        coins   = [c for c in coins   if c["y"] < H+30]

        pr = pygame.Rect(px-18, py-30, 36, 60)
        for e in enemies:
            if pr.colliderect(pygame.Rect(e["x"]-18, e["y"]-30, 36, 60)):
                over = True

        for c in coins[:]:
            if pr.colliderect(pygame.Rect(c["x"]-12, c["y"]-12, 24, 24)):
                coin_count += c["val"]; coins.remove(c)
                spd = base_spd + coin_count * 0.02
                score = coin_count * 10

    # draw
    sc.fill((40, 40, 40))
    pygame.draw.rect(sc, (70,70,70), (RL, 0, RR-RL, H))
    for i in range(1, LANES):
        x = RL + i * LW
        for y in range(int(-60+road_off), H, 60):
            pygame.draw.rect(sc, (200,200,100), (x-2,y,4,30))
    pygame.draw.rect(sc, (220,180,30), (RL-4,0,4,H))
    pygame.draw.rect(sc, (220,180,30), (RR,0,4,H))

    for e in enemies: draw_car(sc, e["x"], e["y"], e["col"])
    for c in coins:   pygame.draw.circle(sc, c["col"], (int(c["x"]), int(c["y"])), 12)

    draw_car(sc, px, py, (220, 50, 50))

    sc.blit(font.render(f"Coins: {coin_count}  Score: {score}", True, (255,255,255)), (8, 10))

    if over:
        t = font.render("GAME OVER  R=restart", True, (255,80,80))
        sc.blit(t, (W//2-t.get_width()//2, H//2-20))

    pygame.display.flip()