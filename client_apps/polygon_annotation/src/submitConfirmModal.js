import React from 'react';
import PropTypes from 'prop-types';
import { ButtonToolbar, Button, ButtonGroup, Modal, Alert } from 'react-bootstrap';


const SubmitConfirmModal = ({ show, onHide, remainingSubmitTime, submitClicked, hasRemainingText, onSetHasRemainingText }) => (
  <Modal show={ show } onHide={ onHide }>
    <Modal.Header closeButton>
      <Modal.Title><h2>Submit</h2></Modal.Title>
    </Modal.Header>

    {/* <Modal.Body>
      { remainingSubmitTime > 0 &&
        <Alert bsStyle='danger'><b>WARNING</b> You can only submit after {remainingSubmitTime} seconds.</Alert>
      }
      Are you sure to submit?
    </Modal.Body> */}

    <Modal.Body>
      { remainingSubmitTime > 0 &&
        <Alert bsStyle='danger'><b>WARNING</b> You can only submit after {remainingSubmitTime} seconds.</Alert>
      }
      <p><b>Please answer: </b>Is there remaining text in the image? (We allow you to submit with remaining text when you have annotated at least 5 words)</p>
      <ButtonToolbar>
        <ButtonGroup type="radio" name="options" defaultValue={1}>
          <Button onClick={(e) => { onSetHasRemainingText(true); }}
                  active={hasRemainingText} >
            Yes
          </Button>
          <Button onClick={(e) => { onSetHasRemainingText(false); }}
                  active={!hasRemainingText}>
            No
          </Button>
        </ButtonGroup>
      </ButtonToolbar>
      
      {hasRemainingText ?
        <p><b>Your answer: </b>There is remaining text in the image.</p> :
        <p><b>Your answer: </b>There is NO remaining text in the image.</p> }

    </Modal.Body>

    <Modal.Footer>
      <Button
        onClick={ submitClicked }
        bsStyle='primary'
        disabled={ remainingSubmitTime > 0 }>
        Submit
      </Button>
      <Button onClick={ onHide }>
        Close
      </Button>
    </Modal.Footer>
  </Modal>
);

SubmitConfirmModal.propTypes = {
  show: PropTypes.bool.isRequired,
  onHide: PropTypes.func.isRequired,
  pausePenalty: PropTypes.bool.isRequired,
  remainingSubmitTime: PropTypes.number.isRequired,
  pausePenaltyCountdown: PropTypes.number.isRequired,
  hasRemainingText: PropTypes.bool.isRequired,
  onSetHasRemainingText: PropTypes.func.isRequired
};

export default SubmitConfirmModal
