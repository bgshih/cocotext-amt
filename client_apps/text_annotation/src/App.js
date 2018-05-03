import React, { Component } from 'react'
import update from 'immutability-helper';
import { Grid, Row, Col, Alert } from 'react-bootstrap'
import { Card } from './Card.js'
import { Toolbar } from './Toolbar.js'
import InstructionModal from './InstructionModal.js'
import './App.css'


class App extends Component {

  constructor(props) {
    super(props);
    this.urlParams = this.parseSearchString(window.location.search.substring(1));
    this.state = {
      cards: [],
      showInstruction: this.urlParams['assignmentId'] === 'ASSIGNMENT_ID_NOT_AVAILABLE',
      hitAccepted: this.urlParams['assignmentId'] !== 'ASSIGNMENT_ID_NOT_AVAILABLE',
      submitEnableCountDown: 15
    }
  }

  parseSearchString(searchStr) {
    if (searchStr.startsWith('?')) {
      searchStr = searchStr.substring(1);
    }
    var parts = searchStr.split('&');
    var params = {};
    for (var i = 0; i < parts.length; i++) {
      var pair = parts[i].split('=');
      const key = decodeURIComponent(pair[0]);
      const value = decodeURIComponent(pair[1]);
      params[key] = value;
    }
    return params;
  };

  componentDidMount() {
    this.fetchTaskData();
    this.startCountDown();
  }

  startCountDown() {
    var timerId;
    timerId = setInterval(
      () => {
        if (this.state.submitEnableCountDown > 0) {
          this.setState({
            submitEnableCountDown: this.state.submitEnableCountDown - 1
          });
        } else {
          clearInterval(timerId);
        }
      },
      1000
    );
  }

  fetchTaskData() {
    const fetchUrl = 'textannot/task/' + this.urlParams['hitId'];
    fetch(fetchUrl)
      .then((response) => response.json())
      .then((taskData) => {
        const textInstanceIds = taskData['textInstances'];
        var cards = [];
        for (var textInstanceId of textInstanceIds) {
          const card = {
            textInstanceId: textInstanceId,
            text: "",
            illegible: false,
            unknownLanguage: false,
          };
          cards.push(card);
        }
        this.setState({
          cards: cards
        });
      })
      .catch((error) => {
        console.error(error);
      });
  }

  submit() {
    const annotationData = this.state.cards;    
    var form = document.createElement("form");
    form.method = 'POST';
    form.action = this.urlParams['turkSubmitTo'] + '/mturk/externalSubmit';
    const appendField = (key, value) => {
      var field = document.createElement("input");
      field.name = key;
      field.value = value;
      form.appendChild(field);
    }
    appendField('assignmentId', this.urlParams['assignmentId']);
    appendField('answerData', JSON.stringify(annotationData));
    document.body.appendChild(form);
    form.submit();
  }
  
  render() {
    const makeCardColumn = (index, card) => (
      <Col key={index.toString()} xs={4} className="CardColumn">
        <Card canvasWidth={256}
              canvasHeight={256}
              textInstanceId={ card.textInstanceId }
              text={ card.text }
              setText={ (text) =>
                {
                  const newCards = update(
                    this.state.cards,
                    {
                      [index]: {text: {$set: text}}
                    }
                  );
                  this.setState({cards: newCards});
                }
              }
              illegible={ card.illegible }
              setIllegible={ (illegible) =>
                {
                  const newCards = update(
                    this.state.cards,
                    {
                      [index]: {illegible: {$set: illegible}}
                    }
                  );
                  this.setState({cards: newCards});
                }
              }
              unknownLanguage={ card.unknownLanguage }
              setUnknownLanguage={ (unknownLanguage) =>
                {
                  const newCards = update(
                    this.state.cards,
                    {
                      [index]: {unknownLanguage: {$set: unknownLanguage}}
                    }
                  );
                  this.setState({ cards: newCards });
                }
              } />
      </Col>
    )

    var cardColumnArray = []
    for (var i = 0; i < this.state.cards.length; i++) {
      cardColumnArray.push(makeCardColumn(i, this.state.cards[i]));
    }

    return (
      <Grid>
        <InstructionModal show={this.state.showInstruction}
                          hideClicked={ () => { this.setState({showInstruction: false}) } }
                          pausePenalty={ false }
                          pausePenaltyCountdown={ 0 } />

        <Row>
          <Col xs={12}>
            <h1>Annotate text in every image</h1>
          </Col>
        </Row>

        {this.urlParams['assignmentId'] === 'ASSIGNMENT_ID_NOT_AVAILABLE' &&
          <Alert bsStyle='danger'>
            <b>WARNING!</b> You have not accepted this HIT yet. Your work will not be saved.
          </Alert>
        }

        <Row>
          <Col xs={12} className="Toolbar">
            <Toolbar instructionClicked={() => { this.setState({showInstruction: !this.state.showInstruction}) }}
                     submitClicked={() => { this.submit(); }}
                     hitAccepted={ this.state.hitAccepted }
                     submitEnableCountDown={ this.state.submitEnableCountDown }/>
          </Col>
        </Row>
        
        <Row>
          { cardColumnArray }
        </Row>
      </Grid>
    )
  }
}

export default App;
