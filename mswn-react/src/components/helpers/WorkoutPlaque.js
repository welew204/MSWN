import React, { useState } from "react";
import { 
    Toggle,
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
    /* query callback fnc */
    function fetchAPI(url) {
        return fetch(url)
        .then((res) => {return res.json()})
    }

    function postAPI(url) {
        fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json',
                        Accept: 'application/json' },
            body: JSON.stringify({
                "date": drillDate,
                "joint_id": jointID,
                "zone_id": zoneID,
                "drill": selectedDrill,
                "position": selectedPosition,
                "rotation_bias": selectedRotation,
                "rails": railsSelected,
                "duration": drillDuration,
                "p_duration": passiveDuration,
                "rpe": drillRPE,
                "load": drillLoad }),
        }).then((res) => console.log(res))
        .catch((error) => {console.error('There has been a problem with your fetch operation:', error)});
    }
    
    /* useQuery's */
    const drillRefData = useQuery(["drillRef"], () => fetchAPI(server_url+"/drill_ref"))
    const boutLogData = useQuery(["boutLog"], () => fetchAPI(server_url+"/bout_log/1"))
    const jointRefData = useQuery(["jointsRef"], () => fetchAPI(server_url+"/joint_ref"))
    /* console.log(jointRefData.isLoading ? "" : jointRefData.data) */
    
    /* state for form components */
    const [moverId, setMoverId] = useState(1)
    /* this needs to get updated from flask */
    const [drillDate, setDrillDate] = useState("")
    const [jointSelected, setJointSelected] = useState("")
    
    const [jointID, setJointID] = useState(0)
    const [zoneID, setZoneID] = useState(0)
    /* console.log("jointId in state: "+ jointID)
    console.log("zoneId in state: "+ zoneID) */

    const [selectedDrill, setSelectedDrill] = useState("CARs")
    const [selectedPosition, setSelectedPosition] = useState(0)
    const [selectedRotation, setSelectedRotation] = useState(-100)
    const [railsSelected, setRailsSelected] = useState(false)
    const [drillDuration, setDrillDuration] = useState(30)
    const [passiveDuration, setPassiveDuration] = useState(0)
    const [drillRPE, setDrillRPE] = useState(5)
    const [drillLoad, setDrillLoad] = useState(0)
    
    if (boutLogData.isLoading) {return <p>Getting your bout data...</p>}
    if (jointRefData.isLoading) {return <p>Ish is loading!</p>}
    if (drillRefData.isLoading) {return <p>Ish is loading!</p>}

    /* console.log(jointRefData.data) */
        
    const jointsArray = jointRefData.data
    .map((joint) => { return( 
        {label: joint["name"], 
        id: joint["id"],
        value: joint["id"].toString(), 
        children: joint["zones"]
            .map((zone, i) => {return ({label: zone["zone_name"], value: `${zone["rowid"]}-${i}`, id: zone["id"]})})})})
            
    const drills = Object.keys(drillRefData.data)
            .map(item => ({ label: item, value: item }))
    
    /* this function logs the ref_joint or ref_zone id into state, so that can be sent off with 'submit_form' */
    function find_tissue(item) {
        const id = item.id
        if (item.children) {
            setJointID(id)
            }
        else {
            setZoneID(id)
        }
    }

    function submit_form() {
        postAPI(server_url+`/add_bout/${moverId}`)
    }

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
            Input Drill
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
                        value: new Date(),
                        closeOverlay: false
                    }
                    ]}
                    style={{ width: 260}}
                    onOk={(date) => setDrillDate(date)}
                />
            </Form.Group>
            <Form.Group controlId='joint'>
                <Form.ControlLabel>Joint / Zone trained:</Form.ControlLabel>
                <Cascader
                    data={jointsArray}
                    style={{ width: 224 }}
                    parentSelectable
                    value={jointSelected}
                    onChange={setJointSelected}
                    onSelect={(item) => find_tissue(item)}
                    /* value= is NOT working as expected, so need to use call-back fnc to find correct path using id? */
                    />
            </Form.Group>
            <Form.Group controlId='drills'>
                <Form.ControlLabel>Drill:</Form.ControlLabel>
                <SelectPicker
                    data={drills}
                    disabledItemValues={jointSelected.includes("-") ? ['CARs', 'capsule CAR'] : ["PRH", "PRLO", "IC1","IC2","IC3"] }
                    searchable={false}
                    style={{ width: 224 }}
                    onSelect={(e) => setSelectedDrill(e)}
                    />
            </Form.Group>
            <Form.Group controlId='position'>
                <Form.ControlLabel>Position of Tissue:</Form.ControlLabel>
                <Slider
                    disabled={ drillRefData.data[selectedDrill].position ? (drillRefData.data[selectedDrill].position.length === 1 ? true : false) : true }
                    value={ drillRefData.data[selectedDrill].position ? (drillRefData.data[selectedDrill].position.length === 1 ? drillRefData.data[selectedDrill].position[0] : selectedPosition) : 0 }
                    /*the slider does not update automatically, slide with the cursor.....?*/
                    min={0}
                    step={25}
                    max={100}
                    graduated
                    progress
                    renderMark={mark => {if (mark === 0) {return position[0]} 
                        else if (mark === 50) {return position[1]} 
                        else if (mark === 100) {return position[2]}
                    }}
                    style={{ width: 250 }}
                    onChangeCommitted={setSelectedPosition}
                />
            </Form.Group>
            <br />
            <Form.Group controlId='rotation'>
                <Form.ControlLabel>Rotation of Joint (IR is - , ER is +):</Form.ControlLabel>
                <Slider
                    value={selectedRotation}
                    disabled={ drillRefData.data[selectedDrill].rotation ? false : true }
                    min={-100}
                    step={drillRefData.data[selectedDrill].rotation?.length === 0 ? 5 : 200}
                    max={100}
                    graduated
                    progress
                    renderMark={mark => {if (mark%25 === 0) {return mark} 
                        else {return null}}}
                    style={{ width: 500 }}
                    onChangeCommitted={setSelectedRotation}
                    />
            </Form.Group>
            <br />
            {drillRefData.data[selectedDrill]?.rails ? (
                <Form.Group controlId="rails">
                <Form.ControlLabel>RAILs tissue trained...?</Form.ControlLabel>
                <Toggle 
                onChange={() => setRailsSelected(prev => !prev)}
                value={railsSelected}
                />
            </Form.Group>) : ""}
            <br />
            {drillRefData.data[selectedDrill]?.["passive duration"] ? (
                <div>
                <Form.Group controlId="rails">
                <Form.ControlLabel>Duration of passive stretch:</Form.ControlLabel>
                <InputNumber 
                    onChange={setPassiveDuration}
                    value={passiveDuration}
                    postfix="seconds"/>
            </Form.Group>
            <br />
            </div>) : ""}
            <Form.Group controlId='duration'>
                <Form.ControlLabel>Duration of effort:</Form.ControlLabel>
                <InputNumber 
                    value={drillDuration}
                    postfix="seconds"
                    onChange={setDrillDuration}
                    />
            </Form.Group>
            <br />
            <Form.Group controlId='rpe'>
                <Form.ControlLabel>Rate of Percieved Exertion (RPE):</Form.ControlLabel>
                <Slider
                    value={drillRPE}
                    min={0}
                    step={1}
                    max={10}
                    graduated
                    progress
                    onChangeCommitted={setDrillRPE}
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
                    value={drillLoad}
                    postfix="lbs"
                    onChange={setDrillLoad}
                    />
            </Form.Group>
            <Form.Group>
                <ButtonToolbar>
                    <Button appearance="primary" onClick={submit_form} >Submit</Button>
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