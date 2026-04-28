import pygame, sys, random, time

W, H = 480, 640
LANES = 4
RL, RR = 80, 400
LW = (RR - RL) // LANES
FPS = 60

def lx(l): return RL + l * LW + LW // 2

def draw_car(sc, x, y, color, shield=False):
    pygame.draw.rect(sc, color, (x-18, y-30, 36, 60), border_radius=6)
    pygame.draw.rect(sc, (255,255,255), (x-18, y-30, 36, 60), 2, border_radius=6)
    pygame.draw.rect(sc, (150,220,255), (x-12, y-22, 24, 14), border_radius=3)
    pygame.draw.rect(sc, (150,220,255), (x-12, y+6, 24, 10), border_radius=2)
    if shield: pygame.draw.ellipse(sc, (0,180,255), (x-22, y-34, 44, 68), 3)

PU_COLORS = {"nitro":(255,140,0), "shield":(0,180,255), "repair":(0,220,100)}
OBS_C = {"barrier":(200,50,50), "oil":(30,30,80), "pothole":(100,80,60), "speedbump":(200,200,50)}
OBS_SLOW = {"oil","pothole","speedbump"}
COIN_DATA = {"b":(1,(180,100,40)), "s":(3,(190,190,190)), "g":(10,(240,200,30))}

pygame.init()
sc = pygame.display.set_mode((W, H))
pygame.display.set_caption("Racer v3")
ck = pygame.time.Clock()

def reset():
    return dict(lane=1, px=lx(1), py=H-100, shield=False, nitro=False, pu=None, pu_end=0,
                enemies=[], coins=[], obs=[], pups=[],
                coins_count=0, dist=0.0, road_off=0,
                te=0, tc=0, to=0, tp=0,
                slowed=False, slow_end=0, base_spd=3.5, spd=3.5, over=False)

g = reset()
font = pygame.font.SysFont(None, 28)

while True:
    dt = ck.tick(FPS) / 1000.0

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
        if ev.type == pygame.KEYDOWN and not g["over"]:
            if ev.key in (pygame.K_LEFT, pygame.K_a): g["lane"]=max(0,g["lane"]-1); g["px"]=lx(g["lane"])
            if ev.key in (pygame.K_RIGHT, pygame.K_d): g["lane"]=min(LANES-1,g["lane"]+1); g["px"]=lx(g["lane"])
        if ev.type == pygame.KEYDOWN and g["over"] and ev.key == pygame.K_r:
            g = reset()

    if not g["over"]:
        if g["pu"]=="nitro" and time.time()>g["pu_end"]: g["nitro"]=False; g["pu"]=None
        if g["slowed"] and time.time()>g["slow_end"]: g["slowed"]=False
        eff = g["spd"]*(0.5 if g["slowed"] else 1)*(3.0 if g["nitro"] else 1)
        g["road_off"] = (g["road_off"]+eff)%60
        g["dist"] += eff*dt*60/8000*100
        factor = min(1+g["dist"]/100*0.3, 2.5); es = eff*factor

        g["te"]+=dt
        if g["te"]>max(0.5,1.5/factor):
            g["te"]=0; l=random.randint(0,LANES-1)
            if not any(e["lane"]==l and e["y"]<60 for e in g["enemies"]):
                g["enemies"].append({"lane":l,"x":lx(l),"y":-80,"spd":es,"col":random.choice([(180,60,60),(60,60,180),(60,160,60)])})
        g["tc"]+=dt
        if g["tc"]>1.0:
            g["tc"]=0
            for l in random.sample(range(LANES),2):
                k=random.choices(["b","s","g"],weights=[10,6,2])[0]; v,c=COIN_DATA[k]
                g["coins"].append({"x":lx(l),"y":-20,"spd":es*0.8,"val":v,"col":c})
        g["to"]+=dt
        if g["to"]>max(1.0,3.0/factor):
            g["to"]=0; k=random.choice(list(OBS_C))
            g["obs"].append({"x":lx(random.randint(0,LANES-1)),"y":-30,"spd":es*0.7,"k":k})
        g["tp"]+=dt
        if g["tp"]>3:
            g["tp"]=0; k=random.choice(["nitro","shield","repair"]); l=random.randint(0,LANES-1)
            g["pups"].append({"x":lx(l),"y":-20,"spd":es*0.7,"k":k,"born":time.time()})

        for obj in g["enemies"]+g["coins"]+g["obs"]+g["pups"]: obj["y"]+=obj["spd"]

        pr=pygame.Rect(g["px"]-18,g["py"]-30,36,60)
        for e in g["enemies"][:]:
            if pr.colliderect(pygame.Rect(e["x"]-18,e["y"]-30,36,60)):
                if g["shield"]: g["shield"]=False;g["pu"]=None;g["enemies"].remove(e)
                else: g["over"]=True
        for o in g["obs"][:]:
            if not g["over"] and pr.colliderect(pygame.Rect(o["x"]-22,o["y"]-12,44,24)):
                if g["shield"]: g["shield"]=False;g["pu"]=None;g["obs"].remove(o)
                elif o["k"] in OBS_SLOW: g["slowed"]=True;g["slow_end"]=time.time()+2;g["obs"].remove(o)
                else: g["over"]=True
        for c in g["coins"][:]:
            if pr.colliderect(pygame.Rect(c["x"]-12,c["y"]-12,24,24)):
                g["coins_count"]+=c["val"]; g["coins"].remove(c); g["spd"]=g["base_spd"]+g["coins_count"]*0.02
        for p in g["pups"][:]:
            if pr.colliderect(pygame.Rect(p["x"]-14,p["y"]-14,28,28)):
                if g["pu"] is None:
                    k=p["k"]
                    if k=="nitro": g["nitro"]=True;g["pu_end"]=time.time()+4;g["pu"]="nitro"
                    elif k=="shield": g["shield"]=True;g["pu"]="shield"
                g["pups"].remove(p)

        g["pups"]=[p for p in g["pups"] if time.time()-p["born"]<5]
        g["enemies"]=[e for e in g["enemies"] if e["y"]<H+80]
        g["coins"]=[c for c in g["coins"] if c["y"]<H+30]
        g["obs"]=[o for o in g["obs"] if o["y"]<H+30]
        g["pups"]=[p for p in g["pups"] if p["y"]<H+30]

    # draw
    sc.fill((40,40,40))
    pygame.draw.rect(sc,(70,70,70),(RL,0,RR-RL,H))
    for i in range(1,LANES):
        x=RL+i*LW
        for y in range(int(-60+g["road_off"]),H,60): pygame.draw.rect(sc,(200,200,100),(x-2,y,4,30))
    pygame.draw.rect(sc,(220,180,30),(RL-4,0,4,H)); pygame.draw.rect(sc,(220,180,30),(RR,0,4,H))

    for e in g["enemies"]: draw_car(sc,e["x"],e["y"],e["col"])
    for c in g["coins"]: pygame.draw.circle(sc,c["col"],(int(c["x"]),int(c["y"])),12)
    for o in g["obs"]:
        pygame.draw.rect(sc,OBS_C[o["k"]],(o["x"]-22,o["y"]-12,44,24),border_radius=4)
        t=pygame.font.SysFont(None,16).render(o["k"][:4].upper(),True,(255,255,255))
        sc.blit(t,(o["x"]-t.get_width()//2,o["y"]-t.get_height()//2))
    for p in g["pups"]:
        pygame.draw.polygon(sc,PU_COLORS[p["k"]],[(p["x"],p["y"]-14),(p["x"]+14,p["y"]+8),(p["x"]-14,p["y"]+8)])

    draw_car(sc,g["px"],g["py"],(220,50,50),g["shield"])

    score=int(g["coins_count"]*10+g["dist"]*5)
    sc.blit(font.render(f"Coins:{g['coins_count']}  Score:{score}",True,(255,255,255)),(8,10))
    bw=200; pct=min(g["dist"]/100,1.0)
    pygame.draw.rect(sc,(100,100,100),(W//2-bw//2,10,bw,14),border_radius=4)
    pygame.draw.rect(sc,(80,200,80),(W//2-bw//2,10,int(bw*pct),14),border_radius=4)
    sc.blit(font.render(f"{int(g['dist'])}%",True,(255,255,255)),(W//2-16,26))
    if g["pu"]:
        lbl=f"NITRO {max(0,g['pu_end']-time.time()):.1f}s" if g["pu"]=="nitro" else g["pu"].upper()
        pt=font.render(lbl,True,PU_COLORS[g["pu"]]); sc.blit(pt,(W-pt.get_width()-10,10))
    if g["slowed"]:
        st=font.render("SLOWED!",True,(255,100,0)); sc.blit(st,(W//2-st.get_width()//2,50))
    if g["over"]:
        t=pygame.font.SysFont(None,42).render("GAME OVER  R=restart",True,(255,80,80))
        sc.blit(t,(W//2-t.get_width()//2,H//2-20))

    pygame.display.flip()