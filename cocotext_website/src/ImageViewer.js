import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { Grid, Row, Col } from 'react-bootstrap';


export class ImageViewer extends Component {

  componentDidMount() {
    this.redraw();
  }

  componentDidUpdate() {
    this.redraw();
  }

  redraw() {
    const ctx = this.refs.c.getContext('2d');
    ctx.clearRect(0, 0, this.props.width, this.props.height);

    if (this.props.imageId === null) {
      return;
    }

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
    }
    im.src = imageUrl;
  }

  render() {
    return (
      <div>
        <canvas 
          width={this.props.width}
          height={this.props.height}
          className="ExplorerCanvas"
          ref="c" />
      </div>
    )
  }
}

ImageViewer.propTypes = {
  width: PropTypes.number.isRequired,
  height: PropTypes.number.isRequired,
  imageId: PropTypes.number
}
