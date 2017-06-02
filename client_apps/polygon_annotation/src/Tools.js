window.paper = require('paper');

export class ChangeViewTool extends window.paper.Tool {
  constructor(setInfobar) {
    super();
    this.setInfobar = setInfobar;
  }

  activate() {
    super.activate();
    this.onMouseDrag = this.handleMouseDrag;
  }

  handleMouseDrag(event) {
    // Note: event.delta is the delta on project space
    // FIXME: problematic movement
    const movementX = event.event.movementX;
    const movementY = event.event.movementY;
    window.paper.view.translate(new window.paper.Point(movementX, movementY));
  }
}


export class DrawPolygonTool extends window.paper.Tool {
  constructor(setInfobar) {
    super();
    // callback
    this.setInfobar = setInfobar;
    this.onComplete = null;
    // status
    this.dynamicPolygon = null;
  }

  activate() {
    if (this.dynamicPolygon !== null) {
      this.dynamicPolygon.remove();
      this.dynamicPolygon = null;
    }

    super.activate();

    // register event handlers
    this.onMouseDown = this.handleMouseDown;
    this.onMouseMove = this.handleMouseMove;
    this.onMouseDrag = this.handleMouseDrag;
    this.onMouseUp = this.handleMouseUp;
    this.onKeyUp = function (event) {
      event.preventDefault();
      if (event.key === 'escape') {
        this.completeCreation();
      }
    }

    // start from a invisible position
    this.startNewPolygon(new window.paper.Point(-1000, -1000));
  }

  startNewPolygon(initPoint) {
    var newPolygon = new window.paper.Path();
    newPolygon.add(initPoint);
    // newPolygon.fillColor = 'rgba(15, 187, 255, 0.5)';
    // newPolygon.strokeColor = 'rgba(15, 187, 255, 0.9)';
    newPolygon.fillColor = 'rgba(0, 255, 0, 0.4)';
    newPolygon.strokeColor = 'rgba(0, 255, 0, 0.9)';
    newPolygon.strokeWidth = 1;
    newPolygon.closed = true; // always closed
    newPolygon.selected = true; // show handles
    this.dynamicPolygon = newPolygon;

    this.setInfobar('info', 'Click on the canvas to put a polygon node.');
  }
  
  handleMouseDown(event) {
    event.event.preventDefault();

    if (this.dynamicPolygon === null) {
      // start a new polygon
      this.startNewPolygon(event.point);
    } else {
      // add a segment (vertex)
      this.dynamicPolygon.add(event.point.clone());
      this.setInfobar('info', 'Move and click to add other nodes. Press ESC to finish this polygon. (The last node will be discarded)');
    }
  }

  handleMouseMove(event) {
    if (this.dynamicPolygon === null) {
      return;
    }

    // move the last segment
    this.dynamicPolygon.lastSegment.point = event.point;
  }

  isPolygonValid(polygon) {
    // more checks
    if (polygon.segments.length <= 3) {
      return false;
    }
    return true;
  }

  completeCreation() {
    if (this.dynamicPolygon === null) {
      return;
    }
    
    if (this.isPolygonValid(this.dynamicPolygon) === true) {
      // remove the last segment and callback
      this.dynamicPolygon.lastSegment.remove();
      this.dynamicPolygon.selected = false;
      var resultPolygon = this.dynamicPolygon;
      if (this.onComplete !== null) {
        this.onComplete(resultPolygon);
      }
      this.setInfobar('info', 'Click on the canvas to draw another. Or click "Edit Polygon" to edit.');
    } else {
      // discard invalid polygon
      this.dynamicPolygon.remove();
      this.setInfobar('warning', 'Polygon discarded: not enough nodes.');
    }

    // reset dynamicPolygon (but it is might not be removed from canvas)
    this.dynamicPolygon = null;
  }
}


export class EditPolygonTool extends window.paper.Tool {
  constructor(setInfobar) {
    super();
    
    this.activePolygon = null;
    this.activeSegment = null;
    this.setInfobar = setInfobar;
  }

  activate() {
    // start receiving events
    super.activate();

    // register event handlers
    this.onMouseMove = this.handleMouseMove;
    this.onMouseDown = this.handleMouseDown;
    this.onMouseDrag = this.handleMouseDrag;
    this.onMouseUp = this.handleMouseUp;
    window.addEventListener('delete_polygon', this.handleDeleteActivePolygon.bind(this));

    this.setInfobar('info', 'Select a polygon to edit.');
  }

  handleMouseMove(event) {
    if (this.activePolygon !== null) {
      // reset segment selection
      for (let segment of this.activePolygon.segments) {
        segment.selected = false;
      }
      
      // set the hit segment to selected
      const hitOptions = {
        segments: true,
        stroke: false,
        fill: false,
        tolerance: 5
      };
      const hitResult = this.activePolygon.hitTest(event.point, hitOptions);
      if (hitResult !== null && hitResult.type === 'segment') {
        for (let i = 0; i < this.activePolygon.segments.length; i++) {
          if (hitResult.segment === this.activePolygon.segments[i]) {
            this.activePolygon.segments[i].selected = true;
            break;
          }
        }
        // for (let segment of this.activePolygon.segments) {
        //   if (hitResult.segment === segment) {
        //     segment.selected = true;
        //     break;
        //   }
        // }
      }
      // const hitResult = window.paper.project.activeLayer.hitTest(event.point, hitOptions);
      // if (hitResult !== null && hitResult.type === 'segment') {
      //   for (let segment of this.activePolygon.segments) {
      //     if (hitResult.segment === segment) {
      //       segment.selected = true;
      //       break;
      //     }
      //   }
      // }
    }
  }

  handleMouseDown(event) {
    const hitTolerance = 5;

    // reset activeSegment
    this.activeSegment = null;

    // set activePolygon to the polygon to be edited
    const fillHitOptions = {
      segments: false,
      stroke: false,
      fill: true,
      tolerance: hitTolerance
    }
    const fillHitResult = window.paper.project.activeLayer.hitTest(event.point, fillHitOptions);
    if (fillHitResult === null || fillHitResult.type !== 'fill') {
      // if nothing is hit, reset active polygon and return
      if (this.activePolygon !== null) {
        this.activePolygon.selected = false;
      }
      this.activePolygon = null;
      this.setInfobar('info', 'Select a polygon to edit.');
      return;
    } else {
      if (this.activePolygon === null) {
        this.activePolygon = fillHitResult.item;
        this.activePolygon.selected = true;
        this.setInfobar('info', 'Drag the polygon or one of its nodes to edit. Click "Delete Polygon" to delete the polygon.');
      }
      // else, continue to the following
    }

    // edit the activePolygon

    // perform another hit test to determine whether to translate the polygon or move a node
    const hitOptions = {
      segments: true,
      stroke: false,
      fill: true,
      tolerance: hitTolerance
    }
    const hitResult = this.activePolygon.hitTest(event.point, hitOptions);
    if (hitResult.type === 'fill') {
      // translate the polygon by mouse dragging
      // do nothing here
    } else if (hitResult.type === 'segment') {
      const segment = hitResult.segment;
      for (var i = 0; i < this.activePolygon.segments.length; i++) {
        if (segment === this.activePolygon.segments[i]) {
          this.activeSegment = segment;
          break;
        }
      }
    }
  }

  // move active segment
  handleMouseDrag(event) {
    if (this.activeSegment !== null) {
      this.activeSegment.point = event.point;
    } else if (this.activePolygon !== null) {
      this.activePolygon.translate(event.delta);
    }
  }

  handleDeleteActivePolygon(event) {
    if (this.activePolygon !== null) {
      this.activePolygon.remove();
    }
  }

  completeEditing() {
    // reset status
    this.activePolygon.selected = false;
    this.activePolygon = null;
    this.activeSegment = null;
  }
}
