import React, { Component } from 'react'
import { Panel, Form, FormControl, Checkbox, Image } from 'react-bootstrap'
import PropTypes from 'prop-types'


export class Card extends Component {
  render() {
    const cropUrl = "textannot/crop/" + this.props.cropId;

    return (
      <Panel>
        <Image src={cropUrl} />
        <Form className="CardForm">
          <FormControl type="text" placeholder="Text in the image"/>
          <Checkbox>Illegible (i)</Checkbox>
          <Checkbox>Unknown Language (u)</Checkbox>
        </Form>
      </Panel>
    )
  }
}

Card.propTypes = {
  cropId: PropTypes.string.isRequired,
  canvasWidth: PropTypes.number.isRequired,
  canvasHeight: PropTypes.number.isRequired,
}
