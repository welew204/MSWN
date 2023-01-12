import React from "react";
import { Modal, Form, Button } from "rsuite";
import { Link } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

export default function AddMoverModal({ open, close }) {
  const [form, setForm] = React.useState({
    firstName: "",
    lastName: "",
  });

  const handleChange = (event) => {
    setForm({ ...form, [event.target.name]: event.target.value });
  };

  const queryClient = useQueryClient();

  const addMover = useMutation({
    mutationFn: (newMover) => {
      fetch("http://127.0.0.1:8000/add_mover", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify([newMover]),
        mode: "cors",
      }).then((res) => console.log(res));
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["movers"] });
    },
  });

  const handleClose = () => close();

  return (
    <Modal size="xs" open={open}>
      <Modal.Header>
        <Modal.Title>Add Mover</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form style={{ padding: 10 }}>
          <Form.Group>
            <Form.Control
              autoComplete="false"
              onChange={(value, event) => handleChange(event)}
              placeholder="First Name"
              name="firstName"
            />
          </Form.Group>
          <Form.Group>
            <Form.Control
              autoComplete="false"
              onChange={(value, event) => handleChange(event)}
              placeholder="Last Name"
              name="lastName"
            />
          </Form.Group>
        </Form>
      </Modal.Body>
      <Modal.Footer>
        <Button onClick={handleClose} appearance="subtle">
          Cancel
        </Button>
        <Link>
          <Button
            onClick={(event) => {
              event.preventDefault();
              addMover.mutate(form);
              handleClose();
            }}
            appearance="primary"
          >
            OK
          </Button>
        </Link>
      </Modal.Footer>
    </Modal>
  );
}
