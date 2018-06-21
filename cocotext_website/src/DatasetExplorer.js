import React, { Component } from 'react';
import { Grid, Row, Col } from 'react-bootstrap';

import ImageViewer from './ImageViewer';
import ImageInfoPanel from './ImageInfoPanel';
import DatasetSearchBar from './DatasetSearchBar';


export class DatasetExplorer extends Component {

  constructor(props) {
    super(props);
    this.state = {
      imageId: 0,
      textInstances: [],
      focusIndex: -1,
    }
  }

  componentDidMount() {
    this.setState({imageId: 432218});
  }

  componentDidUpdate(prevProps, prevState) {
    const { imageId } = this.state;
    if (prevState.imageId !== imageId) {
      this.fetchAnnotations();
    }
  }

  fetchAnnotations() {
    const { imageId } = this.state;
    const annotationUrl = "v2_annotations/" + imageId.toString() + ".json";
    fetch(annotationUrl)
      .then((response) => response.json())
      .then((annotJson) => {
        this.setState({
          textInstances: annotJson['text_instances'],
        })
      })
      .catch((error) => {
        console.error(error);
      });
  }

  render() {
    const { imageId, textInstances, focusIndex } = this.state;

    return (
      <div className="DatasetExplorer">
        <Grid>
          <Row>
            <Col xs={12}>
              <DatasetSearchBar
                imageId={ imageId }
                handleReloadButtonClicked={
                  (value) => {
                    this.setState({imageId: value, focusIndex: -1});
                  }
                }
              />
            </Col>
          </Row>

          <Row>
            <Col lg={9} sm={12}>
              <ImageViewer
                width={850}
                height={850}
                imageId={ imageId }
                textInstances={ textInstances }
                focusIndex={ focusIndex }
                handleSetFocusIndex={
                  (index) => {
                    this.setState({focusIndex: index})
                  }
                }
              />
            </Col>

            <Col lg={3} sm={12}>
              <ImageInfoPanel
                imageId={ imageId }
                textInstances={ textInstances }
                focusIndex={ focusIndex }
                handleSetFocusIndex={
                  (index) => {
                    this.setState({focusIndex: index})
                  }
                }
              />
            </Col>
          </Row>
        </Grid>
      </div>
    );
  }
}

DatasetExplorer.propTypes = {
}