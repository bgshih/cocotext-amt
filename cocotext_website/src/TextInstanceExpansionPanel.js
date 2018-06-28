import React, { Component } from 'react';
import PropTypes from 'prop-types';

import { withStyles } from '@material-ui/core/styles';
import ExpansionPanel from '@material-ui/core/ExpansionPanel';
import ExpansionPanelSummary from '@material-ui/core/ExpansionPanelSummary';
import ExpansionPanelDetails from '@material-ui/core/ExpansionPanelDetails';
import Typography from '@material-ui/core/Typography';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import { FormControl, Input, InputLabel, Select, MenuItem } from '@material-ui/core';


const styles = theme => ({
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
  },
  correctButton: {
    fontSize: 13,
  },
  textField: {
    fontSize: 13,
  },
  form: {
    width: 250,
    marginLeft: 10,
    marginBottom: 20,
  },
});

class TextInstanceExpansionPanel extends Component {

  constructor(props) {
    super(props);
  }

  render() {
    const { classes, text, legibilityLabel, languageLabel, classLabel,
            expanded, panelId, handleSetFocusIndex } = this.props;

    const textDisplay = (legibilityLabel === 0) ? ('"' + text + '"') : "-";

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
              <FormControl className={classes.form}>
                <InputLabel className={classes.textField}>Text</InputLabel>
                <Input className={classes.textField} value={text === "" ? "<None>" : text} disabled={true} />
              </FormControl>

              <FormControl className={classes.form}>
                <InputLabel className={classes.textField}>Legibility</InputLabel>
                <Select className={classes.textField} value={0} disabled={true}>
                  <MenuItem className={classes.textField} value={0}>Legible</MenuItem>
                  <MenuItem className={classes.textField} value={1}>Illegible</MenuItem>
                </Select>
              </FormControl>

              <FormControl className={classes.form}>
                <InputLabel className={classes.textField}>Class</InputLabel>
                <Select className={classes.textField} value={0} disabled={true}>
                  <MenuItem className={classes.textField} value={0}>Machine Printed</MenuItem>
                  <MenuItem className={classes.textField} value={1}>Handwritten</MenuItem>
                </Select>
              </FormControl>

              <FormControl className={classes.form}>
                <InputLabel className={classes.textField}>Language</InputLabel>
                <Select className={classes.textField} value={0} disabled={true}>
                  <MenuItem className={classes.textField} value={0}>English</MenuItem>
                  <MenuItem className={classes.textField} value={1}>non-English</MenuItem>
                </Select>
              </FormControl>

              {/* <Button
                className={classes.correctButton}
                variant="contained"
                onClick={() => {
                  this.setState({correctionModalOn: true})
                }}>
                Correct
              </Button> */}
            </Typography>
          </ExpansionPanelDetails>
        </ExpansionPanel>
      </div>
    );
  }
}

TextInstanceExpansionPanel.propTypes = {
  classes: PropTypes.object.isRequired,
  panelId: PropTypes.number.isRequired,
  expanded: PropTypes.bool.isRequired,
  handleSetFocusIndex: PropTypes.func.isRequired,
  instanceId: PropTypes.string.isRequired,
  text: PropTypes.string.isRequired,
  legibilityLabel: PropTypes.number.isRequired,
  classLabel: PropTypes.number.isRequired,
  languageLabel: PropTypes.number.isRequired,
};

export default withStyles(styles)(TextInstanceExpansionPanel);
