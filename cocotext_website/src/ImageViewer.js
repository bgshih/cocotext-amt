import React, { Component } from 'react';
import PropTypes from 'prop-types';
// import Measure from 'react-measure';

import { withStyles } from '@material-ui/core/styles';
import { withContentRect } from 'react-measure';


const styles = theme => ({
  container: {
    position: "relative"
  },
  imageCanvas: {
    position: "relative",
    left: 0,
    top: 0,
    zIndex: 0,
    background: "#ececec",
  },
  annotationCanvas: {
    position: "absolute",
    left: 0,
    top: 0,
    zIndex: 1,
    background: "transparent",
  }
})


class ImageViewer extends Component {

  constructor(props) {
    super(props);
    this.state = {
      canvasWidth: 512,
      canvasHeight: 512,
      canvasOffsetLeft: 0,
      canvasOffsetTop: 0,
      canvasScale: 1.0,
    }
  }

  updateDimensions() {
    const containerWidth = this.refs.container.offsetWidth;
    this.setState({
      canvasWidth: containerWidth,
      canvasHeight: containerWidth,
    });
  }

  componentDidMount() {
    this.updateDimensions();
    window.addEventListener("resize", this.updateDimensions.bind(this));
  }

  componentWillUnmount() {
    window.removeEventListener("resize", this.updateDimensions.bind(this));
  }

  componentDidUpdate(prevProps, prevState) {
    const { imageId, focusIndex, textInstances } = this.props;
    const { canvasWidth, canvasHeight, canvasOffsetLeft, canvasOffsetTop, canvasScale} = this.state;
    
    if (prevProps.imageId !== imageId ||
        prevState.canvasWidth !== canvasWidth ||
        prevState.canvasHeight !== canvasHeight) {
      this.redrawImage();
      this.redrawAnnotations();
    }

    if (prevState.canvasWidth !== canvasWidth ||
        prevState.canvasHeight !== canvasHeight ||
        prevProps.focusIndex !== focusIndex ||
        prevState.canvasOffsetLeft !== canvasOffsetLeft ||
        prevState.canvasOffsetTop !== canvasOffsetTop ||
        prevState.canvasScale !== canvasScale ||
        JSON.stringify(prevProps.textInstances) !== JSON.stringify(textInstances)) {
      this.redrawAnnotations();
    }
  }

  redrawImage() {
    const {canvasWidth, canvasHeight} = this.state;
    const {imageId} = this.props;

    const ctx = this.refs.imageCanvas.getContext('2d');
    ctx.clearRect(0, 0, canvasWidth, canvasHeight);

    if (imageId === undefined || imageId < 0) {
      return;
    }

    // draw image
    var im = new Image();
    var imageName = imageId.toString();
    imageName = "0".repeat(12 - imageName.length) + imageName + ".jpg";
    const imageUrl = "http://images.cocodataset.org/train2017/" + imageName;
    console.log(imageUrl);
    im.onload = () => {
      const scale = Math.min(canvasWidth / im.width,
                             canvasHeight / im.height);
      const dstWidth = scale * im.width;
      const dstHeight = scale * im.height;
      const dstX = (canvasWidth - dstWidth) / 2;
      const dstY = (canvasHeight - dstHeight) / 2;
      ctx.drawImage(im, 0, 0, im.width, im.height,
                    dstX, dstY, dstWidth, dstHeight);
      this.setState({
        canvasOffsetLeft: dstX,
        canvasOffsetTop: dstY,
        canvasScale: scale,
      })
    }
    im.src = imageUrl;
  }

  redrawAnnotations() {
    const polygonFill = "rgba(102, 255, 102, 0.5)";
    const polygonStroke = "rgba(0, 230, 0, 1.0)";
    const focusPolygonFill = "rgba(255, 255, 0, 0.5)";
    const focusPolygonStroke = "rgb(230, 230, 0, 1.0)";

    const { textInstances, width, height, focusIndex } = this.props;
    const { canvasOffsetLeft, canvasOffsetTop, canvasScale } = this.state;

    const ctx = this.refs.annotationCanvas.getContext('2d');
    ctx.clearRect(0, 0, width, height);

    for (let i = 0; i < textInstances.length; i++) {
      const points = textInstances[i].mask;
      if (points.length < 6) {
        continue; // invalid polygon
      }
      if (i === focusIndex) {
        ctx.fillStyle = focusPolygonFill;
        ctx.strokeStyle = focusPolygonStroke;
      } else {
        ctx.fillStyle = polygonFill;
        ctx.strokeStyle = polygonStroke;
      }
      ctx.lineWidth = 1;
      ctx.beginPath();
      for (let j = 0; j < points.length / 2; j++) {
        const canvasX = canvasOffsetLeft + canvasScale * points[2*j];
        const canvasY = canvasOffsetTop + canvasScale * points[2*j+1];
        if (j === 0) {
          ctx.moveTo(canvasX, canvasY);
        } else {
          ctx.lineTo(canvasX, canvasY);
        }
      }
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
    }
  }

  render() {
    const { classes, width, height } = this.props;
    const { canvasWidth, canvasHeight } = this.state;

    return (
      <div ref="container" className={ classes.container }>
        <canvas 
          width={canvasWidth}
          height={canvasHeight}
          className={ classes.imageCanvas }
          ref="imageCanvas" />
        <canvas
          width={canvasWidth}
          height={canvasHeight}
          className={ classes.annotationCanvas }
          ref="annotationCanvas" />
      </div>
    )
  }
}

ImageViewer.propTypes = {
  classes: PropTypes.object.isRequired,
  imageId: PropTypes.number,
  textInstances: PropTypes.arrayOf(PropTypes.object),
  focusIndex: PropTypes.number.isRequired,
  handleSetFocusIndex: PropTypes.func.isRequired,
}

export default withStyles(styles)(ImageViewer);
