from flask import g, current_app
from datetime import datetime


def_values = {
    "hip": {
        "pcapsule_ir_rom": 35,
        "pcapsule_er_rom": 60,
        "acapsule_ir_rom": 20,
        "acapsule_er_rom": 45
    },
    "knee": {
        "pcapsule_ir_rom": 15,
        "pcapsule_er_rom": 35,
        "acapsule_ir_rom": 10,
        "acapsule_er_rom": 20
    },
    "ankle": {
        "pcapsule_ir_rom": 15,
        "pcapsule_er_rom": 35,
        "acapsule_ir_rom": 5,
        "acapsule_er_rom": 20
    },
    "GH": {
        "pcapsule_ir_rom": 75,
        "pcapsule_er_rom": 90,
        "acapsule_ir_rom": 60,
        "acapsule_er_rom": 75
    },
    "elbow": {
        "pcapsule_ir_rom": 90,
        "pcapsule_er_rom": 90,
        "acapsule_ir_rom": 75,
        "acapsule_er_rom": 75
    },
    "wrist": {
        "pcapsule_ir_rom": 20,
        "pcapsule_er_rom": 40,
        "acapsule_ir_rom": 5,
        "acapsule_er_rom": 25
    },
    "hallux": {
        "pcapsule_ir_rom": 0,
        "pcapsule_er_rom": 0,
        "acapsule_ir_rom": 0,
        "acapsule_er_rom": 0
    },
    "toes": {
        "pcapsule_ir_rom": 0,
        "pcapsule_er_rom": 0,
        "acapsule_ir_rom": 0,
        "acapsule_er_rom": 0
    },
    "scapula": {
        "pcapsule_ir_rom": 0,
        "pcapsule_er_rom": 0,
        "acapsule_ir_rom": 0,
        "acapsule_er_rom": 0
    },
    #each spine section corresponds to the ROTATION of the bony body
    "spine": {
        "c1": {"flexion": 7.5,"extension": 7.5},
        "c2": {"flexion": 5.6,"extension": 5.6},
        "c3": {"flexion": 8.8,"extension": 8.8},
        "c4": {"flexion": 11.0,"extension": 11.0},
        "c5": {"flexion": 11.0,"extension": 11.0},
        "c6": {"flexion": 16.5,"extension": 16.5},
        "c7": {"flexion": 4.9,"extension": 4.9},
        "t1": {"flexion": 1.9,"extension": 2.3},
        "t2": {"flexion": 1.5,"extension": 2.2},
        "t3": {"flexion": 1.4,"extension": 2.1},
        "t4": {"flexion": 1.5,"extension": 1.9},
        "t5": {"flexion": 1.6,"extension": 1.6},
        "t6": {"flexion": 1.7,"extension": 1.5},
        "t7": {"flexion": 1.8,"extension": 1.4},
        "t8": {"flexion": 2.0,"extension": 1.4},
        "t9": {"flexion": 2.2,"extension": 1.5},
        "t10": {"flexion": 2.5,"extension": 1.7},
        "t11": {"flexion": 3.4,"extension": 2.0},
        "t12": {"flexion": 4.5,"extension": 2.4},
        "l1": {"flexion": 2.6,"extension": 2.6},
        "l2": {"flexion": 2.6,"extension": 2.6},
        "l3": {"flexion": 2.6,"extension": 2.6},
        "l4": {"flexion": 2.6,"extension": 2.6},
        "l5": {"flexion": 2.3,"extension": 2.3},
        "s1": {"flexion": 2.3,"extension": 2.3},
        }
    }

def add_ref_vals(db):
    # create db cnx from PASSED in db
    curs = db.cursor()
    # unpack def_vals into sql-ready bundles (field_name, qmarks, field_vals)
    date = datetime.now().strftime("%Y-%m-%d")
    joints_to_add = []
    field_names = "date_updated, joint_name, side, joint_type, ref_pcapsule_ir_rom, ref_pcapsule_er_rom, ref_acapsule_ir_rom, ref_acapsule_er_rom"
    qmarks = ["?" for i in range(8)]
    for joint in def_values.keys():
        if joint == "spine":
            for vertabrae in def_values[joint].keys():
                spine_field_vals = [
                    date, 
                    vertabrae, 
                    "mid", 
                    "spinal", 
                    def_values[joint][vertabrae]["flexion"],
                    def_values[joint][vertabrae]["extension"],
                    def_values[joint][vertabrae]["flexion"]*.85,
                    def_values[joint][vertabrae]["extension"]*.85
                ]
                joints_to_add.append(spine_field_vals)
        else:
            r_field_vals = [
                date,
                joint,
                "R",
                "synovial",
                def_values[joint]["pcapsule_ir_rom"],
                def_values[joint]["pcapsule_er_rom"],
                def_values[joint]["acapsule_ir_rom"],
                def_values[joint]["acapsule_er_rom"]
            ]
            l_field_vals = r_field_vals.copy()
            l_field_vals[2] = "L"
            if joint == "scapula":
                r_field_vals[3] = "sesamoid"
                l_field_vals[3] = "sesamoid"
            joints_to_add.append(r_field_vals)
            joints_to_add.append(l_field_vals)

    # executemany to "joint_reference", commit to db
    curs.executemany(f'INSERT INTO joint_reference (date_updated, joint_name, side, joint_type, ref_pcapsule_ir_rom, ref_pcapsule_er_rom, ref_acapsule_ir_rom, ref_acapsule_er_rom) VALUES ({",".join(qmarks)})', 
        joints_to_add)
    db.commit()
    print("added the JOINT reference values!")
    
def add_zone_ref_values(db):
    # select ref_joints from db (to get joint_id, side)
    curs = db.cursor()
    joints = curs.execute('SELECT * FROM joint_reference').fetchall()
    # `joints` is a list
    zones_to_add = []
    date = datetime.now().strftime("%Y-%m-%d")
    for joint in joints:
        joint_ref_id, date_updated, joint_name, side, joint_type, ref_pcapsule_ir_rom, ref_pcapsule_er_rom, ref_acapsule_ir_rom, ref_acapsule_er_rom = joint
        zone_ref_vals = [date, joint_ref_id, joint_name, side, ""]
        qmarks = ["?" for i in range(5)]
    # generate zones programatically into sql-ready format
    # --spine joints should generate 4 (flex, ext, r_rotate, l_rotate); this can map with the positionality); 
    # --HOWEVER zones with spine as joint-type should NOT be triplicated in tissue_status table
    # ---scapula should generate 4 (pro, re, elev, dep), 
    # -all other joints get 8
        if joint_type == "spinal":
            for z in ["flexion", "extension", "r_rotation", "l_rotation"]:
                spinal_joint_zone_ref_vals = zone_ref_vals.copy()
                spinal_joint_zone_ref_vals[4] = z
                zones_to_add.append(spinal_joint_zone_ref_vals)
        elif joint_type == "sesamoid":
            for z in ["retraction", "protraction", "elevation", "depression"]:
                sesamoid_joint_zone_ref_vals = zone_ref_vals.copy()
                sesamoid_joint_zone_ref_vals[4] = z
                zones_to_add.append(sesamoid_joint_zone_ref_vals)
        else:
            for z in ["flexion", "flex-abd", "abduction", "extend-abd", "extension", "extend-add", "adduction", "flex-add"]:
                synovial_joint_zone_ref_vals = zone_ref_vals.copy()
                synovial_joint_zone_ref_vals[4] = z
                zones_to_add.append(synovial_joint_zone_ref_vals)
    # executemany to "zone_reference", commit to db
    curs.executemany(f'INSERT INTO zones_reference (date_updated, joint_id, joint_name, side, zname) VALUES ({",".join(qmarks)})', 
        zones_to_add)
    db.commit()
    print("added the ZONE reference values!")

def add_new_user():
    # create db cnx
    # SELECT vals from ref tables
    # add neccessary unique user values, then bundle up into sql-ready
    # execute, commit to db
    pass

if __name__=="__main__":
    add_ref_vals()