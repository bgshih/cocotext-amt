import React, { Component } from 'react'
import update from 'immutability-helper';
import { Grid, Row, Col } from 'react-bootstrap'
import { Card } from './Card.js'
import { Toolbar } from './Toolbar.js'
import './App.css'


class App extends Component {

  constructor(props) {
    super(props);
    this.state = {
      cards: [],
    }

    this.urlParams = null;
  }

  componentDidMount() {
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
    this.urlParams = parseSearchString(window.location.search.substring(1));

    this.fetchTaskData();    
  }

  fetchTaskData() {
    const fetchUrl = 'textannot/task/' + this.urlParams['hitId'];
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
    const annotationData = this.state.cards;
    const urlParams = this.urlParams;
    
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
    appendField('answerData', JSON.stringify(annotationData));
    document.body.appendChild(form);
    form.submit();
  }
  
  render() {
    const makeCardColumn = (index, card) => (
      <Col key={index.toString()} xs={4} className="CardColumn">
        <Card canvasWidth={256}
              canvasHeight={256}
              cropId={ card.cropId }
              illegible={ card.illegible }
              setIllegible={ (illegible) => {
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
              setUnknownLanguage={ (unknownLanguage) => {
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
        <Row>
          <Col xs={12}>
            <h1>Annotate text in all images</h1>
          </Col>
        </Row>

        <Row>
          <Col xs={12} className="Toolbar">
            <Toolbar instructionClicked={() => { console.log('instructionClicked'); }}
                     submitClicked={() => { this.submit(); }}
                     submitEnabled={ false } />
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
