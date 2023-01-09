import React, { useState } from "react";
import { NavLink, Link } from "react-router-dom";
import { RsNavLink } from "./helpers/RsNavLink";
import {
  Container,
  Header,
  Content,
  Footer,
  Sidebar,
  Button,
  Navbar,
  Nav,
  Sidenav,
  SidenavBody,
  Timeline,
  Stack,
  Panel,
  Divider,
  Form,
  ButtonToolbar,
} from "rsuite";
import CogIcon from "@rsuite/icons/legacy/Cog";
import { useQuery, useMutation } from "@tanstack/react-query";
import { NavToggle } from "./helpers/NavToggle";

const server_url = "http://127.0.0.1:8000";

export default function WkoutBuilder() {
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
          <h1>Build A Workout</h1>
        </Stack.Item>
        <Stack.Item
          className="THIS ONE"
          style={{ display: "flex", justifyContent: "space-evenly" }}
        >
          <Stack.Item style={{ width: "100%" }}>
            <Form>
              <Form.Group controlId="name">
                <Form.ControlLabel>Username</Form.ControlLabel>
                <Form.Control name="name" />
                <Form.HelpText>Username is required</Form.HelpText>
              </Form.Group>
              <Form.Group controlId="email">
                <Form.ControlLabel>Email</Form.ControlLabel>
                <Form.Control name="email" type="email" />
                <Form.HelpText tooltip>Email is required</Form.HelpText>
              </Form.Group>
              <Form.Group controlId="password">
                <Form.ControlLabel>Password</Form.ControlLabel>
                <Form.Control
                  name="password"
                  type="password"
                  autoComplete="off"
                />
              </Form.Group>
              <Form.Group controlId="textarea">
                <Form.ControlLabel>Textarea</Form.ControlLabel>
                <Form.Control rows={5} name="textarea" />
              </Form.Group>
              <Form.Group>
                <ButtonToolbar>
                  <Button appearance="primary">Submit</Button>
                  <Button appearance="default">Cancel</Button>
                </ButtonToolbar>
              </Form.Group>
            </Form>
          </Stack.Item>
          <Divider vertical style={{ height: "60vh" }} />
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
        </Stack.Item>
        <Stack.Item
          style={{
            display: "flex",
            padding: 10,
            justifyContent: "center",
            gap: 20,
          }}
        >
          <Button as={RsNavLink} href="/wbuilder">
            Save Workout
          </Button>
          <Button as={RsNavLink} href="/record">
            Save Workout Draft
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
