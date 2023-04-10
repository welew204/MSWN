import React from "react";
import { Modal, Form, Button } from "rsuite";
import { Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

export default function AddMoverModal({ open, close, coach_id }) {
  const [form, setForm] = React.useState({
    firstName: "",
    lastName: "",
    coachID: coach_id,
    bodyweight: 0,
  });

  const handleChange = (event) => {
    let new_value = event.target.value;
    if (event.target.name == "bodyweight") {
      new_value = parseInt(new_value);
    }
    setForm({ ...form, [event.target.name]: new_value });
  };

  const queryClient = useQueryClient();

  const addMover = useMutation({
    mutationFn: (newMover) => {
      return fetch("http://127.0.0.1:8000/add_mover", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify([newMover]),
        mode: "cors",
      }).then((res) => console.log(res));
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["movers", coach_id] });
      console.log("The mutation is sucessful!");
    },
  });

  const handleClose = () => {
    // clearing the form...
    setForm({
      firstName: "",
      lastName: "",
      bodyweight: 0,
    });
    return close();
  };
  /* TODO maybe the issue is triggering the re-render of the sidebar 'movers' */

  return (
    <Modal size='xs' open={open} onClose={handleClose}>
      <Modal.Header>
        <Modal.Title>Add Mover</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form style={{ padding: 10 }}>
          <Form.Group>
            <Form.Control
              autoComplete='false'
              onChange={(value, event) => handleChange(event)}
              placeholder='First Name'
              name='firstName'
            />
            <Form.HelpText
              style={{
                marginTop: "8px",
                fontStyle: "italic",
                width: "80%",
              }}>
              * required
            </Form.HelpText>
          </Form.Group>
          <Form.Group>
            <Form.Control
              autoComplete='false'
              onChange={(value, event) => handleChange(event)}
              placeholder='Last Name'
              name='lastName'
            />
            <Form.HelpText
              style={{
                marginTop: "8px",
                fontStyle: "italic",
                width: "80%",
              }}>
              * required
            </Form.HelpText>
          </Form.Group>
          <Form.Group>
            <Form.Control
              autoComplete='false'
              onChange={(value, event) => handleChange(event)}
              placeholder='bodyweight'
              name='bodyweight'
            />
            <Form.HelpText tooltip>
              This information is only for calculating resistance of bodyweight
              activities (default: 150 lbs).
            </Form.HelpText>
          </Form.Group>
        </Form>
      </Modal.Body>
      <Modal.Footer>
        <Button onClick={handleClose} appearance='subtle'>
          Cancel
        </Button>
        <Link>
          <Button
            onClick={(event) => {
              event.preventDefault();
              if (!form.firstName) {
                return void 0;
              } else if (!form.lastName) {
                return void 0;
              }
              addMover.mutate(form);
              handleClose();
            }}
            appearance='primary'>
            OK
          </Button>
        </Link>
      </Modal.Footer>
    </Modal>
  );
}
