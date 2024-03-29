import React from 'react';
import ReactDOM from 'react-dom';
import { DropdownItem, Dropdown, Jumbotron, Alert, HelpBlock, Label, Form, FormGroup, ControlLabel, ToggleButtonGroup, ToggleButton, ButtonGroup, Panel, ListGroup, ListGroupItem, Navbar, Nav, NavItem, NavDropdown, Button, DropdownButton, MenuItem, FormControl, Breadcrumb, Modal, Grid, Row, Col } from 'react-bootstrap';
import Select from 'react-select'
import Chess from 'chess.js';

import { AppNavbar } from './AppNavbar.jsx';
import { List } from 'immutable';
import { Board, MoveTable } from './ChessApp.jsx';
import { WithMoveValidation } from './ChessApp2.jsx';

import { getAllFeatures, getPrediction } from './helpers.jsx';

import 'rc-slider/assets/index.css';
import 'rc-tooltip/assets/bootstrap.css';
import Slider from 'rc-slider';


const crazyMiddleGame = 'r1b1r3/pp1n1pk1/2pR1np1/4p2q/2B1P2P/2N1Qp2/PPP4R/2K3N1 w - - 1 18';
const startingPosition = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
const fens = {
  'Starting Position': startingPosition,
  'Crazy Middlegame': crazyMiddleGame,
  'Simple bishop vs knight endgame': '8/p4k1p/1pn5/6B1/8/5P2/P3K1PP/8 w - - 3 38',
  'Rook endgame': '8/8/1r3k2/R4pp1/8/6P1/6K1/8 w - - 0 55',
  'Tricky Kings Indian Position': 'r1b1q1k1/pp1nn1bp/3p3r/3Pp1p1/1PN1Pp2/2N2P2/P3BBPP/R2Q1RK1 w - - 2 17',
  'Poisoned rook': '3r2k1/2r2ppp/8/8/8/8/PR3PPP/2R3K1 w - - 0 55',
  'Mating attack': 'r2qr1k1/ppp2p2/2np1b1Q/8/6b1/P2B1N2/1PPK1PPP/RN5R w - - 0 1',
};

const OUTCOME_LOSS = 0;
const OUTCOME_BLUNDER = 1;

const start = crazyMiddleGame;

var startingState = () => {
  var state = {
    elo: 2000,
    calculating: true,
    probs: [],
    totalTime: 300,
    timeLeft: 200,
    numMovesShown: 4,
    fen: start
  };
  
  return state;
};


export class ColorPicker extends React.Component {
  constructor(props){
    super(props);
  }
  render = () => {
    return (
      <Row>
        <Col xs={6}>
          <div> Color to move </div>
        </Col>
        <Col xs={6}>
          <ToggleButtonGroup justified type="radio" name="options" value={ this.props.whiteToMove } onChange={value => this.props.setWhiteToMove(value)}>
            <ToggleButton value={ true }>White</ToggleButton>
            <ToggleButton value={ false }>Black</ToggleButton>
          </ToggleButtonGroup>
        </Col>
      </Row>
    );
  }
}

export class FenSelector extends React.Component {
  keyShow = key => {
    return (
      <MenuItem key={key} onClick={ () => this.props.setFen(fens[key]) }> { key }  </MenuItem>
    );
  }


  render = () => {
    return (
      <div style={{padding: '20px'}}>
        <Row style={{marginTop: '10px'}}>
          <ButtonGroup justified>
            <DropdownButton id='dd' className='btn-block' block={true} title='Select position'>
              { Object.keys(fens).map(this.keyShow) }
            </DropdownButton>
          </ButtonGroup>
        </Row>
        <Row style={{marginTop: '10px'}}>
          <Form horizontal>
            <FormGroup>
              <Col componentClass={ControlLabel} xs={2}>fen</Col>
              <Col xs={10}>
                <FormControl
                  ref='inputNode'
                  type='text'
                  value={ this.props.fen }
                  onChange={ this.props.onChange }
                />
              </Col>
            </FormGroup>
          </Form>
        </Row>
      </div>
    );
  }

}


const moveStyle = {
  fontSize: '100%',
  background: 'transparent',
  border: '2px solid #0099CC',
  borderRadius: '5px',
  marginTop: '5px',
  cursor: 'pointer',
  textAlign: 'center',
};

        // <Button onClick={ () => makeMove(move)} style={moveStyle}>
        //   {move}: {prob}%
        // </Button>
const showProb = makeMove => moveProb => {
  const move = moveProb[0];
  const prob = (100 * moveProb[1]).toFixed(0);
  return (
    <div className="text-center" key={moveProb[0]}> 
      <Col xs={3}>
        <span style={{'fontSize': '125%'}}> {move}: {prob}% </span>
      </Col>
    </div>)
}

export class ShowProbs extends React.Component {
  constructor(props){
    super(props);
  }

  render = () => {
    return (
      <Row style={{'marginTop': '20px'}}>
        {this.props.probs.slice(0, this.props.numMovesShown).map(showProb(this.props.makeMove))}
      </Row>
    )
  }
}


/* The main app, which pulls in all the other windows. */
export class App extends React.Component {
  constructor(props){
    super(props);
    this.state = startingState();
  }
  setElo = elo => {
    this.setState({ elo: elo });
  };
  onChange = e => this.setFen(e.target.value)
  getFen = () => this.state.fen;
  setFen = (fen) => {
    this.setState({fen: fen}, () => this.calculateScore());
  }
  makeMove = move => {
    var logic = new Chess(this.getFen());
    logic.move(move, {sloppy: true});
    const fen = logic.fen();
    console.log("Setting to: " + fen);
    this.setFen(fen);
    //this.setFen('rnbqkbnr/pppppppp/8/8/8/P7/1PPPPPPP/RNBQKBNR b KQkq - 0 1');
  }
  setProbs = probs => this.setState({probs: probs});
  setTotalTime = totalTime => this.setState({totalTime: totalTime});
  setTimeLeft = timeLeft => this.setState({timeLeft: timeLeft});
  async calculateScore () {
    this.setState({'calculating': true});
    const fen = this.getFen();
    const isWhite = this.state.isWhite;
    const elo = this.state.elo;
    const totalTime = this.state.totalTime;
    const timeLeft = this.state.timeLeft;
    const pred = await getPrediction(fen, elo, elo, totalTime, timeLeft);
    const outcome = this.state.outcome;
    this.setProbs(pred);
    this.setState({'calculating': false});
  }
  componentDidMount = () => {
    this.calculateScore();
  }

  render = () => {
    return (
      <div>
        <AppNavbar/>
        <Grid fluid={true}>
          <Col sm={6} smOffset={3}>
            <Alert>Warning: This is a toy algorithm! Click on the board to play the moves!</Alert>
            <WithMoveValidation fen={this.getFen()} setFen={this.setFen}/>
            <ShowProbs probs={this.state.probs} numMovesShown={this.state.numMovesShown} makeMove={this.makeMove}/>
            <FenSelector fen={this.getFen()} onChange={this.onChange} setFen={this.setFen}/>
            <Row>
            </Row>
            <Row>
              <Form horizontal>
                <FormGroup>
                  <Col componentClass={ControlLabel} xs={4}>Lichess Rating</Col>
                  <Col xs={7}>
                    <Slider min={500} max={2200} value={ this.state.elo } onChange={this.setElo} onAfterChange={ () => this.calculateScore() }/>
                  </Col>
                  <Col style={{fontSize:'20px'}} xs={3}>
                    { this.state.elo }
                  </Col>
                </FormGroup>
              </Form>
            </Row>
          </Col>
        </Grid>
      </div>
    );
  }
}

App.defaultProps = {
  showInput: false
};


// <ResultDisplay expectedLoss={ this.state.expectedLoss }/>
