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

""" @bp.route('/add_bouts', methods=('POST',))
def add_bouts():
    req = request.get_json()

    db=get_db()
    curs = db.cursor()

    for b in req:
        date = b['date']
        date = b['date']
        date = b['date']
        date = b['date']
        date = b['date']
        date = b['date']
        date = b['date']
        date = b['date']

@bp.route('/delete')

@bp.route('/read_bouts') """
