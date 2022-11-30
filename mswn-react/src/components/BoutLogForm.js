import React from "react";
import { ButtonToolbar, Button, InputNumber, Slider, Cascader, SelectPicker, Form, DatePicker } from 'rsuite'

export default function BoutLogForm() {
    const inpCycs = ["IC 1", "IC 2", "IC 3", "IC 4","IC 5","IC 6","IC 7"]
        .map(item => ({ label: item, value: item }))
  
    const zones = ["capsule", "flexion", "flex-abd", "abduction", "ext-abd", "extension", "ext-add", "adduction", "flex-add"]
        .map(item => ({ label: item, value: item }))

    const joints = ["hip", "knee", "ankle", "GH", "elbow","wrist","spine"]
        .map(function(item) {if (item === "spine") {
            return ({ label: item, value: item, children: [
                {label: "cervical", value: "cervical", children: [
                    {label: "flexion", value: "flexion"},
                    {label: "extension", value: "extension"},
                    {label: "rotation", value: "rotation"}
                ] },
                {label: "thoracic", value: "thoracic", children: [
                    {label: "flexion", value: "flexion"},
                    {label: "extension", value: "extension"},
                    {label: "rotation", value: "rotation"}
                ] },
                {label: "lumbar", value: "lumbar", children: [
                    {label: "flexion", value: "flexion"},
                    {label: "extension", value: "extension"},
                    {label: "rotation", value: "rotation"}
                ] },
                ] })
        } else {return({label: item, value: item, children: zones})}
    }
    )

    const position = ["Regressive (short)", "Mid-range", "Progressive (long)"]

    return(
        <div className="form">
        <h1>
            MSWN
        </h1>
        <h2>
            Input Bout Log
        </h2>
        <hr />
        <Form >
            <Form.Group controlId='date'>
                <DatePicker
                    format="MM-dd-yyyy HH:mm:ss"
                    calendarDefaultDate={new Date()}
                    ranges={[
                    {
                        label: 'Now',
                        value: new Date()
                    }
                    ]}
                    style={{ width: 260}}
                />
            </Form.Group>
            <Form.Group controlId='joint'>
                <Form.ControlLabel>Joint / Zone trained:</Form.ControlLabel>
                <Cascader
                    data={joints}
                    style={{ width: 224 }}
                    />
            </Form.Group>
            <Form.Group controlId='inpCycle'>
                <Form.ControlLabel>Input Cycle:</Form.ControlLabel>
                <SelectPicker
                    data={inpCycs}
                    searchable={false}
                    style={{ width: 224 }}
                    />
            </Form.Group>
            <Form.Group controlId='position'>
                <Form.ControlLabel>Position of Tissue:</Form.ControlLabel>
                <Slider
                    defaultValue={1}
                    min={0}
                    step={1}
                    max={2}
                    graduated
                    progress
                    renderMark={mark => {
                    return position[mark];
                    }}
                    style={{ width: 250 }}
                    />
            </Form.Group>
            <Form.Group controlId='duration'>
                <Form.ControlLabel>Duration of contraction:</Form.ControlLabel>
                <InputNumber 
                    defaultValue={30}
                    postfix="seconds"/>
            </Form.Group>
            <br />
            <Form.Group controlId='rpe'>
                <Form.ControlLabel>Rate of Percieved Exertion (RPE):</Form.ControlLabel>
                <Slider
                    defaultValue={5}
                    min={0}
                    step={1}
                    max={10}
                    graduated
                    progress
                    renderMark={mark => {
                    return mark;
                    }}
                    style={{ width: 500 }}
                    />
            </Form.Group>
            <br />
            <Form.Group controlId='load'>
                <Form.ControlLabel>External Load (optional):</Form.ControlLabel>
                <InputNumber 
                    defaultValue={0}
                    postfix="lbs"
                />
            </Form.Group>
            <Form.Group>
                <ButtonToolbar>
                    <Button appearance="primary">Submit</Button>
                    <Button appearance="default">Cancel</Button>
                </ButtonToolbar>
            </Form.Group>
        </Form>
        </div>
    )
}