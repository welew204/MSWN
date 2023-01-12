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
} from "rsuite";
import { useQuery, useMutation } from "@tanstack/react-query";
import { find } from "rsuite/esm/utils/ReactChildren";

const server_url = "http://127.0.0.1:8000";

export default function RecordWkoutForm() {
  /* query callback fnc */
  function fetchAPI(url) {
    return fetch(url).then((res) => {
      return res.json();
    });
  }

  /* useQuery's */

  const boutLogData = useQuery(["boutLog"], () =>
    fetchAPI(server_url + "/bout_log/1")
  );

  /* console.log(jointRefData.isLoading ? "" : jointRefData.data) */

  /* state for form components */
  const [drillDate, setDrillDate] = useState("");

  const [jointID, setJointID] = useState(0);
  const [zoneID, setZoneID] = useState(0);
  /* console.log("jointId in state: "+ jointID)
    console.log("zoneId in state: "+ zoneID) */

  const [selectedDrill, setSelectedDrill] = useState("CARs");
  const [selectedPosition, setSelectedPosition] = useState(0);
  const [selectedRotation, setSelectedRotation] = useState(-100);
  const [railsSelected, setRailsSelected] = useState(false);
  const [drillDuration, setDrillDuration] = useState(30);
  const [passiveDuration, setPassiveDuration] = useState(0);
  const [drillRPE, setDrillRPE] = useState(5);
  const [drillLoad, setDrillLoad] = useState(0);

  if (boutLogData.isLoading) {
    return <p>Getting your bout data...</p>;
  }

  /* console.log(jointRefData.data) */

  /* this function logs the ref_joint or ref_zone id into state, so that can be sent off with 'submit_form' */
  function find_tissue(item) {
    const id = item.id;
    if (item.children) {
      setJointID(id);
    } else {
      setZoneID(id);
    }
  }

  function submit_form() {
    console.log(
      jointID,
      zoneID,
      selectedDrill,
      drillDate,
      drillDuration,
      drillLoad,
      drillRPE
    );
  }

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

  return (
    <div className="inp-form">
      <Form>
        {true == true ? (
          <Form.Group controlId="rails">
            <Form.ControlLabel>RAILs tissue trained...?</Form.ControlLabel>
            <Toggle
              onChange={() => setRailsSelected((prev) => !prev)}
              value={railsSelected}
            />
          </Form.Group>
        ) : (
          ""
        )}
        <br />
        {true == true ? (
          <div>
            <Form.Group controlId="rails">
              <Form.ControlLabel>
                Duration of passive stretch:
              </Form.ControlLabel>
              <InputNumber
                onChange={setPassiveDuration}
                value={passiveDuration}
                postfix="seconds"
              />
            </Form.Group>
            <br />
          </div>
        ) : (
          ""
        )}
        <Form.Group controlId="duration">
          <Form.ControlLabel>Duration of effort:</Form.ControlLabel>
          <InputNumber
            value={drillDuration}
            postfix="seconds"
            onChange={setDrillDuration}
          />
        </Form.Group>
        <br />
        <Form.Group controlId="rpe">
          <Form.ControlLabel>
            Rate of Percieved Exertion (RPE):
          </Form.ControlLabel>
          <Slider
            value={drillRPE}
            min={0}
            step={1}
            max={10}
            graduated
            progress
            onChangeCommitted={setDrillRPE}
            renderMark={(mark) => {
              return mark;
            }}
            style={{ width: 300 }}
          />
        </Form.Group>
        <br />
        <Form.Group controlId="load">
          <Form.ControlLabel>External Load (optional):</Form.ControlLabel>
          <InputNumber
            value={drillLoad}
            postfix="lbs"
            onChange={setDrillLoad}
          />
        </Form.Group>
        <Form.Group>
          <ButtonToolbar>
            <Button appearance="primary" onClick={submit_form}>
              Submit
            </Button>
            <Button appearance="default">Cancel</Button>
          </ButtonToolbar>
        </Form.Group>
      </Form>
      <div>
        <Timeline endless>{bouts}</Timeline>
      </div>
    </div>
  );
}
