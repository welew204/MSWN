import React, { useState } from "react";
import { NavLink, Link, useOutletContext } from "react-router-dom";
import { RsNavLink } from "./helpers/RsNavLink";
import {
  Container,
  Header,
  Content,
  Footer,
  Sidebar,
  Navbar,
  Nav,
  Sidenav,
  SidenavBody,
  Button,
  Timeline,
  Stack,
  Panel,
  Divider,
  Whisper,
} from "rsuite";
import CogIcon from "@rsuite/icons/legacy/Cog";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { NavToggle } from "./helpers/NavToggle";
import { HumanMap, DrawBouts } from "./helpers/eval_viz_d3";

const server_url = "http://127.0.0.1:8000";

export default function StatusView() {
  return (
    <div>
      <HumanMap />
    </div>
  );
}
