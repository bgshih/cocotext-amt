import React from 'react';
import PropTypes from 'prop-types';
import { Button, Modal, Alert } from 'react-bootstrap';


const InstructionModal = ({ show, onHide, remainingSubmitTime, submitClicked }) => (
  <Modal show={ show } onHide={ onHide }>
    <Modal.Header closeButton>
      <Modal.Title><h2>Submit</h2></Modal.Title>
    </Modal.Header>

    <Modal.Body>
      { remainingSubmitTime > 0 &&
        <Alert bsStyle='danger'><b>WARNING</b> You can only submit after {remainingSubmitTime} seconds.</Alert>
      }
      Are you sure to submit?
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

InstructionModal.propTypes = {
  show: PropTypes.bool.isRequired,
  onHide: PropTypes.func.isRequired,
  pausePenalty: PropTypes.bool.isRequired,
  remainingSubmitTime: PropTypes.number.isRequired,
  pausePenaltyCountdown: PropTypes.number.isRequired,
};

export default InstructionModal
