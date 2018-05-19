import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { Grid, Row, Col } from 'react-bootstrap';

import { ImageViewer } from './ImageViewer';
import ImageInfoPanel from './ImageInfoPanel';

export class DatasetExplorer extends Component {

  constructor(props) {
    super(props);
    this.state = {
      imageId: null,
    }
  }

  componentDidMount() {
    // WARN: REMOVE LATER
    this.setState({imageId: 28547});
  }

  render() {
    return (
      <div className="DatasetExplorer">
        <Grid>
          <Row>
            <Col xs={8}>
              <ImageViewer
                width={750}
                height={750}
                imageId={this.state.imageId}
              />
            </Col>

            <Col xs={4}>
              <p>Image ID: { String(this.state.imageId) }</p>
              <p>#Instances: { 2 }</p>
              <ImageInfoPanel />
            </Col>
          </Row>
        </Grid>
      </div>
    );
  }
}

DatasetExplorer.propTypes = {
}