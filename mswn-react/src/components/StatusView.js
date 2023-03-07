import React, { useState } from "react";
import { NavLink, Link, useOutletContext } from "react-router-dom";
import { RsNavLink } from "./helpers/RsNavLink";
import {
  Container,
  Header,
  Content,
  Footer,
  Sidebar,
  Navbar,
  Nav,
  Sidenav,
  SidenavBody,
  Button,
  Timeline,
  Stack,
  Panel,
  Divider,
  Whisper,
} from "rsuite";
import CogIcon from "@rsuite/icons/legacy/Cog";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { NavToggle } from "./helpers/NavToggle";
import { HumanMap, DrawBouts } from "./helpers/eval_viz_d3";

const server_url = "http://127.0.0.1:8000";

export default function StatusView() {
  return (
    <div>
      <Stack
        style={{
          display: "flex",
          flexDirection: "column",
          marginTop: "20px",
          marginBottom: "20px",
          alignContent: "center",
        }}>
        <Stack.Item>
          <Panel
            header='What Am I Looking At...?'
            collapsible
            bordered
            style={{ width: "400px" }}>
            <p>
              What you see here are all the 'bouts' that this client has
              experienced via your training inputs.
            </p>
          </Panel>
        </Stack.Item>
        <Stack.Item>
          <HumanMap />
        </Stack.Item>
      </Stack>
    </div>
  );
}
