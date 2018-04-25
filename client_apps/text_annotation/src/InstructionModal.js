import React from 'react';
import PropTypes from 'prop-types';
import { Button, Modal, Alert } from 'react-bootstrap';


const InstructionModal = ({ show, hideClicked, pausePenalty, pausePenaltyCountdown }) => (
  <Modal show={ show } onHide={ hideClicked } bsSize='large'>
    <Modal.Header closeButton>
      <Modal.Title><h2>Instructions (Read carefully before starting to work!!)</h2></Modal.Title>
    </Modal.Header>

    <Modal.Body>

      { pausePenalty &&
        <Alert bsStyle='danger'>
          <b>WARNING</b>
          We have detected an error in your answers.
          Please spend some time reading the instructions and reviewing your answers, then submit again.
          Submission to re-open in {pausePenaltyCountdown} seconds.
        </Alert>
      }

      <h3>Job Description</h3>

      <p>
        <b>Your task: Annotate text in every image.</b>
      </p>
      <p>
        If text is illegible (unable to read) check the "Illegible" checkbox.
        If text is not in a langauge that you know, check the "Unknown Language" checkbox.
      </p>

      <p>
        Punctuations and symbols should be annotated as well.
        For your convenience, common symbols have been provided on the toolbar for you to copy and paste.
      </p>

      <p>
        When multiple words exists in one image, only annotate the word in the center and ignore others.
        Hover on the image to show the target word. 
      </p>

      <h3>Examples (click to enlarge)</h3>
      <a target="_blank"
         rel="noopener noreferrer"
         href="https://s3.amazonaws.com/cocotext-amt-resource/text-annotation-examples.png">
        <img alt="Examples"
             src="https://s3.amazonaws.com/cocotext-amt-resource/text-annotation-examples.png"
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
)


InstructionModal.propTypes = {
  show: PropTypes.bool.isRequired,
  hideClicked: PropTypes.func.isRequired,
  pausePenalty: PropTypes.bool.isRequired,
  pausePenaltyCountdown: PropTypes.number.isRequired,
}

export default InstructionModal
