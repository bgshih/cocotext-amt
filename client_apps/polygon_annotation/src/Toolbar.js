import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { ButtonToolbar, ButtonGroup, Button, 
         Glyphicon, Tooltip, OverlayTrigger, Modal } from 'react-bootstrap';
import {ChangeViewTool, DrawPolygonTool, EditPolygonTool} from './Tools';
import * as eventTypes from './eventTypes';
import InstructionModal from './instructionModal';
import SubmitConfirmModal from './submitConfirmModal';

window.paper = require('paper');



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
  constructor(props) {
    super(props);
    this.state = {
      activeTool: 'default',
      showInstructionModal: false,
      showResetWarningModal: false,
      remainingSubmitTime: 20,
    }
  }

  componentDidMount() {
    // create tools
    this.defaultTool = new window.paper.Tool(); // this tool does nothing
    this.changeViewTool = new ChangeViewTool(this.props.setInfobar);
    this.drawPolygonTool = new DrawPolygonTool(this.props.setInfobar);
    this.editPolygonTool = new EditPolygonTool(this.props.setInfobar);

    window.addEventListener('keypress', (e) => {
      switch (e.key) {
        case 'q': // 'q'
          this.zoomIn();
          break;
        case 'w': // 'w'
          this.zoomOut();
          break;
        case 'f': // 'f'
          this.zoomToFit();
          break;
        case 'v': // 'v'
          this.moveView();
          break;
        case 's': // 's'
          this.createPolygon();
          break;
        case 'e': // 'e'
          this.editPolygon();
          break;
        case 'x': // 'x'
          this.deletePolygon();
          break;
        case 'r': // 'r'
          // this.reset();
          break;
        case 'i': // 'i'
          // this.instructions();
          break;
        case 'h':
          this.toggleHints();
          break;
        default:
          break;
      }
    });

    var timerId;
    timerId = setInterval(
      () => {
        if (this.state.remainingSubmitTime > 0) {
          this.setState({
            remainingSubmitTime: this.state.remainingSubmitTime - 1
          });
        } else {
          // penalty time up
          this.setState({
            pausePenalty: false
          });
          // clear timer
          clearInterval(timerId);
        }
      },
      1000
    );
  }

  handleHotKeys(charCode) {

  }

  zoomIn() {
    window.paper.view.zoom *= 1.2;
  }

  zoomOut() {
    window.paper.view.zoom *= 0.8;
  }

  zoomToFit() {
    window.dispatchEvent(new Event(eventTypes.ZOOM_TO_FIT));
  }

  moveView() {
    this.setState({activeTool: 'changeView'});
    this.changeViewTool.activate();
    this.props.setInfobar('info', 'Click and drag the canvas to move it.');
  }

  createPolygon() {
    this.setState({activeTool: 'createPolygon'});
    this.drawPolygonTool.activate();
  }

  editPolygon() {
    this.setState({activeTool: 'editPolygon'});
    this.editPolygonTool.activate();
  }

  deletePolygon() {
    window.dispatchEvent(new Event(eventTypes.DELETE_POLYGON));
  }

  reset() {
    this.setState({showResetWarningModal: true});
  }

  toggleHints() {
    window.dispatchEvent(new Event(eventTypes.TOGGLE_HINTS));
  }

  instructions() {
    this.setState({showInstructionModal: true});
  }

  render() {
    const resetWarningModal = (
      <Modal show={ this.state.showResetWarningModal }
             onHide={ () => this.setState({showResetWarningModal: false}) }>
        <Modal.Header closeButton>
          <Modal.Title>Reset Confirm</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>Confirm resetting? This will clear all your annotations on this image.</p>
        </Modal.Body>
        <Modal.Footer>
          <Button onClick={ () => this.setState({showResetWarningModal: false}) }>
            Go Back
          </Button>
          <Button bsStyle="danger"
                  onClick={ function() {
                    this.setState({showResetWarningModal: false});
                    window.dispatchEvent(new Event(eventTypes.RESET_ANNOTATIONS));
                  }.bind(this) }>
            Reset
          </Button>
        </Modal.Footer>
      </Modal>
    );

    const instructionModal = (
      <InstructionModal
        show={this.state.showInstructionModal}
        upToNPolygons={5}
        hideClicked={() => this.setState({'showInstructionModal': false})}
        pausePenalty={false}
        pausePenaltyCountdown={0} />
    )

    const submitConfirmModal = (
      <SubmitConfirmModal
        show={this.state.showSubmitConfirmModal}
        onHide={() => this.setState({showSubmitConfirmModal: false})}
        remainingSubmitTime={this.state.remainingSubmitTime}
        submitClicked={() => {
          this.setState({showSubmitConfirmModal: false});
          window.dispatchEvent(new Event(eventTypes.SUBMIT_ANNOTATIONS));
        }} />
    );

    // const submitConfirmModal = (
    //   <Modal show={this.state.showSubmitConfirmModal}
    //          onHide={() => this.setState({showSubmitConfirmModal: false})}>
    //     <Modal.Header closeButton>
    //       <Modal.Title>Ready to Submit?</Modal.Title>
    //     </Modal.Header>

    //     <Modal.Body>
    //       <p>(Show some statistics here)</p>
    //     </Modal.Body>

    //     <Modal.Footer>
    //       <Button onClick={ () => this.setState({showSubmitConfirmModal: false}) }>
    //         Go Back
    //       </Button>
    //       <Button bsStyle="primary"
    //               onClick={ () => {
    //                 this.setState({showSubmitConfirmModal: false});
    //                 window.dispatchEvent(new Event(eventTypes.SUBMIT_ANNOTATIONS)); } }>
    //         Submit
    //       </Button>
    //     </Modal.Footer>
    //   </Modal>
    // );

    return (
      <div>
        <ButtonToolbar>
          <ButtonGroup>
            <ButtonWithTooltip onClick={this.zoomIn.bind(this)}
                               tooltipText="Zoom In (q)"
                               glyph="zoom-in" />
            <ButtonWithTooltip onClick={this.zoomOut.bind(this)}
                               tooltipText="Zoom Out (w)"
                               glyph="zoom-out" />
            <ButtonWithTooltip onClick={this.zoomToFit.bind(this)}
                               tooltipText="Zoom To Fit (f)"
                               text="Fit" />
            <ButtonWithTooltip onClick={this.moveView.bind(this)}
                               tooltipText="Move Canvas (v)"
                               glyph="move"
                               active={this.state.activeTool === 'changeView'} />
          </ButtonGroup>

          <ButtonGroup>
            <ButtonWithTooltip onClick={this.createPolygon.bind(this)}
                               tooltipText='Start New Polygon (s)'
                               glyph='plus'
                               active={this.state.activeTool === 'createPolygon'} />
            <ButtonWithTooltip onClick={this.editPolygon.bind(this)}
                               tooltipText='Edit Polygon (e)'
                               glyph='pencil'
                               active={this.state.activeTool === 'editPolygon'} />
            <ButtonWithTooltip onClick={this.deletePolygon.bind(this)}
                               tooltipText='Delete Polygon (x)'
                               glyph='trash' />
            <ButtonWithTooltip onClick={this.reset.bind(this)}
                               tooltipText='Reset'
                               glyph='repeat' />
          </ButtonGroup>

          <ButtonGroup>
            {/*
            <ButtonWithTooltip onClick={this.toggleHints.bind(this)}
                               tooltipText='Toggle Hints (h)'
                               glyph='star-empty' />
                               */}
            <ButtonWithTooltip onClick={this.instructions.bind(this)}
                               tooltipText='Instructions'
                               glyph='info-sign' />
          </ButtonGroup>

          <ButtonGroup>
            <ButtonWithTooltip onClick={ () => this.setState({showSubmitConfirmModal: true}) }
                               buttonStyle='primary'
                               tooltipText='Finish and Submit'
                               text='Submit' />
          </ButtonGroup>
        </ButtonToolbar>

        {resetWarningModal}
        {instructionModal}
        {submitConfirmModal}
      </div>
    );
  }
}
