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
  Panel,
  Stack,
  ButtonGroup,
} from "rsuite";
import { useQuery, useMutation } from "@tanstack/react-query";
import { RsNavLink } from "./RsNavLink";

const server_url = "http://127.0.0.1:8000";

export default function WorkoutBadge({ wkt, onClick, className }) {
  const inputs = wkt.inputs.map((inp) => {
    return (
      <li key={inp.id}>
        <Stack direction='column' alignItems='stretch'>
          <span style={{ fontWeight: "bold" }}>
            {`${inp.ref_joint_name} ${inp.drill_name}`}
          </span>
          <span>
            {`RPE: ${inp.rpe} Total Duration: ${
              parseInt(inp.passive_duration) + parseInt(inp.duration)
            }sec`}
          </span>
        </Stack>
      </li>
    );
  });

  return (
    <Panel
      className={className}
      shaded
      bordered
      style={{ minWidth: 250 }}
      onClick={() => onClick(wkt.id)}
      header={
        <Stack justifyContent='center'>
          <span>{wkt.workout_title}</span>
        </Stack>
      }>
      <Stack direction='column' alignItems='stretch'>
        <h6>Last done: {wkt.last_done}</h6>
        <Panel header='View All Inputs' collapsible bordered>
          <ul>{inputs}</ul>
        </Panel>
      </Stack>
    </Panel>
  );
}
