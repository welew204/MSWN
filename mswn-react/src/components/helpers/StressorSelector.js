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

export default function StressorSelector({
  InputInProgress,
  updateInputInProgress,
  repsTimeArray,
  setWktInProgress,
}) {
  const [timeUnderTension, setTimeUnderTension] = useState(true);

  useEffect(() => {
    // this auto-updates the duration value for 'rep-schemed' MJ inputs, per each mini-set
    // this useEffect updates the reps_array and duration based on MJ boolean
    let new_duration;
    if (!timeUnderTension) {
      new_duration =
        InputInProgress.reps_array.slice(2).reduce((acc, curr_val) => {
          return acc + curr_val;
        }, 0) * InputInProgress.reps_array[1];
      console.log(new_duration);
    } else {
      new_duration = InputInProgress.duration;
    }
    updateInputInProgress(["duration", new_duration]);
  }, [InputInProgress.reps_array]);

  useEffect(() => {
    // this useEffect updates the reps_array and duration based on MJ boolean
    let new_reps_array = [1, 0, 0, 0, 0, 0];
    if (!timeUnderTension) {
      // this means the new rep_arry will start with 1 rep
      new_reps_array[1] = 1;
    } else {
      // this means the new rep-arry will be 0-reps
      new_reps_array[1] = 0;
    }
    updateInputInProgress(["reps_array", new_reps_array]); /* 
        Promise.resolve(updateInputInProgress(["reps_array", repsTimeArray])).then(
          (res) => updateInputInProgress[("duration", new_duration)]
        ); */
  }, [timeUnderTension]);

  return (
    <Form.Group controlId='stressor-selector'>
      <Form.Group>
        {InputInProgress.multijoint ? (
          <div>
            <Form.ControlLabel>Select Stressor Measure: </Form.ControlLabel>
            <Toggle
              checkedChildren='Time Under Tension'
              unCheckedChildren='Number of Reps'
              checked={timeUnderTension}
              onChange={() => setTimeUnderTension((prev) => !prev)}
            />
          </div>
        ) : (
          void 0
        )}
        {timeUnderTension ? (
          <div>
            <Form.ControlLabel>Duration: </Form.ControlLabel>
            <InputNumber
              value={InputInProgress.duration}
              onChange={(v) => updateInputInProgress(["duration", parseInt(v)])}
              step={1}
            />
          </div>
        ) : (
          <div>
            <Form.ControlLabel>Reps: </Form.ControlLabel>
            <InputNumber
              step={1}
              value={repsTimeArray[1]}
              onChange={(v) => {
                let value = parseInt(v);
                value >= 1 ? void 0 : (value = 1);
                let temp_array = [...repsTimeArray];
                temp_array.splice(1, 1, value);
                return updateInputInProgress(["reps_array", temp_array]);
              }}
            />
            <Form.ControlLabel>Rep Cadence: </Form.ControlLabel>
            <InputGroup size='md' style={{ display: "flex", width: "500px" }}>
              <InputGroup.Addon>UP</InputGroup.Addon>
              <InputNumber
                step={1}
                value={repsTimeArray[2]}
                onChange={(v) => {
                  let value = parseInt(v);
                  value >= 1 ? void 0 : (value = 1);
                  let temp_array = [...repsTimeArray];
                  temp_array.splice(2, 1, value);

                  return updateInputInProgress(["reps_array", temp_array]);
                }}
              />
              <InputGroup.Addon>Top</InputGroup.Addon>
              <InputNumber
                step={1}
                value={repsTimeArray[3]}
                onChange={(v) => {
                  let value = parseInt(v);
                  value >= 1 ? void 0 : (value = 1);
                  let temp_array = [...repsTimeArray];
                  temp_array.splice(3, 1, value);

                  return updateInputInProgress(["reps_array", temp_array]);
                }}
              />
              <InputGroup.Addon>DOWN</InputGroup.Addon>
              <InputNumber
                step={1}
                value={repsTimeArray[4]}
                onChange={(v) => {
                  let value = parseInt(v);
                  value >= 1 ? void 0 : (value = 1);
                  let temp_array = [...repsTimeArray];
                  temp_array.splice(4, 1, value);

                  return updateInputInProgress(["reps_array", temp_array]);
                }}
              />
              <InputGroup.Addon>Bottom</InputGroup.Addon>
              <InputNumber
                step={1}
                value={repsTimeArray[5]}
                onChange={(v) => {
                  let value = parseInt(v);
                  value >= 1 ? void 0 : (value = 1);
                  let temp_array = [...repsTimeArray];
                  temp_array.splice(5, 1, value);

                  return updateInputInProgress(["reps_array", temp_array]);
                }}
              />
            </InputGroup>
          </div>
        )}
      </Form.Group>
      <Form.ControlLabel>Mini-sets: </Form.ControlLabel>
      <InputNumber
        step={1}
        value={InputInProgress.reps_array[0]}
        onChange={(v) => {
          let value = parseInt(v);
          value >= 1 ? void 0 : (value = 1);
          let temp_array = [...repsTimeArray];
          temp_array.splice(0, 1, value);

          return updateInputInProgress(["reps_array", temp_array]);
        }}
      />
    </Form.Group>
  );
}
