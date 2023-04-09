from collections import defaultdict
from datetime import datetime
import sqlite3
import click


def add_new_mover(db, first_name, last_name, coach_id, bodyweight=0):
    date = datetime.now().strftime("%Y-%m-%d")
    if bodyweight <= 0:
        bodyweight = 150
    # create db cnx
    curs = db.cursor()
    # add mover to table
    curs.execute('INSERT INTO movers (first_name, last_name, date_added, coach_id, bodyweight) VALUES (?,?,?,?,?)',
                 (first_name, last_name, date, coach_id, bodyweight))
    db.commit()
    mover_id = curs.lastrowid
    # mover_id_Row = curs.execute(
    #    'SELECT id FROM movers WHERE first_name = (?) AND last_name = (?)', (first_name, last_name)).fetchone()

    # SELECT vals from ref tables
    joint_template = curs.execute('SELECT rowid, * FROM ref_joints').fetchall()
    anchor_template = curs.execute('SELECT * FROM ref_anchor').fetchall()
    # add neccessary unique user values, then bundle up into sql-ready
    joints_to_add = []
    for joint in joint_template:
        ref_joint_id, date_updated, bone_end_id_a, bone_end_id_b, joint_name, side, joint_type, ref_pcapsule_ir_rom, ref_pcapsule_er_rom, ref_acapsule_ir_rom, ref_acapsule_er_rom, cx, cy = joint
        to_write = [ref_joint_id, mover_id, side, joint_type, ref_pcapsule_ir_rom,
                    ref_pcapsule_er_rom, ref_acapsule_ir_rom, ref_acapsule_er_rom]
        joints_to_add.append(to_write)
    curs.executemany('''INSERT INTO joints 
                    (ref_joints_id, moverid, side, 
                    joint_type, pcapsule_ir_rom, pcapsule_er_rom, 
                    acapsule_ir_rom, acapsule_er_rom) VALUES (?,?,?,?,?,?,?,?)''',
                     joints_to_add)
    db.commit()
    anchors_to_add = []
    for anchor in anchor_template:
        ref_anchor_id, bone_end_id, ref_zones_id = anchor
        to_write = [mover_id, ref_zones_id, ref_anchor_id]
        anchors_to_add.append(to_write)
    curs.executemany('''INSERT INTO anchor 
                    (moverid, ref_zones_id, ref_anchor_id) VALUES (?,?,?)''',
                     anchors_to_add)
    db.commit()

    anchor_lookups = {}
    movers_anchors = curs.execute('''SELECT
                    anchor.id, 
                    anchor.ref_anchor_id
                    FROM anchor
                    WHERE moverid = (?)''', (mover_id,)).fetchall()
    for anchor in movers_anchors:
        anchor_id, ref_anchor_id = anchor
        anchor_lookups[ref_anchor_id] = anchor_id

    caps_adj_template = curs.execute('''SELECT  
                    ref_capsule_adj.rowid, 
                    ref_capsule_adj.ref_zones_id,
                    ref_capsule_adj.ref_ct_training_status,
                    ref_capsule_adj.ref_anchor_id_a,
                    ref_capsule_adj.ref_anchor_id_b,
                    joints.id
                    FROM ref_capsule_adj
                    LEFT JOIN joints 
                    ON joints.ref_joints_id = ref_capsule_adj.ref_joints_id
                    WHERE joints.moverid = (?)
                    ''', (mover_id,)).fetchall()
    rot_adj_template = curs.execute('''SELECT 
                    ref_rotational_adj.rowid, 
                    ref_rotational_adj.ref_musc_training_status,
                    ref_rotational_adj.ref_ct_training_status,
                    ref_rotational_adj.ref_anchor_id_a,
                    ref_rotational_adj.ref_anchor_id_b,
                    ref_rotational_adj.rotational_bias,
                    joints.id
                    FROM ref_rotational_adj
                    LEFT JOIN joints 
                    ON joints.ref_joints_id = ref_rotational_adj.ref_joints_id
                    WHERE joints.moverid = (?)
                    ''', (mover_id,)).fetchall()
    linear_adj_template = curs.execute('''SELECT 
                    ref_linear_adj.rowid, 
                    ref_linear_adj.ref_zones_id, 
                    ref_linear_adj.ref_musc_training_status, 
                    ref_linear_adj.ref_ct_training_status, 
                    ref_linear_adj.ref_anchor_id_a, 
                    ref_linear_adj.ref_anchor_id_b, 
                    joints.id 
                    FROM ref_linear_adj 
                    INNER JOIN joints 
                    ON joints.ref_joints_id = ref_linear_adj.ref_joints_id
                    WHERE joints.moverid = (?)
                    ''', (mover_id,)).fetchall()

    caps_adj_to_add = []
    for cadj in caps_adj_template:
        ref_capsule_adj_id, ref_zones_id, ref_ct_training_status, ref_anchor_id_a, ref_anchor_id_b, joints_id = cadj
        anchor_id_a = anchor_lookups[ref_anchor_id_a]
        anchor_id_b = anchor_lookups[ref_anchor_id_b]
        to_write = [mover_id, joints_id, ref_zones_id, ref_ct_training_status,
                    None, None, 'default', 'default', None, anchor_id_a, anchor_id_b]
        caps_adj_to_add.append(to_write)
    curs.executemany('''INSERT INTO capsule_adj
                    (moverid, joint_id, ref_zones_id, ct_training_status, a_rom, p_rom, a_rom_source, p_rom_source, assess_event_id, anchor_id_a, anchor_id_b)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)''', caps_adj_to_add)
    db.commit()

    rot_adj_to_add = []
    for radj in rot_adj_template:
        ref_rotational_adj_id, ref_musc_training_status, ref_ct_training_status, ref_anchor_id_a, ref_anchor_id_b, rotational_bias, joints_id = radj
        anchor_id_a = anchor_lookups[ref_anchor_id_a]
        anchor_id_b = anchor_lookups[ref_anchor_id_b]
        to_write = [mover_id, joints_id, ref_musc_training_status,
                    ref_ct_training_status, anchor_id_a, anchor_id_b, rotational_bias]
        rot_adj_to_add.append(to_write)
    curs.executemany('''INSERT INTO rotational_adj
                    (moverid, joint_id, musc_training_status, ct_training_status, anchor_id_a, anchor_id_b, rotational_bias)
                    VALUES (?,?,?,?,?,?,?)''', rot_adj_to_add)
    db.commit()

    lin_adj_to_add = []
    for ladj in linear_adj_template:
        ref_lin_adj_id, ref_zones_id, ref_musc_training_status, ref_ct_training_status, ref_anchor_id_a, ref_anchor_id_b, joints_id = ladj
        anchor_id_a = anchor_lookups[ref_anchor_id_a]
        anchor_id_b = anchor_lookups[ref_anchor_id_b]
        to_write = [mover_id, joints_id, ref_zones_id, ref_musc_training_status,
                    ref_ct_training_status, anchor_id_a, anchor_id_b, None, None, 'default', 'default', None]
        lin_adj_to_add.append(to_write)
    curs.executemany('''INSERT INTO linear_adj
                    (moverid, joint_id, ref_zones_id, musc_training_status, ct_training_status, anchor_id_a, anchor_id_b, a_rom, p_rom, a_rom_source, p_rom_source, assess_event_id)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''', lin_adj_to_add)
    db.commit()

    print(
        f'New mover added! Name: {first_name} {last_name}\n>>>Total tissues added: {len(caps_adj_to_add) + len(rot_adj_to_add) + len(lin_adj_to_add)}')

    return mover_id


@click.command('mswn-add-mover')
def add_user_command():
    # trying to stash this import INSIDE the actual click command, to avoid
    # a circular import when using (add_new_mover) inside f_db!
    from server_side.f_db import get_db
    db = get_db()
    fname = input("What's the first name...?  ")
    lname = input("What's the last name...?  ")
    bodyweight = int(input(
        "What's your body weight \n(used exclusively for calculating body-weight exercise resistance)...?  "))
    add_new_mover(db, fname, lname, bodyweight)
    click.echo('Flask: new mover added.')


def add_user_to_app(app):
    app.cli.add_command(add_user_command)


if __name__ == "__main__":
    # testing flow...
    db = sqlite3.connect(
        '/Users/williamhbelew/Hacking/MSWN/instance/mswnapp.sqlite')
    add_new_mover(db, 'Tester', 'Dummy')
    add_new_mover(db, 'Test', 'Ickle')
