import React, { Component } from 'react'
import { Grid, Row, Col } from 'react-bootstrap'
import { Card } from './Card.js'
import logo from './logo.svg'
import './App.css'


class App extends Component {

  constructor(props) {
    super(props);
    this.state = {
      cards: [],
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
      var params = {};
      for (var i = 0; i < parts.length; i++) {
        var pair = parts[i].split('=');
        const key = decodeURIComponent(pair[0]);
        const value = decodeURIComponent(pair[1]);
        params[key] = value;
      }
      return params;
    };
    const urlParams = parseSearchString(window.location.search.substring(1));

    const fetchUrl = window.location.origin + '/textannot/task/' + urlParams['hitId'];
    fetch(fetchUrl)
      .then((response) => response.json())
      .then((taskData) => {
        const cropIds = taskData['crop_names'];
        var cards = [];
        for (var cropId of cropIds) {
          const card = {
            cropId: cropId,
            textAnnotation: null,
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

  }
  
  render() {
    const makeCardColumn = (index, card) => (
      <Col key={index.toString()} xs={4} className='cardColumn'>
        <Card canvasWidth={256}
              canvasHeight={256}
              cropId={ card.cropId } />
      </Col>
    )

    var cardColumnArray = []
    for (var i = 0; i < this.state.cards.length; i++) {
      cardColumnArray.push(makeCardColumn(i, this.state.cards[i]));
    }

    return (
      <Grid>
        <Row>
          <h1>Annotate text in all images</h1>
        </Row>
        <Row>
          { cardColumnArray }
        </Row>
      </Grid>
    )
  }
}

export default App;
