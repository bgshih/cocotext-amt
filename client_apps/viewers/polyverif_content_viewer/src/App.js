import React, { Component } from 'react';
import ReactDOM from 'react-dom';
// import logo from './logo.svg';
import './App.css';
import { Card } from './Card.js';
import { Grid, Row, Col, FormGroup, FormControl, ControlLabel, Button, ButtonGroup, DropdownButton, MenuItem, ListGroupItem, Alert } from 'react-bootstrap';

import * as constants from './constants.js';
const CONTENT_TYPE = 'CONTENT';
const RESPONSE_TYPE = 'RESPONSE';

class App extends Component {
  constructor(props) {
    super(props);

    this.state = {
      invalidJson: false,
      objectType: CONTENT_TYPE,
      cards: [],
    }
  }

  changeObjectType(type) {
    if (this.objectType !== type) {
      // clear cards
      this.setState({
        objectType: type,
        cards: []
      });
    }
  }

  fetchData(data) {
    try {
      var idList = JSON.parse(data);
    } catch (error) {
      console.warn(error);
      this.setState({
        invalidJson: true
      });
      return;
    }

    this.setState({
      invalidJson: false
    });

    const idStrList = idList.map((id) => (id.toString()));
    const query = idStrList.join(',');
    var fetchUrl;
    if (this.state.objectType === CONTENT_TYPE) {
      fetchUrl = constants.API_SERVER_URL + '/polyverif/_content/' + query;
    } else if (this.state.objectType === RESPONSE_TYPE) {
      fetchUrl = constants.API_SERVER_URL + '/polyverif/_response/' + query;
    } else {
      console.error("Unknown type: " + this.state.objectType);
      return;
    }
    console.log(fetchUrl);

    fetch(fetchUrl)
      .then((response) => response.json())
      .then((responseData) => {
        var newCards = this.state.objectType === CONTENT_TYPE ?
          responseData['contents'] : responseData['responses'];

        for (var i = 0; i < newCards.length; i++) {
          newCards[i]['contentOrResponseId'] = idStrList[i];
        }

        this.setState({
          cards: newCards
        });
      })
      .catch((error) => {
        console.warn(error);
      })
  }

  render() {
    const makeCardCol = (idx, card) => (
      <Col key={idx.toString()} xs={4} className='cardCol'>
        <Card contentOrResponseId={ card.contentOrResponseId }
              canvasWidth={256}
              canvasHeight={256}
              instanceId={ card.id }
              verificationStatus={ card.verification } />
      </Col>
    )

    var cardCols = [];
    for (var i = 0; i < this.state.cards.length; i++) {
      cardCols.push(makeCardCol(i, this.state.cards[i]));
    }

    return (
      <Grid>
        <h1>Content Viewer</h1>

        <form>
          <FormGroup>
            <ControlLabel>
              { this.state.objectType === CONTENT_TYPE ? "Content IDs" : "Response IDs" }
            </ControlLabel>
            <FormControl componentClass="textarea"
                         ref="inputData"
                         placeholder="Input a list of content IDs in JSON format" />
          </FormGroup>

          <ButtonGroup>
            <Button className="btn btn-primary"
                    onClick={ () => {
                      this.fetchData(ReactDOM.findDOMNode(this.refs.inputData).value);
                    } }>
              Fetch
            </Button>
            <DropdownButton id="typeChoice" title={"Object Type: " + this.state.objectType}>
              <MenuItem eventKey="1"
                        onClick={() => { this.changeObjectType(CONTENT_TYPE); }}>
                Content
              </MenuItem>
              <MenuItem eventKey="2"
                        onClick={() => { this.changeObjectType(RESPONSE_TYPE); }}>
                Response
              </MenuItem>
            </DropdownButton>
          </ButtonGroup>

          { this.state.invalidJson === true &&
            <Alert bsStyle='danger'>Invalid JSON</Alert>
          }
        </form>

        <ListGroupItem>
          <Row>
            { cardCols }
          </Row>
        </ListGroupItem>
      </Grid>
    );
  }
}

export default App;
