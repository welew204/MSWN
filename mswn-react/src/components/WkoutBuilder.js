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
  IconButton,
} from "rsuite";
import CogIcon from "@rsuite/icons/legacy/Cog";
import TrashIcon from "@rsuite/icons/Trash";
import { useQuery, useMutation } from "@tanstack/react-query";
import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";
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
  console.log(wktInProgress);

  const [selectedInput, setSelectedInput] = useState(1);
  const [schemaArray, setSchemaArray] = useState([]);
  /* console.log("SELECTED INPUT: " + selectedInput); */

  function flatten_schema(schema) {
    /* given an object (schema), recursively walk into it:
    - concatenated SETxINPUT (eg: A1)
    - append this to a schemaArray object
    - when done pass this into state, and */
    const schemaArrayDraft = Object.keys(schema).map((set) => {
      var tagged_circuit = [];
      for (let inp in schema[set].circuit) {
        const tagged_inp = set + (parseInt(inp) + 1).toString();
        tagged_circuit.push(tagged_inp);
      }
      return tagged_circuit;
    });
    return schemaArrayDraft.flat();
  }

  function update_schema() {
    /* given a schemaArray:
    - split into KEY and circuit-value
    - write a new schema object for wktInProgress
    - updateWkt */
  }

  useEffect(() => {
    setSchemaArray(flatten_schema(wktInProgress.schema));
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
        body: JSON.stringify(wktInProgress),
        mode: "cors",
      }).then((res) => console.log(res));
    },
  });

  const workoutsQuery = useQuery(["workouts"], () => {
    return fetchAPI(server_url + `/workouts/${activeMover}`);
  });

  /* const trainingLogData = useQuery(["trainingLog"], () =>
    fetchAPI(server_url + `/bout_log/${activeMover}`)
  ); */

  if (workoutsQuery.isLoading) return "Loading...";
  if (workoutsQuery.isError) return `Error: error`;
  /* if (boutLogData.isLoading) {
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
  }); */

  function fetchAPI(url) {
    return fetch(url).then((res) => res.json());
  }
  function updateWkt(field, UpdValue) {
    setWktInProgress((prev) => ({ ...prev, [field]: UpdValue }));
  }

  function removeInput(inputID) {
    console.log(inputID);

    const targetSet = Object.keys(wktInProgress.schema).find((set) =>
      wktInProgress.schema[set].circuit.includes(inputID.toString())
    );

    console.log(targetSet);
    var new_schema = {};
    if (wktInProgress.schema[targetSet].circuit.length > 1) {
      console.log(wktInProgress.schema[targetSet].circuit);
      const new_circuit = wktInProgress.schema[targetSet].circuit.filter(
        (val) => val != inputID
      );
      new_schema = {
        ...wktInProgress.schema,
        [targetSet]: {
          ...wktInProgress.schema[targetSet],
          circuit: [new_circuit],
        },
      };
    } else {
      /* update `schema` to remove empty set, then update proceeding sets LETTER (decrement by 1)*/
      const schemaAsArray = Object.entries(wktInProgress.schema);
      const newSchemaAsArray = schemaAsArray.filter(
        ([key, val]) => key != targetSet
      );
      console.log(newSchemaAsArray);
      const targetSetCharCode = targetSet.charCodeAt(0);
      for (let index in newSchemaAsArray) {
        var setLetterCode = newSchemaAsArray[index][0].charCodeAt(0);
        if (setLetterCode < targetSetCharCode) {
          continue;
        } else {
          var newSetLetter = String.fromCharCode(setLetterCode - 1);
          newSchemaAsArray[index][0] = newSetLetter;
        }
      }
      console.log(newSchemaAsArray);
      new_schema = Object.fromEntries(newSchemaAsArray);
    }
    /* convert object to array */
    const inputsAsArray = Object.entries(wktInProgress.inputs);
    /* filter array to leave out clicked input */
    const newInputsArray = inputsAsArray.filter(([key, val]) => key != inputID);
    /* grab id of last input in NEW array to be the new selectedInput */
    const newSelectedInput = newInputsArray.at(-1)[0];
    /* convert updated list back into object */
    const newInputs = Object.fromEntries(newInputsArray);
    /* update wktInProgress */
    setWktInProgress((prev) => ({
      ...prev,
      inputs: newInputs,
      schema: new_schema,
    }));
    setSelectedInput(newSelectedInput);
  }

  const rx_inputs = Object.keys(wktInProgress.inputs).map((inp, index) => (
    <Draggable
      key={`${wktInProgress.inputs[inp].id}`}
      draggableId={`${wktInProgress.inputs[inp].id}`}
      index={index}>
      {(provided, snapshot) => (
        <div
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          ref={provided.innerRef}>
          <Panel
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              height: "85px",
            }}
            onClick={() => setSelectedInput(wktInProgress.inputs[inp].id)}
            shaded
            className={
              selectedInput == wktInProgress.inputs[inp].id
                ? "selected-inp-plaque"
                : "inp-plaque"
            }
            bordered>
            {wktInProgress.inputs[inp].ref_joint_id &&
            wktInProgress.inputs[inp].drill_name ? (
              <h5 style={{ margin: "auto" }}>
                {`${wktInProgress.inputs[inp].ref_joint_side} ${wktInProgress.inputs[inp].ref_joint_name} ${wktInProgress.inputs[inp].drill_name}`}
              </h5>
            ) : (
              <Loader vertical speed='slow' size='md'></Loader>
            )}
            {wktInProgress.inputs[inp].completed ? (
              <h6 style={{ margin: "auto" }}>
                {`RPE: ${wktInProgress.inputs[inp].rpe}/10`} <br />
                {`Duration: ${wktInProgress.inputs[inp].duration} secs`}
              </h6>
            ) : (
              <h5 style={{ margin: "auto" }}>...building workout...</h5>
            )}
            {wktInProgress.inputs[inp].completed ? (
              <div>
                <IconButton
                  onClick={(e) => {
                    e.stopPropagation();
                    removeInput(wktInProgress.inputs[inp].id);
                  }}
                  style={{ marginLeft: "auto" }}
                  size='md'
                  icon={<TrashIcon />}
                />
              </div>
            ) : (
              void 0
            )}
          </Panel>
        </div>
      )}
    </Draggable>
  ));

  return (
    <DragDropContext onDragEnd={() => console.log("dropped the thing!")}>
      <Stack
        style={{
          height: "100%",
          minHeight: "100%",
          justifyContent: "space-around",
          alignItems: "center",
        }}>
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
          <Stack.Item
            style={{ display: "flex", justifyContent: "space-around" }}>
            <h1>Build A Workout</h1>
          </Stack.Item>
          <Divider />
          <Stack.Item
            style={{ display: "flex", justifyContent: "space-evenly" }}>
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
              className='workoutSchema'
              style={{
                display: "flex",
                flexDirection: "column",
                alignContent: "stretch",
                minWidth: 200,
                width: "100%",
                gap: 10,
              }}>
              <WktTitle
                title={wktInProgress.workout_title}
                onChange={updateWkt}
              />
              <Droppable droppableId='droppable'>
                {(provided, snapshot) => (
                  <div {...provided.droppableProps} ref={provided.innerRef}>
                    {rx_inputs}
                    {provided.placeholder}
                  </div>
                )}
              </Droppable>
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
          {/* <Timeline endless>{bouts}</Timeline> */}
        </Stack.Item>
      </Stack>
    </DragDropContext>
  );
}
