import React, { Component } from 'react';
import PropTypes from 'prop-types';

import { withStyles } from '@material-ui/core/styles';
import { Button } from '@material-ui/core';

import TextInstanceExpansionPanel from './TextInstanceExpansionPanel.js';


const styles = theme => ({
  panelHead: {
    fontSize: 13,
    marginBottom: 5
  },
  hr: {
    marginTop: 10,
    marginBottom: 10
  },
  button: {
    fontSize: 13,
  }
})


class ImageInfoPanel extends Component {

  constructor(props) {
    super(props);
    this.state = {
      imageReported: false,
    }
  }

  reportImage() {
    const { imageId } = this.props;

    fetch('/corrections/', {
      method: 'POST',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        "image_id": imageId,
      })
    })
    .then(() => {
      this.setState({
        imageReported: true,
      });
    })
    .catch((error) => {
      console.log(error);
    });
  }

  render() {
    const { imageReported } = this.state;
    const { classes, imageId, textInstances, focusIndex, handleSetFocusIndex } = this.props;

    return (
      <div>
        <p className={ classes.panelHead }>
          Image: { imageId }
        </p>
        <p className={ classes.panelHead }>
          Number of instances: { textInstances.length }
        </p>
        {imageReported ?
          (
            <p>Image reported</p>
          ):
          (
            <Button
              className={classes.button}
              color="secondary"
              onClick={() => {this.reportImage();}}>
              Report Image
            </Button>
          )
        }

        <hr className={ classes.hr } />
        {textInstances.map((instance, index) => (
          <TextInstanceExpansionPanel
            panelId={ index }
            expanded={ focusIndex === index }
            handleSetFocusIndex={ handleSetFocusIndex }
            annotation={ instance }
          />
        ))}

      </div>
    );
  }
}

ImageInfoPanel.propTypes = {
  classes: PropTypes.object.isRequired,
  imageId: PropTypes.number.isRequired,
  textInstances: PropTypes.arrayOf(PropTypes.shape({
    instance_id: PropTypes.string,
    text: PropTypes.string,
    legibility: PropTypes.number,
    class: PropTypes.number,
    language: PropTypes.number,
  })),
  focusIndex: PropTypes.number.isRequired,
  handleSetFocusIndex: PropTypes.func.isRequired,
};

export default withStyles(styles)(ImageInfoPanel);
