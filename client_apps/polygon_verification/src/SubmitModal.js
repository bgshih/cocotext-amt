import React from 'react';
import PropTypes from 'prop-types';
import { Button, Modal } from 'react-bootstrap';

const SubmitModal = ({ show, hideClicked, submitConfirmed }) => (
  <Modal show={ show } onHide={ hideClicked }>
    <Modal.Header closeButton>
      <Modal.Title>Ready to Submit?</Modal.Title>
    </Modal.Header>

    <Modal.Body>
      <p>Ready to Submit?</p>
    </Modal.Body>

    <Modal.Footer>
      <Button onClick={ hideClicked }>
        Go Back
      </Button>
      <Button bsStyle="primary"
              onClick={ submitConfirmed }>
        Submit
      </Button>
    </Modal.Footer>
  </Modal>
);

SubmitModal.propTypes = {
  show: PropTypes.bool.isRequired,
  hideClicked: PropTypes.func.isRequired,
  submitConfirmed: PropTypes.func.isRequired
};

export default SubmitModal
