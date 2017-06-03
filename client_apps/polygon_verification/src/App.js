import React, { Component } from 'react';
import './App.css';
import { Grid, Row, Col, ListGroup, ListGroupItem } from 'react-bootstrap';
import { Toolbar } from './Toolbar';
import { Card } from './Card';
import SubmitModal from './SubmitModal';
import InstructionModal from './InstructionModal';
import update from 'immutability-helper';


class App extends Component {
  constructor(props) {
    super(props);
    this.urlParams = null;

    this.state = {
      cards: [],
      urlParams: null,
      showSubmitModal: false,
      showInstructionModal: false
    }
  }

  componentDidMount() {
    this.fetchTaskData();
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
    this.setState({
      urlParams: urlParams
    })

    const fetchUrl = window.location.origin + '/poly-verif-task/by-hit/' + urlParams['hitId'];
    fetch(fetchUrl)
      .then((response) => response.json())
      .then((tasksData) => {
        var cards = [];
        for (var task of tasksData) {
          const card = {
            id: task.id,
            verification: task.verification,
            imageUrl: task.imageUrl,
            polygon: task.polygon,
          }
          cards.push(card);
        }
        this.setState({
          cards: cards
        });
      });
  }

  submit() {
    const urlParams = this.state.urlParams;

    var form = document.createElement("form");
    form.method = 'POST';
    form.action = urlParams.turkSubmitTo + '/mturk/externalSubmit';
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

  render() {
    const handleCardClicked = (idx) => () => {
      const oldCards = this.state.cards;
      if (idx >= oldCards.length) {
        console.error('Internal error: Exceeded maximum legnth.');
        return;
      }
      const oldCard = oldCards[idx];
      const oldVerification = oldCard.verification;
      const transitionTable = {
        'UNVERIFIED': 'WRONG',
        'WRONG': 'UNSURE',
        'UNSURE': 'UNVERIFIED',
        'CORRECT': 'UNVERIFIED' // should not happen
      }
      var newVerification = transitionTable[oldVerification];
      const newCard = update(oldCard, {
        verification: {$set: newVerification}
      });
      const newCards = update(oldCards, {
        $splice: [[idx, 1, newCard]]
      });
      this.setState({cards: newCards})
    }

    const makeCardCol = (idx, card) => (
      <Col xs={4} className='cardCol'>
        <Card onCardClicked={ handleCardClicked(idx) }
              verification={ card.verification }
              canvasWidth={256}
              canvasHeight={256}
              imageUrl={ card.imageUrl }
              polygon={ card.polygon } />
      </Col>
    )

    var cardCols = [];
    for (var i = 0; i < this.state.cards.length; i++) {
      cardCols.push(makeCardCol(i, this.state.cards[i]));
    }

    return (
      <Grid>
        <h1>Review these annotations</h1>

        <ListGroup>
          <ListGroupItem>
            <Toolbar instructionClicked={ () => {
                       this.setState({ showInstructionModal: !this.state.showInstructionModal })
                     } }
                     submitClicked={ () => {
                       this.setState({ showSubmitModal: !this.state.showSubmitModal })
                     } } />
          </ListGroupItem>

          <ListGroupItem>
            <Grid>
              <Row>
                { cardCols }
              </Row>
            </Grid>
          </ListGroupItem>
        </ListGroup>

        <SubmitModal show={ this.state.showSubmitModal }
                     hideClicked={ () => { this.setState({ showSubmitModal: false }) } }
                     submitConfirmed={ this.submit.bind(this) } />
        <InstructionModal show={ this.state.showInstructionModal }
                          hideClicked={ () => { this.setState({ showInstructionModal: false }) } } />
      </Grid>
    );
  }
}

export default App;
