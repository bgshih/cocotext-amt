import React, { Component } from 'react';
import { Grid, Row, Col, ListGroup, ListGroupItem, Alert } from 'react-bootstrap';
import { Canvas } from './Canvas.js';
import { Toolbar } from './Toolbar.js';
import './App.css';


export class App extends Component {
  constructor(props) {
    super(props);

    this.state = {
      alertType: 'info',
      alertContent: '',
      imageUrl: null,
      hints: [],
      existingPolygons: [],
      urlParams: {}
    }
  }

  setInfobar(type, content) {
    this.setState({
      'alertType': type,
      'alertContent': content
    })
  }

  componentDidMount() {
    this.setInfobar('info', 'To start drawing, click the "New Polygon" button.');
    this.fetchTaskData();
  }

  fetchTaskData() {
    // parse URL
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
    var urlParams = parseSearchString(window.location.search.substring(1));
    for (var k in urlParams) {
      console.log('key: ' + k + '; value: ' + urlParams[k]);
    }

    this.setState({
      urlParams: urlParams
    })

    // fetch task data and set state
    const fetchUrl = window.location.origin + '/poly-annot-task/by-hit/' + urlParams['hitId'];
    console.log('Fetching ' + fetchUrl);
    fetch(fetchUrl)
      .then((response) => response.json())
      .then((responseJson) => {
        this.setState({
          'imageUrl': responseJson.imageUrl,
          'hints': responseJson.hints,
          'existingPolygons': responseJson.existingPolygons,
        })
      });
  }

  render() {
    return (
      <Grid> <Row> <Col>
        <h2>Draw polygons around the words hinted by stars</h2>

        <ListGroup>
          <ListGroupItem>
            <Toolbar setInfobar={this.setInfobar.bind(this)} />
          </ListGroupItem>

          <ListGroupItem>
            <Canvas width="800"
                    height="600"
                    imageUrl={this.state.imageUrl}
                    hints={this.state.hints}
                    existingPolygons={this.state.existingPolygons}
                    urlParams={this.state.urlParams} />
          </ListGroupItem>

          <Alert bsStyle={this.state.alertType}>{this.state.alertContent}</Alert>
        </ListGroup>
        
      </Col> </Row> </Grid>
    );
  }
}

export default App;
