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
  Button,
  Nav,
  Sidenav,
  SidenavBody,
  Stack,
  Timeline,
  Divider,
  Panel,
  SelectPicker,
} from "rsuite";
import CogIcon from "@rsuite/icons/legacy/Cog";
import { useQuery, useMutation } from "@tanstack/react-query";
import { NavToggle } from "./helpers/NavToggle";
import InputForm from "./helpers/InputForm";

const server_url = "http://127.0.0.1:8000";

export default function RecordWkout() {
  return (
    <Stack
      style={{ height: "100%", minHeight: "100%" }}
      justifyContent="space-around"
      alignItems="center"
    >
      <Stack.Item
        style={{
          height: "100%",
          minHeight: "100%",
          flexGrow: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "stretch",
          justifyContent: "space-between",
        }}
      >
        <Stack.Item style={{ display: "flex", justifyContent: "space-around" }}>
          <h1>Record A Workout</h1>
        </Stack.Item>
        <Stack.Item>
          <SelectPicker
            style={{ display: "flex", margin: 10, alignSelf: "center" }}
            data={[
              { label: "Buns 'n Guns", value: "Buns 'n Guns" },
              { label: "GH Capsule-itis", value: "GH Capsule-itis" },
              {
                label: "Operation: Booty Call",
                value: "Operation: Booty Call",
              },
            ]}
          ></SelectPicker>
        </Stack.Item>
        <Stack.Item
          style={{
            display: "flex",
            justifyContent: "space-evenly",
            alignItems: "stretch",
          }}
        >
          <Stack.Item
            style={{
              display: "flex",
              flexDirection: "column",
              alignContent: "stretch",
              minWidth: 200,
              width: "100%",
              gap: 10,
            }}
            className="workoutSchema"
          >
            <Panel className="inp-plaque" bordered header="--Input--"></Panel>
            <Panel className="inp-plaque" bordered header="--Input--"></Panel>
            <Panel className="inp-plaque" bordered header="--Input--"></Panel>
          </Stack.Item>
          <Divider vertical style={{ height: "60vh" }} />
          <Stack.Item
            className="THIS ONE"
            style={{ width: "100%", padding: 10 }}
          >
            <InputForm />
          </Stack.Item>
        </Stack.Item>
        <Stack.Item
          style={{
            display: "flex",
            padding: 10,
            justifyContent: "center",
            gap: 20,
          }}
        >
          <Button as={RsNavLink} href="/mover">
            Record Workout
          </Button>
          <Button as={RsNavLink} href="/record">
            Pause Workout
          </Button>
        </Stack.Item>
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
