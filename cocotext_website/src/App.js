import React, { Component } from 'react';
import './App.css';

import { Grid, Row, Col } from 'react-bootstrap';
import { DatasetExplorer } from './DatasetExplorer';
import { CssBaseline } from '@material-ui/core';


class App extends Component {

  render() {
    const featureColumn = (featureTitle, featureText) => (
      <Col xs={12} md={4} className="FeatureColumn">
        <h3 className="FeatureTitle">
          { featureTitle }
        </h3>
        <p className="FeatureText">
          { featureText }
        </p>
      </Col>
    )
  
    return (
      <div>
        {/* <Grid fluid={true}>
          <Row className="TitleJumbotronRow">
            <Grid fluid={false} className="TitleJumbotron">
              <h1 className="Title">COCO-Text</h1>
              <p className="Subtitle">
                A Large-Scale Scene Text Dataset, Based on <a className="SubtitleLink" href="http://cocodataset.org/">MSCOCO</a>
              </p>
              <div className="TitleButtonGroup">
                <button className="TitleButton1">Download v2.0</button>
                <button className="TitleButton2">Explore</button>
              </div>
            </Grid>
          </Row>
        </Grid> */}

        <Grid>
          {/* <Row>
            <Grid fluid={false}>
              <Row className="FeaturesRow">
                {
                  featureColumn(
                    "Large-Scale",
                    "63,686 images, 145,859 text instances."
                  )
                }
                {
                  featureColumn(
                    "Fine Annotations",
                    "We provide segmentation-level annotations for all words."
                  )
                }
                { 
                  featureColumn(
                    "Attributes",
                    "Three attributes are labeled for every word: machine-printed vs. handwritten, legible vs. illgible, and English vs. non-English")
                }
              </Row>
            </Grid>
          </Row>

          <hr /> */}

          <Row>
            <Col xs={12}>
              <h2>Dataset Explorer</h2>
            </Col>
            <DatasetExplorer />
          </Row>

          <hr />

          {/* <Row>
            <Col xs={12}>
              <h2>Download Annotations</h2>
              <p></p>
            </Col>
          </Row> */}
          
        </Grid>

      </div>
    );
  }
}

export default App;
