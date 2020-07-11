import random
import string
from StatementGame.database import conn, c, d, get_table_id
import json

with open("StatementGame/gameNames.json") as f:
    CODES = json.loads(f.read())

def get_game_code():
    return random.choice(CODES)


def new_game():
    c.execute("INSERT INTO game (code) VALUES ('{}')".format(get_game_code()))
    conn.commit()
    return c.lastrowid


def get_members(game_id):
    d.execute("SELECT * FROM player WHERE game={}".format(game_id))
    return d.fetchall()


def get_game(game_id):
    d.execute("SELECT * FROM game WHERE code='{}'".format(game_id))
    return d.fetchone()


def remove_code(game_id):
    d.execute("UPDATE game SET code=NULL WHERE id={}".format(game_id))
    conn.commit()


def get_summary_data(game_id):
    d.execute('select round.id, game, round, statement.text as "real", p.text as "fake" from round join statement on statement.id=round.regularStatement join statement p on round.falseStatement=p.id where game={}'.format(game_id))
    rs = d.fetchall()
    for r in rs:
        d.execute("select player.id, player.name, player.alien, response.level as 'response' from response join player on player.id=response.player where round={} and player.alien=0".format(r["id"]))
        r["humans"] = d.fetchall()

        d.execute("select player.id, player.name, player.alien, response.level as 'response' from response join player on player.id=response.player where round={} and player.alien=1".format(r["id"]))
        r["aliens"] = d.fetchall()

    return rs


def delete_game(game_id):
    c.execute("DELETE FROM game WHERE id={}".format(game_id))
    conn.commit()


def is_game_running(game_id):
    c.execute("SELECT COUNT(*) FROM game WHERE id={}".format(game_id))
    return bool(c.fetchone()[0] > 0)