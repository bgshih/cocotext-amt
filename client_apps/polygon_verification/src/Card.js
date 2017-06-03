import React, { Component } from 'react';
import { Panel } from 'react-bootstrap';
import PropTypes from 'prop-types';

export class Card extends Component {
  componentDidMount() {
    // load image and draw polygon in the canvas
    const ctx = this.refs.c.getContext('2d');
    var image = new Image();
    image.onload = function() {
      const canvasWidth = this.props.canvasWidth;
      const canvasHeight = this.props.canvasHeight;
      const scale = Math.min(canvasWidth / image.width,
                             canvasHeight / image.height);
      const offsetX = (canvasWidth - scale * image.width) / 2;
      const offsetY = (canvasHeight - scale * image.height) / 2;
      ctx.drawImage(image, 0, 0, image.width, image.height,
                           offsetX, offsetY, canvasWidth, canvasHeight);
      
      // draw polygon after image is loaded
      const points = this.props.polygon;
      ctx.beginPath();
      for (var i = 0; i < points.length; i++) {
        const point = points[i];
        const canvasX = offsetX + scale * point.x;
        const canvasY = offsetY + scale * point.y;
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
    }
    image.src = this.props.imageUrl;
  }
  
  render() {
    const panelColors = {
      'UNVERIFIED': 'white',
      'CORRECT': '#5cb85c',
      'UNSURE': '#f0ad4e',
      'WRONG': '#d9534f'
    }
    const panelStyle = {
      backgroundColor: panelColors[this.props.verification]
    }

    return (
      <Panel onClick={ this.props.onCardClicked }
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
  onCardClicked: PropTypes.func.isRequired,
  verification: PropTypes.oneOf(['CORRECT', 'UNSURE', 'WRONG']),
  canvasWidth: PropTypes.number.isRequired,
  canvasHeight: PropTypes.number.isRequired,
  imageUrl: PropTypes.string.isRequired,
  polygon: PropTypes.arrayOf(PropTypes.shape({
    x: PropTypes.number.isRequired,
    y: PropTypes.number.isRequired
  })).isRequired
}
