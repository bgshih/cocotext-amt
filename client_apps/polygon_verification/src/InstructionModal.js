import React from 'react';
import PropTypes from 'prop-types';
import { Button, Modal, Alert } from 'react-bootstrap';

const InstructionModal = ({ show, hideClicked, pausePenalty, pausePenaltyCountdown }) => (
  <Modal show={ show } onHide={ hideClicked } bsSize='large'>
    <Modal.Header closeButton>
      <Modal.Title><h2>READ THE FOLLOWING INSTRUCTIONS CAREFULLY BEFORE STARTING TO WORK</h2></Modal.Title>
    </Modal.Header>

    <Modal.Body>

      { pausePenalty &&
        <Alert bsStyle='danger'><b>WARNING</b> We detect an error in your answers. Please spend some time to read the instructions, review your answers, and submit again. Submission to re-open in {pausePenaltyCountdown} seconds.</Alert>
      }

      <h3>Job Description</h3>

      <p>We are collecting a dataset of text in natural images. In this dataset, each word should be annotated by a polygon that tightly surrounds it. We have some existing annotations. Your job is to judge these annotations.</p>
      <p>You will shown a grid of cards, each an annotation. Click on the cards to mark them as correct (green) or wrong (red). Submit after marking all cards.</p>

      <p><b>NOTE:</b> At this point, most of the annotations are rectangles. And most are wrong.</p>
      
      <h3>Examples</h3>
      <img src="https://s3.amazonaws.com/cocotext-amt-resource/polygon-verification-examples.png"></img>

      <h3>Tips</h3>
      <ul>
        <li>Click "All Correct" or "All Wrong" to mark all at once.</li>
        <li>Shortcuts are available. Move your mouse to the toolbar buttons to see their tooltips.</li>
      </ul>

    </Modal.Body>

    <Modal.Footer>
      <Button onClick={ hideClicked }>
        Close
      </Button>
    </Modal.Footer>
  </Modal>
);

InstructionModal.propTypes = {
  show: PropTypes.bool.isRequired,
  hideClicked: PropTypes.func.isRequired,
  pausePenalty: PropTypes.bool.isRequired,
  pausePenaltyCountdown: PropTypes.number.isRequired,
};

export default InstructionModal
