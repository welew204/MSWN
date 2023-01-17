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
  Button,
  Nav,
  Sidenav,
  SidenavBody,
  Stack,
  Timeline,
  Divider,
  Panel,
  SelectPicker,
  Loader,
} from "rsuite";
import CogIcon from "@rsuite/icons/legacy/Cog";
import { useQuery, useMutation } from "@tanstack/react-query";
import { NavToggle } from "./helpers/NavToggle";
import InputForm from "./helpers/InputForm";
import RecordWkoutForm from "./helpers/RecordWkoutForm";

const server_url = "http://127.0.0.1:8000";

export default function RecordWkout() {
  const [selectedWorkout, setSelectedWorkout] = useOutletContext();
  const [selectInp, setSelectInp] = useState("");

  function fetchAPI(url) {
    return fetch(url).then((res) => res.json());
  }

  const workoutsQuery = useQuery(["workouts"], () => {
    return fetchAPI(server_url + "/workouts");
  });
  if (workoutsQuery.isLoading) return "Loading...";
  if (workoutsQuery.isError) return `Error: error`;

  const workouts = workoutsQuery.data;

  const wkoutSelect = workouts.map((wkt) => {
    return { label: wkt.workout_title, value: wkt.id };
  });

  const index_of_selectedWorkout = () => {
    const selWktIndex = workouts.indexOf(
      workouts.find((wkt) => wkt.id == selectedWorkout)
    );
    return selWktIndex;
  };
  /* need INPUTS to dynamically update even BEFORE selectedWorkout is set; right now I'm just drawing the '0'-th workout!! */

  const inputs = workouts[index_of_selectedWorkout()].inputs.map((inp) => (
    <Panel
      key={inp.id}
      onClick={() => setSelectInp(inp.id)}
      shaded
      className={selectInp == inp.id ? "selected-inp-plaque" : "inp-plaque"}
      bordered
      header={`${inp.ref_joint_name} ${inp.drill_name}`}></Panel>
  ));

  function findWorkout(wktid) {
    const selWkt = workouts.find((wkt) => wkt.id == wktid);
    return selWkt;
  }

  return (
    <Stack
      style={{ height: "100%", minHeight: "100%" }}
      justifyContent='space-around'
      alignItems='center'>
      <Stack.Item
        style={{
          height: "100%",
          minHeight: "100%",
          flexGrow: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: "stretch",
          justifyContent: "space-between",
        }}>
        <Stack.Item style={{ display: "flex", justifyContent: "space-around" }}>
          <h1>Record A Workout</h1>
        </Stack.Item>
        <Stack.Item>
          <SelectPicker
            style={{ display: "flex", margin: 10, alignSelf: "center" }}
            onSelect={(v, i, e) => {
              setSelectedWorkout(v);
            }}
            data={wkoutSelect}
            defaultValue={
              selectedWorkout ? selectedWorkout : ""
            }></SelectPicker>
        </Stack.Item>
        <Stack.Item
          style={{
            display: "flex",
            justifyContent: "space-evenly",
            alignItems: "stretch",
          }}>
          <Stack.Item
            style={{
              display: "flex",
              flexDirection: "column",
              alignContent: "stretch",
              minWidth: 200,
              width: "100%",
              gap: 10,
              padding: 10,
            }}
            className='workoutSchema'>
            {workoutsQuery.isSuccess ? inputs : <Loader size='lg' />}
          </Stack.Item>
          <Divider vertical style={{ height: "70vh" }} />

          <Stack.Item style={{ width: "100%", padding: 10 }}>
            <RecordWkoutForm
              selectedInput={
                selectInp
                  ? findWorkout(selectedWorkout).inputs.find(
                      (inp) => inp.id == selectInp
                    )
                  : ""
              }
            />
          </Stack.Item>
        </Stack.Item>
        <Stack.Item
          style={{
            display: "flex",
            padding: 10,
            justifyContent: "center",
            gap: 20,
          }}>
          <Button as={RsNavLink} href='/mover'>
            Record Workout
          </Button>
          <Button as={RsNavLink} href='/record'>
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
