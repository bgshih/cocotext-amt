import React, { Component } from 'react'
import { Panel, Form, FormControl, Checkbox } from 'react-bootstrap'
import PropTypes from 'prop-types'


export class Card extends Component {

  componentDidMount() {
    const ctx = this.refs.c.getContext('2d');
    var im = new Image();
    const imageUrl = "textannot/crop/" + this.props.cropId;
    im.onload = () => {
      const canvasWidth = this.props.canvasWidth;
      const canvasHeight = this.props.canvasHeight;
      const scale = Math.min(canvasWidth / im.width,
                             canvasHeight / im.height);
      const dstWidth = scale * im.width;
      const dstHeight = scale * im.height;
      const dstX = (canvasWidth - dstWidth) / 2;
      const dstY = (canvasHeight - dstHeight) / 2;
      ctx.drawImage(im, 0, 0, im.width, im.height,
                    dstX, dstY, dstWidth, dstHeight);
    }
    im.src = imageUrl;
  }

  render() {
    return (
      <Panel>
        <canvas ref="c"
                width={ this.props.canvasWidth }
                height={ this.props.canvasHeight }
                className="CardCanvas" />
        <Form className="CardForm">
          <FormControl type="text" placeholder="Text in the image"/>
          <Checkbox checked={ this.props.illegible }>
            Illegible (i)
          </Checkbox>
          <Checkbox checked={ this.props.unknownLanguage }>
            Unknown Language (u)
          </Checkbox>
        </Form>
      </Panel>
    )
  }
}

Card.propTypes = {
  canvasWidth: PropTypes.number.isRequired,
  canvasHeight: PropTypes.number.isRequired,
  cropId: PropTypes.string.isRequired,
  illegible: PropTypes.bool.isRequired,
  setIllegible: PropTypes.func.isRequired,
  unknownLanguage: PropTypes.bool.isRequired,
  setUnknownLanguage: PropTypes.func.isRequired,
}
