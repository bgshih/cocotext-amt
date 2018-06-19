import React, { Component } from 'react';
import PropTypes from 'prop-types';

import { withStyles } from '@material-ui/core/styles';
import ExpansionPanel from '@material-ui/core/ExpansionPanel';
import ExpansionPanelSummary from '@material-ui/core/ExpansionPanelSummary';
import ExpansionPanelDetails from '@material-ui/core/ExpansionPanelDetails';
import Typography from '@material-ui/core/Typography';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';

import TextInstanceExpansionPanel from './TextInstanceExpansionPanel.js';


export class ImageInfoPanel extends Component {  
  render() {
    return (
      <div>
        <TextInstanceExpansionPanel
          instanceId={"12345"}
          textAnnotation={"hello"}
          legible={false}
          machinePrinted={true}
          language={"English"}
        />
      </div>
    );
  }
}

ImageInfoPanel.propTypes = {
  // textInstances: PropTypes.arrayOf(PropTypes.instanceOf)
};

// export default withStyles(styles)(ImageInfoPanel);
export default ImageInfoPanel;
