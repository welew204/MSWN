import React, { useState, useRef, useEffect } from "react";
import { select } from "d3-selection";
import { scaleLinear } from "d3-scale";
import humanSvg from "..../body_svg/humanOutline.svg";

export default function HumanMap({ data }) {
  const svgRef = useRef(null);

  const [bodyData, setBodyData] = useState([]);

  useEffect(() => {}, []);
  // initial setting of data from API; useQuery instead

  useEffect(() => {
    // Bind d3
    const svg = select(svgRef.current);
    // ala... svg.select("#head").attr("fill", data.headColor);
    // Add new d3 elements
    // Update existing d3 elements
    // remove old d3 elements
  }, [bodyData]);
  // update data when bodyData changes
  return (
    <div>
      <svg ref={svgRef}>
        {/* several 'zone' shapes that I can attach 
      and set attributes on ala */}
      </svg>
    </div>
  );
}
