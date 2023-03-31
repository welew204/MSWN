import React, { useEffect, useState } from "react";
import { NavLink, Link, Outlet } from "react-router-dom";
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
  Loader,
  Panel,
  List,
} from "rsuite";
import { useQuery, useMutation } from "@tanstack/react-query";

export default function Coaches() {
  return (
    <Panel
      style={{
        marginLeft: "auto",
        marginRight: "auto",
        marginTop: "15vh",
        width: "500px",
        margin: "30px",
      }}
      header='Coaches'
      shaded
      bordered
      bodyFill>
      <List style={{ margin: "15px", width: "100%" }} hover bordered>
        <List.Item>Will Belew</List.Item>
        <List.Item>Marlie Couto</List.Item>
        <List.Item>Dewey Nielsen</List.Item>
        <List.Item>Guest</List.Item>
      </List>
    </Panel>
  );
}
