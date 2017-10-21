import React, { Component } from 'react';
import { Pagination, Panel } from 'react-bootstrap';

import * as constants from './constants';


export class MultiImagesViewer extends Component {
  constructor(props) {
    super(props);
    this.state = {
      activeIndex: 0
    }
    this.handleKeyDown = this.handleKeyDown.bind(this);
  }

  componentDidMount() {
    window.addEventListener("keydown", this.handleKeyDown);
  }

  componentWillUnmount() {
    window.removeEventListener("keydown", this.handleKeyDown);
  }

  componentDidUpdate(prevProps, prevState) {
    if (prevProps.imagesList.length !== this.props.imagesList.length) {
      this.setState({
        activeIndex: 0
      });
    }
  }

  handleKeyDown(e) {
    var newActiveIndex;
    switch (e.keyCode) {
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
      case 49: // digit 1
      case 50: // digit 2
      case 51: // digit 3
      case 52: // digit 4
        const imageAndAnnotations = this.getActiveImageAndAnnotations();
        if (imageAndAnnotations !== null) {
          const mark = {
            49: 'C', // correct
            50: 'W', // wrong
            51: 'R', // revision-or-further-work
            52: 'U', // unchecked
          }[e.keyCode]
          this.props.setAdminMark(this.state.activeIndex, mark);
        }
        break;
      default:
        break;
    }
  }

  getActiveImageAndAnnotations() {
    const imageAndAnnotations = this.state.activeIndex >= 0 && this.state.activeIndex < this.props.imagesList.length ? this.props.imagesList[this.state.activeIndex] : null;
    return imageAndAnnotations;
  }

  render() {
    const imageAndAnnotations = this.getActiveImageAndAnnotations();
    const imageId = imageAndAnnotations === null ? null : imageAndAnnotations.imageId;
    const annotations = imageAndAnnotations === null ? null : imageAndAnnotations.annotations;
    const adminMark = imageAndAnnotations === null ? null : imageAndAnnotations.adminMark;
    const hasRemainingText = imageAndAnnotations === null ? null : imageAndAnnotations.hasRemainingText;

    return (
      <div>
        <ImageViewer
          canvasWidth={this.props.canvasWidth}
          canvasHeight={this.props.canvasHeight}
          imageId={imageId}
          annotations={annotations}
          adminMark={adminMark}
          hasRemainingText={hasRemainingText}
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
    const imageUrlTemplate = constants.COCO_IMAGE_URL_PREFIX;
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
        ctx.lineWidth = 3;
        ctx.strokeStyle = 'rgba(0, 255, 0, 0.9)';
        ctx.stroke();
        ctx.fillStyle = 'rgba(255, 255, 255, 0.0)';
        ctx.fill();
      }
    }
    image.src = imageUrl;
  }

  render() {
    const panelColorsDict = {
      'U': 'white', // unmarked
      'C': '#5cb85c', // marked as correct
      'W': '#d9534f', // marked as wrong
      'R': '#f4d942' // marked as need-revision-or-more-work
    }
    const panelStyle = {
      backgroundColor: panelColorsDict[this.props.adminMark]
    }

    return (
      <Panel header={ "ID: " + this.props.imageId + " " +
                      "hasRemainingText: " + this.props.hasRemainingText }
             style={ panelStyle }
             className="cardPanel">
        <canvas ref="canvas"
                width={ this.props.canvasWidth }
                height={ this.props.canvasHeight }
                className="cardCanavs" />
      </Panel>
    );
  }
}
