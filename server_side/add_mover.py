from datetime import datetime
import click

from server_side.f_db import get_db

def add_new_mover(db, first_name, last_name):
    date = datetime.now().strftime("%Y-%m-%d")
    # create db cnx
    curs = db.cursor()
    # add mover to table
    curs.execute('INSERT INTO movers (first_name, last_name, date_added) VALUES (?,?,?)',
        (first_name, last_name, date))
    db.commit()
    mover_id_Row = curs.execute('SELECT id FROM movers WHERE first_name = (?) AND last_name = (?)', (first_name, last_name)).fetchone()
    mover_id = mover_id_Row["id"]
    print(mover_id)
    # SELECT vals from ref tables
    joint_template = curs.execute('SELECT * FROM joint_reference').fetchall()
    zones_template = curs.execute('SELECT * FROM zones_reference').fetchall()
    # add neccessary unique user values, then bundle up into sql-ready
    joints_to_add = []
    for joint in joint_template:
        joint_ref_id, date_updated, joint_name, side, joint_type, ref_pcapsule_ir_rom, ref_pcapsule_er_rom, ref_acapsule_ir_rom, ref_acapsule_er_rom = joint
        to_write = [mover_id, joint_ref_id, joint_name, side, ref_pcapsule_ir_rom, ref_pcapsule_er_rom, ref_acapsule_ir_rom, ref_acapsule_er_rom]
        joints_to_add.append(to_write)
    curs.executemany('''INSERT INTO joints 
                    (moverid, joint_reference_id, joint_name, 
                    side, pcapsule_ir_rom, pcapsule_er_rom, 
                    acapsule_ir_rom, acapsule_er_rom) VALUES (?,?,?,?,?,?,?,?)''',
                    joints_to_add)
    db.commit()
    zones_to_add = []
    for zone in zones_template:
        zone_ref_id, date, joint_ref_id, joint_name, side, zname, reference_progressive_p_rom, reference_progressive_a_rom, reference_regressive_p_rom, reference_regressive_a_rom = zone
        to_write = [mover_id, joint_ref_id, zone_ref_id, side, zname, ref_pcapsule_ir_rom, ref_pcapsule_er_rom, ref_acapsule_ir_rom, ref_acapsule_er_rom]
        zones_to_add.append(to_write)
    curs.executemany('''INSERT INTO zones 
                    (moverid, joint_id, zone_reference_id, 
                    side, zname, progressive_p_rom, progressive_a_rom, 
                    regressive_p_rom, regressive_a_rom) VALUES (?,?,?,?,?,?,?,?, ?)''',
                    zones_to_add)
    db.commit()
    print(f'New mover added! Name: {first_name}, {last_name}\nJoints added: {len(joints_to_add)}\nZones added: {len(zones_to_add)}')

    # execute, commit to db

@click.command('mswn-add-mover')
def add_user_command():
    db = get_db()
    fname = input("What's the first name...?")
    lname = input("What's the last name...?")
    add_new_mover(db, fname, lname)
    click.echo('MSWN: new mover added.')

def add_user_to_app(app):
    app.cli.add_command(add_user_command)