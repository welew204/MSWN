DROP TABLE IF EXISTS movers;
DROP TABLE IF EXISTS coaches;
DROP TABLE IF EXISTS joint_reference;
--DROP TABLE IF EXISTS joint_adjacency;
DROP TABLE IF EXISTS joints;
DROP TABLE IF EXISTS zones_reference;
--DROP TABLE IF EXISTS zone_adjacency;
DROP TABLE IF EXISTS zones;
DROP TABLE IF EXISTS bout_log;
DROP TABLE IF EXISTS assess_log;
DROP TABLE IF EXISTS tissue_status;

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

CREATE TABLE joint_reference (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_updated TEXT NOT NULL,
    joint_name TEXT NOT NULL,
    side TEXT NOT NULL,
    joint_type TEXT NOT NULL,
    ref_pcapsule_ir_rom REAL NOT NULL,
    ref_pcapsule_er_rom REAL NOT NULL,
    ref_acapsule_ir_rom REAL NOT NULL,
    ref_acapsule_er_rom REAL NOT NULL
);

--CREATE TABLE joint_adjacency (
--    a INTEGER NOT NULL REFERENCES joint_reference (id),
--    b INTEGER NOT NULL REFERENCES joint_reference (id),
--    (a, b) PRIMARY KEY
--);

CREATE TABLE joints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    moverid INTEGER NOT NULL,
    joint_reference_id INTEGER NOT NULL,
    joint_name TEXT NOT NULL,
    side TEXT NOT NULL,
    pcapsule_ir_rom REAL NOT NULL,
    pcapsule_er_rom REAL NOT NULL,
    acapsule_ir_rom REAL NOT NULL,
    acapsule_er_rom REAL NOT NULL,
    capsule_training_status BLOB, 
    --similar to tissue_status in zones table
    FOREIGN KEY (moverid) REFERENCES movers (id),
    FOREIGN KEY (joint_reference_id) REFERENCES joint_reference (id),
    FOREIGN KEY (joint_name) REFERENCES joint_reference (joint_name),
    FOREIGN KEY (side) REFERENCES joint_reference (side)
);

CREATE TABLE zones_reference (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_updated TEXT NOT NULL,
    joint_id INTEGER NOT NULL,
    zname TEXT NOT NULL,
    side TEXT NOT NULL,
    reference_progressive_p_rom REAL,
    reference_progressive_a_rom REAL,
    reference_regressive_p_rom REAL,
    reference_regressive_a_rom REAL,
    FOREIGN KEY (joint_id) REFERENCES joints (id),
    FOREIGN KEY (side) REFERENCES joints (side)
);

--CREATE TABLE zone_adjacency (
--    a INTEGER NOT NULL REFERENCES zone_reference (id),
--    b INTEGER NOT NULL REFERENCES zone_reference (id),
--    (a, b) PRIMARY KEY
--);

CREATE TABLE zones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    moverid INTEGER NOT NULL,
    joint_id INTEGER NOT NULL,
    zone_reference_id INTEGER NOT NULL,
    side TEXT NOT NULL,
    zname TEXT NOT NULL,
    progressive_p_rom REAL,
    progressive_a_rom REAL,
    regressive_p_rom REAL,
    regressive_a_rom REAL,
    FOREIGN KEY (joint_id) REFERENCES joints (id),
    FOREIGN KEY (zone_reference_id) REFERENCES zone_reference (id),
    FOREIGN KEY (side) REFERENCES joints (side),
    FOREIGN KEY (moverid) REFERENCES movers (id)
);

CREATE TABLE bout_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    moverid INTEGER NOT NULL,
    tissue_id INTEGER NOT NULL,
    joint_id INTEGER NOT NULL,
    input_cycle INTEGER,
    rotational_bias REAL NOT NULL,
    position INT NOT NULL,
    duration INT NOT NULL,
    passive_duration INT,
    rpe INT NOT NULL,
    external_load INT,
    comments TEXT,
    FOREIGN KEY (tissue_id) REFERENCES zones (id),
    FOREIGN KEY (joint_id) REFERENCES joint_id (id),
    FOREIGN KEY (moverid) REFERENCES movers (id)
);

CREATE TABLE assess_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    moverid INTEGER NOT NULL,
    joint_id INTEGER NOT NULL,
    tissue_id INTEGER,
    a_rom REAL,
    p_rom REAL,
    pcapsule_rom REAL,
    acapsule_rom REAL,
    --can I safely 'stash' more assessment values in this table if/when I want?????????? YESSSSS
    FOREIGN KEY (tissue_id) REFERENCES zones (id),
    FOREIGN KEY (joint_id) REFERENCES joints (id),
    FOREIGN KEY (moverid) REFERENCES movers (id)
);

CREATE TABLE tissue_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    moverid INTEGER NOT NULL,
    side TEXT NOT NULL,
    tissue_layer TEXT NOT NULL,
    tissue_id INTEGER NOT NULL,
    tissue_layer_training_status BLOB,
    FOREIGN KEY (tissue_id) REFERENCES zones (id),
    FOREIGN KEY (side) REFERENCES zones (side),
    FOREIGN KEY (moverid) REFERENCES users (id)
);