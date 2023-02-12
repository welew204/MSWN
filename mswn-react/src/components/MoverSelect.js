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
import WorkoutBadge from "./helpers/WorkoutBadge";

const server_url = "http://127.0.0.1:8000";

export default function MoverSelect(props) {
  function fetchAPI(url) {
    return fetch(url).then((res) => {
      return res.json();
    });
  }
  const queryClient = useQueryClient();

  const [selectedWorkout, setSelectedWorkout, activeMover] = useOutletContext();

  const workoutsQuery = useQuery(["workouts", activeMover], () => {
    return fetchAPI(server_url + `/workouts/${activeMover}`);
  });
  const handleDelete = useMutation({
    mutationFn: (wktID) => {
      fetch(server_url + "/delete_workout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify([activeMover, wktID]),
        mode: "cors",
      })
        .then((res) => console.log(res.json()))
        .then(setSelectedWorkout(workoutsQuery.data[0].id));
    },
    onSuccess: (data) => {
      queryClient.setQueryData(["workouts", [activeMover]], data);
    },
  });
  if (workoutsQuery.isLoading) return "Loading...";
  if (workoutsQuery.isFetching) return "Loading...";
  if (workoutsQuery.isError) return `Error: error`;

  const wkouts = workoutsQuery.data.map((wkt) => (
    <Stack.Item
      className={wkt.id == selectedWorkout ? "selected-workout" : ""}
      key={wkt.id}>
      <WorkoutBadge
        className={wkt.id == selectedWorkout ? "selected-workout" : ""}
        wkt={wkt}
        onClick={() => setSelectedWorkout(wkt.id)}
        onDelete={(wkt_to_delete) => handleDelete.mutate(wkt_to_delete)}
      />
    </Stack.Item>
  ));

  return (
    <Stack
      style={{ height: "100%", minHeight: "100%" }}
      justifyContent='space-around'>
      <Stack.Item style={{ height: "100%", minHeight: "100%", flexGrow: 1 }}>
        <Stack
          style={{ height: "100%", minHeight: "100%" }}
          spacing={50}
          direction='column'
          justifyContent='space-between'>
          <Header>
            <h1>Select A Workout</h1>
          </Header>
          <Stack wrap size='lg' spacing={20}>
            {wkouts}
          </Stack>
          <Stack spacing={20}>
            <Button as={RsNavLink} href='/wbuilder'>
              Build A Workout
            </Button>
            <Button as={RsNavLink} href='/record'>
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
        }}>
        <Timeline endless>
          <Timeline.Item>**last workout**</Timeline.Item>
          <Timeline.Item>**last workout**</Timeline.Item>
          <Timeline.Item>**last workout**</Timeline.Item>
        </Timeline>
      </Stack.Item>
    </Stack>
  );
}
