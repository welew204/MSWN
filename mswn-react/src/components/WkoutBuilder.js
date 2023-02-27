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
  Toggle,
} from "rsuite";
import CogIcon from "@rsuite/icons/legacy/Cog";
import TrashIcon from "@rsuite/icons/Trash";
import ConversionIcon from "@rsuite/icons/Conversion";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";
import { NavToggle } from "./helpers/NavToggle";
import InputForm from "./helpers/InputForm";
import WktTitle from "./helpers/WktTitle";
import MultiJointInput from "./helpers/MultiJointInput";

const server_url = "http://127.0.0.1:8000";

export default function WkoutBuilder() {
  const default_new_input = {
    ref_joint_id: "",
    ref_joint_name: "",
    id: 1,
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
  const [multiJointInput, setMultiJointInput] = useState(true);

  const [wktInProgress, setWktInProgress] = useState({
    id: "",
    workout_title: "",
    date_init: "",
    moverid: activeMover,
    comments: "",
    inputs: {
      1: default_new_input,
    },
    schema: [{ circuit: ["1"], iterations: 1 }],
  });
  console.log(wktInProgress);

  const [selectedInput, setSelectedInput] = useState(1);
  const [schemaArray, setSchemaArray] = useState([]);
  /* console.log("SELECTED INPUT: " + selectedInput); */

  /* 
  given an object (schema), recursively walk into it:
  - concatenated SETxINPUT (eg: A1)
  - append this to a schemaArray object
  - when done pass this into state, and....
  
  function flatten_schema(schema) {
    const schemaArrayDraft = schema.map((set) => {
      const set_letter = String.fromCharCode(65+set)
      var tagged_circuit = [];
      for (let inp in set.circuit) {
        const tagged_inp = `${set_letter}${parseInt(inp) + 1}-${
          schema[set].circuit[inp]
        }`;
        tagged_circuit.push(tagged_inp);
      }
      return tagged_circuit;
    });
    const res = schemaArrayDraft.flat();
    console.log(res);
    return res;
  } */

  /* function update_schema(sArray) {
    /* given a schemaArray:
    - split into KEY and circuit-value
    - write a new schema object for wktInProgress
    - updateWkt */
  /* var schema_result = {};
    for (let inp in sArray) {
      var set = inp[0];
      var index = inp.slice(1);
      schema_result = {
        ...schema_result,
        [set]: { circuit: [...circuit.splice(index)] },
      };
    }
  } */

  /*   useEffect(() => {
    setSchemaArray(flatten_schema(wktInProgress.schema));
  }, [wktInProgress.schema]); */

  useEffect(() => {
    setWktInProgress((prev) => {
      const date = new Date().toJSON();
      return { ...prev, date_init: date.slice(0, 10) };
    });
  }, []);

  const queryClient = useQueryClient();

  const updateDB = useMutation({
    mutationFn: () => {
      return fetch(server_url + "/write_workout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(wktInProgress),
        mode: "cors",
      }).then((res) => console.log(res));
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workouts", activeMover] });
      console.log("The mutation is sucessful!");
    },
  });

  const workoutsQuery = useQuery(["workouts"], () => {
    return fetchAPI(server_url + `/workouts/${activeMover}`);
  });

  if (workoutsQuery.isLoading) return "Loading...";
  if (workoutsQuery.isError) return `Error: error`;

  function fetchAPI(url) {
    return fetch(url).then((res) => res.json());
  }
  function updateWkt(field, UpdValue) {
    setWktInProgress((prev) => ({ ...prev, [field]: UpdValue }));
  }

  /*   function reorderSchema(result) {
    const source = result.source.index;
    const destination = result.destination.index;
    var newly_ordered_schema = Array.from(schemaArray);
    const [removed] = newly_ordered_schema.splice(source, 1);
    // correctly ORDERED inputs, tho just need to re-write for proper set-assignment
    newly_ordered_schema.splice(destination, 0, removed);
    // break up 'removed' into constituent parts (set, index, input_id)
    const moved_item_array = removed.split("-");
    const set = moved_item_array[0][0];
    const drill_index = moved_item_array[0].slice(1);
    const input_id = moved_item_array[1][0];
    var current_set = "A";
    var result = [];
    for (let i in newly_ordered_schema) {
      var current_item_array = newly_ordered_schema[i].split("-");
      var drill_set = current_item_array[0][0];
      var circuit_index = current_item_array[0].slice(1);
      var current_input_id = current_item_array[1][0];
      if (drill_set === current_set) {
        continue;
      }
      // eventually this will need to also handle walking through the circuit of drills IN that set
      else {
        var new_schema_tag = `${current_set}${circuit_index}-${current_input_id}`;
        result.push(new_schema_tag);
        current_set = (current_set.charCodeAt(0) + 1).fromCharCode();
      }
    }
  } */

  function removeInput(inputID) {
    console.log(inputID);

    const targetSet = wktInProgress.schema.find((set) => {
      return set.circuit.includes(inputID.toString());
    });

    const target_set_index = wktInProgress.schema.indexOf(targetSet);

    console.log(targetSet);
    console.log(target_set_index);
    var new_schema = [];
    if (targetSet.circuit.length > 1) {
      const new_circuit = targetSet.circuit.filter((val) => val != inputID);
      new_schema = [
        ...wktInProgress.schema,
        {
          ...wktInProgress.schema[target_set_index],
          circuit: [new_circuit],
        },
      ];
    } else {
      /* update `schema` to remove empty set, then update proceeding sets LETTER (decrement by 1)*/
      new_schema = wktInProgress.schema.filter((set) => set != targetSet);
      console.log(new_schema);
      /* THIS ISN'T needed now that the schema is already an array, 
      tho this code may help w/ translating 
      index into set-letter, eventually....
      
      const targetSetCharCode = targetSet.charCodeAt(0);
      for (let index in newSchemaAsArray) {
        var setLetterCode = newSchemaAsArray[index][0].charCodeAt(0);
        if (setLetterCode < targetSetCharCode) {
          continue;
        } else {
          var newSetLetter = String.fromCharCode(setLetterCode - 1);
          newSchemaAsArray[index][0] = newSetLetter;
        }
        console.log(newSchemaAsArray);
        new_schema = Object.fromEntries(newSchemaAsArray);
      }
      setSchemaArray(flatten_schema(new_schema));
      */
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

  const n_rx_inputs = wktInProgress.schema.map((inp, index) => {
    // break up the inp into useful pieces
    var set = String.fromCharCode(65 + index);
    var input_id = inp.circuit[0];
    const inp_details = wktInProgress.inputs[input_id];
    return (
      <Draggable key={input_id} draggableId={input_id} index={index}>
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
              onClick={() => setSelectedInput(input_id)}
              shaded
              className={
                selectedInput == input_id ? "selected-inp-plaque" : "inp-plaque"
              }
              bordered>
              {inp_details?.ref_joint_id && inp_details?.drill_name ? (
                <h5 style={{ margin: "auto" }}>
                  {`${inp_details.ref_joint_side} ${inp_details.ref_joint_name} ${inp_details.drill_name}`}
                </h5>
              ) : (
                void 0
              )}
              {inp_details.completed ? (
                <h6 style={{ margin: "auto" }}>
                  {`RPE: ${inp_details.rpe}/10`} <br />
                  {`Duration: ${inp_details.duration} secs`}
                </h6>
              ) : (
                <h5 style={{ margin: "auto" }}>... input in progress ...</h5>
              )}
              {inp_details.completed ? (
                <div>
                  <IconButton
                    onClick={(e) => {
                      e.stopPropagation();
                      removeInput(input_id);
                    }}
                    style={{ marginLeft: "auto" }}
                    size='md'
                    icon={<TrashIcon />}
                  />
                </div>
              ) : (
                void 0
              )}
              {/* THIS IS AN iconButton to help with schema-building eventuallY 
              
              {index !== 0 && wktInProgress.inputs[input_id].completed ? (
                <div>
                  <IconButton
                    onClick={(e) => {
                      e.stopPropagation();
                      console.log("This will link inputs into a circuit");
                    }}
                    style={{ position: "absolute", transform: "" }}
                    icon={<ConversionIcon />}
                    size='sm'
                  />
                </div>
              ) : (
                void 0
              )} */}
            </Panel>
          </div>
        )}
      </Draggable>
    );
  });

  function handleDrag(result) {
    const target_input = result.draggableId;
    const source = result.source.index;
    const destination = result.destination.index;
    const new_schema = Array.from(wktInProgress.schema);
    const [removed] = new_schema.splice(source, 1);
    new_schema.splice(destination, 0, removed);
    setWktInProgress((prev) => ({ ...prev, schema: new_schema }));
  }

  return (
    <DragDropContext onDragEnd={(result) => handleDrag(result)}>
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
              <Toggle
                style={{ display: "flex", justifyContent: "space-around" }}
                checked={multiJointInput}
                onChange={setMultiJointInput}
                size='lg'
                checkedChildren='Multi Joint'
                unCheckedChildren='Single Joint'></Toggle>
              <Divider />
              {multiJointInput ? (
                <MultiJointInput />
              ) : (
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
              )}
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
                    {n_rx_inputs}
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
            {/* <Button as={RsNavLink} href='/wbuilder'>
              Save Workout Draft
            </Button> */}
          </Stack.Item>
        </Stack.Item>
      </Stack>
    </DragDropContext>
  );
}
