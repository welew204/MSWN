import React, { useState, useEffect } from "react";
import { NavLink, Link, useOutletContext } from "react-router-dom";
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
  Whisper,
  Tooltip,
  Loader,
} from "rsuite";
import CogIcon from "@rsuite/icons/legacy/Cog";
import { useQuery, useMutation } from "@tanstack/react-query";
import { NavToggle } from "./helpers/NavToggle";
import InputForm from "./helpers/InputForm";
import WktTitle from "./helpers/WktTitle";

const server_url = "http://127.0.0.1:8000";

export default function WkoutBuilder() {
  const default_new_input = {
    ref_joint_id: "",
    ref_joint_name: "",
    id: "1",
    ref_zones_id_a: "",
    ref_zones_id_b: "",
    fixed_side_anchor_id: "",
    rotational_value: "",
    start_coord: "",
    end_coord: "",
    drill_name: "",
    duration: "",
    passive_duration: "",
    rpe: "",
    external_load: "",
    ref_joint_side: "",
  };

  const [selectedWorkout, setSelectedWorkout, activeMover] = useOutletContext();
  const [wktInProgress, setWktInProgress] = useState({
    id: "",
    workout_title: "",
    date_init: "",
    moverid: activeMover,
    comments: "",
    inputs: {
      1: default_new_input,
    },
    schema: { A: { circuit: ["1"], iterations: 1 } },
  });
  /* console.log(wktInProgress); */

  const [selectedInput, setSelectedInput] = useState(1);
  /* console.log("SELECTED INPUT: " + selectedInput); */

  useEffect(() => {
    setWktInProgress((prev) => {
      const date = new Date().toJSON();
      return { ...prev, date_init: date.slice(0, 10) };
    });
  }, []);

  const updateDB = useMutation({
    mutationFn: () => {
      fetch(server_url + "/write_workout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify([wktInProgress]),
        mode: "cors",
      }).then((res) => console.log(res));
    },
  });

  const workoutsQuery = useQuery(["workouts"], () => {
    return fetchAPI(server_url + `/workouts/${activeMover}`);
  });

  const boutLogData = useQuery(["boutLog"], () =>
    fetchAPI(server_url + `/bout_log/${activeMover}`)
  );

  if (workoutsQuery.isLoading) return "Loading...";
  if (workoutsQuery.isError) return `Error: error`;
  if (boutLogData.isLoading) {
    return <p>Getting your bout data...</p>;
  }

  const bout_array = boutLogData.data["bout_log"];
  const bouts = bout_array.map((bout, i) => {
    return (
      <Timeline.Item key={`bout_${bout_array[i].id}`} time={bout_array[i].date}>
        {bout_array[i].comments}, RPE: {bout_array[i].rpe}, External Load:{" "}
        {bout_array[i].external_load}
      </Timeline.Item>
    );
  });

  function fetchAPI(url) {
    return fetch(url).then((res) => res.json());
  }
  function updateWkt(field, UpdValue) {
    setWktInProgress((prev) => ({ ...prev, [field]: UpdValue }));
  }

  const rx_inputs = Object.keys(wktInProgress.inputs).map((inp) => (
    <Panel
      key={wktInProgress.inputs[inp].id}
      onClick={() => setSelectedInput(wktInProgress.inputs[inp].id)}
      shaded
      className={
        selectedInput == wktInProgress.inputs[inp].id
          ? "selected-inp-plaque"
          : "inp-plaque"
      }
      style={{ display: "flex", justifyContent: "center" }}
      bordered
      header={
        wktInProgress.inputs[inp].ref_joint_id &&
        wktInProgress.inputs[inp].drill_name ? (
          `${wktInProgress.inputs[inp].ref_joint_side} ${wktInProgress.inputs[inp].ref_joint_name} ${wktInProgress.inputs[inp].drill_name}`
        ) : (
          <Loader vertical speed='slow' size='md'></Loader>
        )
      }>
      {wktInProgress.inputs[inp].completed
        ? `RPE: ${wktInProgress.inputs[inp].rpe}/10, Duration: ${wktInProgress.inputs[inp].duration} secs`
        : "Building workout..."}
    </Panel>
  ));

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
          <h1>Build A Workout</h1>
        </Stack.Item>
        <Divider />
        <Stack.Item style={{ display: "flex", justifyContent: "space-evenly" }}>
          <Stack.Item
            className='THIS ONE'
            style={{ width: "100%", padding: 10 }}>
            <h3 style={{ display: "flex", justifyContent: "space-around" }}>
              Define an Input...
            </h3>
            <Divider />
            <InputForm
              key={`${selectedInput}`}
              updateDB={updateDB}
              setSelectedInput={setSelectedInput}
              default_new_input={default_new_input}
              setWktInProgress={setWktInProgress}
              wktInProgress={wktInProgress}
              updateWkt={updateWkt}
              selectedInput={selectedInput}
            />
          </Stack.Item>
          <Divider vertical style={{ height: "60vh", alignSelf: "center" }} />
          <Stack.Item
            style={{
              display: "flex",
              flexDirection: "column",
              alignContent: "stretch",
              minWidth: 200,
              width: "100%",
              gap: 10,
            }}
            className='workoutSchema'>
            <WktTitle
              title={wktInProgress.workout_title}
              onChange={updateWkt}
            />
            {rx_inputs}
          </Stack.Item>
        </Stack.Item>
        <Stack.Item
          style={{
            display: "flex",
            padding: 10,
            justifyContent: "center",
            gap: 20,
          }}>
          <Button as={RsNavLink} href='/mover' onClick={updateDB.mutate}>
            Save Workout
          </Button>
          <Button as={RsNavLink} href='/wbuilder'>
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
        }}>
        <Timeline endless>{bouts}</Timeline>
      </Stack.Item>
    </Stack>
  );
}
