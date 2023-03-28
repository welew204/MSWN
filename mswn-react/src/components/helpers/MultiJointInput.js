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
  Input,
  Divider,
  InputGroup,
} from "rsuite";
import { useQuery, useMutation } from "@tanstack/react-query";
import { find } from "rsuite/esm/utils/ReactChildren";
import StressorSelector from "./StressorSelector";

const server_url = "http://127.0.0.1:8000";

export default function MultiJointInput({
  updateDB,
  setSelectedInput,
  default_new_input,
  setWktInProgress,
  wktInProgress,
  updateWkt,
  selectedInput,
}) {
  const [mirrorStatus, setMirrorStatus] = useState([false, false]);

  function fetchAPI(url) {
    return fetch(url).then((res) => {
      return res.json();
    });
  }

  async function submit_form() {
    console.log(wktInProgress.inputs);
    /* const sets = Object.entries(wktInProgress.schema);
    const next_set = String.fromCharCode(
      sets
      .find((set) => set[1].circuit.includes(`${selectedInput}`))
      .at(0)
      .charCodeAt() + 1
      ); */
    // conditional check if mirror is selected; if so then duplicate
    // value to other side
    let inputsPayload;
    let schemaPayload;
    let input_index;
    console.log(mirrorStatus);
    mirrorStatus[1]
      ? (input_index = parseInt(Object.keys(wktInProgress.inputs).at(-1)) + 2)
      : (input_index = parseInt(Object.keys(wktInProgress.inputs).at(-1)) + 1);
    console.log(input_index);
    // waiting for build out of mirrorInput func
    /* if (mirrorStatus[1]) {
      inputsPayload = {
        ...wktInProgress.inputs,
        [selectedInput]: { ...InputInProgress, completed: true },
        //THIS below should be the MIRRORED input, but struggling to get the mirrorIDs in state
        [selectedInput + 1]: {
          ...InputInProgress,
          id: InputInProgress.id + 1,
          ref_joint_id: mirrorJointID[0],
          ref_joint_side: mirrorJointID[1],
          ref_zones_id_a: mirrorZoneID,
          completed: true,
        },
      };
      schemaPayload = [
        ...wktInProgress.schema,
        {
          circuit: [`${InputInProgress.id + 1}`],
          iterations: 1,
        },
      ];
    } else {
      inputsPayload = {
        ...wktInProgress.inputs,
        [selectedInput]: { ...InputInProgress, completed: true },
      };
      schemaPayload = [...wktInProgress.schema];
    } */
    inputsPayload = {
      ...wktInProgress.inputs,
      [selectedInput]: { ...InputInProgress, completed: true },
    };
    schemaPayload = [...wktInProgress.schema];
    console.log(inputsPayload);
    return Promise.resolve(updateWkt("inputs", inputsPayload))
      .then((res) =>
        setWktInProgress((prev) => {
          return {
            ...prev,
            inputs: {
              ...prev.inputs,
              [input_index]: { ...default_new_input, id: input_index },
            },
            schema: [
              ...schemaPayload,
              {
                circuit: [`${input_index}`],
                iterations: 1,
              },
            ],
          };
        })
      )
      .then((res) => setSelectedInput(input_index));
  }

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

  const InputInProgress = wktInProgress.inputs[selectedInput];
  console.log(InputInProgress);

  // need to query possible multi-joint inputs >> for SelectInput ('drill_name's)
  const drill_array = [
    { name: "push-up", id: "1" },
    { name: "forward lunge", id: "2" },
    { name: "plank", id: "3" },
  ];
  const drills = drill_array.map((drill, index) => {
    return {
      label: drill["name"],
      id: drill["id"],
      value: drill["id"].toString(),
    };
  });

  return (
    <div>
      <Form>
        <Form.Group controlId='exercise-name'>
          <Form.ControlLabel>Exercise Name:</Form.ControlLabel>
          <SelectPicker
            onChange={(value) => {
              !value
                ? updateInputInProgress(["drill_name", ""])
                : updateInputInProgress([
                    "drill_name",
                    drills.find((drill) => drill.id == value).label,
                  ]);
            }}
            data={drills}></SelectPicker>
        </Form.Group>
        <Divider />
        <StressorSelector
          InputInProgress={InputInProgress}
          updateInputInProgress={updateInputInProgress}
          repsTimeArray={InputInProgress.reps_array}
          setWktInProgress={setWktInProgress}
        />
        <Divider />
        <Form.Group controlId='rpe'>
          <Form.ControlLabel>
            Rate of Percieved Exertion (RPE):
          </Form.ControlLabel>
          {/* <Form.Control name='rpe' rule={rpeRule} /> */}
          <Slider
            min={0}
            step={1}
            max={10}
            graduated
            progress
            renderMark={(mark) => {
              return mark;
            }}
            style={{ width: "80%" }}
            value={parseInt(InputInProgress.rpe)}
            onChange={(v) => updateInputInProgress(["rpe", parseInt(v)])}

            /* onChangeCommitted={(value) => updateInputInProgress(["rpe", value])} */
          />
        </Form.Group>
        <br />
        <Form.Group controlId='load'>
          <Form.ControlLabel>External Load (optional):</Form.ControlLabel>
          <InputNumber
            postfix='lbs'
            step={1}
            value={InputInProgress.external_load}
            onChange={(v) => {
              let value = parseInt(v);
              value >= 0 ? void 0 : (value = 0);
              updateInputInProgress(["external_load", value]);
            }}
          />
        </Form.Group>
        <Form.Group>
          <ButtonToolbar>
            <Button appearance='primary' onClick={submit_form}>
              Add to Workout
            </Button>
            <Button
              appearance='default'
              /* onClick={() =>
                updateWkt("inputs", {
                  ...wktInProgress.inputs,
                  [selectedInput]: default_new_input,
                })
              } */
            >
              Cancel
            </Button>
          </ButtonToolbar>
        </Form.Group>
      </Form>
    </div>
  );
}
