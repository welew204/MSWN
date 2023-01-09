import React, { useState } from "react";
import { NavLink, Link } from "react-router-dom";
import { RsNavLink } from "./helpers/RsNavLink";
import {
  Container,
  Header,
  Content,
  Footer,
  Sidebar,
  Navbar,
  Button,
  Nav,
  Sidenav,
  SidenavBody,
} from "rsuite";
import CogIcon from "@rsuite/icons/legacy/Cog";
import { useQuery, useMutation } from "@tanstack/react-query";
import { NavToggle } from "./helpers/NavToggle";

const server_url = "http://127.0.0.1:8000";

export default function RecordWkout() {
  return (
    <div className="rw">
      <div className="rw-inp">
        <h1>Workout</h1>
        <h3>Input Res (and Rx)</h3>
      </div>
      <div className="wbld-bt">
        <Button as={RsNavLink} href="/mover">
          Clear Input
        </Button>
        <Button as={RsNavLink} href="/record">
          Record A Workout
        </Button>
      </div>
    </div>
  );
}
