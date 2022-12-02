from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
import sys

from werkzeug.exceptions import abort

from server_side.f_db import get_db

bp = Blueprint('tissues', __name__)

@bp.route('/')
def index():
    #print(f"Got this far (to {index})", file=sys.stderr)
    db=get_db()
    bouts = db.execute(
        'SELECT * FROM boutLog'
    ).fetchall()

    return jsonify({"bouts": bouts}), 201

@bp.route('/add_bouts', methods=('POST',))
def add_bouts():
    req = request.get_json()

    db=get_db()
    curs = db.cursor()
    bouts_to_input = []

    for b in req:
        bundle = []
        field_names = []
        qmarks = []
        for key in list(b.keys()):
            # exec() function runs a string as python, so I can use an f-string to dynamically create vraible from a stirng
            exec(f"{key}_field = b[key]")
            # then, I add the field_name (string) to an array
            field_names.append(f"{key}_field")
            # then, I add the value of that variable to the bundle
            bundle.append(exec(f"{key}_field"))
            # and finally a question mark for each field
            qmarks += '?'
        # once I've gone through ALL keys included in the request bout, I will have a tuple that has...
        bouts_to_input.append([field_names, qmarks, bundle])
    
    for bout in bouts_to_input:
        curs.execute(f'INPUT INTO bout_log ({tuple(bout[0])}) VALUES ({tuple(bout[1])})', (bout[2]))
        db.commit()
    



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
