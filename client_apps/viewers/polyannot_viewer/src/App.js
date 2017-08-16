import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import './App.css';
import { Grid, FormGroup, FormControl, Button, ButtonGroup, Alert } from 'react-bootstrap';
import { MenuItem, DropdownButton } from 'react-bootstrap';

import {MultiImagesViewer} from './MultiImagesViewer';

const API_SERVER_URL = window.location.origin;

const QUERY_BY_IMAGE_IDS = 'QUERY_BY_IMAGE_IDS';
const QUERY_BY_WORKER_ID = 'QUERY_BY_WORKER_ID';
const QUERY_BY_TASK_IDS = 'QUERY_BY_TASK_IDS';


class App extends Component {
  constructor(props) {
    super(props);
    
    this.state = {
      invalidJson: false,
      imagesList: [],
      queryMode: QUERY_BY_IMAGE_IDS
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
        break;
      case QUERY_BY_TASK_IDS:
        const taskIdList = this.validateAndParseJson(inputData);
        const taskIdStrList = taskIdList.map((id) => (id.toString()));
        query = taskIdStrList.join(',');
        fetchUrl = API_SERVER_URL + '/polyannot/_annotations/by_task_ids/' + query;
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

  render() {
    const placeholderTextDict = {
      QUERY_BY_IMAGE_IDS: "Input a list of image IDs in JSON format",
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
            </DropdownButton>
          </ButtonGroup>

          { this.state.invalidJson === true &&
            <Alert bsStyle='danger'>Invalid JSON</Alert>
          }
        </form>

        <MultiImagesViewer
          imagesList={this.state.imagesList}
          canvasWidth={800}
          canvasHeight={600} />
      </Grid>
    );
  }
}

export default App;
