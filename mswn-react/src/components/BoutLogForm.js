import React from "react";
import { 
    ButtonToolbar, 
    Button, 
    InputNumber, 
    Slider, 
    Cascader, 
    SelectPicker, 
    Form, 
    DatePicker,
    Timeline } from 'rsuite'
import { useQuery, useMutation } from "@tanstack/react-query";

const server_url = "http://127.0.0.1:8000"

export default function BoutLogForm() {
    const inpCycs = ["IC 1", "IC 2", "IC 3", "IC 4","IC 5","IC 6","IC 7"]
    .map(item => ({ label: item, value: item }))
    
    function fetchAPI(url) {
        return fetch(url)
            .then((res) => {return res.json()})
    }

    const boutLogData = useQuery(["boutLog"], () => fetchAPI(server_url+"/bout_log/1"))
    const jointRefData = useQuery(["joints_ref"], () => fetchAPI(server_url+"/joint_ref"))
    
    if (boutLogData.isLoading) {return <p>Getting your bout data...</p>}
    if (jointRefData.isLoading) {return <p>Ish is loading!</p>}
    
    const joint_list = Object.keys(jointRefData.data)
    const jointsArray = joint_list
        .map((joint) => { return( 
            {label: joint, 
            value: joint, 
            children: jointRefData.data[joint]
                .map(zone => {return ({label: zone, value: zone})})})})
    
    const position = ["Regressive (short)", "Mid-range", "Progressive (long)"]

    const bout_array = boutLogData.data["bout_log"]
    const bouts = bout_array
                .map((bout, i) => {return(
                    <Timeline.Item key={`bout_${bout_array[i].id}`}time={bout_array[i].date}>
                        {bout_array[i].comments}, RPE: {bout_array[i].rpe}, External Load: {bout_array[i].external_load}
                    </Timeline.Item>
                )})

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
                    data={jointsArray}
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
            <br />
            <Form.Group controlId='rotation'>
                <Form.ControlLabel>Rotation of Joint (IR is - , ER is +):</Form.ControlLabel>
                <Slider
                    defaultValue={0}
                    min={-105}
                    step={5}
                    max={105}
                    graduated
                    progress
                    renderMark={mark => {if (mark%15 === 0) {return mark} 
                        else {return null}}}
                    style={{ width: 500 }}
                    />
            </Form.Group>
            <br />
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
        <div>
            <Timeline endless>
                {bouts}
            </Timeline>
        </div>
        </div>
    )
}