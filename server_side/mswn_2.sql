mswn_2

DROP TABLE IF EXISTS ref_bone_end;
DROP TABLE IF EXISTS ref_bone_adj;
DROP TABLE IF EXISTS ref_capsule_anchor;
DROP TABLE IF EXISTS ref_capsule_adj;
DROP TABLE IF EXISTS ref_rotational_tissue_anchor;
DROP TABLE IF EXISTS ref_rotational_tissue_adj;
DROP TABLE IF EXISTS ref_linear_tissue_anchor;
DROP TABLE IF EXISTS ref_linear_tissue_adj;
DROP TABLE IF EXISTS bone_end;
DROP TABLE IF EXISTS bone_adj;
DROP TABLE IF EXISTS capsule_anchor;
DROP TABLE IF EXISTS capsule_adj;
DROP TABLE IF EXISTS rotational_tissue_anchor;
DROP TABLE IF EXISTS rotational_tissue_adj;
DROP TABLE IF EXISTS linear_tissue_anchor;
DROP TABLE IF EXISTS linear_tissue_adj;

DROP TABLE IF EXISTS programming_log;
DROP TABLE IF EXISTS bout_log;
DROP TABLE IF EXISTS assess_events;
DROP TABLE IF EXISTS assess_joints_log;

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

