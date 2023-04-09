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

const server_url = "http://127.0.0.1:8000";

export default function Coaches() {
  const [pwEnter, setPwEnter] = useState(false);
  const [coachSelected, setCoachSelected] = useState("");

  function fetchAPI(url) {
    return fetch(url).then((res) => {
      return res.json();
    });
  }
  const coaches = useQuery({
    queryKey: ["coaches"],
    queryFn: () => fetchAPI(server_url + "/coaches_list"),
  });

  if (coaches.isLoading) return "Loading...";
  if (coaches.isError) return "Error loading coaches!";

  let incoming_coaches = [];

  for (var key in coaches.data) {
    let coach_obj = coaches.data[key];
    coach_obj["coach_id"] = parseInt(key);
    incoming_coaches.push(coach_obj);
  }

  //console.log(incoming_coaches);

  const coach_list = incoming_coaches.map((coach_obj) => (
    <List.Item
      onClick={() => handleCoachSelect(coach_obj.coach_id)}
      key={coach_obj.coach_id}>
      {`${coach_obj.first_name} ${coach_obj.last_name}`}
    </List.Item>
  ));

  function handleCoachSelect(coachID) {
    console.log(coachID);
    setCoachSelected(coachID);
    setPwEnter(true);
  }

  return (
    <div>
      <CoachLoginModal
        coachSelected={coaches.data[coachSelected]}
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
          {coach_list}
        </List>
      </Panel>
    </div>
  );
}
