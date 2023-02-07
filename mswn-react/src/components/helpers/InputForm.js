import React, { useEffect, useState } from "react";
import {
  Toggle,
  ButtonToolbar,
  Button,
  InputNumber,
  Slider,
  Cascader,
  SelectPicker,
  Form,
  DatePicker,
  Timeline,
  Schema,
  RangeSlider,
} from "rsuite";
import { useQuery, useMutation } from "@tanstack/react-query";
import { find } from "rsuite/esm/utils/ReactChildren";

const server_url = "http://127.0.0.1:8000";

export default function InputForm({
  updateDB,
  setSelectedInput,
  wktInProgress,
  updateWkt,
  selectedInput,
  setWktInProgress,
  default_new_input,
}) {
  /* query callback fnc */
  function fetchAPI(url) {
    return fetch(url).then((res) => {
      return res.json();
    });
  }

  /* useQuery's */
  const drillRefData = useQuery(["drillRef"], () =>
    fetchAPI(server_url + "/drill_ref")
  );
  const boutLogData = useQuery(["boutLog"], () =>
    fetchAPI(server_url + "/bout_log/1")
  );
  const jointRefData = useQuery(["jointsRef"], () =>
    fetchAPI(server_url + "/joint_ref")
  );
  /* console.log(jointRefData.isLoading ? "" : jointRefData.data) */

  /* state for form components */
  const [drillDate, setDrillDate] = useState("");

  const [jointSelected, setJointSelected] = useState("");
  /* console.log(jointSelected);*/

  const [jointID, setJointID] = useState(0);
  const [zoneID, setZoneID] = useState(0);

  useEffect(() => setJointID(wktInProgress[selectedInput]?.ref_joint_id), []);
  useEffect(() => setZoneID(wktInProgress[selectedInput]?.ref_zones_id_a), []);
  /* console.log("jointId in state: " + jointID); */
  /* console.log("zoneId in state: " + zoneID); */

  if (boutLogData.isLoading) {
    return <p>Getting your bout data...</p>;
  }
  if (jointRefData.isLoading) {
    return <p>Ish is loading!</p>;
  }
  if (drillRefData.isLoading) {
    return <p>Ish is loading!</p>;
  }

  const jointsArray = jointRefData.data.map((joint, index) => {
    return {
      label: joint["name"],
      id: joint["id"],
      value: joint["id"].toString(),
      children: joint["zones"].map((zone, i) => {
        return {
          label: zone["zone_name"],
          value: `${zone["rowid"]}-${zone["id"]}`,
          id: zone["id"],
        };
      }),
    };
  });

  const drills = Object.keys(drillRefData.data).map((item) => ({
    label: item,
    value: item,
  }));

  /* this function logs the ref_joint or ref_zone id into state, so that can be sent off with 'submit_form' */
  function find_tissue(value) {
    /* checks if value is null (meaning the user has CLEARED the select box) */
    if (!value) {
      setJointID("");
      setZoneID("");
      updateWkt("inputs", {
        ...wktInProgress.inputs,
        [selectedInput]: {
          ...wktInProgress.inputs[selectedInput],
          ref_joint_id: "",
          ref_joint_name: "",
          ref_joint_side: "",
        },
      });
    } else if (!value.includes("-")) {
      setJointID(value);
      setZoneID("");
      const target_joint = jointRefData.data.find((joint) => joint.id == value);
      /* nb *target_joint ==> a joint Object, with ALL zones includes inside .zones array */
      updateWkt("inputs", {
        ...wktInProgress.inputs,
        [selectedInput]: {
          ...wktInProgress.inputs[selectedInput],
          ref_joint_id: value,
          ref_joint_name: target_joint.zones[0].joint_name,
          ref_zones_id_a: "",
          ref_zones_id_b: "",
          ref_joint_side: target_joint.zones[0].side,
        },
      });
      console.log(
        `setting Joint ID!: ${target_joint.id}, ${target_joint.zones[0].side}, ${target_joint.name}`
      );
    } else {
      /* console.log("ZONE return 'item'... " + item); */
      /* const zone_id = id; */
      const [joint_id, zone_id] = value.split("-");
      setJointID(joint_id);
      setZoneID(zone_id);
      const target_joint = jointRefData.data.find(
        (joint) => joint.id == joint_id
      );
      const target_zone = target_joint.zones.find((zone) => zone.id == zone_id);
      updateWkt("inputs", {
        ...wktInProgress.inputs,
        [selectedInput]: {
          ...wktInProgress.inputs[selectedInput],
          ref_joint_id: joint_id,
          ref_joint_name: target_joint.zones[0].joint_name,
          ref_joint_side: target_joint.zones[0].side,
          ref_zones_id_a: zone_id,
          ref_zone_name: target_zone.zone_name,
        },
      });
      console.log(
        `setting Zone ID!: ${target_joint.id}-${target_zone.id}, ${target_zone.side}, ${target_zone.zone_name}`
      );

      /* nb *target_zone ==> a zone Object, with these params:
      - id, 
      - joint-name,
      - joint_type,
      - side,
      - zone_name
       */
    }
  }
  /* updateInputInProgress(["ref_joint_id", id]);
  updateInputInProgress(["ref_joint_name", label]); */

  async function submit_form() {
    const input_index = Object.keys(wktInProgress.inputs).length + 1;
    const sets = Object.entries(wktInProgress.schema);
    const next_set = String.fromCharCode(
      sets
        .find((set) => set[1].circuit.includes(`${selectedInput}`))
        .at(0)
        .charCodeAt() + 1
    );

    return Promise.resolve(
      updateWkt("inputs", {
        ...wktInProgress.inputs,
        [selectedInput]: { ...InputInProgress, completed: true },
      })
    )
      .then((res) =>
        setWktInProgress((prev) => {
          return {
            ...prev,
            inputs: {
              ...prev.inputs,
              [input_index]: { ...default_new_input, id: input_index },
            },
            schema: {
              ...prev.schema,
              [next_set]: {
                circuit: [`${input_index}`],
                iterations: 1,
              },
            },
          };
        })
      )
      .then((res) => setSelectedInput(input_index));
  }
  /* TODO need to add 'model' for schema to do validation correctly */
  const jointRule = Schema.Types.StringType().isRequired(
    "Please select a joint or a specific joint-zone."
  );
  const drillRule = Schema.Types.StringType().isRequired(
    "Please select a drill."
  );
  const timeRule = Schema.Types.StringType().isRequired(
    "Please select an intended duration."
  );
  const rpeRule = Schema.Types.StringType().isRequired(
    "Please select an intented RPE."
  );

  const position = ["Regressive (short)", "Progressive (long)"];

  const bout_array = boutLogData.data["bout_log"];
  const bouts = bout_array.map((bout, i) => {
    return (
      <Timeline.Item key={`bout_${bout_array[i].id}`} time={bout_array[i].date}>
        {bout_array[i].comments}, RPE: {bout_array[i].rpe}, External Load:{" "}
        {bout_array[i].external_load}
      </Timeline.Item>
    );
  });

  function updateInputInProgress(value) {
    const [field, updVal] = value;
    const new_results = {
      ...wktInProgress.inputs[selectedInput],
      [field]: updVal,
    };
    updateWkt("inputs", {
      ...wktInProgress.inputs,
      [selectedInput]: new_results,
    });
    console.log("finished updating input: " + value);
  }
  /* nb... InputInProgress, shortened here to assist with readability  */
  const InputInProgress = wktInProgress.inputs[selectedInput];
  console.log(InputInProgress);

  return (
    <div className='inp-form'>
      <Form>
        <Form.Group
          controlId='joint'
          /* style={{ display: "flex", justifyContent: "space-evenly" }} */
        >
          <Form.Group>
            <Form.ControlLabel>Joint / Zone trained:</Form.ControlLabel>
            {/* <Form.Control name='joint' rule={jointRule} /> */}
            <Cascader
              key={`${selectedInput}-joint_zone_a`}
              data={jointsArray}
              style={{ width: 224 }}
              value={
                !InputInProgress.ref_zones_id_a
                  ? `${InputInProgress.ref_joint_id}`
                  : `${InputInProgress.ref_joint_id}-${InputInProgress.ref_zones_id_a}`
              }
              parentSelectable
              onChange={(value) => {
                find_tissue(value);
              }}
            />
          </Form.Group>
          {/* <Form.Group>
            <Form.ControlLabel>Secondary zone trained: (opt)</Form.ControlLabel>
            <Cascader
              key={`${selectedInput}-b_zone`}
              disabled={true}
              data={
                jointID
                  ? [jointsArray.find((joint) => joint.id == jointID)]
                  : []
              }
              style={{ width: 224 }}
              value={
                InputInProgress.ref_joint_id
                  ? InputInProgress.ref_zones_id_b
                    ? `${InputInProgress.ref_joint_id}-${InputInProgress.ref_zones_id_b}`
                    : `${InputInProgress.ref_joint_id}`
                  : "n/a"
              }
              onChange={(value) => {
                if (value.includes("-")) {
                  const [joint_id, zone_b_id] = value.split("-");
                  updateInputInProgress(["ref_zones_id_b", zone_b_id]);
                }
              }}
            />
          </Form.Group> */}
        </Form.Group>
        <Form.Group controlId='drills'>
          <Form.ControlLabel>Drill:</Form.ControlLabel>
          {/* <Form.Control name='drill' rule={drillRule} /> */}
          <SelectPicker
            key={`${selectedInput}-drill`}
            cleanable
            onClean={() => updateInputInProgress(["drill_name", ""])}
            value={`${InputInProgress.drill_name}`}
            data={drills}
            disabled={InputInProgress.ref_joint_id ? false : true}
            disabledItemValues={
              zoneID
                ? ["CARs"]
                : ["PRH", "Muscular Scan", "IC1", "IC2", "IC3", "capsule CAR"]
            }
            searchable={false}
            style={{ width: 224 }}
            onSelect={(value) => updateInputInProgress(["drill_name", value])}
          />
        </Form.Group>
        {["IC1", "IC2"].includes(InputInProgress.drill_name) ? (
          <Form.Group controlId='rails'>
            <Form.ControlLabel>RAILs tissue trained...?</Form.ControlLabel>
            <Toggle
              key={`${selectedInput}-rails`}
              /* disabled={
                ["IC1", "IC2"].includes(InputInProgress.drill_name)
                ? false
                : true
              } */
              onChange={(v, e) => updateInputInProgress(["rails", v])}
              checked={InputInProgress.rails ? InputInProgress.rails : false}
            />
          </Form.Group>
        ) : (
          void 0
        )}
        {["IC3", "Muscular Scan"].includes(InputInProgress.drill_name) ? (
          <Form.Group
            controlId='position'
            style={{
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
            }}>
            <Form.ControlLabel>
              Select Start/End of Contraction
            </Form.ControlLabel>
            <RangeSlider
              key={`${selectedInput}-rangeSlider`}
              handleStyle={{ marginLeft: "0%", fontSize: "x-small" }}
              value={InputInProgress.coords}
              min={0}
              step={5}
              max={100}
              graduated
              progress
              renderMark={(mark) => {
                if (mark === 0) {
                  return position[0];
                } else if (mark === 100) {
                  return position[1];
                }
              }}
              style={{ width: "80%" }}
              onChange={(value) => {
                updateInputInProgress(["coords", value]);
              }}
            />
          </Form.Group>
        ) : (
          <Form.Group
            controlId='position'
            style={{
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
            }}>
            <Form.ControlLabel>Position of Tissue:</Form.ControlLabel>
            <Slider
              key={`${selectedInput}-position`}
              handleStyle={{ marginLeft: "0%", fontSize: "x-small" }}
              min={0}
              step={5}
              max={100}
              disabled={
                ["PRH", "CARs", "capsule CAR", "IC1"].includes(
                  InputInProgress.drill_name
                )
                  ? true
                  : false
              }
              value={
                InputInProgress.drill_name == "PRH"
                  ? 0
                  : parseInt(InputInProgress.start_coord)
              }
              graduated
              progress
              renderMark={(mark) => {
                if (mark === 0) {
                  return position[0];
                } else if (mark === 100) {
                  return position[1];
                }
              }}
              style={{ width: "80%" }}
              onChange={(v) => updateInputInProgress(["start_coord", v])}
              /* onChangeCommitted={(value) =>
                  updateInputInProgress(["start_coord", value])
                } */
            />
          </Form.Group>
        )}
        <br />
        <Form.Group controlId='rotation'>
          <Form.ControlLabel>
            Rotation/Bias of Joint (IR is - , ER is +):
          </Form.ControlLabel>
          <Slider
            key={`${selectedInput}-rotation`}
            value={
              InputInProgress.rotational_value
                ? InputInProgress.rotational_value
                : void 0
            }
            disabled={
              InputInProgress.ref_joint_id
                ? ["capsule CAR", "CARs"].includes(InputInProgress.drill_name)
                  ? true
                  : false
                : true
            }
            defaultValue={0}
            min={-100}
            step={5}
            max={100}
            graduated
            progress
            renderMark={(mark) => {
              if (["IC1"].includes(InputInProgress.drill_name)) {
                if (Math.abs(mark) === 100) {
                  return mark;
                }
              } else {
                if (mark % 25 === 0) {
                  return mark;
                } else {
                  return null;
                }
              }
            }}
            style={{ width: "80%" }}
            onChange={void 0}
            onChangeCommitted={(value) =>
              updateInputInProgress(["rotational_value", value])
            }
          />
        </Form.Group>

        <br />
        {["IC1", "IC2"].includes(InputInProgress.drill_name) ? (
          <div>
            <Form.Group controlId='passiveDuration'>
              <Form.ControlLabel>
                Duration of passive stretch:
              </Form.ControlLabel>
              <InputNumber
                key={`${selectedInput}-passiveDuration`}
                onChange={(value) =>
                  updateInputInProgress(["passive_duration", value])
                }
                value={
                  InputInProgress.passive_duration
                    ? InputInProgress.passive_duration
                    : ""
                }
                postfix='seconds'
              />
            </Form.Group>
            <br />
          </div>
        ) : (
          ""
        )}
        <Form.Group controlId='duration'>
          <Form.ControlLabel>Duration of effort:</Form.ControlLabel>
          {/* <Form.Control name='duration' rule={timeRule} /> */}
          <InputNumber
            key={`${selectedInput}-duration`}
            disabled={InputInProgress.drill_name ? false : true}
            onChange={(value) => updateInputInProgress(["duration", value])}
            value={InputInProgress.duration ? InputInProgress.duration : ""}
            postfix='seconds'
          />
        </Form.Group>

        <br />
        <Form.Group controlId='rpe'>
          <Form.ControlLabel>
            Rate of Percieved Exertion (RPE):
          </Form.ControlLabel>
          {/* <Form.Control name='rpe' rule={rpeRule} /> */}
          <Slider
            disabled={InputInProgress.drill_name ? false : true}
            key={`${selectedInput}-rpe`}
            value={InputInProgress.rpe ? InputInProgress.rpe : 0}
            min={0}
            step={1}
            max={10}
            graduated
            progress
            renderMark={(mark) => {
              return mark;
            }}
            style={{ width: "80%" }}
            onChange={(value) => updateInputInProgress(["rpe", value])}
            /* onChangeCommitted={(value) => updateInputInProgress(["rpe", value])} */
          />
        </Form.Group>
        <br />
        <Form.Group controlId='load'>
          <Form.ControlLabel>External Load (optional):</Form.ControlLabel>
          <InputNumber
            value={
              InputInProgress.external_load ? InputInProgress.external_load : ""
            }
            disabled={
              InputInProgress.drill_name
                ? ["IC1", "IC2"].includes(InputInProgress.drill_name)
                  ? true
                  : false
                : true
            }
            postfix='lbs'
            onChange={(value) =>
              updateInputInProgress(["external_load", value])
            }
          />
        </Form.Group>
        <Form.Group>
          <ButtonToolbar>
            <Button appearance='primary' onClick={submit_form}>
              Add to Workout
            </Button>
            <Button
              appearance='default'
              onClick={() =>
                updateWkt("inputs", {
                  ...wktInProgress.inputs,
                  [selectedInput]: default_new_input,
                })
              }>
              Cancel
            </Button>
          </ButtonToolbar>
        </Form.Group>
      </Form>
    </div>
  );
}
