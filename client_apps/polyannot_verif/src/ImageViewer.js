import React, { Component } from 'react';
import { Panel } from 'react-bootstrap';
import PropTypes from 'prop-types';

import * as constants from './constants';


export class ImageViewer extends Component {
  constructor(props) {
    super(props);
    this.state = {
      scale: 1.0,
      offset: {
        x: 0,
        y: 0
      }
    }

    this.ctx = null;
    this.image = new Image();
    
    this.mouseIsDown = false;
    this.lastMousePosition = null;
    this.handleKeyDown = this.handleKeyDown.bind(this);
  }

  componentDidMount() {
    this.ctx = this.refs.canvas.getContext('2d');
    this.loadImage();
    window.addEventListener("keydown", this.handleKeyDown);
  }

  componentWillUnmount() {
    window.removeEventListener("keydown", this.handleKeyDown);
  }

  componentDidUpdate(prevProps, prevState) {
    if (this.props.canvasWidth !== prevProps.canvasWidth ||
        this.props.canvasHeight !== prevProps.canvasHeight ||
        this.props.imageId !== prevProps.imageId) {
      this.loadImage();
    }

    if (this.state.scale !== prevState.scale ||
        this.state.offset.x !== prevState.offset.x ||
        this.state.offset.y !== prevState.offset.y) {
      this.updateCanvas();
    }
  }

  handleMouseDrag(e) {
    if (this.lastMousePosition === null) {
      this.lastMousePosition = {
        x: e.clientX,
        y: e.clientY
      };
    }

    if (this.mouseIsDown === true) {
      // drag event detected
      const deltaX = e.clientX - this.lastMousePosition.x;
      const deltaY = e.clientY - this.lastMousePosition.y;
      const newOffset = {
        x: this.state.offset.x + deltaX,
        y: this.state.offset.y + deltaY
      };
      this.setState({
        offset: newOffset
      });
    }

    this.lastMousePosition = {
      x: e.clientX,
      y: e.clientY
    };
  }

  handleKeyDown(e) {
    switch (e.keyCode) {
      case 219: // '['
        this.zoom(0.9);
        break;
      case 221: // ']'
        this.zoom(1.1);
        break;
      case 48: // '0'
        this.zoomToFit();
        break;
      default:
        break;
    }
  }

  zoom(relativeScale) {
    const newScale = this.state.scale * relativeScale;
    this.setState({
      scale: newScale
    });
  }

  zoomToFit() {
    if (this.imageReady === false) {
      return;
    }
    const imageWidth = this.image.width;
    const imageHeight = this.image.height;
    const canvasWidth = this.props.canvasWidth;
    const canvasHeight = this.props.canvasHeight;
    const newScale = Math.min(canvasWidth / imageWidth, canvasHeight / imageHeight);
    this.setState({
      scale: newScale,
      offset: { x: 0, y: 0 }
    });
  }

  loadImage() {
    if (!this.props.imageId) {
      return;
    }

    // draw image and annotations
    const leadingZeros = '0'.repeat(12 - this.props.imageId.toString().length);
    const imageUrl = constants.COCO_IMAGE_URL_PREFIX +
                     leadingZeros +
                     this.props.imageId.toString() +
                     '.jpg';
    this.image.onload = () => {
      this.zoomToFit();
      this.updateCanvas();
    }
    this.image.src = imageUrl;
  }

  imageReady() {
    const ready = (this.image.complete && this.image.naturalWidth > 0);
    return ready;
  }

  boxIntersection(box1, box2) {
    const xmin = Math.max(box1.x, box2.x);
    const ymin = Math.max(box1.y, box2.y);
    const xmax = Math.min(box1.x + box1.width, box2.x + box2.width);
    const ymax = Math.min(box1.y + box1.height, box2.y + box2.height);
    const newBox = {
      x: xmin,
      y: ymin,
      width: Math.max(xmax - xmin, 0),
      height: Math.max(ymax - ymin, 0)
    }
    return newBox;
  }

  updateCanvas() {
    // clear canvas
    const canvasWidth = this.props.canvasWidth;
    const canvasHeight = this.props.canvasHeight;
    this.ctx.clearRect(0, 0, canvasWidth, canvasHeight);

    if (this.imageReady() === false) {
      // image not loaded or invalid
      return;
    }

    const imageWidth = this.image.width;
    const imageHeight = this.image.height;

    // in canvas' perspective
    const imageViewedByCanvas = {
      x: this.state.offset.x,
      y: this.state.offset.y,
      width: imageWidth * this.state.scale,
      height: imageHeight * this.state.scale,
    };
    const imageViewedByCanvasClipped = this.boxIntersection(
      imageViewedByCanvas,
      {x: 0, y: 0, width: canvasWidth, height: canvasHeight}
    );

    // in image's perspective
    const canvasViewedByImage = {
      x: -this.state.offset.x / this.state.scale,
      y: -this.state.offset.y / this.state.scale,
      width: canvasWidth / this.state.scale,
      height: canvasHeight / this.state.scale
    };
    const canvasViewedByImageClipped = this.boxIntersection(
      canvasViewedByImage,
      {x: 0, y: 0, width: imageWidth, height: imageHeight}
    );

    this.ctx.drawImage(
      this.image,
      canvasViewedByImageClipped.x, canvasViewedByImageClipped.y,
      canvasViewedByImageClipped.width, canvasViewedByImageClipped.height,
      imageViewedByCanvasClipped.x, imageViewedByCanvasClipped.y,
      imageViewedByCanvasClipped.width, imageViewedByCanvasClipped.height
    );
    
    // draw annotations
    for (const annotation of this.props.annotations) {
      const polygon = annotation.polygon;
      this.ctx.beginPath();
      for (var i = 0; i < polygon.length; i++) {
        const point = polygon[i];
        const canvasX = this.state.offset.x + this.state.scale * point.x;
        const canvasY = this.state.offset.y + this.state.scale * point.y;
        if (i === 0) {
          this.ctx.moveTo(canvasX, canvasY);
        } else {
          this.ctx.lineTo(canvasX, canvasY);
        }
      }
      this.ctx.closePath();
      this.ctx.lineWidth = 3;
      this.ctx.strokeStyle = 'rgba(0, 255, 0, 0.9)';
      this.ctx.stroke();
      this.ctx.fillStyle = 'rgba(255, 255, 255, 0.0)';
      this.ctx.fill();
    }
  }

  render() {
    const panelColorsDict = {
      'U': 'white', // unmarked
      'C': '#5cb85c', // marked as correct
      'W': '#d9534f', // marked as wrong
      'R': '#f4d942' // marked as need-revision-or-more-work
    }
    const panelStyle = {
      backgroundColor: panelColorsDict[this.props.userMark]
    }
    const statusStr = {
      'U': 'Unverified',
      'C': 'Correct and Complete',
      'W': 'Bad',
      'R': 'Correct but Incomplete'
    }[this.props.userMark];
    const headerStr = "ID: " + this.props.imageId.toString() + "; " +
                      "Status: " + statusStr;

    return (
      <Panel header={ headerStr }
             style={ panelStyle }
             className="cardPanel">
        <canvas ref="canvas"
                width={ this.props.canvasWidth }
                height={ this.props.canvasHeight }
                className="ImageViewerCanvas"
                onMouseDown={ (e) => {this.mouseIsDown = true;} }
                onMouseUp={ (e) => {this.mouseIsDown = false;} }
                onMouseMove={ (e) => {this.handleMouseDrag(e);} }
         />
      </Panel>
    );
  }
}

ImageViewer.propTypes = {
  canvasWidth: PropTypes.number.isRequired,
  canvasHeight: PropTypes.number.isRequired,
  imageId: PropTypes.number,
  annotations: PropTypes.arrayOf(PropTypes.shape({
    polygon: PropTypes.arrayOf(PropTypes.shape({
      x: PropTypes.number.isRequired,
      y: PropTypes.number.isRequired
    })),
  })),
  userMask: PropTypes.string
};
