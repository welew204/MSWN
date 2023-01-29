import React, { useState, useEffect } from "react";
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
  DatePicker,
} from "rsuite";
import CogIcon from "@rsuite/icons/legacy/Cog";
import { useQuery, useMutation } from "@tanstack/react-query";
import { NavToggle } from "./helpers/NavToggle";
import InputForm from "./helpers/InputForm";
import RecordWkoutForm from "./helpers/RecordWkoutForm";

const server_url = "http://127.0.0.1:8000";

export default function RecordWkout() {
  const [selectedWorkout, setSelectedWorkout, activeMover] = useOutletContext();
  const [selectInp, setSelectInp] = useState("");
  const [workoutResults, setWorkoutResults] = useState({});

  const workoutsQuery = useQuery(["workouts"], () => {
    return fetchAPI(server_url + `/workouts/${activeMover}`);
  });
  /*   setWorkoutResults(workoutsQuery.data
   */
  function updateWorkoutResults(inputId, UpdValue) {
    setWorkoutResults((prev) => ({ ...prev, [inputId]: UpdValue }));
  }

  /* //TODO... need to make this go the right end-point */
  const updateDB = useMutation({
    mutationFn: (newMover) => {
      fetch(server_url + "/record_workout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify([workoutResults]),
        mode: "cors",
      }).then((res) => console.log(res));
    },
  });

  /* need to use workoutsQuery to set workoutResults right away,
    then make function to update these results,
    then pass that function to Child RecordWorkoutForm, 
    then use that prop on 'Save Input' click;
    then submit form (useMutation) to DB,
    DB has to parse all the inputs into Bouts!
    */

  function fetchAPI(url) {
    return fetch(url).then((res) => res.json());
  }

  const boutLogData = useQuery(["boutLog"], () =>
    fetchAPI(server_url + `/bout_log/${activeMover}`)
  );
  if (boutLogData.isLoading) {
    return <p>Getting your bout data...</p>;
  }

  if (workoutsQuery.isLoading) return "Loading...";
  if (workoutsQuery.isError) return `Error: error`;

  const workouts = workoutsQuery.data;

  /* HACK: the DEFAULT TITLE behavior here is handled locally,, but needs to get handled higher up */
  const wkoutSelect = workouts.map((wkt) => {
    var wkt_label = "";
    wkt.workout_title
      ? (wkt_label = wkt.workout_title)
      : (wkt_label = `${wkt.date_init} Workout`);
    return { label: wkt_label, value: wkt.id };
  });

  const index_of_selectedWorkout = () => {
    const selWktIndex = workouts.indexOf(
      workouts.find((wkt) => wkt.id == selectedWorkout)
    );
    return selWktIndex;
  };

  const inputs = workouts[index_of_selectedWorkout()]?.inputs.map((inp) => (
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

  if (Object.keys(workoutResults).length == 0) {
    const selWkt = findWorkout(selectedWorkout);
    for (let w in Object.keys(selWkt.inputs)) {
      updateWorkoutResults(selWkt.inputs[w].id, {
        Rx: { ...selWkt.inputs[w] },
        results: {
          rails: false,
          passive_duration: 0,
          duration: 0,
          rpe: 0,
          external_load: 0,
        },
      });
      /* NEXT: ALSO a seperate results object that will get the recorded stuff, that is then grabbed to send to server!
      Then, clean up the earlier version, get the end-point delivering!
      then, write the parser in python :)
      then, build the workoutbuilder */
    }
  }
  console.log(workoutResults);

  const bout_array = boutLogData.data["bout_log"];
  const bouts = bout_array.map((bout, i) => {
    return (
      <Timeline.Item key={`bout_${bout_array[i].id}`} time={bout_array[i].date}>
        {bout_array[i].comments}, RPE: {bout_array[i].rpe}, External Load:{" "}
        {bout_array[i].external_load}
      </Timeline.Item>
    );
  });
  /* console.log(bouts.len()); */

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
            <Divider />
            <DatePicker
              onChange={(value) => updateWorkoutResults("date", value)}
              format='yyyy-MM-dd HH:mm'
              placeholder={"Select Date"}
            />
          </Stack.Item>
          <Divider vertical style={{ height: "70vh" }} />

          <Stack.Item style={{ width: "100%", padding: 10 }}>
            <RecordWkoutForm
              key={selectInp}
              selectedInput={
                selectInp
                  ? findWorkout(selectedWorkout)?.inputs.find(
                      (inp) => inp.id == selectInp
                    )
                  : ""
              }
              workoutResults={workoutResults}
              updateWorkoutResults={updateWorkoutResults}
              updateDB={(event) => {
                event.preventDefault();
                updateDB.mutate();
              }}
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
          <Button
            as={RsNavLink}
            href='/mover'
            onClickCapture={() => updateDB.mutate()}>
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
          {bouts.len != 0 ? (
            bouts
          ) : (
            <Timeline.Item>**No Bouts Yet!**</Timeline.Item>
          )}
        </Timeline>
      </Stack.Item>
    </Stack>
  );
}
