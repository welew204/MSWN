import { useState, React } from "react";
import { Modal, Form, Button, ButtonToolbar } from "rsuite";
import { Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function CoachLoginModal({ coachSelected, open, close }) {
  // 'coachSelected' is now an object w/ first_ and last_name and coach_id props
  const [pwEntry, setPwEntry] = useState("");
  const { login } = useAuth();

  function handleSubmit(event) {
    event.preventDefault();
    pwEntry == ""
      ? void 0
      : login({ coach: coachSelected.coach_id, password: pwEntry });
  }

  return (
    <Modal
      style={{}}
      open={open}
      size='sm'
      onKeyDown={(event) => {
        event.keyCode == 13 ? handleSubmit(event) : void 0;
      }}>
      <Modal.Header>
        <Modal.Title>Coach Login</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form style={{ padding: 10 }}>
          <Form.Group>
            <Form.Control
              autoComplete='false'
              placeholder='Password'
              name='password'
              value={pwEntry}
              onChange={setPwEntry}
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
            <ButtonToolbar>
              <Button appearance='primary' onClick={handleSubmit}>
                Submit
              </Button>
              <Button appearance='default' onClick={() => close(false)}>
                Cancel
              </Button>
            </ButtonToolbar>
          </Form.Group>
        </Form>
      </Modal.Body>
    </Modal>
  );
}
