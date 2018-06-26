import React from 'react';
import PropTypes from 'prop-types';

import { withStyles } from '@material-ui/core/styles';
import ExpansionPanel from '@material-ui/core/ExpansionPanel';
import ExpansionPanelSummary from '@material-ui/core/ExpansionPanelSummary';
import ExpansionPanelDetails from '@material-ui/core/ExpansionPanelDetails';
import Typography from '@material-ui/core/Typography';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';


const styles = theme => ({
  // root: {
  //   width: '100%',
  // },
  heading: {
    fontSize: 13,
    flexBasis: '40%',
    flexShrink: 0,
  },
  secondaryHeading: {
    // fontSize: theme.typography.pxToRem(20),
    fontSize: 13,
    color: theme.palette.text.secondary,
    textOverflow: "ellipsis",
    overflow: "hidden",
    width: "60%"
  },
  details: {
    fontSize: 13
  }
});

function TextInstanceExpansionPanel(props) {
  const { classes, textAnnotation, legible, machinePrinted, language,
          expanded, panelId, handleSetFocusIndex } = props;

  const textDisplay = (legible && language === "English") ? ('"' + textAnnotation + '"') : "-";

  return (
    <div>
      <ExpansionPanel
        expanded={expanded}
        onChange={ () => {
          const newFocusIndex = expanded ? -1 : panelId;
          handleSetFocusIndex(newFocusIndex);
        } }>
        <ExpansionPanelSummary expandIcon={<ExpandMoreIcon />}>
          <Typography className={classes.heading}>{ "Instance " + panelId }</Typography>
          <Typography className={classes.secondaryHeading}>{ textDisplay }</Typography>
        </ExpansionPanelSummary>
        <ExpansionPanelDetails>
          <Typography className={classes.details}>
            <ul>
              <li>{ "Text: " + textDisplay }</li>
              <li>{ "Legible: " + (legible ? "True" : "False") }</li>
              <li>{ "Machine Printed: " + (machinePrinted ? "True" : "False") }</li>
              <li>{ "Language: " + language}</li>
            </ul>
          </Typography>
        </ExpansionPanelDetails>
      </ExpansionPanel>
    </div>
  );
}

TextInstanceExpansionPanel.propTypes = {
  classes: PropTypes.object.isRequired,
  panelId: PropTypes.number.isRequired,
  expanded: PropTypes.bool.isRequired,
  handleSetFocusIndex: PropTypes.func.isRequired,
  instanceId: PropTypes.string.isRequired,
  legible: PropTypes.bool.isRequired,
  machinePrinted: PropTypes.bool.isRequired,
  language: PropTypes.string.isRequired,
};

export default withStyles(styles)(TextInstanceExpansionPanel);
