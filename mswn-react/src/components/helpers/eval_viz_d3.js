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
  const [currentPrettyBouts, setCurrentPrettyBouts] = useState([]);

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

  function calc_rot_bouts(target_joint, proximal_joint, rotational_value) {
    const tcx = parseInt(target_joint.attr("cx"));
    const tcy = parseInt(target_joint.attr("cy"));
    const pcx = parseInt(proximal_joint.attr("cx"));
    const pcy = parseInt(proximal_joint.attr("cy"));
    const x_diff = Math.abs(tcx - pcx);
    const y_diff = Math.abs(tcy - pcy);
    const proximity = Math.hypot(x_diff, y_diff);
    var placement_factor;
    if (rotational_value == "") {
      placement_factor = Math.random();
    } else {
      placement_factor = 1 - Math.abs(rotational_value) / 100;
    }
    const placement_along_axis = Math.round(placement_factor * (proximity / 3));
    // this will eventually be related to tissue_type (passed into this function)

    const vector_angle = Math.atan2(pcy - tcy, pcx - tcx);
    // this angle is in RADIANs
    // TO MAKE IT INTO DEGREES ...
    // (Math.atan2(pcy - tcy, pcx - tcx) * 180) / Math.PI + 180;
    //the * 180/ pi converts, then +180 makes it a positive degree
    const res_x =
      Math.round(Math.cos(vector_angle) * placement_along_axis) + tcx;
    const res_y =
      Math.round(Math.sin(vector_angle) * placement_along_axis) + tcy;
    // now [res_x + tcx, res_y + tcy] is x,y for point ALONG the vector between targ and prox
    // now to RANDOMIZE away from this vector
    const noise_factor = 50;
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
    const noise_factor = 50;
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

  useEffect(() => {
    // Bind d3
    // svgRef.current = mapRef;
    if (boutsQuery.isSuccess) {
      const pretty_bouts = boutsQuery.data.status.map((d) => {
        let j_id = d.id;
        let target = select("#" + d.joint_name_selector);
        let prox_target = select("#" + d.proximal_joint_selector);
        // could also choose to 'select' the 'svg_zone' ???

        // now calculating the size of the dot proportional to rpe&duration
        // rpe should be threshold, ie over 8 it is 2, under that it is 1
        // duration should scale, but slowly
        let intensity = d.rpe / 5;
        d.duration > 10 ? (intensity = intensity + d.duration / 10) : void 0;
        //console.log(d.proximal_joint_selector);
        if (d.tissue_type == "capsular") {
          let bout_points = calc_capsular_bouts(target);
          let point_color = "blue";
          let pkg = [
            bout_points[0],
            bout_points[1],
            point_color,
            j_id,
            intensity,
          ];
          return pkg;
        } else if (d.tissue_type == "rotational") {
          let bout_points = calc_rot_bouts(
            target,
            prox_target,
            d.rotational_value
          );
          let point_color = "#055403";
          let pkg = [
            bout_points[0],
            bout_points[1],
            point_color,
            j_id,
            intensity,
          ];
          return pkg;
        } else {
          let bout_points = calc_rot_and_linear_bouts(target, prox_target);
          let point_color = "#06bd00";
          let pkg = [
            bout_points[0],
            bout_points[1],
            point_color,
            j_id,
            intensity,
          ];
          return pkg;
        }
      });

      console.log(pretty_bouts.at(0));
      console.log(pretty_bouts.at(-1));

      //console.log(svgRef.current);
      const svg = select(svgRef.current);

      //remove previous dots!
      const everything = svg.selectAll(".drawn");
      everything.remove();

      const target = svg
        .select("g")
        .selectAll()
        .data(pretty_bouts, (d) => d[3]);

      target
        .join("circle")
        .classed("drawn", true)
        .attr("id", (d) => d[3])
        .attr("r", (d) => d[4])
        .attr("cx", (d) => d[0])
        .attr("cy", (d) => d[1])
        .attr("fill", (d) => d[2])
        .attr("opacity", 0.5);

      target.exit().remove();
    }
    /* return () => {
      console.log("unmounting...");
      const target = select("g").selectAll("drawn").datum(null);
    }; */
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

  console.log(boutsQuery.data.status.at(0));

  return (
    <div>
      <HumanSvg /* viewbox={(10, 10, 50, 50)} */ ref={svgRef}></HumanSvg>
    </div>
  );
}
