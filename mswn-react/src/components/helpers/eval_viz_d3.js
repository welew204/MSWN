import React, { useState, useRef, useEffect, useLayoutEffect } from "react";
import { select } from "d3-selection";
import { scaleLinear } from "d3-scale";
import { ReactComponent as HumanSvg } from "./humanOutline2.svg";

export function HumanMap({ data }) {
  const svgRef = useRef(null);

  //useEffect(() => {}, []);
  // initial setting of data from API; useQuery instead

  useEffect(() => {
    // Bind d3
    // svgRef.current = mapRef;
    const svg = select(svgRef.current);

    // ala... svg.select("#head").attr("fill", data.headColor);
    // Add new d3 elements
    // Update existing d3 elements
    // remove old d3 elements
  }, []);
  // update data when bodyData changes

  return (
    <div>
      <HumanSvg ref={svgRef}></HumanSvg>
    </div>
  );
}

export function DrawBouts() {
  const [bodyData, setBodyData] = useState([]);

  useLayoutEffect(() => {
    const target = select("g");
    var joint = select("#jt-r-gh");

    console.log(joint);

    target
      .enter()
      .merge(target)
      .append("circle")
      .attr("id", "trying!")
      .attr("r", "5")
      .attr("cx", "150")
      .attr("cy", "300")
      .attr("stroke", "white")
      .attr("fill", "green");

    target.exit().remove();

    console.log(target);
  }, []);

  return (
    <div>
      <h1> Hi Rik</h1>
    </div>
  );
}
