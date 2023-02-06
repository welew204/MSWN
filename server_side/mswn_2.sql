DROP TABLE IF EXISTS movers;
DROP TABLE IF EXISTS coaches;

DROP TABLE IF EXISTS ref_bone_end;
DROP TABLE IF EXISTS ref_joints;
DROP TABLE IF EXISTS ref_anchor;
DROP TABLE IF EXISTS ref_capsule_adj;
DROP TABLE IF EXISTS ref_rotational_adj;
DROP TABLE IF EXISTS ref_linear_adj;
DROP TABLE IF EXISTS ref_zones;
DROP TABLE IF EXISTS joints;
DROP TABLE IF EXISTS anchor;
DROP TABLE IF EXISTS capsule_adj;
DROP TABLE IF EXISTS rotational_adj;
DROP TABLE IF EXISTS linear_adj;
DROP TABLE IF EXISTS zones;
DROP TABLE IF EXISTS tissues;

DROP TABLE IF EXISTS programmed_drills;
DROP TABLE IF EXISTS workouts;
DROP TABLE IF EXISTS incomplete_log;

DROP TABLE IF EXISTS bout_log;
DROP TABLE IF EXISTS assess_event_log;
DROP TABLE IF EXISTS assess_tissue_log;

--each anchor_table is just:
--id, zone_associated,
--other_end_of_... (null)?? 

--each adj table is:
--primary key of TWO items, zone_associated,
--other_end_of_... (null)??
--training status BLOB

--are all the ref_tables needed?
--ct/muscle tissue model?? they NEED each other...
--building off the integral idea... could ALL of the inputs be a summation of sorts?
-- so that the decay is just a daily decrement fromt that score etc

---> plan: code in the conditional "stress this, like that" for a 
-- selection of drills, which are options to be called in react;
-- ZONES are now actually procedural directions given to python
-- (not actual tissues) which translates into force vectors within
-- the collective phase space of a region of zones capacity

CREATE TABLE movers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_added TEXT NOT NULL
);

CREATE TABLE coaches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_added TEXT NOT NULL
);

CREATE TABLE ref_bone_end (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bone_name TEXT NOT NULL,
    end INT NOT NULL, 
    side TEXT NOT NULL
);
--'end' vals... 0 = proximal, 1 = distal, 2, 3 (extra attachments)

CREATE TABLE ref_joints (
    date_updated TEXT NOT NULL,
    bone_end_id_a INTEGER NOT NULL,
    bone_end_id_b INTEGER NOT NULL,
    joint_name TEXT NOT NULL,
    side TEXT NOT NULL,
    joint_type TEXT NOT NULL,
    ref_pcapsule_ir_rom REAL,
    ref_pcapsule_er_rom REAL,
    ref_acapsule_ir_rom REAL,
    ref_acapsule_er_rom REAL,
    PRIMARY KEY (bone_end_id_a, bone_end_id_b),
    FOREIGN KEY (bone_end_id_a) REFERENCES ref_bone_end (id),
    FOREIGN KEY (bone_end_id_b) REFERENCES ref_bone_end (id)
);

CREATE TABLE ref_zones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_updated TEXT NOT NULL,
    ref_joints_id INTEGER NOT NULL,
    zone_name TEXT NOT NULL,
    side TEXT NOT NULL,
    reference_progressive_p_rom REAL,
    reference_progressive_a_rom REAL,
    reference_regressive_p_rom REAL,
    reference_regressive_a_rom REAL,
    FOREIGN KEY (ref_joints_id) REFERENCES ref_joints (rowid)
);

CREATE TABLE ref_anchor (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bone_end_id INTEGER NOT NULL,
    ref_zones_id INTEGER NOT NULL,
    FOREIGN KEY (bone_end_id) REFERENCES ref_bone_end (id),
    FOREIGN KEY (ref_zones_id) REFERENCES ref_zones (id)
);


CREATE TABLE ref_capsule_adj (
    ref_joints_id INTEGER NOT NULL,
    ref_zones_id INTEGER NOT NULL,
    ref_ct_training_status BLOB,
    ref_anchor_id_a INTEGER NOT NULL,
    ref_anchor_id_b INTEGER NOT NULL,
    PRIMARY KEY (ref_anchor_id_a, ref_anchor_id_b),
    FOREIGN KEY (ref_joints_id) REFERENCES ref_joints (rowid),
    FOREIGN KEY (ref_zones_id) REFERENCES ref_zones (id),
    FOREIGN KEY (ref_anchor_id_a) REFERENCES ref_anchor (id),
    FOREIGN KEY (ref_anchor_id_b) REFERENCES ref_anchor (id)
);

CREATE TABLE ref_rotational_adj (
    ref_musc_training_status BLOB,
    ref_ct_training_status BLOB,
    ref_joints_id INTEGER NOT NULL,
    ref_anchor_id_a INTEGER NOT NULL,
    ref_anchor_id_b INTEGER NOT NULL,
    rotational_bias TEXT NOT NULL, 
    PRIMARY KEY (ref_anchor_id_a, ref_anchor_id_b),
    FOREIGN KEY (ref_joints_id) REFERENCES ref_joints (rowid),
    FOREIGN KEY (ref_anchor_id_a) REFERENCES ref_anchor (id),
    FOREIGN KEY (ref_anchor_id_b) REFERENCES ref_anchor (id)
);
--"rotational_bias" must be "IR" or "ER"

CREATE TABLE ref_linear_adj (
    ref_joints_id INTEGER NOT NULL,
    ref_zones_id INTEGER NOT NULL,
    ref_musc_training_status BLOB,
    ref_ct_training_status BLOB,
    ref_anchor_id_a INTEGER NOT NULL,
    ref_anchor_id_b INTEGER NOT NULL,
    PRIMARY KEY (ref_anchor_id_a, ref_anchor_id_b),
    FOREIGN KEY (ref_joints_id) REFERENCES ref_joints (rowid),
    FOREIGN KEY (ref_zones_id) REFERENCES ref_zones (id),
    FOREIGN KEY (ref_anchor_id_a) REFERENCES ref_anchor (id),
    FOREIGN KEY (ref_anchor_id_b) REFERENCES ref_anchor (id)
);


CREATE TABLE anchor (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    moverid INTEGER NOT NULL,
    ref_zones_id INTEGER NOT NULL,
    ref_anchor_id INTEGER NOT NULL,
    FOREIGN KEY (moverid) REFERENCES movers (id),
    FOREIGN KEY (ref_anchor_id) REFERENCES ref_anchor (id),
    FOREIGN KEY (ref_zones_id) REFERENCES ref_zones (id)
);

CREATE TABLE joints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ref_joints_id INTEGER NOT NULL,
    moverid INTEGER NOT NULL,
    side TEXT NOT NULL,
    joint_type TEXT NOT NULL,
    pcapsule_ir_rom REAL,
    pcapsule_er_rom REAL,
    acapsule_ir_rom REAL,
    acapsule_er_rom REAL,
    FOREIGN KEY (moverid) REFERENCES movers (id),
    FOREIGN KEY (ref_joints_id) REFERENCES ref_joints (rowid)
);

CREATE TABLE capsule_adj (
    moverid INTEGER NOT NULL,
    joint_id INTEGER NOT NULL,
    ref_zones_id INTEGER NOT NULL,
    ct_training_status BLOB,
    a_rom REAL, 
    p_rom REAL, 
    a_rom_source TEXT NOT NULL, 
    p_rom_source TEXT NOT NULL, 
    assess_event_id INTEGER,
    anchor_id_a INTEGER NOT NULL,
    anchor_id_b INTEGER NOT NULL,
    PRIMARY KEY (anchor_id_a, anchor_id_b),
    FOREIGN KEY (assess_event_id) REFERENCES assess_tissue_log (id),
    FOREIGN KEY (moverid) REFERENCES movers (id),
    FOREIGN KEY (joint_id) REFERENCES joints (id),
    FOREIGN KEY (ref_zones_id) REFERENCES ref_zones (id),
    FOREIGN KEY (anchor_id_a) REFERENCES anchor (id),
    FOREIGN KEY (anchor_id_b) REFERENCES anchor (id)
);

--arom, prom ...this is set by default OR by a specific assessment
-- arom_source, etc.... must be either 'default' or 'assessment'

CREATE TABLE rotational_adj (
    moverid INTEGER NOT NULL,
    joint_id INTEGER NOT NULL,
    musc_training_status BLOB,
    ct_training_status BLOB,
    anchor_id_a INTEGER NOT NULL,
    anchor_id_b INTEGER NOT NULL,
    rotational_bias TEXT NOT NULL, 
    PRIMARY KEY (anchor_id_a, anchor_id_b),
    FOREIGN KEY (moverid) REFERENCES movers (id),
    FOREIGN KEY (joint_id) REFERENCES joints (id)
    FOREIGN KEY (anchor_id_a) REFERENCES anchor (id),
    FOREIGN KEY (anchor_id_b) REFERENCES anchor (id)
);
--rot_bias... must be "IR" or "ER"

CREATE TABLE linear_adj (
    moverid INTEGER NOT NULL,
    joint_id INTEGER NOT NULL,
    ref_zones_id INTEGER NOT NULL,
    musc_training_status BLOB,
    ct_training_status BLOB,
    anchor_id_a INTEGER NOT NULL,
    anchor_id_b INTEGER NOT NULL,
    a_rom REAL, 
    p_rom REAL, 
    a_rom_source TEXT NOT NULL, 
    p_rom_source TEXT NOT NULL, 
    assess_event_id INTEGER,
    PRIMARY KEY (anchor_id_a, anchor_id_b),
    FOREIGN KEY (assess_event_id) REFERENCES assess_tissue_log (id),
    FOREIGN KEY (moverid) REFERENCES movers (id),
    FOREIGN KEY (joint_id) REFERENCES joints (id),
    FOREIGN KEY (ref_zones_id) REFERENCES ref_zones (id)
    FOREIGN KEY (anchor_id_a) REFERENCES anchor (id),
    FOREIGN KEY (anchor_id_b) REFERENCES anchor (id)
);

CREATE TABLE bout_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL, 
    moverid INTEGER NOT NULL,
    joint_id INTEGER NOT NULL,
    programmed_drills_id INTEGER NOT NULL,
    rotational_value TEXT,
    joint_motion TEXT NOT NULL, 
    start_coord INTEGER,
    end_coord INTEGER,
    capsular_tissue_id INTEGER,
    rotational_tissue_id INTEGER,
    linear_tissue_id INTEGER,
    duration INTEGER NOT NULL,
    passive_duration INTEGER,
    rpe INT NOT NULL,
    external_load INTEGER, 
    tissue_type TEXT NOT NULL,
    FOREIGN KEY (programmed_drills_id) REFERENCES programmed_drills (id),
    FOREIGN KEY (joint_id) REFERENCES joints (id),
    FOREIGN KEY (moverid) REFERENCES movers (id)
);

CREATE TABLE incomplete_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL, 
    moverid INTEGER NOT NULL,
    joint_id INTEGER NOT NULL,
    ref_zones_id_a INTEGER NOT NULL,
    ref_zones_id_b INTEGER,
    fixed_side_anchor_id INTEGER NOT NULL,
    rotational_bias TEXT,
    joint_motion TEXT NOT NULL, 
    start_coord INTEGER,
    end_coord INTEGER,
    tissue_id INTEGER,
    drill_name TEXT,
    duration INTEGER NOT NULL,
    passive_duration INTEGER,
    rpe INT NOT NULL,
    external_load INTEGER,
    comments TEXT, 
    validated TEXT,
    FOREIGN KEY (fixed_side_anchor_id) REFERENCES anchor (id),
    FOREIGN KEY (joint_id) REFERENCES joints (id),
    FOREIGN KEY (ref_zones_id_a) REFERENCES ref_zones (id),
    FOREIGN KEY (ref_zones_id_b) REFERENCES ref_zones (id),
    FOREIGN KEY (tissue_id) REFERENCES tissues (id),
    FOREIGN KEY (moverid) REFERENCES movers (id)
);

--will be a division of the drill given usually
--joint_motion: must be 'rotation' or 'fe'
--movement_id INTEGER, --doesn't HAVE to be part of a movement (which will be generated by selecting a DRILL and time-stamping (seperate table needed)) because always must retain ability to simply enter a raw joint motion!
--workout_id INTEGER NOT NULL, --DOES HAVE to be part of a workout (which will be generated by a time-stamped record event (seperate table needed))

CREATE TABLE assess_event_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    moverid INTEGER NOT NULL,
    assess_type TEXT,
    comments TEXT,
    FOREIGN KEY (moverid) REFERENCES movers (id)
);

CREATE TABLE tissues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    moverid INTEGER NOT NULL,
    tissue_type TEXT NOT NULL, 
    capsule_tissue_id INTEGER,
    rotational_tissue_id INTEGER,
    linear_tissue_id INTEGER,
    FOREIGN KEY (moverid) REFERENCES movers (id),
    FOREIGN KEY (capsule_tissue_id) REFERENCES capsule_adj (id),
    FOREIGN KEY (rotational_tissue_id) REFERENCES rotational_adj (id),
    FOREIGN KEY (linear_tissue_id) REFERENCES linear_adj (id)
);

--tissue_type: must be 'capsule', 'rotational', 'linear'

CREATE TABLE assess_tissue_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assess_event_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    moverid INTEGER NOT NULL,
    joint_id INTEGER NOT NULL,
    tissue_id INTEGER, 
    a_rom REAL,
    p_rom REAL,
    pcapsule_rom REAL,
    acapsule_rom REAL,
    FOREIGN KEY (assess_event_id) REFERENCES assess_event_log (id),
    FOREIGN KEY (tissue_id) REFERENCES tissues (id),
    FOREIGN KEY (joint_id) REFERENCES joints (id),
    FOREIGN KEY (moverid) REFERENCES movers (id)
);

CREATE TABLE workouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_init TEXT NOT NULL,
    last_done TEXT,
    coach_id TEXT,
    workout_title TEXT,
    moverid INTEGER,
    comments TEXT,
    FOREIGN KEY (coach_id) REFERENCES coaches (id),
    FOREIGN KEY (moverid) REFERENCES movers (id)
);

CREATE TABLE programmed_drills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    moverid INTEGER NOT NULL,
    joint_id INTEGER NOT NULL,
    workout_id INTEGER NOT NULL,
    input_sequence TEXT,
    circuit_iterations INTEGER,
    ref_zones_id_a INTEGER,
    ref_zones_id_b INTEGER,
    fixed_side_anchor_id INTEGER NOT NULL,
    rotational_value INTEGER,
    start_coord INTEGER,
    end_coord INTEGER,
    drill_name TEXT,
    rails TEXT,
    duration INTEGER NOT NULL,
    passive_duration INTEGER,
    rpe INT NOT NULL,
    external_load INTEGER,
    comments TEXT,
    FOREIGN KEY (fixed_side_anchor_id) REFERENCES anchor (id),
    FOREIGN KEY (joint_id) REFERENCES joints (id),
    FOREIGN KEY (ref_zones_id_a) REFERENCES ref_zones (id),
    FOREIGN KEY (ref_zones_id_b) REFERENCES ref_zones (id),
    FOREIGN KEY (workout_id) REFERENCES workout (id),
    FOREIGN KEY (moverid) REFERENCES movers (id)
);

