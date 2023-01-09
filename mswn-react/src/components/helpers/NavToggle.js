import React from 'react';
import { Navbar, Nav } from 'rsuite';
import CogIcon from '@rsuite/icons/legacy/Cog';
import AngleLeftIcon from '@rsuite/icons/legacy/AngleLeft';
import AngleRightIcon from '@rsuite/icons/legacy/AngleRight';
import GearCircleIcon from '@rsuite/icons/legacy/GearCircle';
import DashboardIcon from '@rsuite/icons/Dashboard';
import GroupIcon from '@rsuite/icons/legacy/Group';
import MagicIcon from '@rsuite/icons/legacy/Magic';



export const NavToggle = ({ expand, onChange }) => {
    return (
      <Navbar appearance="subtle" className="nav-toggle">
        <Nav>
          <Nav.Menu
            noCaret
            placement="topStart"
            trigger="click"
            title={<CogIcon style={{ width: 20, height: 20 }} size="sm" />}
          >
            <Nav.Item>Help</Nav.Item>
            <Nav.Item>Settings</Nav.Item>
            <Nav.Item>Sign out</Nav.Item>
          </Nav.Menu>
        </Nav>
  
        <Nav pullRight>
          <Nav.Item onClick={onChange} style={{ width: 56, textAlign: 'center' }}>
            {expand ? <AngleLeftIcon /> : <AngleRightIcon />}
          </Nav.Item>
        </Nav>
      </Navbar>
    );
  };