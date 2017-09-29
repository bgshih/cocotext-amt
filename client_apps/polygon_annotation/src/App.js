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
      urlParams: {},
      hasRemainingText: false,
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

    const urlParams = this.parseUrlParams();
    this.fetchTaskData(urlParams);

    this.setState({
      urlParams: urlParams
    });
  }

  parseUrlParams() {
    // parse URL
    const parseSearchString = (searchStr) => {
      console.log(searchStr);
      
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

    return urlParams;
  }

  fetchTaskData(urlParams) {
    // fetch task data and set state
    const fetchUrl = window.location.origin + '/polyannot/task/' + urlParams['hitId'];
    fetch(fetchUrl)
      .then((response) => response.json())
      .then((taskData) => {
        this.setState({
          'imageUrl': taskData.imageUrl,
          'hints': taskData.hints,
          'staticPolygons': taskData.staticPolygons,
        })
      });
  }

  render() {
    return (
      <Grid> <Row> <Col>
        <h2>Draw polygons to surround every word in this image</h2>

        <ListGroup>
          {this.state.urlParams.assignmentId === 'ASSIGNMENT_ID_NOT_AVAILABLE' &&
            <Alert bsStyle='danger'><b>WARNING!</b> You have not accepted this HIT yet. Your work will not be saved.</Alert>
          }

          <ListGroupItem>
            <Toolbar setInfobar={this.setInfobar.bind(this)}
                     hasRemainingText={this.state.hasRemainingText}
                     onSetHasRemainingText={(has) => { this.setState({hasRemainingText: has}); }} />
          </ListGroupItem>

          <ListGroupItem>
            <Canvas width="1000"
                    height="800"
                    imageUrl={this.state.imageUrl}
                    hints={this.state.hints}
                    staticPolygons={this.state.staticPolygons}
                    urlParams={this.state.urlParams}
                    hasRemainingText={this.state.hasRemainingText} />
          </ListGroupItem>

          <Alert bsStyle={this.state.alertType}>{this.state.alertContent}</Alert>
        </ListGroup>
        
      </Col> </Row> </Grid>
    );
  }
}

export default App;
