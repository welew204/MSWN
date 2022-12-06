from collections import defaultdict
from operator import itemgetter
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
import sys

from werkzeug.exceptions import abort

from server_side.f_db import get_db

bp = Blueprint('tissues', __name__)

@bp.route('/')
def index(mover_id):
    #print(f"Got this far (to {index})", file=sys.stderr)
    db=get_db()
    bouts = db.execute(
        'SELECT * FROM bout_log'
    ).fetchall()

    return 'Done', 201

@bp.route('/joint_ref')
def joint_ref():
    #print(f"Got this far (to {index})", file=sys.stderr)
    db=get_db()
    joint_ref = defaultdict(list)
    joint_ref_final = defaultdict(list)

    # BELOW returns a list of sqlite3.Row objects (with index, and keys), but is NOT a real dict
    zone_ref_rows = db.execute('SELECT zones_reference.id, zones_reference.joint_name, zones_reference.side, zones_reference.zname, joint_reference.joint_type FROM zones_reference INNER JOIN joint_reference ON zones_reference.joint_id=joint_reference.id').fetchall()
    for row in zone_ref_rows:
        zone = {k: row[k] for k in row.keys()}
        # only want one side and spine for reference
        if row["side"] == "R" or row["side"] == "mid":
            joint_ref[row["joint_name"]].append(zone)
    # making nested object to send to react:
    for joint in joint_ref.keys():
        for zone in joint_ref[joint]:
            if zone["joint_type"] != "spinal":
                joint_ref_final[joint].append(zone['zname'])
            else:
                if joint[0] == "c":
                    if zone['zname'] not in joint_ref_final["c_spine"]:
                        joint_ref_final["c_spine"].append(zone['zname'])
                elif joint[0] == "t":
                    if zone['zname'] not in joint_ref_final["t_spine"]:
                        joint_ref_final["t_spine"].append(zone['zname'])
                elif joint[0] == "l":
                    if zone['zname'] not in joint_ref_final["l_spine"]:
                        joint_ref_final["l_spine"].append(zone['zname'])
            
    return jsonify(joint_ref_final), 200

@bp.route('/ttstatus/<int:mover_id>')
def ttstatus(mover_id):
    #print(f"Got this far (to {index})", file=sys.stderr)
    db=get_db()
    tissue_status = []
    # BELOW returns a list of sqlite3.Row objects (with index, and keys), but is NOT a real dict
    tissue_status_rows = db.execute(
        'SELECT * FROM tissue_status WHERE moverid = (?)', (mover_id,)
    ).fetchall()
    # this converts all rows returned into dictiornary, that is added to the tissue_status list
    for row in tissue_status_rows:
        tissue_status.append({k: row[k] for k in row.keys()})
    return jsonify({"tissue_status": tissue_status}), 200

@bp.route('/bout_log/<int:mover_id>')
def bout_log(mover_id):
    #print(f"Got this far (to {index})", file=sys.stderr)
    db=get_db()
    bout_log = []
    # BELOW returns a list of sqlite3.Row objects (with index, and keys), but is NOT a real dict
    bout_log_rows = db.execute(
        'SELECT * FROM bout_log WHERE moverid = (?)', (mover_id,)
    ).fetchall()
    # this converts all rows returned into dictiornary, that is added to the tissue_status list
    for row in bout_log_rows:
        bout_log.append({k: row[k] for k in row.keys()})
    # sort on way to react into DESCENDING order from most recent (by ['date'])
    bout_log_final = sorted(bout_log, key=itemgetter('date'), reverse=True)
    return jsonify({"bout_log": bout_log_final}), 200

@bp.route('/add_bouts/<int:moverid>', methods=('POST',))
def add_bouts(moverid):
    req = request.get_json()

    db=get_db()
    curs = db.cursor()
    bouts_to_input = []

    for b in req:
        print(b)
        bundle = []
        field_names = []
        qmarks = []
        for key in list(b.keys()):
            # exec() function runs a string as python, so I can use an f-string to dynamically create vraible from a stirng
            exec(f"{key}_field = b[key]")
            exec(f"print({key}_field)")
            # then, I add the field_name (string) to an array -- THIS MUST MATCH THE DB!
            field_names.append(f"{key}")
            # then, I add the value of that variable to the bundle
            exec(f"bundle.append({key}_field)")
            # and finally a question mark for each field
            qmarks += '?'
        # once I've gone through ALL keys included in the request bout, I will have a tuple that has...
        bundle.insert(1,moverid)
        field_names.insert(1,"moverid")
        qmarks.insert(1,"?")
        bouts_to_input.append([field_names, qmarks, bundle])
        
    
    for bout in bouts_to_input:
        field_names = ",".join(bout[0])
        qmarks = ",".join(bout[1])
        curs.execute(f'INSERT INTO bout_log ({field_names}) VALUES ({qmarks})', (bout[2]))
        db.commit()

    return f"{len(bouts_to_input)} bout(s) logged!", 201
    



"""     curs = db.cursor()
    fname = def_values["fname"]
    lname = def_values["lname"]
    date_added = def_values["date_updated"]
    default_joints_array = []
    default_zones_array = []

    for joint in def_values["joints"].keys():
        if joint == "spine":
            for vertabrae in joint["spine"].keys(): """

"""
@bp.route('/delete_bouts')

@bp.route('/read_bouts') """
