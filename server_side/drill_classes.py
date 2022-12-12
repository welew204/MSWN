import uuid
import datetime as dt

class InputCycle1:
    def __init__(self, joint, bias, zone):
        self.joint = joint
        self.bias = bias
        self.zone = zone
        # need to SELECT ref_tissues that correspond with this joint:bias:zone from DB, store to arrays of tissue_ref_id...
        self.tissues_trained_prog = []
        self.tissues_trained_reg = []
    def apply_impact(self, mover_id, duration, rpe, load=1, passive_duration=0, pails=True, rails=False):
        self.mover_id = mover_id
        self.duration = duration
        self.rpe = rpe
        self.load = load
        self.passive_duration = passive_duration
        self.pails = pails
        self.rails = rails
        # this generates a psuedo-random key to help group bouts as PART of this input upon application
        self.date_applied = dt.datetime.now()
        self.input_id = uuid.uuid4()
        tissues_to_write_to = []
        if pails:
            for tissue in self.tissues_trained_prog:
                pass
                # need to SELECT mover-specific tissue_ids, then use that combined with IMPACT vals to create np.array
                # that will get stored in each tissue's BLOBs (musc, ct which we KNOW bc this IC is isometric)
        if rails:
            for tissue in self.tissues_trained_prog:
                pass
        # executemany using tissues to write to
        # seperate execute to bout_log
    # add assign() when getting to progrmaming step