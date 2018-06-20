import React, { Component } from 'react';
import PropTypes from 'prop-types';

import { withStyles } from '@material-ui/core/styles';


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
      canvasOffsetLeft: 0,
      canvasOffsetTop: 0,
      canvasScale: 1.0,
    }
  }

  componentDidUpdate(prevProps, prevState) {
    const { imageId, width, height } = this.props;
    if (prevProps.imageId !== imageId ||
        prevProps.width !== width ||
        prevProps.height !== height) {
      this.redrawImage();
      // this.redrawAnnotations();
    }

    this.redrawAnnotations();
  }

  redrawImage() {
    const ctx = this.refs.imageCanvas.getContext('2d');
    ctx.clearRect(0, 0, this.props.width, this.props.height);

    if (this.props.imageId === null) {
      return;
    }

    // draw image
    var im = new Image();
    var imageName = this.props.imageId.toString();
    imageName = "0".repeat(12 - imageName.length) + imageName + ".jpg";
    const imageUrl = "http://images.cocodataset.org/train2017/" + imageName;
    console.log(imageUrl);
    im.onload = () => {
      const width = this.props.width;
      const height = this.props.height;
      const scale = Math.min(width / im.width,
                             height / im.height);
      const dstWidth = scale * im.width;
      const dstHeight = scale * im.height;
      const dstX = (width - dstWidth) / 2;
      const dstY = (height - dstHeight) / 2;
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

    const { textInstances, width, height } = this.props;
    const { canvasOffsetLeft, canvasOffsetTop, canvasScale } = this.state;

    const ctx = this.refs.annotationCanvas.getContext('2d');
    ctx.clearRect(0, 0, width, height);

    for (var textInstance of textInstances) {
      const points = textInstance.polygon;
      if (points.length < 3) {
        continue; // invalid polygon
      }
      ctx.fillStyle = polygonFill;
      ctx.strokeStyle = polygonStroke;
      ctx.lineWidth = 1;
      ctx.beginPath();
      for (var i = 0; i < points.length; i++) {
        const canvasX = canvasOffsetLeft + canvasScale * points[i].x;
        const canvasY = canvasOffsetTop + canvasScale * points[i].y;
        if (i === 0) {
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

    return (
      <div className={ classes.container }>
        <canvas 
          width={width}
          height={height}
          className={ classes.imageCanvas }
          ref="imageCanvas" />
        <canvas
          width={width}
          height={height}
          className={ classes.annotationCanvas }
          ref="annotationCanvas" />
      </div>
    )
  }
}

ImageViewer.propTypes = {
  classes: PropTypes.object.isRequired,
  width: PropTypes.number.isRequired,
  height: PropTypes.number.isRequired,
  imageId: PropTypes.number,
  textInstances: PropTypes.arrayOf(PropTypes.object),
  focusIndex: PropTypes.number.isRequired,
  handleSetFocusIndex: PropTypes.func.isRequired,
}

export default withStyles(styles)(ImageViewer);
