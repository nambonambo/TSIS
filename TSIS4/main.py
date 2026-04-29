import pygame, sys, random, json
from config import *
try:
    import db; DB_ON = True
except: DB_ON = False
 
pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Snake TSIS4")
clock = pygame.time.Clock()
F = pygame.font.SysFont("monospace", 16)
FB = pygame.font.SysFont("monospace", 44, bold=True)
FM = pygame.font.SysFont("monospace", 24)
 
# ── utils ──
def cfg():
    try: return json.load(open("settings.json"))
    except: return {"snake_color":[0,200,0],"grid":True,"sound":False}
 
def save_cfg(s): json.dump(s, open("settings.json","w"), indent=2)
 
def rnd(exc):
    while True:
        p = (random.randint(0,COLS-1), random.randint(0,ROWS-1))
        if p not in exc: return p
 
def txt(s, fn, color=WHT): return fn.render(s, True, color)
 
def btn(label, r, hover=False):
    pygame.draw.rect(screen, (70,70,110) if hover else PNL, r, border_radius=5)
    pygame.draw.rect(screen, GRY, r, 1, border_radius=5)
    t = FM.render(label, True, WHT)
    screen.blit(t, (r.x+(r.w-t.get_width())//2, r.y+(r.h-t.get_height())//2))
 
def blit_center(surface, y, color=WHT, fn=None):
    fn = fn or FM
    screen.blit(surface, (W//2-surface.get_width()//2, y))
 
def screen_menu():
    username = ""
    buttons = ["Play","Leaderboard","Settings","Quit"]
    rects = [pygame.Rect(W//2-100, 290+i*58, 200, 42) for i in range(4)]
    while True:
        mx,my = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_BACKSPACE: username = username[:-1]
                elif e.key == pygame.K_RETURN: pass
                elif len(username)<18 and e.unicode.isprintable(): username += e.unicode
            if e.type == pygame.MOUSEBUTTONDOWN:
                for i,r in enumerate(rects):
                    if r.collidepoint(mx,my):
                        if buttons[i]=="Play": return username or "Player"
                        if buttons[i]=="Leaderboard": screen_leaderboard(); break
                        if buttons[i]=="Settings": screen_settings(); break
                        if buttons[i]=="Quit": pygame.quit(); sys.exit()
        screen.fill(DRK)
        screen.blit(txt("SNAKE", FB, GRN), (W//2-80, 80))
        screen.blit(txt("Name:", F, GRY), (W//2-100, 200))
        ir = pygame.Rect(W//2-100,220,200,36)
        pygame.draw.rect(screen, PNL, ir, border_radius=4)
        pygame.draw.rect(screen, CYN, ir, 1, border_radius=4)
        screen.blit(FM.render(username+"|", True, WHT), (ir.x+6, ir.y+6))
        for label,r in zip(buttons,rects): btn(label, r, r.collidepoint(mx,my))
        pygame.display.flip(); clock.tick(60)
 
def screen_leaderboard():
    rows = []
    if DB_ON:
        try: rows = db.top10()
        except: pass
    back = pygame.Rect(W//2-80, H-70, 160, 40)
    while True:
        mx,my = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN and back.collidepoint(mx,my): return
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE: return
        screen.fill(DRK)
        screen.blit(txt("LEADERBOARD", FB, YLW), (W//2-140,40))
        for i,(col,h) in enumerate(zip([50,120,340,450,560],["#","Name","Score","Level","Date"])):
            screen.blit(txt(h, F, GRY), (col,110))
        for rank,(name,score,lvl,dt) in enumerate(rows,1):
            y = 140+rank*32; c = YLW if rank==1 else WHT
            for val,x in zip([rank,name,score,lvl,dt],[50,120,340,450,560]):
                screen.blit(txt(str(val), F, c), (x,y))
        if not rows: screen.blit(txt("No records yet", FM, GRY), (W//2-90, 250))
        btn("Back", back, back.collidepoint(mx,my))
        pygame.display.flip(); clock.tick(60)
 
def screen_settings():
    s = cfg()
    colors = {"Green":[0,200,0],"Blue":[0,100,220],"Orange":[255,140,0],"White":[220,220,220]}
    cnames = list(colors.keys())
    ci = next((i for i,v in enumerate(colors.values()) if list(v)==s["snake_color"]), 0)
    save_btn = pygame.Rect(W//2-100, H-100, 200, 42)
    while True:
        mx,my = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if pygame.Rect(W//2-100,200,200,40).collidepoint(mx,my): s["grid"] = not s["grid"]
                if pygame.Rect(W//2-100,260,200,40).collidepoint(mx,my): s["sound"] = not s["sound"]
                if pygame.Rect(W//2-100,320,200,40).collidepoint(mx,my):
                    ci = (ci+1)%len(cnames); s["snake_color"] = list(colors[cnames[ci]])
                if save_btn.collidepoint(mx,my): save_cfg(s); return
        screen.fill(DRK)
        screen.blit(txt("SETTINGS", FB, YLW), (W//2-100,60))
        for label,key,y in [("Grid","grid",200),("Sound","sound",260)]:
            r = pygame.Rect(W//2-100,y,200,40)
            pygame.draw.rect(screen,PNL,r,border_radius=5)
            pygame.draw.rect(screen,GRY,r,1,border_radius=5)
            t = FM.render(f"{label}: {'ON' if s[key] else 'OFF'}", True, CYN if s[key] else WHT)
            screen.blit(t,(r.x+(r.w-t.get_width())//2, r.y+8))
        cr = pygame.Rect(W//2-100,320,200,40)
        pygame.draw.rect(screen,PNL,cr,border_radius=5); pygame.draw.rect(screen,GRY,cr,1,border_radius=5)
        screen.blit(FM.render(f"Color: {cnames[ci]}", True, tuple(colors[cnames[ci]])), (cr.x+8,cr.y+8))
        btn("Save & Back", save_btn, save_btn.collidepoint(mx,my))
        pygame.display.flip(); clock.tick(60)
 
def screen_gameover(score, level, pb):
    r_btn = pygame.Rect(W//2-210,380,190,42)
    m_btn = pygame.Rect(W//2+20,380,190,42)
    while True:
        mx,my = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if r_btn.collidepoint(mx,my): return "retry"
                if m_btn.collidepoint(mx,my): return "menu"
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r: return "retry"
                if e.key == pygame.K_ESCAPE: return "menu"
        screen.fill(DRK)
        for t,y,c in [(txt("GAME OVER",FB,RED),150,RED),(txt(f"Score: {score}",FM,WHT),250,WHT),
                      (txt(f"Level: {level}",FM,WHT),290,WHT),(txt(f"Best: {pb}",FM,YLW),330,YLW)]:
            screen.blit(t,(W//2-t.get_width()//2,y))
        btn("Retry [R]",r_btn,r_btn.collidepoint(mx,my)); btn("Menu [Esc]",m_btn,m_btn.collidepoint(mx,my))
        pygame.display.flip(); clock.tick(60)
 
# ── game logic ──
def run_game(pid, pb):
    s = cfg()
    snake_col = tuple(s["snake_color"]); show_grid = s["grid"]
    cx,cy = COLS//2, ROWS//2
    snake = [(cx,cy),(cx-1,cy),(cx-2,cy)]
    d = (1,0); nd = (1,0)
    score=0; level=1; eaten=0; fps=FPS
    obstacles = []
    shield = False; effect = None; effect_end = 0
 
    # food: (pos, weight, spawn_time, lifetime, poisoned)
    def new_food():
        exc = set(snake)|set(obstacles)
        pos = rnd(exc)
        w = random.choice([1,2,3])
        lt = random.randint(5000,10000)
        poison = random.random() < 0.15
        return [pos, w, pygame.time.get_ticks(), lt, poison]
 
    # bonus: (pos, type, spawn_time)  types: speed/slow/shield
    def new_bonus():
        exc = set(snake)|set(obstacles)
        return [rnd(exc), random.choice(["speed","slow","shield"]), pygame.time.get_ticks()]
 
    def place_obstacles():
        obs = []
        head = snake[0]
        for _ in range(4+level*2):
            for _ in range(60):
                p = rnd(set(snake)|set(obs))
                if abs(p[0]-head[0])>3 or abs(p[1]-head[1])>3:
                    obs.append(p); break
        return obs
 
    food = new_food()
    bonus = None
    bonus_next = pygame.time.get_ticks() + random.randint(5000,12000)
    BCOL = {"speed":CYN,"slow":BLU,"shield":PRP}
 
    while True:
        clock.tick(fps)
        now = pygame.time.get_ticks()
        mx,my = pygame.mouse.get_pos()
 
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                dirs={pygame.K_UP:(0,-1),pygame.K_DOWN:(0,1),pygame.K_LEFT:(-1,0),pygame.K_RIGHT:(1,0),
                      pygame.K_w:(0,-1),pygame.K_s:(0,1),pygame.K_a:(-1,0),pygame.K_d:(1,0)}
                if e.key in dirs:
                    nd2 = dirs[e.key]
                    if (nd2[0]+d[0], nd2[1]+d[1]) != (0,0): nd = nd2
 
        d = nd
        if effect and now > effect_end:
            effect = None; fps = FPS + (level-1)*2
 
        head = ((snake[0][0]+d[0])%COLS, (snake[0][1]+d[1])%ROWS)
 
        if head in snake[1:] or head in obstacles:
            if shield: shield = False
            else: return score, level
 
        snake.insert(0, head)
 
        if head == food[0]:
            if food[4]:  # poisoned
                for _ in range(2):
                    if len(snake)>1: snake.pop()
                if len(snake)<=1: return score, level
            else:
                score += food[1]; eaten += 1
                if eaten % 5 == 0:
                    level += 1; fps = FPS + (level-1)*2
                    if level >= 3: obstacles = place_obstacles()
            food = new_food()
        else:
            snake.pop()
 
        if now - food[2] > food[3]: food = new_food()
 
        if bonus is None and now >= bonus_next: bonus = new_bonus()
        if bonus:
            if now - bonus[2] > 8000: bonus = None; bonus_next = now+random.randint(5000,12000)
            elif head == bonus[0]:
                bt = bonus[1]
                if bt=="speed": fps+=5; effect="SPEED"; effect_end=now+5000
                elif bt=="slow": fps=max(2,fps-4); effect="SLOW"; effect_end=now+5000
                elif bt=="shield": shield=True; effect="SHIELD"; effect_end=now+99999
                bonus=None; bonus_next=now+random.randint(8000,15000)
 
        # draw
        screen.fill(DRK)
        if show_grid:
            for x in range(0,W,C): pygame.draw.line(screen,(30,30,45),(x,0),(x,H))
            for y in range(0,H,C): pygame.draw.line(screen,(30,30,45),(0,y),(W,y))
 
        for ox,oy in obstacles:
            pygame.draw.rect(screen,GRY,(ox*C,oy*C,C,C))
 
        for i,(sx,sy) in enumerate(snake):
            pygame.draw.rect(screen, WHT if i==0 else snake_col, (sx*C+1,sy*C+1,C-2,C-2))
 
        fx,fy = food[0]
        fc = (120,0,0) if food[4] else (RED if food[1]==1 else ORG if food[1]==2 else YLW)
        pygame.draw.rect(screen,fc,(fx*C+2,fy*C+2,C-4,C-4))
        screen.blit(F.render(f"+{food[1]}",True,WHT),(fx*C,fy*C-12))
 
        if bonus:
            bx,by = bonus[0]
            pygame.draw.rect(screen,BCOL[bonus[1]],(bx*C,by*C,C,C))
 
        pygame.draw.rect(screen,PNL,(0,0,W,28))
        hud = f"Score:{score}  Level:{level}  PB:{pb}"
        if effect: hud += f"  [{effect}]"
        if shield: hud += "  [SHIELD]"
        screen.blit(F.render(hud,True,WHT),(6,6))
 
        pygame.display.flip()
 
# ── main loop ──
def main():
    if DB_ON:
        try: db.init()
        except: pass
 
    while True:
        username = screen_menu()
        pid = None; pb = 0
        if DB_ON:
            try: pid = db.get_or_create(username); pb = db.best(pid)
            except: pass
 
        while True:
            score, level = run_game(pid, pb)
            if DB_ON and pid:
                try: db.save(pid,score,level); pb = db.best(pid)
                except: pass
            action = screen_gameover(score, level, pb)
            if action == "menu": break
 
main()