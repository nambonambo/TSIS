W, H, C = 800, 640, 20
COLS, ROWS = W // C, H // C
FPS = 10

DB = dict(dbname="snake_game", user="postgres", password="1234", host="localhost", port=5432)

BLK=(0,0,0); WHT=(255,255,255); GRN=(0,200,0); RED=(200,0,0)
DRD=(120,0,0); YLW=(255,220,0); ORG=(255,140,0); GRY=(80,80,80)
CYN=(0,220,220); PRP=(160,0,200); BLU=(0,100,200); DRK=(20,20,30)
PNL=(30,30,45)