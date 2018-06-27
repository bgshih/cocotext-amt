import React, { Component } from 'react';
import PropTypes from 'prop-types';

import { Dialog, DialogTitle, FormControl, Input, InputLabel, Select,
         withStyles, DialogContent, DialogActions, Button, Typography, TextField, MenuItem } from "@material-ui/core";


const styles = theme => ({
  dialogTitle: {
    fontSize: 16
  },
  form: {
    width: 300,
    height: 30,
    marginLeft: 20,
    marginRight: 20,
    marginTop: 20,
  },
  textField: {
    fontSize: 13,
  },
  button: {
    fontSize: 13
  }
});

class TextInstanceCorrectionDialog extends Component {

  constructor(props) {
    super(props);
  }

  render() {
    const { classes, open, handleClosed } = this.props;
    
    return (
      <Dialog
        aria-labelledby="simple-dialog-title"
        open={open}
        onClose={handleClosed}>
        <DialogTitle>
          <Typography className={classes.dialogTitle}>
            Enter Corrections
          </Typography>
        </DialogTitle>
        <DialogContent>
          <FormControl className={classes.form}>
            <InputLabel className={classes.textField}>Text</InputLabel>
            <Input className={classes.textField} />
          </FormControl>
          <FormControl className={classes.form}>
            <InputLabel className={classes.textField}>Legibility</InputLabel>
            <Select className={classes.textField}>
              <MenuItem className={classes.textField}>Legible</MenuItem>
              <MenuItem className={classes.textField}>Illegible</MenuItem>
            </Select>
          </FormControl>
          <FormControl className={classes.form}>
            <InputLabel className={classes.textField}>Class</InputLabel>
            <Select>
              <MenuItem className={classes.textField}>Machine Printed</MenuItem>
              <MenuItem className={classes.textField}>Handwritten</MenuItem>
            </Select>
          </FormControl>
          <FormControl className={classes.form}>
            <InputLabel className={classes.textField}>Language</InputLabel>
            <Select className={classes.textField}>
              <MenuItem className={classes.textField}>English</MenuItem>
              <MenuItem className={classes.textField}>non-English</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button color="primary" className={classes.button}>
            Submit
          </Button>
          <Button color="primary"  className={classes.button} onClick={handleClosed}>
            Cancel
          </Button>
        </DialogActions>
      </Dialog>
    )
  }
};

TextInstanceCorrectionDialog.propTypes = {
  classes: PropTypes.object.isRequired,
  open: PropTypes.bool.isRequired,
  handleClosed: PropTypes.func.isRequired,
}

export default withStyles(styles)(TextInstanceCorrectionDialog);
