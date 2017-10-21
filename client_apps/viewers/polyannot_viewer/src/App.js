import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import './App.css';
import { Grid, FormGroup, FormControl, Button, ButtonGroup, Alert } from 'react-bootstrap';
import { MenuItem, DropdownButton } from 'react-bootstrap';
import update from 'immutability-helper';

import {MultiImagesViewer} from './MultiImagesViewer';

const API_SERVER_URL = window.location.origin;

const QUERY_BY_IMAGE_IDS = 'QUERY_BY_IMAGE_IDS';
const QUERY_BY_WORKER_ID = 'QUERY_BY_WORKER_ID';
const QUERY_UNVERIFIED = 'QUERY_UNVERIFIED';
const QUERY_BY_TASK_IDS = 'QUERY_BY_TASK_IDS';


class App extends Component {
  constructor(props) {
    super(props);
    
    this.state = {
      invalidJson: false,
      imagesList: [],
      queryMode: QUERY_BY_IMAGE_IDS,
      showUnverified: false,
    };
  }

  validateAndParseJson(jsonData) {
    var output;
    try {
      output = JSON.parse(jsonData);
    } catch (error) {
      console.warn(error);
      this.setState({
        invalidJson: true
      });
      return [];
    }
    this.setState({
      invalidJson: false
    });
    return output;
  }

  fetchDataBasedOnMode(inputData) {
    var query, fetchUrl;
    switch (this.state.queryMode) {
      case QUERY_BY_IMAGE_IDS:
        const imageIdList = this.validateAndParseJson(inputData);
        const imageIdStrList = imageIdList.map((id) => (id.toString()));
        query = imageIdStrList.join(',');
        fetchUrl = API_SERVER_URL + '/polyannot/_annotations/by_image_ids/' + query;
        break;
      case QUERY_BY_WORKER_ID:
        const workerId = inputData;
        fetchUrl = API_SERVER_URL + '/polyannot/_annotations/by_worker_id/' + workerId;
        if (this.state.showUnverified === true) {
          fetchUrl += '/unverified/';
        }
        break;
      case QUERY_BY_TASK_IDS:
        const taskIdList = this.validateAndParseJson(inputData);
        const taskIdStrList = taskIdList.map((id) => (id.toString()));
        query = taskIdStrList.join(',');
        fetchUrl = API_SERVER_URL + '/polyannot/_annotations/by_task_ids/' + query;
        break;
      case QUERY_UNVERIFIED:
        fetchUrl = API_SERVER_URL + '/polyannot/_annotations/unverified/';
        break;
      default:
        console.error('Unknown query mode: ' + this.state.queryMode);
        break;
    }
    
    this.fetchImagesList(fetchUrl);
  }

  fetchImagesList(fetchUrl) {
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

  setAdminMarksFromUserMarks() {
    // deep copy imagesList
    const imagesListJson = JSON.stringify(this.state.imagesList);
    var newImagesList = JSON.parse(imagesListJson);
    for (var imageAndAnnotations of newImagesList) {
      if (imageAndAnnotations !== null) {
        const hasRemainingText = imageAndAnnotations.hasRemainingText;
        if (hasRemainingText === null) {
          imageAndAnnotations.adminMark = 'U';
        } else if (hasRemainingText === true) {
          imageAndAnnotations.adminMark = 'R';
        } else if (hasRemainingText === false) {
          imageAndAnnotations.adminMark = 'C';
        }
      }
    }
    this.setState({
      imagesList: newImagesList
    })
  }

  submitAdminMarks() {
    var adminMarks = {}
    for (var imageAndAnnotation of this.state.imagesList) {
      const submissionId = imageAndAnnotation.submissionId;
      const mark = imageAndAnnotation.adminMark;
      adminMarks[submissionId] = mark;
    }
    const fetchUrl = API_SERVER_URL + '/polyannot/_annotations/set_admin_marks/';
    fetch(fetchUrl, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',    
      },
      body: JSON.stringify(adminMarks)
    })
    .then(() => {alert("Submitted");})
    .catch((error) => {
      console.warn(error);
    });
  }

  render() {
    const placeholderTextDict = {
      QUERY_BY_IMAGE_IDS: "Input a list of image IDs in JSON format",
      QUERY_UNVERIFIED: "Leave blank",
      QUERY_BY_WORKER_ID: "Input worker ID",
      QUERY_BY_TASK_IDS: "Input a list of task IDs in JSON format"
    }

    return (
      <Grid>
        <h1>Image Annotation Browswer</h1>

        <form>
          <FormGroup>
            <FormControl componentClass="textarea"
                         ref="inputData"
                         placeholder={placeholderTextDict[this.state.queryMode]} />
          </FormGroup>

          <ButtonGroup>
            <Button className="btn btn-primary"
                    onClick={ () => {
                      this.fetchDataBasedOnMode(ReactDOM.findDOMNode(this.refs.inputData).value);
                    } }>
              Update
            </Button>
            <DropdownButton id="typeChoice" title={"Query Mode: " + this.state.queryMode}>
              <MenuItem eventKey="1"
                        onClick={() => { this.setState({queryMode: QUERY_BY_IMAGE_IDS}); }}>
                Image IDs
              </MenuItem>
              <MenuItem eventKey="2"
                        onClick={() => { this.setState({queryMode: QUERY_BY_WORKER_ID}); }}>
                Worker ID
              </MenuItem>
              <MenuItem eventKey="3"
                        onClick={() => { this.setState({queryMode: QUERY_BY_TASK_IDS}); }}>
                Task IDs
              </MenuItem>
              <MenuItem eventKey="4"
                        onClick={() => { this.setState({queryMode: QUERY_UNVERIFIED}); }}>
                All
              </MenuItem>
            </DropdownButton>
            <Button onClick={ () => {
                      this.setState({
                        showUnverified: !this.state.showUnverified
                      })
                    } }>
              {this.state.showUnverified ? "Unverified" : "All"}
            </Button>
          </ButtonGroup>

          <ButtonGroup>
            <Button className="btn btn-primary"
                    onClick={() => {this.submitAdminMarks()}}>
              Submit admin marks
            </Button>
            <Button className="btn btn-primary"
                    onClick={() => {this.setAdminMarksFromUserMarks()}}>
              Set admin marks from user marks 
            </Button>
          </ButtonGroup>

          { this.state.invalidJson === true &&
            <Alert bsStyle='danger'>Invalid JSON</Alert>
          }
        </form>

        <MultiImagesViewer
          imagesList={this.state.imagesList}
          canvasWidth={1100}
          canvasHeight={1000}
          setAdminMark={(idx, mark) => {
            const newImagesList = update(this.state.imagesList, {[idx]: {adminMark: {$set: mark}}});
            this.setState({imagesList: newImagesList});
          }} />
      </Grid>
    );
  }
}

export default App;
