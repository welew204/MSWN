from datetime import datetime
import sqlite3

import click
from flask import current_app, g

from server_side.db_ref_vals import build_anchors, build_ref_bone_end_vals, build_joint_ref_vals, build_zone_ref_vals, build_adj
from server_side.hashing import hash_password
from server_side.add_mover import add_new_mover

"""creating connection to DB (even if it doesn't exist yet

g = "special object that is unique for each request"; stores data that might be accesed by multiple functions
during request

current_app = "special object that points to the Flask app handling the request

"""


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


"""Python functions that will run SQL commands"""


def init_db():
    db = get_db()

    with current_app.open_resource('mswn_2.sql') as f:
        db.executescript(f.read().decode('utf8'))

    build_ref_bone_end_vals(db=db)
    build_joint_ref_vals(db=db)
    build_zone_ref_vals(db=db)
    build_anchors(db=db)
    build_adj(db=db)
    # autopopulate two coach users (Will Belew, Guest)
    curs = db.cursor()
    wb_pw = "eggplant204"
    wb_hashed = hash_password(wb_pw)
    tuhday = datetime.now().strftime("%Y-%m-%d")
    curs.execute('''INSERT INTO coaches 
                    (first_name, 
                    last_name,
                    date_added,
                    hpassword
                    ) VALUES (?,?,?,?)''',
                 ("Will", "Belew", tuhday, wb_hashed))
    guest_pw = "workNice"
    guest_hashed = hash_password(guest_pw)
    curs.execute('''INSERT INTO coaches 
                    (first_name, 
                    last_name,
                    date_added,
                    hpassword
                    ) VALUES (?,?,?,?)''',
                 ("Guest", "User", tuhday, guest_hashed))
    db.commit()
    print("~~default coaches added!")
    # autopopulate a mover (Debbie Mover)
    c_id = curs.execute(
        '''SELECT id FROM coaches WHERE first_name = (?) AND last_name = (?)''', ("Will", "Belew")).fetchone()
    g_id = curs.execute(
        '''SELECT id FROM coaches WHERE first_name = (?) AND last_name = (?)''', ("Guest", "User")).fetchone()
    add_new_mover(db, "Debbie", "Mover", c_id["id"], 130)
    add_new_mover(db, "JoeBlow", "Mover", g_id["id"], 160)
    print("~~~default movers added!")


@click.command('init-db')
def init_db_command():
    """clear the existing data and create new tables"""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
