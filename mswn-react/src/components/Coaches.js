import React, { useEffect, useState } from "react";
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
  Loader,
  Panel,
  List,
} from "rsuite";
import { useQuery, useMutation } from "@tanstack/react-query";
import CoachLoginModal from "./helpers/CoachLoginModal";

export default function Coaches() {
  const [pwEnter, setPwEnter] = useState(false);
  const [coachSelected, setCoachSelected] = useState("");

  function handleCoachSelect(event) {
    const coach = event.target.innerText;
    setCoachSelected(coach);
    setPwEnter(true);
  }

  return (
    <div>
      <CoachLoginModal
        coachSelected={coachSelected}
        open={pwEnter}
        close={setPwEnter}
      />
      <Panel
        style={{
          marginLeft: "auto",
          marginRight: "auto",
          marginTop: "15vh",
          width: "500px",
        }}
        header='Coaches'
        shaded
        bordered
        bodyFill>
        <List style={{ margin: "15px", width: "100%" }} hover bordered>
          <List.Item onClick={handleCoachSelect}>Will Belew</List.Item>
          <List.Item onClick={handleCoachSelect}>Marlie Couto</List.Item>
          <List.Item onClick={handleCoachSelect}>Dewey Nielsen</List.Item>
          <List.Item onClick={handleCoachSelect}>Guest</List.Item>
        </List>
      </Panel>
    </div>
  );
}
