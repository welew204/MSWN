import React, { useEffect, useState } from "react";
import { NavLink, Link, Outlet, Navigate } from "react-router-dom";
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
  Loader,
} from "rsuite";
import CogIcon from "@rsuite/icons/legacy/Cog";
import { useQuery, useMutation } from "@tanstack/react-query";
import { NavToggle } from "./helpers/NavToggle";
import AddMoverModal from "./AddMoverModal";
import { useAuth } from "./hooks/useAuth";

const server_url = "http://127.0.0.1:8000";

export default function Home() {
  const { user, logout } = useAuth();

  const [activeMover, setActiveMover] = useState(0);
  const [selectedWorkout, setSelectedWorkout] = useState("");
  const [addMoverOpen, setAddMoverOpen] = useState(false);

  const workoutsQuery = useQuery({
    queryKey: ["workouts", activeMover],
    queryFn: () => fetchAPI(server_url + `/workouts/${activeMover}`),
  });

  function fetchAPI(url) {
    return fetch(url).then((res) => {
      return res.json();
    });
  }
  const movers = useQuery({
    queryKey: ["movers", user.coach],
    queryFn: () => fetchAPI(`${server_url}/movers_list/${user.coach}`),
  });

  // this feels HACKY and not neccesary
  useEffect(() => {
    fetchAPI(`${server_url}/movers_list/${user.coach}`).then((data) => {
      const arbMoverId = Object.values(data).at(0)[0];
      setActiveMover(arbMoverId);
    });
  }, [user]);

  /* HACK: this useEffect feels hacky a bit, in that the original item returned gets a 404
  (before the activeMover is set) */
  useEffect(() => {
    fetchAPI(`${server_url}/workouts/${activeMover}`)
      .then((data) => (data != [] ? setSelectedWorkout(data[0]?.id) : void 0))
      .then(console.log(`Got the workouts for mover_id: ${activeMover}`));
  }, [activeMover]);

  if (!user) {
    return <Navigate to='/coaches' />;
  }
  if (movers.isLoading) return "Loading...";
  if (movers.isError) return `Error: error`;
  if (workoutsQuery.isLoading) return "Loading...";
  if (workoutsQuery.isError) return `Error: error`;

  var incoming_movers = [];

  for (var key in movers.data) {
    incoming_movers.push(movers.data[key]);
  }

  const movers_list = incoming_movers.map((mvr) => (
    <Nav.Item
      key={mvr[0]}
      eventKey={`${mvr[0]}`}>{`${mvr[1]} ${mvr[2]}`}</Nav.Item>
  ));

  /* console.log(movers.data); */

  return (
    <Container className='home-frame'>
      <Header>
        <Navbar style={{ fontSize: "20px" }}>
          <Nav>
            <Nav.Item
              as={RsNavLink}
              href='/dashboard/mover'
              style={{ color: "#13B532" }}>
              MSWN
            </Nav.Item>
            <Nav.Item as={RsNavLink} href='/dashboard/mover'>
              Move
            </Nav.Item>
            <Nav.Item as={RsNavLink} href='/dashboard/status'>
              Status
            </Nav.Item>
            {/* <Nav.Item>Assess</Nav.Item> */}
          </Nav>

          <Nav pullRight style={{ marginRight: "30px" }}>
            <Nav.Item as={RsNavLink} href='/coaches' onClick={logout}>
              Logout
            </Nav.Item>
          </Nav>
        </Navbar>
      </Header>
      <Container className='homescreen-mid'>
        <AddMoverModal
          open={addMoverOpen}
          close={setAddMoverOpen}
          coach_id={user.coach}
        />
        <Sidebar
          style={{ overflow: "auto", marginRight: "10px" }}
          className='sidebar'>
          <Sidenav
            style={{ overflow: "auto" }}
            expanded={true}
            appearance='subtle'>
            <Sidenav.Body>
              <Nav
                activeKey={
                  activeMover
                    ? `${activeMover}`
                    : `${Object.keys(movers.data).at(0)[0]}`
                }
                onSelect={(e) => {
                  setActiveMover(e);
                }}>
                {movers_list}
              </Nav>
            </Sidenav.Body>
            <Button onClick={setAddMoverOpen}>Add Mover</Button>
          </Sidenav>
        </Sidebar>
        <Content className='content' style={{ margin: "15px" }}>
          <Outlet
            context={[selectedWorkout, setSelectedWorkout, activeMover]}
          />

          {/* one of MoverSelect, WorkoutBuilder, RecordWorkout */}
        </Content>
      </Container>
      <Footer
        style={{
          display: "flex",
          justifyContent: "center",
          paddingTop: "20px",
        }}>
        TM Controlled Fall Engineering
      </Footer>
    </Container>
  );
}
