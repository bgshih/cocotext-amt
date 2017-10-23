import React, { Component } from 'react';
import './App.css';
import update from 'immutability-helper';
import {Grid, Button, ButtonToolbar, Alert} from 'react-bootstrap';
import { MultiImagesViewer } from './MultiImagesViewer';

const API_SERVER_URL = window.location.origin;
const WORKER_ID = 'A383I2LLYX9LJM';


class App extends Component {
  constructor(props) {
    super(props);
    
    this.state = {
      imagesList: [
        {
          imageId: 98882,
          annotations: [
            {
              polygon: [
                {x: 100, y: 100},
                {x: 200, y: 100},
                {x: 200, y: 200},
                {x: 100, y: 200}
              ]
            },
          ],
          userMark: 'C'
        }
      ],
      showInstructions: true
    };
  }

  fetchImagesList() {
    const fetchUrl = API_SERVER_URL + '/polyannot/_annotations/unverified/';
    fetch(fetchUrl)
      .then((response) => response.json())
      .then((responseData) => {
        const imagesList = responseData['imagesList'];
        this.setState({imagesList: imagesList});
      })
      .catch((error) => {
        console.warn(error);
      });
  }

  submitUserMarks() {
    var userMarks = {}
    for (var imageAndAnnotation of this.state.imagesList) {
      const submissionId = imageAndAnnotation.submissionId;
      const mark = imageAndAnnotation.userMark;
      userMarks[submissionId] = mark;
    }
    const submitJson = {
      userId: WORKER_ID,
      userMarks: userMarks,
    }

    const fetchUrl = API_SERVER_URL + '/polyannot/_annotations/set_user_marks/';
    fetch(fetchUrl, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(submitJson)
    })
    .then(() => {alert("Submitted. Click Fetch get the next batch.");})
    .catch((error) => {
      console.warn(error);
    });
  }

  render() {
    return (
      <Grid>
        <h1>Verify these annotations</h1>

        {this.state.showInstructions &&
        <Alert bsStyle="info"
               onDismiss={() => {
                 this.setState({showInstructions: false});
               }}>
          <p><strong>Usage</strong></p>
          <ul>
            <li>Click "Fetch" to get images</li>
            <li>Drag image with mouse to move around</li>
            <li>'[' : Zoom out</li>
            <li>']' : Zoom in</li>
            <li>'0' : Zoom to fit</li>
            <li>'left-arrow': Go to previous image.</li>
            <li>'right-arrow': Go to next image.</li>
            <li>'1' : Mark as "Correct and Complete"</li>
            <li>'2' : Mark as "Bad"</li>
            <li>'3' : Mark as "Correct and Incomplete"</li>
            <li>'4' : Mark as "Unverified"</li>
            <li>Click "Submit" to submit your results</li>
          </ul>
          <p>Mark "Unverified" if you are uncertain. In such cases, please contact me with screenshots.</p>
        </Alert>
        }

        <ButtonToolbar>
          <Button onClick={ (e) => { this.fetchImagesList(); }}>
            Fetch
          </Button>

          <Button bsStyle='primary'
                  onClick={ (e) => { this.submitUserMarks(); } }>
            Submit
          </Button>
        </ButtonToolbar>

        <MultiImagesViewer
          imagesList={this.state.imagesList}
          canvasWidth={1000}
          canvasHeight={800}
          setUserMark={(idx, mark) => {
            const newImagesList = update(
              this.state.imagesList,
              {
                [idx]: {userMark: {$set: mark}}
              }
            );
            this.setState({imagesList: newImagesList});
          }} />
      </Grid>
    );
  }
}

export default App;
