import React from 'react';
import PropTypes from 'prop-types';
import { Button, Modal } from 'react-bootstrap';

const InstructionModal = ({ show, hideClicked }) => (
  <Modal show={ show } onHide={ hideClicked }>
    <Modal.Header closeButton>
      <Modal.Title>Instructions</Modal.Title>
    </Modal.Header>

    <Modal.Body>
      <p>Show instructions here</p>
    </Modal.Body>

    <Modal.Footer>
      <Button onClick={ hideClicked }>
        Go Back
      </Button>
    </Modal.Footer>
  </Modal>
);

InstructionModal.propTypes = {
  show: PropTypes.bool.isRequired,
  hideClicked: PropTypes.func.isRequired,
};

export default InstructionModal
