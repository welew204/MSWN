import React, { useState } from "react";
import { NavLink, Link, Outlet } from "react-router-dom";
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
} from "rsuite";
import CogIcon from "@rsuite/icons/legacy/Cog";
import { useQuery, useMutation } from "@tanstack/react-query";
import { NavToggle } from "./helpers/NavToggle";

const server_url = "http://127.0.0.1:8000";

export default function Home() {
  /* this needs to be linked up via the Routing functionality */
  const [currentView, setCurrentView] = useState("MoverSelect");
  const [expand, setExpand] = useState(true);

  /* query: SELECT movers */
  const incoming_movers = [
    "Marlie Couto",
    "Max Judelson",
    "Debbie Gold",
    "Julie Humphrey",
    "Rik Belew",
    "Nathy Kane",
  ];

  const movers = incoming_movers.map((id) => <Nav.Item>{id}</Nav.Item>);

  const a = 5;

  return (
    <Container className="home-frame">
      <Header>
        <Navbar>
          <Nav>
            <Nav.Item as={RsNavLink} href="/mover" style={{ color: "#13B532" }}>
              MSWN
            </Nav.Item>
            <Nav.Item as={RsNavLink} href="/mover">
              Move
            </Nav.Item>
            <Nav.Item>Status</Nav.Item>
            <Nav.Item>Assess</Nav.Item>
          </Nav>

          <Nav pullRight>
            <Nav.Item icon={<CogIcon />}>Settings</Nav.Item>
          </Nav>
        </Navbar>
      </Header>
      <Container className="homescreen-mid">
        <Sidebar
          className="sidebar"
          /* style={{ display: 'flex', flexDirection: 'column'}} */
          /* width={expand ? 260 :56} */
          collapsible
        >
          <Sidenav expanded={expand} appearance="subtle">
            <Sidenav.Body>
              <Nav>{movers}</Nav>
            </Sidenav.Body>
          </Sidenav>
        </Sidebar>
        <Content className="content">
          <Outlet />
          {/* one of MoverSelect, WorkoutBuilder, RecordWorkout */}
        </Content>
      </Container>

      <Footer>TM Controlled Fall Engineering</Footer>
    </Container>
  );
}
