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

const server_url = "http://127.0.0.1:8000";

export default function MultiJointInput() {
  const [timeUnderTension, setTimeUnderTension] = useState(true);
  function fetchAPI(url) {
    return fetch(url).then((res) => {
      return res.json();
    });
  }

  return (
    <div>
      <Form>
        <Form.Group controlId='exercise-name'>
          <Form.ControlLabel>Exercise Name:</Form.ControlLabel>
          <Cascader></Cascader>
        </Form.Group>
        <Divider />
        <Form.Group controlId='stressor-selector'>
          <Form.Group>
            <Form.ControlLabel>Select Stressor Measure: </Form.ControlLabel>
            <Toggle
              checkedChildren='Time Under Tension'
              unCheckedChildren='Number of Reps'
              checked={timeUnderTension}
              onChange={setTimeUnderTension}
            />
            {timeUnderTension ? (
              <div>
                <Form.ControlLabel>Duration: </Form.ControlLabel>
                <InputNumber step={1} />
              </div>
            ) : (
              <div>
                <Form.ControlLabel>Reps: </Form.ControlLabel>
                <InputNumber step={1} />
                <Form.ControlLabel>Rep Cadence: </Form.ControlLabel>
                <InputGroup size='md' style={{ display: "flex" }}>
                  <InputGroup.Addon>UP</InputGroup.Addon>
                  <InputNumber />
                  <InputGroup.Addon>Top</InputGroup.Addon>
                  <InputNumber />
                  <InputGroup.Addon>DOWN</InputGroup.Addon>
                  <InputNumber />
                  <InputGroup.Addon>Bottom</InputGroup.Addon>
                  <InputNumber />
                </InputGroup>
              </div>
            )}
          </Form.Group>
          <Form.ControlLabel>Sets: </Form.ControlLabel>
          <InputNumber step={1} />
        </Form.Group>
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

            /* onChangeCommitted={(value) => updateInputInProgress(["rpe", value])} */
          />
        </Form.Group>
        <br />
        <Form.Group controlId='load'>
          <Form.ControlLabel>External Load (optional):</Form.ControlLabel>
          <InputNumber postfix='lbs' />
        </Form.Group>
        <Form.Group>
          <ButtonToolbar>
            <Button appearance='primary'>Add to Workout</Button>
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
