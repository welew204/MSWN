import React, { useState } from "react";
import { NavLink, Link } from "react-router-dom";
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
} from "rsuite";
import CogIcon from "@rsuite/icons/legacy/Cog";
import { useQuery, useMutation } from "@tanstack/react-query";
import { NavToggle } from "./helpers/NavToggle";

const server_url = "http://127.0.0.1:8000";

export default function MoverSelect() {
  return (
    <Stack
      style={{ height: "100%", minHeight: "100%" }}
      justifyContent="space-around"
    >
      <Stack.Item style={{ height: "100%", minHeight: "100%", flexGrow: 1 }}>
        <Stack
          style={{ height: "100%", minHeight: "100%" }}
          spacing={50}
          direction="column"
          justifyContent="space-between"
        >
          <Header>
            <h1>Select A Workout</h1>
          </Header>
          <Stack wrap size="lg" spacing={20}>
            <Stack.Item>
              <Panel className="wkout-bdg" bordered header="Wkout Name"></Panel>
            </Stack.Item>
            <Stack.Item>
              <Panel className="wkout-bdg" bordered header="Wkout Name"></Panel>
            </Stack.Item>
            <Stack.Item>
              <Panel className="wkout-bdg" bordered header="Wkout Name"></Panel>
            </Stack.Item>
          </Stack>
          <Stack spacing={20}>
            <Button as={RsNavLink} href="/wbuilder">
              Build A Workout
            </Button>
            <Button as={RsNavLink} href="/record">
              Record A Workout
            </Button>
          </Stack>
        </Stack>
      </Stack.Item>
      <Divider vertical style={{ height: "70vh" }} />
      <Stack.Item
        style={{
          height: "100%",
          minHeight: "100%",
          alignSelf: "stretch",
          padding: 40,
        }}
      >
        <Timeline endless>
          <Timeline.Item>**last workout**</Timeline.Item>
          <Timeline.Item>**last workout**</Timeline.Item>
          <Timeline.Item>**last workout**</Timeline.Item>
        </Timeline>
      </Stack.Item>
    </Stack>
  );
}
