import React, { Component } from 'react';
import PropTypes from 'prop-types';

import { Grid, Row, Col } from 'react-bootstrap';
import { withStyles } from '@material-ui/core/styles';

import DatasetExplorer from './DatasetExplorer';

import './App.css';


const styles = theme => ({
  container: {
    // minWidth: 1500,
  }
});

const ANNOTATION_FORMAT_STR = `\
{
  "images": [
    {
      "id": int,
      "filename": string,
      "width": int,
      "height": int,
      "set": 0 (train) | 1 (val) | 2 (test),
    },
    ...
  ],
  "annotations": [
    {
      "id": int,
      "imageId": int,
      "mask": [x1, y1, x2, y2, ..., xn, yn] (coordinates of polygon vertices),
      "text": str,
      "legibility": 0 (legible) | 1 (illgible),
      "type": 0 (machine-printed) | 1 (handwritten),
      "language": 0 (English) | 1 (not English),
    },
    ...
  ]
}
`


class App extends Component {

  render() {
    const { classes } = this.props;

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
        <Grid fluid={true}>
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
        </Grid>

        <Grid className={classes.container}>
          <Row>
            <Grid fluid={false}>
              <Row className="FeaturesRow">
                {
                  featureColumn(
                    "Large-Scale",
                    "COCO-Text V2.0 contains 63,686 images with 239,506 annotated text instances."
                  )
                }
                {
                  featureColumn(
                    "Mask Annotations",
                    "Segmentation mask is annotated for every word, allowing fine-level detection."
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

          <hr />

          <Row>
            <Col xs={12}>
              <h2>Dataset Explorer</h2>
            </Col>
            <DatasetExplorer />
            <Col xs={12}>
              <p><i>NOTE: Test images not included</i></p>
            </Col>
          </Row>

          <hr />

          <Row>
            <Col xs={12}>
              <h2>Download</h2>
              <p>Train+Validation annotations: <a href="/cocotext.v3.zip">cocotext_v3.trainval.zip [12 MB]</a></p>
              <p>By downloading the annotations, you agree to our <a href="">Terms of Use</a>.</p>
              <p>The images are the 2014 train images of MSCOCO. They can be downloaded separately at the <a href="http://cocodataset.org/#download">MSCOCO website</a>.</p>
            </Col>
          </Row>

          <hr/>

          <Row>
            <Col xs={12}>
              <h2>API</h2>
              <p>Please use the updated (v2.0) <a href="https://github.com/bgshih/coco-text">COCO-Text Evaluation Toolbox</a> for parsing annotations and evaluating results. Refer to the repository for usage.</p>
            </Col>
          </Row>

          <hr/>

          <Row>
            <Col xs={12}>
              <h2>Terms of Use</h2>
              <p></p>
            </Col>
          </Row>
          
        </Grid>

      </div>
    );
  }
}

App.propTypes = {
  classes: PropTypes.object.isRequired,
}

export default withStyles(styles)(App);
