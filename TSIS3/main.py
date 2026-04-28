import pygame, sys
from racer import Game, FPS
from ui import menu, name_input, settings_screen, lb_screen, gameover_screen
from persistence import load_settings, save_settings, load_leaderboard, save_score

pygame.init()
sc=pygame.display.set_mode((480,640)); pygame.display.set_caption("RACER"); ck=pygame.time.Clock()
settings=load_settings(); pname=None

def run_game():
    g=Game(settings); prev=pygame.time.get_ticks()
    while not g.over:
        dt=(pygame.time.get_ticks()-prev)/1000.0; prev=pygame.time.get_ticks()
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: return "quit",g
            if ev.type==pygame.KEYDOWN:
                if ev.key in(pygame.K_LEFT,pygame.K_a): g.move(-1)
                if ev.key in(pygame.K_RIGHT,pygame.K_d): g.move(1)
                if ev.key==pygame.K_ESCAPE: return "menu",g
        g.update(dt); g.draw(sc); pygame.display.flip(); ck.tick(FPS)
    return "over",g

while True:
    action=menu(sc,ck)
    if action=="quit": break
    elif action=="play":
        if not pname:
            pname=name_input(sc,ck)
            if not pname: break
        res,g=run_game()
        if res=="quit": break
        if res=="over":
            save_score(pname,g.score,g.dist)
            r=gameover_screen(sc,ck,g.score,g.dist,g.coins_count,g.won)
            if r=="quit": break
    elif action=="lb": lb_screen(sc,ck,load_leaderboard())
    elif action=="settings":
        ns=settings_screen(sc,ck,settings); settings.update(ns); save_settings(settings)

pygame.quit(); sys.exit()