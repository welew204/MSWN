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
  Button,
} from "rsuite";
import CogIcon from "@rsuite/icons/legacy/Cog";
import { useQuery, useMutation } from "@tanstack/react-query";
import { NavToggle } from "./helpers/NavToggle";
import AddMoverModal from "./AddMoverModal";

const server_url = "http://127.0.0.1:8000";

export default function Home() {
  function fetchAPI(url) {
    return fetch(url).then((res) => {
      return res.json();
    });
  }

  const [activeMover, setActiveMover] = useState("");
  const [addMoverOpen, setAddMoverOpen] = useState(false);

  /* query: SELECT movers */
  const movers = useQuery({
    queryKey: ["movers"],
    queryFn: () => fetchAPI(server_url + "/movers_list"),
  });

  if (movers.isLoading) return "Loading...";
  if (movers.isError) return `Error: error`;
  var incoming_movers = [];

  for (var key in movers.data) {
    incoming_movers.push(movers.data[key]);
  }

  const movers_list = incoming_movers.map((mvr) => (
    <Nav.Item
      key={mvr[0]}
      eventKey={`${mvr[0]}`}
    >{`${mvr[1]} ${mvr[2]}`}</Nav.Item>
  ));

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
      <Container className="homescreen-mid" style={{ height: "90vh" }}>
        <AddMoverModal open={addMoverOpen} close={setAddMoverOpen} />
        <Sidebar style={{ overflow: "auto" }} className="sidebar" collapsible>
          <Sidenav
            style={{ overflow: "auto" }}
            expanded={true}
            appearance="subtle"
          >
            <Sidenav.Body>
              <Nav activeKey={activeMover} onSelect={setActiveMover}>
                {movers_list}
              </Nav>
            </Sidenav.Body>
            <Button onClick={setAddMoverOpen}>Add Mover</Button>
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
