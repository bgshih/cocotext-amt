import React, { Component } from 'react'
import PropTypes from 'prop-types'

// const Canvas = ({polygons, onCanvasMouseMove, onCanvasMouseClick, onCanvasMouseDrag}) => (
//   <div>
//     <canvas onMouseMove={onCanvasMouseMove}
//             onClick={onCanvasMouseClick}
//             onDrag={onCanvasMouseDrag} />
//   </div>
// )

class CanvasTool {
  handleMouseMove() { }
  handleMouseDrag() { }
}

class ViewChangeTool extends CanvasTool {
  handleMouseDrag() {
    
  }
}

class Canvas extends Component {
  static propTypes = {
    polygons: ...
    viewParams: PropTypes.shape()
  }

  constructor(props) {
    this.viewTool = ViewChangeTool(this.props.onViewChange)

    this.paper = require('paper')
    this.activeTool = this.viewTool
  }

  componentWillUpdate(newProps) {
    // change canavs tool
    switch newProps.tool
    this.activeTool = ...

    // draw polygons
    ...
  }

  render() {
    return (
      <div>
        <canvas onMouseMove={this.activeTool.handleMouseMove}
                onMouseDrag={this.activeTool.handleMouseDrag}
                onClick={this.activeTool.handleClick} />
      </div>
    )
  }
}
