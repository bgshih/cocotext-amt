import React, { Component } from 'react';
import ReactDOM from 'react-dom';
import { Grid, FormGroup, FormControl, Button, ButtonGroup, Alert, Pagination, Panel } from 'react-bootstrap';


export class MultiImagesViewer extends Component {
  constructor(props) {
    super(props);
    this.state = {
      activeIndex: 0
    }
  }

  handleKeyPress(keyCode) {
    console.log(keyCode);
    var newActiveIndex;
    switch (keyCode) {
      case 37: // left arrow
        newActiveIndex = Math.max(this.state.activeIndex - 1, 0);
        this.setState({
          activeIndex: newActiveIndex});
        break;
      case 39: // right arrow
        newActiveIndex = Math.min(this.state.activeIndex + 1, this.props.imagesList.length - 1);
        this.setState({
          activeIndex: newActiveIndex});
        break;
    }
  }

  render() {
    const imageAndAnnotations = this.state.activeIndex >= 0 && this.state.activeIndex < this.props.imagesList.length ?
      this.props.imagesList[this.state.activeIndex] : null;
    const imageId = imageAndAnnotations === null ? null : imageAndAnnotations.imageId;
    const annotations = imageAndAnnotations === null ? null : imageAndAnnotations.annotations;

    return (
      <div>
        <ImageViewer
          canvasWidth={this.props.canvasWidth}
          canvasHeight={this.props.canvasHeight}
          imageId={imageId}
          annotations={annotations}
          onKeyDown={(e) => {this.handleKeyPress(e.keyCode)} }
        />
        <Pagination
          prev next first last ellipsis boundaryLinks
          items={this.props.imagesList.length}
          maxButtons={10}
          activePage={this.state.activeIndex + 1}
          onSelect={(e) => {
            this.setState({'activeIndex': e - 1});
          }}
        />
      </div>
    );
  }
}


class ImageViewer extends Component {
  componentDidUpdate(prevProps, prevState) {
    if (this.props.canvasWidth !== prevProps.canvasWidth ||
        this.props.canvasHeight !== prevProps.canvasHeight ||
        this.props.imageId !== prevProps.imageId) {
      
      this.updateCanvas();
    }
    // this.updateCanvas();
  }

  updateCanvas() {
    var ctx = this.refs.canvas.getContext('2d');
    const canvasWidth = this.props.canvasWidth;
    const canvasHeight = this.props.canvasHeight;
    ctx.clearRect(0, 0, canvasWidth, canvasHeight);

    if (!this.props.imageId) {
      return;
    }

    // draw image and annotations
    const image = new Image();
    const imageUrlTemplate = 'https://s3.amazonaws.com/cocotext-images/train2014/COCO_train2014_';
    const leadingZeros = '0'.repeat(12 - this.props.imageId.toString().length);
    const imageUrl = imageUrlTemplate + leadingZeros + this.props.imageId.toString() + '.jpg';
    image.onload = () => {
      // image are resized and centered on the canvas
      const imageWidth = image.width;
      const imageHeight = image.height;
      const scale = Math.min(
        canvasWidth / imageWidth,
        canvasHeight / imageHeight);
      const dstWidth = scale * imageWidth;
      const dstHeight = scale * imageHeight;
      const dstX = (canvasWidth - dstWidth) / 2;
      const dstY = (canvasHeight - dstHeight) / 2;
      ctx.drawImage(
        image, 0, 0, imageWidth, imageHeight,
        dstX, dstY, dstWidth, dstHeight);

      // draw annotations
      for (var annotation of this.props.annotations) {
        const polygon = annotation.polygon;
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
        ctx.fillStyle = 'rgba(255, 255, 255, 0.0)';
        ctx.fill();
      }
    }
    image.src = imageUrl;
  }

  render() {
    return (
      <Panel header={ "ID: " + this.props.imageId }
            className="cardPanel">
        <canvas ref="canvas"
                width={ this.props.canvasWidth }
                height={ this.props.canvasHeight }
                className="cardCanavs" />
      </Panel>
    );
  }
}
