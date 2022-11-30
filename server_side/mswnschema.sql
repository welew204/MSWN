DROP TABLE IF EXISTS joints;
DROP TABLE IF EXISTS zones;
DROP TABLE IF EXISTS boutLog;
--DROP TABLE IF EXISTS assessLog;

CREATE TABLE joints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jname TEXT NOT NULL,
    norm_pcapsule REAL NOT NULL,
    norm_acapsule REAL NOT NULL
);

CREATE TABLE zones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jid INTEGER NOT NULL,
    zname TEXT NOT NULL,
    norm_prom REAL NOT NULL,
    norm_arom REAL NOT NULL,
    training_status BLOB,
    FOREIGN KEY (jid) REFERENCES joints (id)
);

CREATE TABLE boutLog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    tid INTEGER NOT NULL,
    input_cycle INTEGER,
    rot_bias REAL NOT NULL,
    position INT NOT NULL,
    rpe INT NOT NULL,
    ext_load INT,
    comments TEXT,
    FOREIGN KEY (tid) REFERENCES zones (id)
);