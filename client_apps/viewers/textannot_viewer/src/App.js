import React, { Component } from 'react';
import { Grid, Row, Col } from 'react-bootstrap'
import { Card } from './Card.js'
import logo from './logo.svg';
import './App.css';

class App extends Component {

  constructor(props) {
    super(props);
    this.state = {
      cards: [],
    }
  }

  componentDidMount() {
    this.fetchData();
  }

  fetchData() {
    const fetchUrl = '/textannot/response/' + window.location.search;
    fetch(fetchUrl)
      .then((response) => response.json())
      .then((responseData) => {
        this.setState({
          cards: responseData['responses']
        });
      })
      .catch((error) => {
        console.error(error);
      });
  }

  render() {
    const makeCardColumn = (index, card) => (
      <Col key={index.toString()} xs={4} className="CardColumn">
        <Card canvasWidth={256}
              canvasHeight={256}
              textInstanceId={ card.textInstanceId }
              text={ card.text }
              illegible={ card.illegible }
              unknownLanguage={ card.unknownLanguage }
              worker={ card.worker }/>
      </Col>
    )

    var cardColumnArray = []
    for (var i = 0; i < this.state.cards.length; i++) {
      cardColumnArray.push(makeCardColumn(i, this.state.cards[i]));
    }

    return (
      <Grid>
        <Row>
          { cardColumnArray }
        </Row>
      </Grid>
    );
  }
}

export default App;
