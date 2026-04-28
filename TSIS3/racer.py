import pygame, random, time

W,H=480,640; LANES=4; RL,RR=80,400; LW=(RR-RL)//LANES; FPS=60
CAR_COLORS={"red":(220,50,50),"blue":(50,100,220),"green":(50,200,80),"yellow":(220,200,30)}
PU_COLORS={"nitro":(255,140,0),"shield":(0,180,255),"repair":(0,220,100)}
OBS_C={"barrier":(200,50,50),"oil":(30,30,80),"pothole":(100,80,60),"speedbump":(200,200,50)}
OBS_SLOW={"oil","pothole","speedbump"}

def lx(l): return RL+l*LW+LW//2

class Game:
    def __init__(self, settings):
        d=settings.get("difficulty","normal")
        self.base_spd={"easy":2.5,"normal":3.5,"hard":5.0}.get(d,3.5)
        self.spd=self.base_spd
        self.car_col=CAR_COLORS.get(settings.get("car_color","red"),(220,50,50))
        self.lane=1; self.px=lx(1); self.py=H-100
        self.shield=False; self.nitro=False; self.pu=None; self.pu_end=0; self.lives=3; self.hit_flash=0
        self.enemies=[]; self.coins=[]; self.obs=[]; self.pups=[]
        self.coins_count=0; self.dist=0.0; self.road_off=0
        self.te=self.tc=self.to=self.tp=0
        self.slowed=False; self.slow_end=0
        self.over=False; self.won=False

    def move(self, d):
        self.lane=max(0,min(LANES-1,self.lane+d)); self.px=lx(self.lane)

    def _spawn_ok(self, lane):
        return not any(e["lane"]==lane and e["y"]<60 for e in self.enemies)

    def update(self, dt):
        if self.over: return
        if self.pu=="nitro" and time.time()>self.pu_end: self.nitro=False; self.pu=None
        if self.slowed and time.time()>self.slow_end: self.slowed=False
        eff=self.spd*(0.5 if self.slowed else 1)*(3.0 if self.nitro else 1)
        self.road_off=(self.road_off+eff)%60
        self.dist+=eff*dt*60/8000*100
        factor=min(1+self.dist/100*0.3,2.5); es=eff*factor

        self.te+=dt
        if self.te>max(0.5,1.5/factor):
            self.te=0; lane=random.randint(0,LANES-1)
            if self._spawn_ok(lane): self.enemies.append({"lane":lane,"x":lx(lane),"y":-80,"spd":es,"col":random.choice([(180,60,60),(60,60,180),(60,160,60)])})
        self.tc+=dt
        if self.tc>1.0:
            self.tc=0
            for lane in random.sample(range(LANES),2):
                k=random.choices(["b","s","g"],weights=[10,6,2])[0]
                v,c={"b":(1,(180,100,40)),"s":(3,(190,190,190)),"g":(10,(240,200,30))}[k]
                self.coins.append({"x":lx(lane),"y":-20,"spd":es*0.8,"val":v,"col":c})
        self.to+=dt
        if self.to>max(1.0,3.0/factor):
            self.to=0; k=random.choice(list(OBS_C))
            self.obs.append({"x":lx(random.randint(0,LANES-1)),"y":-30,"spd":es*0.7,"k":k})
        self.tp+=dt
        if self.tp>3:
            self.tp=0; k=random.choice(["nitro","shield","repair"]); lane=random.randint(0,LANES-1)
            self.pups.append({"x":lx(lane),"y":-20,"spd":es*0.7,"k":k,"born":time.time()})

        for obj in self.enemies+self.coins+self.obs+self.pups: obj["y"]+=obj["spd"]

        pr=pygame.Rect(self.px-18,self.py-30,36,60)
        for e in self.enemies[:]:
            if pr.colliderect(pygame.Rect(e["x"]-18,e["y"]-30,36,60)):
                if self.shield: self.shield=False;self.pu=None;self.enemies.remove(e)
                else:
                    self.lives-=1; self.enemies.remove(e); self.hit_flash=0.4
                    if self.lives<=0: self.over=True; return
        for o in self.obs[:]:
            if pr.colliderect(pygame.Rect(o["x"]-22,o["y"]-12,44,24)):
                if self.shield: self.shield=False;self.pu=None;self.obs.remove(o)
                elif o["k"] in OBS_SLOW: self.slowed=True;self.slow_end=time.time()+2;self.obs.remove(o)
                else:
                    self.lives-=1; self.obs.remove(o); self.hit_flash=0.4
                    if self.lives<=0: self.over=True; return
        for c in self.coins[:]:
            if pr.colliderect(pygame.Rect(c["x"]-12,c["y"]-12,24,24)):
                self.coins_count+=c["val"]; self.coins.remove(c); self.spd=self.base_spd+self.coins_count*0.02
        for p in self.pups[:]:
            if pr.colliderect(pygame.Rect(p["x"]-14,p["y"]-14,28,28)):
                if self.pu is None:
                    k=p["k"]
                    if k=="nitro": self.nitro=True;self.pu_end=time.time()+4;self.pu="nitro"
                    elif k=="shield": self.shield=True;self.pu="shield"
                    elif k=="repair": self.lives=min(self.lives+1,3)
                self.pups.remove(p)

        self.pups=[p for p in self.pups if time.time()-p["born"]<5]
        self.enemies=[e for e in self.enemies if e["y"]<H+80]
        self.coins=[c for c in self.coins if c["y"]<H+30]
        self.obs=[o for o in self.obs if o["y"]<H+30]
        self.pups=[p for p in self.pups if p["y"]<H+30]
        if self.hit_flash>0: self.hit_flash-=dt
        if self.dist>=100: self.won=True; self.over=True

    @property
    def score(self): return int(self.coins_count*10+self.dist*5)

    def draw(self, sc):
        sc.fill((40,40,40))
        pygame.draw.rect(sc,(70,70,70),(RL,0,RR-RL,H))
        for i in range(1,LANES):
            x=RL+i*LW
            for y in range(int(-60+self.road_off),H,60): pygame.draw.rect(sc,(200,200,100),(x-2,y,4,30))
        pygame.draw.rect(sc,(220,180,30),(RL-4,0,4,H)); pygame.draw.rect(sc,(220,180,30),(RR,0,4,H))

        for e in self.enemies:
            pygame.draw.rect(sc,e["col"],(e["x"]-18,e["y"]-30,36,60),border_radius=6)
            pygame.draw.rect(sc,(150,220,255),(e["x"]-12,e["y"]-22,24,14),border_radius=3)
        for c in self.coins: pygame.draw.circle(sc,c["col"],(int(c["x"]),int(c["y"])),12)
        for o in self.obs:
            pygame.draw.rect(sc,OBS_C[o["k"]],(o["x"]-22,o["y"]-12,44,24),border_radius=4)
            t=pygame.font.SysFont(None,16).render(o["k"][:4].upper(),True,(255,255,255))
            sc.blit(t,(o["x"]-t.get_width()//2,o["y"]-t.get_height()//2))
        for p in self.pups:
            pygame.draw.polygon(sc,PU_COLORS[p["k"]],[(p["x"],p["y"]-14),(p["x"]+14,p["y"]+8),(p["x"]-14,p["y"]+8)])

        pygame.draw.rect(sc,self.car_col,(self.px-18,self.py-30,36,60),border_radius=6)
        pygame.draw.rect(sc,(255,255,255),(self.px-18,self.py-30,36,60),2,border_radius=6)
        pygame.draw.rect(sc,(150,220,255),(self.px-12,self.py-22,24,14),border_radius=3)
        if self.shield: pygame.draw.ellipse(sc,(0,180,255),(self.px-22,self.py-34,44,68),3)

        if self.hit_flash>0:
            flash=pygame.Surface((W,H),pygame.SRCALPHA)
            flash.fill((255,0,0,int(min(self.hit_flash/0.4,1)*120)))
            sc.blit(flash,(0,0))

        f=pygame.font.SysFont(None,28); fh=pygame.font.SysFont(None,36)
        sc.blit(f.render(f"Coins:{self.coins_count}",True,(255,255,255)),(8,10))
        sc.blit(f.render(f"Score:{self.score}",True,(255,255,200)),(8,36))
        sc.blit(fh.render("♥"*self.lives+"♡"*(3-self.lives),True,(220,60,60)),(8,60))
        bw=200; pct=min(self.dist/100,1.0)
        pygame.draw.rect(sc,(100,100,100),(W//2-bw//2,10,bw,14),border_radius=4)
        pygame.draw.rect(sc,(80,200,80),(W//2-bw//2,10,int(bw*pct),14),border_radius=4)
        sc.blit(f.render(f"{int(self.dist)}%",True,(255,255,255)),(W//2-16,26))
        if self.pu:
            lbl=f"NITRO {max(0,self.pu_end-time.time()):.1f}s" if self.pu=="nitro" else self.pu.upper()
            pt=f.render(lbl,True,PU_COLORS.get(self.pu,(255,255,255))); sc.blit(pt,(W-pt.get_width()-10,10))
        if self.slowed:
            st=f.render("SLOWED!",True,(255,100,0)); sc.blit(st,(W//2-st.get_width()//2,50))