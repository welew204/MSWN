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
  PanelGroup,
  List,
  Slider,
  RangeSlider,
} from "rsuite";
import CogIcon from "@rsuite/icons/legacy/Cog";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { NavToggle } from "./helpers/NavToggle";
import { HumanMap, DrawBouts } from "./helpers/eval_viz_d3";

const server_url = "http://127.0.0.1:8000";

export default function StatusView() {
  return (
    <div style={{ display: "flex" }}>
      <Stack
        direction='row'
        alignItems='flex-start'
        justifyContent='flex-start'
        style={{
          marginTop: "20px",
          marginBottom: "20px",
        }}>
        <Stack.Item>
          <HumanMap />
        </Stack.Item>
        <Stack.Item style={{ display: "flex", margin: "20px", width: "100%" }}>
          <PanelGroup bordered style={{}}>
            <Panel
              eventKey={1}
              header='What Am I Looking At...?'
              collapsible
              bordered
              /* style={{ width: "400px" }} */
            >
              <p>
                What you see here are all the individual stressors ('bouts')
                that this client has experienced via training inputs.
              </p>
            </Panel>
            <Panel
              eventKey={2}
              defaultExpanded
              header='Legend'
              collapsible
              bordered>
              <List>
                <List.Item
                  style={{
                    display: "flex",
                    flexDirection: "row",
                  }}>
                  <div
                    style={{
                      margin: "5px",
                      width: "10px",
                      height: "10px",
                      display: "inline-block",
                      borderRadius: "50%",
                      backgroundColor: "#06bd00",
                      opacity: ".7",
                    }}
                  />
                  <p> = Linear Stressor</p>
                </List.Item>
                <List.Item style={{ display: "flex", flexDirection: "row" }}>
                  <div
                    style={{
                      margin: "5px",
                      width: "10px",
                      height: "10px",
                      display: "inline-block",
                      borderRadius: "50%",
                      backgroundColor: "#055403",
                      opacity: ".7",
                    }}
                  />
                  <p> = Rotational Stressor</p>
                </List.Item>
                <List.Item style={{ display: "flex", flexDirection: "row" }}>
                  <div
                    style={{
                      margin: "5px",
                      width: "10px",
                      height: "10px",
                      display: "inline-block",
                      borderRadius: "50%",
                      backgroundColor: "blue",
                      opacity: ".7",
                    }}
                  />
                  <p> = Capsular Stressor</p>
                </List.Item>
                <List.Item style={{ display: "flex", flexDirection: "row" }}>
                  <div
                    style={{
                      margin: "5px",
                      width: "20px",
                      height: "20px",
                      display: "inline-block",
                      borderRadius: "50%",
                      backgroundColor: "gray",
                      opacity: ".7",
                    }}
                  />
                  <p> → circle size proportional to RPE & Duration</p>
                </List.Item>
              </List>
            </Panel>
            <Panel
              eventKey={3}
              header='Date Filter (not completed)'
              collapsible
              bordered>
              <div style={{ display: "flex", width: "100%" }}>
                <RangeSlider
                  style={{ width: "90%" }}
                  defaultValue={[0, 12]}
                  max={12}
                  progress
                  graduated
                  step={1}
                />
              </div>
            </Panel>
          </PanelGroup>
        </Stack.Item>
      </Stack>
    </div>
  );
}
