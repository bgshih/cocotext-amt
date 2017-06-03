import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { ButtonToolbar, ButtonGroup, Button, 
         Glyphicon, Tooltip, OverlayTrigger } from 'react-bootstrap';


const ButtonWithTooltip = ({ onClick, tooltipText, buttonStyle, glyph, text, active, disabled }) => {
  var innerHTML;
  if (glyph !== undefined) {
    innerHTML = (<Glyphicon glyph={glyph}></Glyphicon>);
  } else {
    innerHTML = (<div>{text}</div>);
  }

  return (
    <OverlayTrigger placement="bottom" overlay={<Tooltip id="tooltip">{tooltipText}</Tooltip>}>
      <Button bsStyle={buttonStyle} onClick={onClick} active={active} disabled={disabled}>
        {innerHTML}
      </Button>
    </OverlayTrigger>
  );
};

ButtonWithTooltip.propTypes = {
  onClick: PropTypes.func.isRequired,
  tooltipText: PropTypes.string.isRequired,
  style: PropTypes.string,
  glyph: PropTypes.string,
  text: PropTypes.string,
  active: PropTypes.bool,
  disabled: PropTypes.bool
}

ButtonWithTooltip.defaultProps = {
  style: "default",
  active: false,
  disabled: false,
}


export class Toolbar extends Component {
  render() {
    return (
      <div>
        <ButtonToolbar>
          <ButtonGroup>
            <ButtonWithTooltip onClick={ this.props.instructionClicked }
                               tooltipText='Instructions'
                               glyph='info-sign' />
          </ButtonGroup>

          <ButtonGroup>
            <ButtonWithTooltip onClick={ this.props.submitClicked }
                               buttonStyle='primary'
                               tooltipText='Finish and Submit'
                               text='Submit' />
          </ButtonGroup>
        </ButtonToolbar>
      </div>
    );
  }
}

Toolbar.propTypes = {
  instructionClicked: PropTypes.func.isRequired,
  submitClicked: PropTypes.func.isRequired
}
