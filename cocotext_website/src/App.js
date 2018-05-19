import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';

import { Grid, Row, Col, Button, ButtonToolbar } from 'react-bootstrap';


class App extends Component {
  render() {
    return (
      <div>
        <Grid fluid={true}>
          <Row className="TitleJumbotronRow">
            <Grid fluid={false} className="TitleJumbotron">
              <h1 className="Title">COCO-Text</h1>
              <p className="Subtitle">A Large-scale scene text dataset, based on MSCOCO</p>
              <div className="TitleButtonGroup">
                <Button bsStyle="default" className="TitleButton1">Download V2.0</Button>
                <Button bsStyle="default">Explore</Button>
              </div>
            </Grid>
          </Row>
        </Grid>

        <Grid>
          <Row>
            <Grid fluid={false}>
              <Row>
                <Col xs={12} md={4}>
                  <h2 className="SummaryTitle">
                    Large-Scale
                  </h2>
                  <p className="SummaryText">
                    63,686 images, 145,859 text instances.
                  </p>
                </Col>

                <Col xs={12} md={4}>
                  <h2 className="SummaryTitle">
                    Fine Annotations
                  </h2>
                  <p className="SummaryText">
                    We provide segmentation-level annotations for all words.
                  </p>
                </Col>

                <Col xs={12} md={4}>
                  <h2 className="SummaryTitle">
                    Attributes
                  </h2>
                  <p className="SummaryText">
                    Three attributes are labeled for every word:
                    <ul>
                      <li>Machine-printed / Handwritten</li>
                      <li>Legible / Illgible</li>
                      <li>English / non-English</li>
                    </ul>
                  </p>
                </Col>
              </Row>
            </Grid>
          </Row>
        </Grid>
      </div>
    );
  }
}

export default App;
