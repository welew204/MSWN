import React, { useState, useRef, useEffect, useLayoutEffect } from "react";
import { select } from "d3-selection";
import { scaleLinear } from "d3-scale";
import { ReactComponent as HumanSvg } from "./humanOutline2.svg";
import { useQuery } from "@tanstack/react-query";
import { useOutletContext } from "react-router-dom";

const server_url = "http://127.0.0.1:8000";

export function HumanMap({ data }) {
  function fetchAPI(url) {
    return fetch(url).then((res) => res.json());
  }

  const svgRef = useRef(null);
  const [selectedWorkout, setSelectedWorkout, activeMover] = useOutletContext();

  //useEffect(() => {}, []);
  // initial setting of data from API; useQuery instead
  const boutsQuery = useQuery(["bouts", activeMover], () => {
    return fetchAPI(server_url + `/status/${activeMover}`);
  });

  function calc_capsular_bouts(targetJ) {
    const tcx = parseInt(targetJ.attr("cx"));
    const tcy = parseInt(targetJ.attr("cy"));
    const random_angle = Math.random() * Math.PI * 2;
    const noise_factor = 10;
    const random_length = Math.random() * noise_factor + 5;

    const new_x = Math.round(Math.cos(random_angle) * random_length) + tcx;
    const new_y = Math.round(Math.sin(random_angle) * random_length) + tcy;

    return [new_x, new_y];
  }

  function calc_rot_and_linear_bouts(targetJ, proximalJ) {
    const tcx = parseInt(targetJ.attr("cx"));
    const tcy = parseInt(targetJ.attr("cy"));
    const pcx = parseInt(proximalJ.attr("cx"));
    const pcy = parseInt(proximalJ.attr("cy"));
    const x_diff = Math.abs(tcx - pcx);
    const y_diff = Math.abs(tcy - pcy);
    const proximity = Math.hypot(x_diff, y_diff);
    const random_length = Math.round(Math.random() * proximity);
    // this will eventually be related to tissue_type (passed into this function)

    const vector_angle = Math.atan2(pcy - tcy, pcx - tcx);
    // this angle is in RADIANs
    // TO MAKE IT INTO DEGREES ...
    // (Math.atan2(pcy - tcy, pcx - tcx) * 180) / Math.PI + 180;
    //the * 180/ pi converts, then +180 makes it a positive degree
    const res_x = Math.round(Math.cos(vector_angle) * random_length) + tcx;
    const res_y = Math.round(Math.sin(vector_angle) * random_length) + tcy;
    // now [res_x + tcx, res_y + tcy] is x,y for point ALONG the vector between targ and prox
    // now to RANDOMIZE away from this vector
    const noise_factor = 40;
    const noisey_x =
      Math.round(
        Math.cos(vector_angle + Math.PI / 2) *
          (Math.random() - 0.5) *
          noise_factor
      ) + res_x;
    const noisey_y =
      Math.round(
        Math.sin(vector_angle + Math.PI / 2) *
          (Math.random() - 0.5) *
          noise_factor
      ) + res_y;

    return [noisey_x, noisey_y];
  }

  console.log(svgRef.current);

  useEffect(() => {
    console.log("running my use effect!");
    // Bind d3
    // svgRef.current = mapRef;
    if (boutsQuery.isSuccess) {
      const pretty_bouts = boutsQuery.data.status.map((d) => {
        let j_id = d.id;
        let target = select("#" + d.joint_name_selector);
        let prox_target = select("#" + d.proximal_joint_selector);
        //console.log(d.proximal_joint_selector);
        if (d.tissue_type == "capsular") {
          let bout_points = calc_capsular_bouts(target);
          let point_color = "blue";
          let pkg = [bout_points[0], bout_points[1], point_color, j_id];
          return pkg;
        } else {
          let bout_points = calc_rot_and_linear_bouts(target, prox_target);
          let point_color = "green";
          let pkg = [bout_points[0], bout_points[1], point_color, j_id];
          return pkg;
        }
      });

      console.log(pretty_bouts.at(0));
      console.log(pretty_bouts.at(-1));
      //console.log(boutsQuery.data.at(-1));
      // find the right joint > id
      // find the right zone > proximity to joint-id
      // calculate the axis (neighboring joint)
      // calculate 'joint_distance' value for each
      // noisify points (lots for counter-axis, a little for joint_distance value)

      // THEN, how do I handle selecting and binding data to the selection?
      console.log(svgRef.current.children[0].children);
      const svg = select(svgRef.current);

      const target = svg
        .select("g")
        .selectAll()
        .data(pretty_bouts, (d) => d[3]);

      target
        .join("circle")
        .attr("id", (d) => d[3])
        .attr("r", "1")
        .attr("cx", (d) => d[0])
        .attr("cy", (d) => d[1])
        .attr("fill", (d) => d[2]);

      target.exit().remove();

      console.log(svgRef.current.children[0].children.length);
      /* const target = select("g").selectAll().data(pretty_bouts);
      
      console.log(target);

      target
        .enter()
        .merge(target)
        .append("circle")
        .attr("id", (d) => d[3])
        .attr("r", "1")
        .attr("cx", (d) => d[0])
        .attr("cy", (d) => d[1])
        .attr("fill", (d) => d[2]);

      target.exit().remove(); */

      //console.log(removed);
    }
    // ala... svg.select("#head").attr("fill", data.headColor);
    // Add new d3 elements
    // Update existing d3 elements
    // remove old d3 elements
  }, [boutsQuery]);
  // update data when bodyData changes

  if (boutsQuery.isLoading) {
    return <h4>Loading...</h4>;
  }
  if (boutsQuery.isError) {
    return <h4>Error!</h4>;
  }

  console.log(boutsQuery.data);

  return (
    <div>
      <HumanSvg /* viewbox={(10, 10, 50, 50)} */ ref={svgRef}></HumanSvg>
    </div>
  );
}
