import React, { Component } from 'react';
import './App.css';
import { Grid, Row, Col, ListGroup, ListGroupItem, Alert } from 'react-bootstrap';
import update from 'immutability-helper';

import { Toolbar } from './Toolbar';
import { Card } from './Card';
import SubmitModal from './SubmitModal';
import InstructionModal from './InstructionModal';
import * as constants from './constants';


class App extends Component {
  constructor(props) {
    super(props);

    this.state = {
      cards: [],
      urlParams: null,
      showSubmitModal: false,
      showInstructionModal: false,
      previewMode: false,
      pausePenalty: false,
      pausePenaltyCountdown: 0,
      gtAnswers: {} 
    }
  }

  componentDidMount() {
    this.fetchTaskData();

    this.setAllCardStatus('W');
  }

  fetchTaskData() {
    // parse URL parameters
    const parseSearchString = (searchStr) => {
      if (searchStr.startsWith('?')) {
        searchStr = searchStr.substring(1);
      }
      var parts = searchStr.split('&');
      var params = {}
      for (var i = 0; i < parts.length; i++) {
        var pair = parts[i].split('=');
        const key = decodeURIComponent(pair[0]);
        const value = decodeURIComponent(pair[1]);
        params[key] = value;
      }
      return params;
    }
    const urlParams = parseSearchString(window.location.search.substring(1));
    for (var k in urlParams) {
      console.log('key: ' + k + '; value: ' + urlParams[k]);
    }

    if (!('hitId' in urlParams && 'assignmentId' in urlParams)) {
      console.error('Invalid URL parameters');
      return;
    }

    this.setState({ urlParams: urlParams })

    // preview mode
    if (urlParams['assignmentId'] === 'ASSIGNMENT_ID_NOT_AVAILABLE') {
      this.setState({
        previewMode: true,
        showInstructionModal: true,
      })
    }

    const fetchUrl = constants.API_SERVER_URL + '/polyverif/' + urlParams['hitId'];
    fetch(fetchUrl)
      .then((response) => response.json())
      .then((taskData) => {
        const contents = taskData['contents'];
        var cards = [];
        for (var content of contents) {
          const card = {
            instanceId: content.id,
            verificationStatus: content.verification
          }
          cards.push(card);
        }
        this.setState({
          cards: cards
        });

        // fetch groundtruth sentinel contents
        this.setState({
          gtAnswers: taskData['gtAnswers']
        });
      });
  }

  checkSentinelCorrect() {
    // check gtAnswers
    const gtAnswers = this.state.gtAnswers;
    var correct = true;
    for (var card of this.state.cards) {
      if (gtAnswers[card.instanceId] !== undefined &&
          gtAnswers[card.instanceId] !== card.verificationStatus) {
        correct = false;
      }
    }

    this.setState({
      hasCheckedSentinel: true
    });

    return correct;
  }
  
  startPenaltyPause(pauseSeconds=15) {
    // close submit modal, show instruction modal, and start a penalty pause countdown
    this.setState({
      showSubmitModal: false,
      showInstructionModal: true,
      pausePenalty: true,
      pausePenaltyCountdown: pauseSeconds
    });

    var timerId;
    timerId = setInterval(
      () => {
        if (this.state.pausePenaltyCountdown > 0) {
          this.setState({
            pausePenaltyCountdown: this.state.pausePenaltyCountdown - 1
          });
        } else {
          // penalty time up
          this.setState({
            pausePenalty: false
          });
          // clear timer
          clearInterval(timerId);
        }
      },
      1000
    );
  }

  submit() {
    // check sentinel correctness before submit to MTurk
    // TODO
    if (!this.state.hasCheckedSentinel && this.checkSentinelCorrect() === false) {
      this.startPenaltyPause(15);
      return;
    }
    
    const urlParams = this.state.urlParams;

    // submit answer to MTurk
    var form = document.createElement("form");
    form.action = urlParams.turkSubmitTo + '/mturk/externalSubmit';
    form.method = 'POST';
    const appendField = (key, value) => {
      var field = document.createElement("input");
      field.name = key;
      field.value = value;
      form.appendChild(field);
    }
    appendField('assignmentId', urlParams.assignmentId);
    appendField('answerData', JSON.stringify(this.state.cards));
    document.body.appendChild(form);

    form.submit();
  }

  setAllCardStatus(newStatus) {
    const oldCards = this.state.cards;
    var newCards = [];
    for (var i = 0; i < oldCards.length; i++) {
      const oldCard = oldCards[i];
      const newCard = update(oldCard, {
        verificationStatus: {$set: newStatus}
      });
      newCards.push(newCard);
    }
    this.setState({cards: newCards});
  }

  render() {
    const handleCardClicked = (idx) => () => {
      const oldCards = this.state.cards;
      if (idx >= oldCards.length) {
        console.error('Internal error: Exceeded maximum legnth.');
        return;
      }
      const oldCard = oldCards[idx];
      const oldVerification = oldCard.verificationStatus;
      const transitionTable = {
        'U': 'W',
        'W': 'C',
        'C': 'W'
      }
      var newVerification = transitionTable[oldVerification];
      const newCard = update(oldCard, {
        verificationStatus: {$set: newVerification}
      });
      const newCards = update(oldCards, {
        $splice: [[idx, 1, newCard]]
      });
      this.setState({cards: newCards});
    }

    const makeCardCol = (idx, card) => (
      <Col key={idx.toString()} xs={4} className='cardCol'>
        <Card onCardClicked={ handleCardClicked(idx) }
              canvasWidth={256}
              canvasHeight={256}
              instanceId={ card.instanceId }
              verificationStatus={ card.verificationStatus } />
      </Col>
    )

    var cardCols = [];
    for (var i = 0; i < this.state.cards.length; i++) {
      cardCols.push(makeCardCol(i, this.state.cards[i]));
    }

    return (
      <Grid>
        <h1>Review these annotations</h1>

        { this.state.previewMode === true &&
          <Alert bsStyle='danger'>You are in the preview mode. Your edits will not be stored until you accept this HIT.</Alert>
        }

        <ListGroup>
          <ListGroupItem>
            <Toolbar setAllCorrectClicked={ () => this.setAllCardStatus('C') }
                     setAllWrongClicked={ () => this.setAllCardStatus('W') }
                     instructionClicked={ () => {
                       this.setState({ showInstructionModal: !this.state.showInstructionModal })
                     } }
                     submitClicked={ () => {
                       if (this.state.previewMode) {
                         return;
                       } else if (this.state.pausePenalty === true) {
                         this.setState({ showInstructionModal: true })
                       } else {
                        this.setState({ showSubmitModal: !this.state.showSubmitModal })
                       }
                     } }
                     submitEnabled={ !this.state.previewMode }
            />
          </ListGroupItem>

          <ListGroupItem>
            <Row>
              { cardCols }
            </Row>
          </ListGroupItem>
        </ListGroup>

        <SubmitModal show={ this.state.showSubmitModal }
                     hideClicked={ () => { this.setState({ showSubmitModal: false }) } }
                     submitConfirmed={ this.submit.bind(this) } />
        <InstructionModal show={ this.state.showInstructionModal }
                          hideClicked={ () => { this.setState({ showInstructionModal: false }) } }
                          pausePenalty={ this.state.pausePenalty }
                          pausePenaltyCountdown={ this.state.pausePenaltyCountdown }
                          />
      </Grid>
    );
  }
}

export default App;
