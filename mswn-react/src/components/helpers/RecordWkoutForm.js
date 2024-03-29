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

  function updateInputForm(value) {
    const [field, updVal] = value;
    const new_results = {
      ...workoutResults[selectedInput.id].results,
      [field]: updVal,
    };
    updateWorkoutResults(selectedInput.id, {
      ...workoutResults[selectedInput.id],
      results: new_results,
    });
  }

  if (!selectedInput)
    return <h2>Or, select an input to begin recording results...</h2>;
  else {
    console.log(selectedInput);
  }

  return (
    <div className='inp-form'>
      <Form>
        <h2
          style={{
            textAlign: "center",
          }}>
          {selectedInput.multijoint
            ? `${selectedInput.drill_name}`
            : `${selectedInput.ref_joint_name} ${selectedInput.drill_name}`}
        </h2>
        <p>
          "***Some info defining the guidelines of this drill --eventually this
          will be an cg-animation (blender)***
        </p>
        <Divider />

        {workoutResults[selectedInput.id].Rx.rails != null ? (
          <Form.Group controlId='rails'>
            <Form.ControlLabel>RAILs tissue trained...?</Form.ControlLabel>
            {workoutResults[selectedInput.id].Rx.rails ? (
              <h4>Rx: RAILs indicated</h4>
            ) : (
              <h4>Rx: RAILs not indicated</h4>
            )}
            <Toggle
              key={selectedInput.id}
              onChange={(v) => updateInputForm(["rails", v])}
              checked={workoutResults[selectedInput.id].results.rails}
            />
          </Form.Group>
        ) : (
          void 0
        )}

        <br />
        {workoutResults[selectedInput.id].Rx.passive_duration ? (
          <Form.Group controlId='p_dur'>
            <Form.ControlLabel>Duration of passive stretch:</Form.ControlLabel>
            <h4>{`Rx: ${selectedInput.passive_duration}sec`}</h4>
            <InputNumber
              onChange={(v, e) => updateInputForm(["passive_duration", v])}
              value={workoutResults[selectedInput.id].results.passive_duration}
              postfix='seconds'
            />
          </Form.Group>
        ) : (
          void 0
        )}
        <br />

        <Form.Group controlId='reps-array'>
          <Form.ControlLabel>Rep scheme defined:</Form.ControlLabel>
          <h4>{`Rx: ${selectedInput.reps_array[0]} mini-sets`}</h4>
          <InputNumber
            onChange={(v, e) => {
              var new_reps_array = selectedInput.reps_array.map((val, ind) =>
                ind == 0 ? parseInt(v) : val
              );
              return updateInputForm(["reps_array", new_reps_array]);
            }}
            value={workoutResults[selectedInput.id].results.reps_array[0]}
            postfix='mini-sets'
          />
        </Form.Group>

        <br />
        {selectedInput.reps_array[1] > 0 ? (
          <Form.Group controlId='reps'>
            <Form.ControlLabel>Rep count (per mini-set):</Form.ControlLabel>
            <h4>{`Rx: ${selectedInput.reps_array[1]} reps`}</h4>
            <h6>{`Tempo indicated: ${selectedInput.reps_array[4]}-${selectedInput.reps_array[5]}-${selectedInput.reps_array[2]}-${selectedInput.reps_array[3]}`}</h6>
            <InputNumber
              onChange={(v, e) =>
                updateInputForm([
                  "reps_array",
                  [
                    ...selectedInput.reps_array.slice(0, 1),
                    parseInt(v),
                    ...selectedInput.reps_array.slice(2),
                  ],
                ])
              }
              value={workoutResults[selectedInput.id].results.reps_array[1]}
              postfix='repetitions'
            />
          </Form.Group>
        ) : (
          <Form.Group controlId='duration'>
            <Form.ControlLabel>
              Duration of effort (per mini-set):
            </Form.ControlLabel>
            <h4>{`Rx: ${selectedInput.duration}sec`}</h4>
            <InputNumber
              onChange={(v, e) => updateInputForm(["duration", parseInt(v)])}
              value={workoutResults[selectedInput.id].results.duration}
              postfix='seconds'
            />
          </Form.Group>
        )}

        <br />
        <Form.Group controlId='rpe'>
          <Form.ControlLabel>
            Rate of Percieved Exertion (RPE):
          </Form.ControlLabel>
          <h4>{`Rx: ${selectedInput.rpe}`}</h4>
          <Slider
            onChange={(v, e) => updateInputForm(["rpe", v])}
            value={workoutResults[selectedInput.id].results.rpe}
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
            value={workoutResults[selectedInput.id].results.external_load}
            postfix='lbs'
          />
        </Form.Group>
        <Form.Group>
          <ButtonToolbar>
            <Button
              appearance='primary'
              onClick={(e) => updateDB(e, selectedInput.id)}>
              Save Input
            </Button>
            <Button
              appearance='default'
              onClick={() =>
                updateWorkoutResults(selectedInput.id, {
                  ...workoutResults[selectedInput.id],
                  results: {
                    rails: false,
                    passive_duration: 0,
                    duration: 0,
                    rpe: 0,
                    external_load: 0,
                  },
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
