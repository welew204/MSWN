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
  IconButton,
} from "rsuite";
import TrashIcon from "@rsuite/icons/Trash";
import { useOutletContext } from "react-router-dom";
import { useQuery, useMutation } from "@tanstack/react-query";
import { RsNavLink } from "./RsNavLink";

const server_url = "http://127.0.0.1:8000";

export default function WorkoutBadge({ wkt, onClick, className, onDelete }) {
  const inputs = wkt.inputs.map((inp) => {
    return (
      <li key={inp.id}>
        <Stack direction='column' alignItems='stretch'>
          <span style={{ fontWeight: "bold" }}>
            {`${inp.ref_joint_name} ${inp.drill_name}`}
          </span>
          <span>
            {`RPE: ${inp.rpe} Total Duration: ${
              parseInt(inp.passive_duration ? inp.passive_duration : 0) +
              parseInt(inp.duration)
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
      style={{ display: "flex", flexDirection: "column", minWidth: 250 }}
      onClick={() => onClick(wkt.id)}
      header={
        <Stack justifyContent='center'>
          <span>{wkt.workout_title}</span>
        </Stack>
      }>
      <div
        style={{
          display: "flex",
          width: "100%",
          justifyContent: "space-around",
          alignItems: "center",
        }}>
        <Stack direction='column' alignItems='center'>
          {wkt.last_done ? (
            <h6
              style={
                {
                  /* margin: "5px" */
                }
              }>
              Last done: {wkt.last_done}
            </h6>
          ) : (
            <p style={{ fontStyle: "italic" }}>~Never done!~</p>
          )}
          <Panel header='View All Inputs' collapsible bordered>
            <ul>{inputs}</ul>
          </Panel>
        </Stack>
        <IconButton
          style={{ marginLeft: "auto" }}
          icon={<TrashIcon />}
          size='md'
          onClick={(e) => {
            e.stopPropagation();
            onDelete(wkt.id);
          }}
        />
      </div>
    </Panel>
  );
}
