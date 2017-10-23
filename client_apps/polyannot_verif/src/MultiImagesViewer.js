import React, { Component } from 'react';
import { Pagination } from 'react-bootstrap';
import PropTypes from 'prop-types';

import { ImageViewer } from './ImageViewer';


export class MultiImagesViewer extends Component {
  constructor(props) {
    super(props);
    this.state = {
      activeIndex: 0
    }
    this.handleKeyDown = this.handleKeyDown.bind(this);
  }

  componentDidMount() {
    window.addEventListener("keydown", this.handleKeyDown);
  }

  componentWillUnmount() {
    window.removeEventListener("keydown", this.handleKeyDown);
  }

  componentDidUpdate(prevProps, prevState) {
    if (this.props.imagesList.length !== prevProps.imagesList.length) {
      this.setState({
        activeIndex: 0
      });
    }
  }

  handleKeyDown(e) {
    var newActiveIndex;
    switch (e.keyCode) {
      case 37: // left arrow
        newActiveIndex = Math.max(this.state.activeIndex - 1, 0);
        this.setState({
          activeIndex: newActiveIndex});
        break;
      case 39: // right arrow
        newActiveIndex = Math.min(this.state.activeIndex + 1, this.props.imagesList.length - 1);
        this.setState({
          activeIndex: newActiveIndex});
        break;
      case 49: // digit 1
      case 50: // digit 2
      case 51: // digit 3
      case 52: // digit 4
        const imageAndAnnotations = this.getActiveImageAndAnnotations();
        if (imageAndAnnotations !== null) {
          const mark = {
            49: 'C', // correct
            50: 'W', // wrong
            51: 'R', // revision-or-further-work
            52: 'U', // unchecked
          }[e.keyCode];
          this.props.setUserMark(this.state.activeIndex, mark);
        }
        break;
      default:
        break;
    }
  }

  getActiveImageAndAnnotations() {
    const imageAndAnnotations = (this.state.activeIndex >= 0 && 
      this.state.activeIndex < this.props.imagesList.length) ?
      this.props.imagesList[this.state.activeIndex] :
      null;
    return imageAndAnnotations;
  }

  render() {
    const imageAndAnnotations = this.getActiveImageAndAnnotations();
    const imageId = imageAndAnnotations === null ? null : imageAndAnnotations.imageId;
    const annotations = imageAndAnnotations === null ? null : imageAndAnnotations.annotations;
    const userMark = imageAndAnnotations === null ? null : imageAndAnnotations.userMark;

    return (
      <div>
        <ImageViewer
          canvasWidth={this.props.canvasWidth}
          canvasHeight={this.props.canvasHeight}
          imageId={imageId}
          annotations={annotations}
          userMark={userMark}
        />
        <Pagination
          prev next first last ellipsis boundaryLinks
          items={this.props.imagesList.length}
          maxButtons={10}
          activePage={this.state.activeIndex + 1}
          onSelect={(e) => {
            this.setState({'activeIndex': e - 1});
          }}
        />
      </div>
    );
  }
}

MultiImagesViewer.propTypes = {
  canvasWidth: PropTypes.number.isRequired,
  canvasHeight: PropTypes.number.isRequired,
  imagesList: PropTypes.array.isRequired,
  setUserMark: PropTypes.func.isRequired,
};
