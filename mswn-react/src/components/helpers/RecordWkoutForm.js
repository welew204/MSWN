import React, { useState } from "react";
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
  Divider,
  Loader,
} from "rsuite";
import { useQuery, useMutation } from "@tanstack/react-query";
import { find } from "rsuite/esm/utils/ReactChildren";

const server_url = "http://127.0.0.1:8000";

export default function RecordWkoutForm({
  selectedInput,
  workoutResults,
  updateWorkoutResults,
  updateDB,
}) {
  /* query callback fnc */
  function fetchAPI(url) {
    return fetch(url).then((res) => {
      return res.json();
    });
  }

  /* console.log(jointRefData.isLoading ? "" : jointRefData.data) */

  /* state for form components */

  const [inputFormArray, SetInputFormArray] = useState([
    selectedInput.id,
    {
      ref_joint_id: [],
      rails: false,
      passive_duration: 0,
      duration: 0,
      rpe: 0,
      external_load: 0,
      tissue_id: "",
      workout_id: "",
    },
  ]);
  console.log(inputFormArray);

  function updateInputForm(value) {
    const [field, updVal] = value;
    const new_inputFormArray = [
      selectedInput.id,
      { ...inputFormArray[1], [field]: updVal },
    ];
    SetInputFormArray(new_inputFormArray);
    pushToWorkout();
  }

  const pushToWorkout = () => updateWorkoutResults(inputFormArray);
  /* QUESTION FOR HACKERS: 
  seems that state doesn't get updated IN the actual function--
  so do I just have to chain a bunch of functions together, or??? 
  OR: am I doing something else wrong bc I am not seeing the fully 
  updated state when I submit the form...
  */

  if (selectedInput == "")
    return <h2>Select an input to begin recording results...</h2>;

  /* console.log(jointRefData.data) */

  /* this function logs the ref_joint or ref_zone id into state, so that can be sent off with 'submit_form' */
  /* function find_tissue(item) {
    const id = item.id;
    if (item.children) {
      setJointID(id);
    } else {
      setZoneID(id);
    }
  } */

  const position = ["Regressive (short)", "Progressive (long)"];

  return (
    <div className='inp-form'>
      <Form>
        <h2
          style={{
            textAlign: "center",
          }}>{`${selectedInput.ref_joint_name} ${selectedInput.drill_name}`}</h2>
        <Divider />
        <Form.Group controlId='rails'>
          <Form.ControlLabel>RAILs tissue trained...?</Form.ControlLabel>
          {<h4>not indicated</h4>}
          <Toggle
            onChange={(v, e) => updateInputForm(["rails", v])}
            value={inputFormArray.rails}
          />
        </Form.Group>

        <br />
        <Form.Group controlId='p_dur'>
          <Form.ControlLabel>Duration of passive stretch:</Form.ControlLabel>
          <h4>{`Rx: ${selectedInput.passive_duration}sec`}</h4>
          <InputNumber
            onChange={(v, e) => updateInputForm(["passive_duration", v])}
            value={inputFormArray.passive_duration}
            postfix='seconds'
          />
        </Form.Group>
        <br />

        <Form.Group controlId='duration'>
          <Form.ControlLabel>Duration of effort:</Form.ControlLabel>
          <h4>{`Rx: ${selectedInput.duration}sec`}</h4>
          <InputNumber
            onChange={(v, e) => updateInputForm(["duration", v])}
            value={inputFormArray.duration}
            postfix='seconds'
          />
        </Form.Group>
        <br />
        <Form.Group controlId='rpe'>
          <Form.ControlLabel>
            Rate of Percieved Exertion (RPE):
          </Form.ControlLabel>
          <h4>{`Rx: ${selectedInput.rpe}`}</h4>
          <Slider
            onChange={(v, e) => updateInputForm(["rpe", v])}
            value={inputFormArray.rpe}
            min={0}
            step={1}
            max={10}
            graduated
            progress
            renderMark={(mark) => {
              return mark;
            }}
            style={{ width: 300 }}
          />
        </Form.Group>
        <br />
        <Form.Group controlId='load'>
          <Form.ControlLabel>External Load (optional):</Form.ControlLabel>
          {
            <h4>
              Rx:{" "}
              {selectedInput.external_load != ""
                ? `${selectedInput.external_load}`
                : "none"}
            </h4>
          }
          <InputNumber
            onChange={(v, e) => updateInputForm(["external_load", v])}
            value={inputFormArray.external_load}
            postfix='lbs'
          />
        </Form.Group>
        <Form.Group>
          <ButtonToolbar>
            <Button appearance='primary' onClick={updateDB}>
              Save Input
            </Button>
            <Button appearance='default'>Cancel</Button>
          </ButtonToolbar>
        </Form.Group>
      </Form>
    </div>
  );
}
