import React, { Component } from 'react';
import { Panel } from 'react-bootstrap';
import PropTypes from 'prop-types';

import * as constants from './constants.js';


export class Card extends Component {
  componentDidMount() {
    this.redrawCanvas();
  }

  componentDidUpdate(prevProps, prevState) {
    if (this.props.instanceId === prevProps.instanceId) {
      return;
    }
    this.redrawCanvas();
  }

  redrawCanvas() {
    var ctx = this.refs.c.getContext('2d');
    const canvasWidth = this.props.canvasWidth;
    const canvasHeight = this.props.canvasHeight;
    ctx.clearRect(0, 0, canvasWidth, canvasHeight);

    // load instance image and polygon
    var image = new Image();
    const imageUrl = constants.API_SERVER_URL + '/textins/' + this.props.instanceId + '/crop/';
    const polygonUrl = constants.API_SERVER_URL + '/textins/' + this.props.instanceId + '/crop/polygon/';
    image.onload = () => {
      const scale = Math.min(canvasWidth / image.width,
                             canvasHeight / image.height);
      const dstWidth = scale * image.width;
      const dstHeight = scale * image.height;
      const dstX = (canvasWidth - dstWidth) / 2;
      const dstY = (canvasHeight - dstHeight) / 2;
      ctx.drawImage(image, 0, 0, image.width, image.height,
                           dstX, dstY, dstWidth, dstHeight);

      fetch(polygonUrl)
        .then((response) => response.json())
        .then((responseJson) => responseJson['relativePolygon'])
        .then((polygon) => {
          // draw polygon after image is loaded
          ctx.beginPath();
          for (var i = 0; i < polygon.length; i++) {
            const point = polygon[i];
            const canvasX = dstX + scale * point.x;
            const canvasY = dstY + scale * point.y;
            if (i === 0) {
              ctx.moveTo(canvasX, canvasY);
            } else {
              ctx.lineTo(canvasX, canvasY);
            }
          }
          ctx.closePath();
          ctx.lineWidth = 1;
          ctx.strokeStyle = 'rgba(0, 255, 0, 0.9)';
          ctx.stroke();
          ctx.fillStyle = 'rgba(0, 255, 0, 0.2)';
          ctx.fill();
        })
    }
    image.src = imageUrl;
  }
  
  render() {
    const panelColors = {
      'U': 'white',
      'C': '#5cb85c',
      'W': '#d9534f'
    }
    const panelStyle = {
      backgroundColor: panelColors[this.props.verificationStatus]
    }

    return (
      <Panel header={ "ID: " + this.props.contentOrResponseId }
             style={ panelStyle }
             className="cardPanel">
        <canvas ref="c"
                width={ this.props.canvasWidth }
                height={ this.props.canvasHeight }
                className="cardCanavs" />
      </Panel>
    )
  }
}

Card.propTypes = {
  canvasWidth: PropTypes.number.isRequired,
  canvasHeight: PropTypes.number.isRequired,
  contentOrResponseId: PropTypes.string.isRequired,
  instanceId: PropTypes.string.isRequired,
  verificationStatus: PropTypes.oneOf(['U', 'C', 'W']).isRequired,
}
