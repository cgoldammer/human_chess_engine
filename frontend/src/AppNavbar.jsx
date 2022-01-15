import React, { Component } from 'react';
import { Nav, Navbar, NavDropdown, Modal, NavItem, MenuItem } from 'react-bootstrap';

export const appName = 'Human Moves';

export class AppNavbar extends React.Component {
  constructor(props){
    super(props);
    this.state = { showAbout: false };
  }
  setAbout = val => this.setState({ showAbout: val })
  render = () => {
    return (
      <div style={{ marginBottom: 0 }}>
        <Navbar collapseOnSelect style={{ marginBottom: 0, borderRadius: 0 }}>
          <Navbar.Header>
            <Navbar.Brand>
              <a href='#brand'>{ appName } </a>
            </Navbar.Brand>
            <Navbar.Toggle />
          </Navbar.Header>
          <Navbar.Collapse>
            <Nav pullRight>
              <NavItem onClick={ () => this.setAbout(true) }>
                About
              </NavItem>
            </Nav>
          </Navbar.Collapse>
        </Navbar>
        <Modal show={this.state.showAbout} onHide={() => this.setAbout(false)}>
          <Modal.Header closeButton>
            <Modal.Title>About</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <p>This tells you what a human would play in a position.  </p>
            <p>This is based on Lichess data. We use a neural network
            to predict the moves that humans have played</p>
            <p>For more about me, check out <a target='_blank' href='https://www.chrisgoldammer.com'>my homepage</a>!</p>
            <p>If you have feedback or ideas, just send me an <a href='mailto:goldammer.christian@gmail.com'>email</a>!</p>
          </Modal.Body>
        </Modal>
      </div>
    );
  }
}
