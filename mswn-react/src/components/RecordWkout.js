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
  Toggle,
  Rate,
} from "rsuite";
import CogIcon from "@rsuite/icons/legacy/Cog";
import { useQuery, useMutation } from "@tanstack/react-query";
import InputForm from "./helpers/InputForm";
import RecordWkoutForm from "./helpers/RecordWkoutForm";
import CheckRoundIcon from "@rsuite/icons/CheckRound";

const server_url = "http://127.0.0.1:8000";

export default function RecordWkout() {
  const [selectedWorkout, setSelectedWorkout, activeMover] = useOutletContext();
  const [selectInp, setSelectInp] = useState("");
  const [workoutResults, setWorkoutResults] = useState({});
  const [doAsRxd, setDoAsRxd] = useState(false);
  console.log(selectInp);
  console.log(selectedWorkout);
  // need to build out this functionality ^^

  const workoutsQuery = useQuery(["workouts", activeMover], () => {
    return fetchAPI(server_url + `/workouts/${activeMover}`);
  });

  const doneWorkoutsQuery = useQuery(["doneWorkouts", activeMover], () => {
    return fetchAPI(server_url + `/training_log/${activeMover}`);
  });

  function updateWorkoutResults(inputId, UpdValue) {
    setWorkoutResults((prev) => ({ ...prev, [inputId]: UpdValue }));
  }

  const updateDB = useMutation({
    mutationFn: (target_input) => {
      const just_this_bout_object = {
        date_done: workoutResults.date_done,
        workout_id: workoutResults.workout_id,
        mover_id: workoutResults.mover_id,
        [target_input]: { ...workoutResults[target_input] },
      };
      return fetch(server_url + "/record_bout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(just_this_bout_object),
        mode: "cors",
      }).then((res) => console.log(res));
    },
  });

  const workout_confirmation = [
    workoutResults.date_done,
    workoutResults.workout_id,
    workoutResults.mover_id,
  ];

  const confirm_workout = useMutation({
    mutationFn: () => {
      return fetch(server_url + "/record_workout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(workout_confirmation),
        mode: "cors",
      }).then((res) => console.log(res));
    },
  });

  function fetchAPI(url) {
    return fetch(url).then((res) => res.json());
  }

  console.log("Workout Results...");
  console.log(workoutResults);

  useEffect(() => {
    if (workoutsQuery.isSuccess) {
      const tuhday = new Date().toISOString();
      clearWorkoutVals(tuhday);
    } else {
      void 0;
    }
  }, [selectedWorkout]);

  /* const boutLogData = useQuery(["boutLog"], () =>
    fetchAPI(server_url + `/bout_log/${activeMover}`)
  );
  if (boutLogData.isLoading) {
    return <p>Getting your bout data...</p>;
  } */

  if (workoutsQuery.isLoading) return "Loading...";
  if (workoutsQuery.isError) return `Error: error`;
  if (doneWorkoutsQuery.isLoading) return "Loading...";
  if (doneWorkoutsQuery.isError) return `Error: error`;

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
      onClick={() => setSelectInp(`${inp.id}`)}
      shaded
      className={selectInp == inp.id ? "selected-inp-plaque" : "inp-plaque"}
      bordered
      header={
        inp.multijoint == 1
          ? `${inp.drill_name}`
          : `${inp.side} ${inp.ref_joint_name} ${inp.drill_name}`
      }></Panel>
  ));

  function clearWorkoutVals(date) {
    const selWkt = findWorkout(selectedWorkout);
    let blankResults = {
      mover_id: activeMover,
      workout_id: selectedWorkout,
      date_done: date,
    };
    for (let w in [...selWkt.inputs.keys()]) {
      blankResults = {
        ...blankResults,
        [selWkt.inputs[w].id]: {
          Rx: { ...selWkt.inputs[w] },
          results: {
            rails: false,
            passive_duration: 0,
            duration: 0,
            rpe: 0,
            external_load: 0,
            reps_array: [0, 0, 1, 1, 1, 1],
          },
        },
      };
    }
    setWorkoutResults(blankResults);
  }

  function findWorkout(wktid) {
    const selWkt = workoutsQuery.data.find((wkt) => wkt.id == wktid);
    console.log(selWkt);
    return selWkt;
  }

  const doneWorkoutsSelected = doneWorkoutsQuery.data["training_log"].map(
    (wkt) => {
      if (wkt.id !== selectedWorkout) {
        void 0;
      } else {
        return (
          <Timeline.Item
            key={`doneWorkout_${wkt.id}`}
            time={new Date(wkt.date).toLocaleString()}>
            <p>{wkt.workout_title}</p>
          </Timeline.Item>
        );
      }
    }
  );

  function handleDoRXdToggle(value) {
    console.log(doAsRxd);
    console.log(value);
    setDoAsRxd((prev) => !prev);
    if (value == false) {
      clearWorkoutVals(workoutResults.date_done);
    } else {
      var all_new_results = {};
      for (let i of Object.keys(workoutResults)) {
        if (["date_done", "mover_id", "workout_id"].includes(i)) {
          all_new_results = { ...all_new_results, [i]: workoutResults[i] };
        } else {
          console.log(workoutResults[i]);
          var rxd_results = {
            rails: workoutResults[i].Rx.rails,
            passive_duration: workoutResults[i].Rx.passive_duration,
            duration: workoutResults[i].Rx.duration,
            rpe: workoutResults[i].Rx.rpe,
            external_load: workoutResults[i].Rx.external_load,
            reps_array: workoutResults[i].Rx.reps_array,
          };
          var new_payload = { ...workoutResults[i], results: rxd_results };
          all_new_results = { ...all_new_results, [i]: new_payload };
        }
      }
      setWorkoutResults(all_new_results);
      const input_to_see = workouts[index_of_selectedWorkout()]?.inputs[0].id;
      setSelectInp(input_to_see);
    }
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
        <Stack.Item
          style={{
            display: "flex",
            width: "400px",
            margin: 10,
            alignSelf: "center",
          }}>
          <SelectPicker
            style={{
              display: "flex",
              width: "400px",
              margin: 10,
            }}
            onSelect={(v, i, e) => {
              setDoAsRxd(false);
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
            flexDirection: "row",
            margin: "auto",
            alignContent: "center",
            alignItems: "center",
          }}>
          <h4 style={{ display: "flex", marginRight: "15px" }}>Do as Rx'd?</h4>
          <Toggle
            checked={doAsRxd}
            onChange={(value) => handleDoRXdToggle(value)}
          />
        </Stack.Item>
        <Stack.Item
          style={{
            display: "flex",
            flexDirection: "row",
            margin: "auto",
            alignContent: "center",
            alignItems: "center",
          }}>
          <Rate
            disabled={true} /* {!doAsRxd} */
            defaultValue={5}
            allowHalf
            vertical
            character={<CheckRoundIcon />}
            color='cyan'
          />
        </Stack.Item>
        <Divider />

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
              preventOverflow
              onChange={(value) =>
                updateWorkoutResults("date_done", value.toISOString())
              }
              format='yyyy-MM-dd HH:mm'
              placeholder={Date(workoutResults.date_done)}
            />
          </Stack.Item>
          <Divider vertical style={{ height: "100%" }} />

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
              updateDB={(event, value) => {
                event.preventDefault();
                updateDB.mutate(value);
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
            href='/dashboard/mover'
            onClick={() => confirm_workout.mutate()}>
            Record Workout
          </Button>
          {/* <Button as={RsNavLink} href='/record'>
            Pause Workout
          </Button> */}
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
        <Timeline endless>{doneWorkoutsSelected}</Timeline>
      </Stack.Item>
    </Stack>
  );
}
