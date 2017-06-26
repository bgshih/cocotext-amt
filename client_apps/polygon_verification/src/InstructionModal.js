import React from 'react';
import PropTypes from 'prop-types';
import { Button, Modal, Alert } from 'react-bootstrap';

const InstructionModal = ({ show, hideClicked, pausePenalty, pausePenaltyCountdown }) => (
  <Modal show={ show } onHide={ hideClicked } bsSize='large'>
    <Modal.Header closeButton>
      <Modal.Title><h2>Instructions (read carefully before starting to work!)</h2></Modal.Title>
    </Modal.Header>

    <Modal.Body>

      { pausePenalty &&
        <Alert bsStyle='danger'><b>WARNING</b> We have detected an error in your answers. Please spend some time reading the instructions and reviewing your answers, then submit again. Submission to re-open in {pausePenaltyCountdown} seconds.</Alert>
      }

      <h3>Job Description</h3>

      <p>We are collecting a dataset of text in natural images. In this dataset, each word should be annotated by a polygon that tightly surrounds it. We have some existing annotations. Your job is to judge these annotations.</p>
      <p>You will shown a grid of cards, each an annotation. Click on the cards to mark them as correct (green) or wrong (red). Submit after marking all cards.</p>

      <p>At this point, most of the annotations are rectangles and most are wrong. You need to find the correct ones.</p>

      <h3>Examples (click to enlarge)</h3>
      <a target="_blank"
         rel="noopener noreferrer"
         href="https://s3.amazonaws.com/cocotext-amt-resource/polygon-verification-examples.jpg">
        <img alt="Examples"
             src="https://s3.amazonaws.com/cocotext-amt-resource/polygon-verification-examples.jpg"
             width="800">
        </img>
      </a>

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
