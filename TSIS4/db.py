import psycopg2
from config import DB

def conn(): return psycopg2.connect(**DB)

def init():
    c = conn(); cur = c.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS players(id SERIAL PRIMARY KEY, username VARCHAR(50) UNIQUE NOT NULL);
        CREATE TABLE IF NOT EXISTS game_sessions(id SERIAL PRIMARY KEY, player_id INT REFERENCES players(id), score INT NOT NULL, level_reached INT NOT NULL, played_at TIMESTAMP DEFAULT NOW());
    """)
    c.commit(); cur.close(); c.close()

def get_or_create(username):
    c = conn(); cur = c.cursor()
    cur.execute("SELECT id FROM players WHERE username=%s", (username,))
    row = cur.fetchone()
    if not row:
        cur.execute("INSERT INTO players(username) VALUES(%s) RETURNING id", (username,))
        row = cur.fetchone(); c.commit()
    cur.close(); c.close(); return row[0]

def save(pid, score, level):
    c = conn(); cur = c.cursor()
    cur.execute("INSERT INTO game_sessions(player_id,score,level_reached) VALUES(%s,%s,%s)", (pid,score,level))
    c.commit(); cur.close(); c.close()

def top10():
    c = conn(); cur = c.cursor()
    cur.execute("SELECT p.username,gs.score,gs.level_reached,TO_CHAR(gs.played_at,'DD.MM.YY') FROM game_sessions gs JOIN players p ON p.id=gs.player_id ORDER BY gs.score DESC LIMIT 10")
    r = cur.fetchall(); cur.close(); c.close(); return r

def best(pid):
    c = conn(); cur = c.cursor()
    cur.execute("SELECT MAX(score) FROM game_sessions WHERE player_id=%s", (pid,))
    r = cur.fetchone(); cur.close(); c.close(); return r[0] or 0