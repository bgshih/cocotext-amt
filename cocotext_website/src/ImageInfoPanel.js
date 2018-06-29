import React, { Component } from 'react';
import PropTypes from 'prop-types';

import { withStyles } from '@material-ui/core/styles';

import TextInstanceExpansionPanel from './TextInstanceExpansionPanel.js';


const styles = theme => ({
  panelHead: {
    fontSize: 13,
    marginBottom: 5
  },
  hr: {
    marginTop: 10,
    marginBottom: 10
  }
})


class ImageInfoPanel extends Component {

  correctInstance() {
    
  }

  render() {
    const { classes, imageId, textInstances, focusIndex, handleSetFocusIndex } = this.props;

    return (
      <div>
      <p className={ classes.panelHead }>
          Image: { imageId }
        </p>
        <p className={ classes.panelHead }>
          Number of instances: { textInstances.length }
        </p>
        <hr className={ classes.hr } />
        {textInstances.map((instance, index) => (
          <TextInstanceExpansionPanel
            instanceId={ instance.instanceId }
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
    text: PropTypes.string,
    legibility: PropTypes.number,
    class: PropTypes.number,
    language: PropTypes.number,
  })),
  focusIndex: PropTypes.number.isRequired,
  handleSetFocusIndex: PropTypes.func.isRequired,
};

export default withStyles(styles)(ImageInfoPanel);
