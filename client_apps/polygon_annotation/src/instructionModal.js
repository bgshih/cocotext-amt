import React from 'react';
import PropTypes from 'prop-types';
import { Button, Modal, Alert } from 'react-bootstrap';


const InstructionModal = ({ show, upToNPolygons, hideClicked, pausePenalty, pausePenaltyCountdown }) => (
  <Modal show={ show } onHide={ hideClicked } bsSize='large'>
    <Modal.Header closeButton>
      <Modal.Title><h2>Instructions (Read carefully!! The instructions have been updated since its last version!!)</h2></Modal.Title>
    </Modal.Header>

    <Modal.Body>

      { pausePenalty &&
        <Alert bsStyle='danger'><b>WARNING</b> We have detected an error in your answers. Please spend some time reading the instructions and reviewing your answers, then submit again. Submission to re-open in {pausePenaltyCountdown} seconds.</Alert>
      }

      <h2>Job Description</h2>

      <p>
We are collecting a dataset of text in natural images.
In this dataset, each word should be annotated by a polygon that <b>tightly surrounds</b> it.
Use the tool we provide to draw polygons around words you could find.</p>

<p><b>You must annotate <i>**ALL**</i> words you can find in the image. Ignore words that are too small and blurry to read.</b></p>

      <p><b>Every polygon should surround only one word. Do NOT draw a polygon to surround multiple.</b></p>

      <p>Existing annotations are displayed in blue color. Skip those words!</p>

      <p>We define "word" a sequence of characters without blank space. Words such as "CocaCola", "www.google.com" are considered one word rather than two. Some words have large character space, which should not be interpreted as blank space symbols.</p>

      <p>Check the information bar at the bottom of the image for the interactive instructions of tool usages.</p>

      <p>Be careful! All your annotations will be examined. Your submissions will be rejected if they fail to reach the minimum quality standard. On the other hand, we will reward you and let you work on more of our HITs if your produce high-quality annotations.</p>

      <h2>Instruction by examples (click to enlarge)</h2>
      <a target="_blank"
         rel="noopener noreferrer"
         href="https://s3.amazonaws.com/cocotext-amt-resource/polygon-annotation-examples.png">
        <img alt="Examples"
             src="https://s3.amazonaws.com/cocotext-amt-resource/polygon-annotation-examples.png"
             width="800">
        </img>
      </a>

      <h2>Bonus Policy</h2>
      <p>Since the number of words in an image is not fixed, we reward worker based on the number of words they have annotated. Specifically:</p>
      <ul>
        <li>Under 5 annotations: no extra bonus</li>
        <li>More than 5 annotations: each worth $0.01</li>
        <li>For every 500 images correctly annotated: $10</li>
      </ul>
      <p>Bonus will be calculated and sent on weekly basis.</p>

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
  upToNPolygons: PropTypes.number.isRequired,
  hideClicked: PropTypes.func.isRequired,
  pausePenalty: PropTypes.bool.isRequired,
  pausePenaltyCountdown: PropTypes.number.isRequired,
};

export default InstructionModal
