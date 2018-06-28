import React, { Component } from 'react';
import { Grid, Row, Col } from 'react-bootstrap';

import ImageViewer from './ImageViewer';
import ImageInfoPanel from './ImageInfoPanel';
import DatasetSearchBar from './DatasetSearchBar';


export class DatasetExplorer extends Component {

  constructor(props) {
    super(props);
    this.state = {
      imageId: -1,
      imageIdList: [],
      imageIndex: -1,
      textInstances: [],
      focusIndex: -1,
    }
  }

  componentDidMount() {
    this.fetchImageIdList();
  }

  componentDidUpdate(prevProps, prevState) {
    const { imageId, imageIndex, imageIdList } = this.state;
    if (prevState.imageId !== imageId) {
      this.fetchAnnotations();
    }

    if (prevState.imageIndex !== imageIndex) {
      const newImageId = imageIdList[imageIndex];
      this.setState({imageId: newImageId});
    }
  }

  fetchImageIdList() {
    const imageIdListUrl = "image_list.min.json";
    fetch(imageIdListUrl)
      .then((response) => response.json())
      .then((imageListJson) => {
        this.setState({
          imageIdList: imageListJson['image_list_min']
        })
      })
      .then(() => {this.setImageIndexById(432218);})
      .catch((error) => {
        console.error(error);
      });
  }

  fetchAnnotations() {
    const { imageId } = this.state;
    const annotationUrl = "v3/" + imageId.toString() + ".json";
    fetch(annotationUrl)
      .then((response) => response.json())
      .then((annotJson) => {
        this.setState({
          textInstances: annotJson['annotations'],
        })
      })
      .catch((error) => {
        console.error(error);
      });
  }

  handleKeyPress(event) {
    const { imageIndex, focusIndex, imageIdList, textInstances } = this.state;
    const numberOfImages = imageIdList.length;
    const numberOfInstances = textInstances.length;

    if (numberOfImages === 0) {
      return;
    }

    console.log(event.key);

    switch(event.key) {
      case '{':
        this.setState({
          imageIndex: Math.max(0, imageIndex - 1)
        });
        break;
      case '}':
        this.setState({
          imageIndex: Math.min(numberOfImages - 1, imageIndex + 1)
        });
        break;
      case '[':
        // focusIndex can be -1 (no focus)
        this.setState({
          focusIndex: Math.max(-1, focusIndex - 1)
        });
        break;
      case ']':
        this.setState({
          focusIndex: Math.min(numberOfInstances - 1, focusIndex + 1)
        });
        break;
      default:
        break;
    }
  }

  setImageIndexById(imageId) {
    const { imageIdList } = this.state;
    const imageIndex = imageIdList.findIndex((id) => (id === imageId));
    this.setState({
      imageIndex: imageIndex
    });
  }

  render() {
    const { textInstances, focusIndex, imageId } = this.state;

    return (
      <div className="DatasetExplorer" onKeyPress={this.handleKeyPress.bind(this)} tabIndex="0">
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
            <Col lg={8} sm={12}>
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

            <Col lg={4} sm={12}>
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