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

  render() {
    const { classes, imageId, textInstances } = this.props;

    return (
      <div>
      <p className={ classes.panelHead }>
          Image: { imageId }
        </p>
        <p className={ classes.panelHead }>
          Number of instances: { textInstances.length }
        </p>
        <hr className={ classes.hr } />
        {textInstances.map(instance => (
          <TextInstanceExpansionPanel
            instanceId={ instance.instanceId }
            textAnnotation={ instance.text }
            legible={ instance.legible }
            machinePrinted={ instance.machinePrinted }
            language={ instance.unknownLanguage ? "non-English" : "English" }
          />
        ))}

      </div>
    );
  }
}

ImageInfoPanel.propTypes = {
  classes: PropTypes.object.isRequired,
  imageId: PropTypes.number.isRequired,
  textInstances: PropTypes.arrayOf(PropTypes.object)
};

export default withStyles(styles)(ImageInfoPanel);
