import pygame
W,H=480,640; ACC=(220,180,30); DK=(30,30,30); WH=(255,255,255)

def btn(s,text,r,f,hi=False):
    pygame.draw.rect(s,ACC if hi else (80,80,80),r,border_radius=8)
    pygame.draw.rect(s,WH,r,2,border_radius=8)
    t=f.render(text,True,(0,0,0) if hi else WH)
    s.blit(t,(r.centerx-t.get_width()//2,r.centery-t.get_height()//2))

def hit(r,p): return r.collidepoint(p)

def menu(sc,ck):
    f1=pygame.font.SysFont(None,56); f=pygame.font.SysFont(None,36)
    bs=[("play","Play",200),("lb","Leaderboard",270),("settings","Settings",340),("quit","Quit",410)]
    while True:
        sc.fill(DK); t=f1.render("RACER",True,ACC); sc.blit(t,(W//2-t.get_width()//2,100))
        mx,my=pygame.mouse.get_pos()
        rs={k:pygame.Rect(140,y,200,50) for k,_,y in bs}
        for k,l,_ in bs: btn(sc,l,rs[k],f,rs[k].collidepoint(mx,my))
        pygame.display.flip()
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: return "quit"
            if ev.type==pygame.MOUSEBUTTONDOWN:
                for k,_,_ in bs:
                    if hit(rs[k],ev.pos): return k
        ck.tick(60)

def name_input(sc,ck):
    f=pygame.font.SysFont(None,36); name=""; b=pygame.Rect(140,340,200,50)
    while True:
        sc.fill(DK); sc.blit(f.render("Enter your name:",True,WH),(120,200))
        pygame.draw.rect(sc,(60,60,60),(100,250,280,44),border_radius=6)
        pygame.draw.rect(sc,ACC,(100,250,280,44),2,border_radius=6)
        sc.blit(f.render(name+"|",True,ACC),(110,260))
        btn(sc,"Start",b,f,True); pygame.display.flip()
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: return None
            if ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_RETURN and name.strip(): return name.strip()
                elif ev.key==pygame.K_BACKSPACE: name=name[:-1]
                elif len(name)<16 and ev.unicode.isprintable(): name+=ev.unicode
            if ev.type==pygame.MOUSEBUTTONDOWN and hit(b,ev.pos) and name.strip(): return name.strip()
        ck.tick(60)

def settings_screen(sc,ck,s):
    f=pygame.font.SysFont(None,34); s=dict(s); back=pygame.Rect(140,520,200,50)
    cols=["red","blue","green","yellow"]; diffs=["easy","normal","hard"]
    while True:
        sc.fill(DK); sc.blit(f.render("SETTINGS",True,ACC),(160,40))
        sb=pygame.Rect(100,120,280,44); btn(sc,f"Sound: {'ON' if s['sound'] else 'OFF'}",sb,f,s["sound"])
        sc.blit(f.render("Car Color:",True,WH),(100,190))
        for i,c in enumerate(cols): btn(sc,c,pygame.Rect(100+i*90,220,80,36),pygame.font.SysFont(None,24),s["car_color"]==c)
        sc.blit(f.render("Difficulty:",True,WH),(100,290))
        for i,d in enumerate(diffs): btn(sc,d,pygame.Rect(100+i*120,320,108,36),pygame.font.SysFont(None,24),s["difficulty"]==d)
        btn(sc,"Back & Save",back,f,True); pygame.display.flip()
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: return s
            if ev.type==pygame.MOUSEBUTTONDOWN:
                if hit(sb,ev.pos): s["sound"]=not s["sound"]
                for i,c in enumerate(cols):
                    if hit(pygame.Rect(100+i*90,220,80,36),ev.pos): s["car_color"]=c
                for i,d in enumerate(diffs):
                    if hit(pygame.Rect(100+i*120,320,108,36),ev.pos): s["difficulty"]=d
                if hit(back,ev.pos): return s
        ck.tick(60)

def lb_screen(sc,ck,lb):
    f=pygame.font.SysFont(None,32); fs=pygame.font.SysFont(None,26); back=pygame.Rect(140,560,200,50)
    while True:
        sc.fill(DK); sc.blit(f.render("TOP 10",True,ACC),(180,30))
        for i,e in enumerate(lb[:10]):
            sc.blit(fs.render(f"{i+1}. {e['name']}  {e['score']}pts  {e['distance']}m",True,ACC if i==0 else WH),(40,80+i*44))
        if not lb: sc.blit(f.render("No scores yet.",True,(120,120,120)),(130,200))
        btn(sc,"Back",back,f,True); pygame.display.flip()
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: return
            if ev.type==pygame.MOUSEBUTTONDOWN and hit(back,ev.pos): return
        ck.tick(60)

def gameover_screen(sc,ck,score,dist,coins,won):
    fb=pygame.font.SysFont(None,52); f=pygame.font.SysFont(None,34)
    r=pygame.Rect(80,440,140,50); m=pygame.Rect(260,440,140,50)
    while True:
        sc.fill(DK)
        sc.blit(fb.render("YOU WIN!" if won else "GAME OVER",True,(80,255,80) if won else (255,80,80)),(W//2-120,100))
        for i,(l,v) in enumerate([("Score",score),("Distance",f"{int(dist)}%"),("Coins",coins)]):
            sc.blit(f.render(f"{l}: {v}",True,WH),(140,200+i*40))
        btn(sc,"Retry",r,f,True); btn(sc,"Menu",m,f,True); pygame.display.flip()
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: return "quit"
            if ev.type==pygame.MOUSEBUTTONDOWN:
                if hit(r,ev.pos): return "retry"
                if hit(m,ev.pos): return "menu"
        ck.tick(60)