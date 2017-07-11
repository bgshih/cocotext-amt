import React, { Component } from 'react';
import * as eventTypes from './eventTypes';

window.paper = require('paper');


export class Canvas extends Component {
  constructor(props) {
    super(props);

    this.annotationShapeLayer = null;
    this.staticShapeLayer = null;
    this.imageLayer = null;
  }

  componentDidMount() {
    // setup paper.js on canvas
    window.paper.setup(this.refs.rawCanvas);
    window.paper.settings.handleSize = 8;

    // create paper.js layers
    // layer order: imageLayer on the bottom, annotationShapeLayer on the top
    this.imageLayer = window.paper.project.activeLayer;
    this.staticShapeLayer = new window.paper.Layer();
    this.annotationShapeLayer = new window.paper.Layer();

    // canvas event listeners
    window.addEventListener(eventTypes.ZOOM_TO_FIT, this.zoomToFit.bind(this));
    window.addEventListener(eventTypes.RESET_ANNOTATIONS, this.resetAnnotations.bind(this));
    window.addEventListener(eventTypes.SUBMIT_ANNOTATIONS, this.submitAnnotations.bind(this));
    window.addEventListener(eventTypes.TOGGLE_HINTS, this.toggleHints.bind(this));

    // create image raster
    this.imageLayer.activate();
    this.raster = new window.paper.Raster();

    this.annotationShapeLayer.activate();
  }

  componentWillUpdate(nextProps, nextState) {
    if (this.props.imageUrl !== nextProps.imageUrl) {
      this.loadImage(nextProps.imageUrl);
      this.drawHints(nextProps.hints);
      this.drawStaticPolygons(nextProps.staticPolygons);
    }
  }

  /**
   * Load image from given URL and change the view to fit the image.
   */
  loadImage(imageUrl) {
    this.imageLayer.activate();

    this.raster.source = imageUrl;
    this.raster.onLoad = () => {
      // in the project space, image is aligned to the topleft
      this.raster.pivot = this.raster.bounds.topLeft;
      this.raster.position = new window.paper.Point(0, 0);
      // adjust view to fit image
      this.zoomToFit();
    };

    this.annotationShapeLayer.activate();
  }

  /**
   * Draw hints as stars on the static shape layer.
   */
  drawHints(hints) {
    this.staticShapeLayer.activate();

    for (var i = 0; i < hints.length; i++) {
      const hintX = hints[i].x;
      const hintY = hints[i].y;
      const hintCenter = new window.paper.Point(hintX, hintY);
      const nPoints = 5;
      const r1 = 2;
      const r2 = 3 * r1;
      const hintPath = new window.paper.Path.Star(hintCenter, nPoints, r1, r2);
      hintPath.fillColor = 'yellow';
      hintPath.strokeWidth = 1;
      hintPath.strokeColor = 'red';
    }

    this.annotationShapeLayer.activate();
  }

  /**
   * Draw existing polygons on the static shape layer.
   */
  drawStaticPolygons(polygons) {
    this.staticShapeLayer.activate();

    for (var i = 0; i < polygons.length; i++) {
      const polygonPoints = polygons[i];

      var staticPolygon = new window.paper.Path();
      for (var j = 0; j < polygonPoints.length; j++) {
        const pointX = polygonPoints[j].x;
        const pointY = polygonPoints[j].y;
        staticPolygon.add(new window.paper.Point(pointX, pointY));
      }
      staticPolygon.closed = true;
      staticPolygon.selected = false;
      staticPolygon.fillColor = 'rgba(0, 0, 255, 0.4)';
      staticPolygon.strokeColor = 'rgba(0, 0, 255, 0.8)';
      staticPolygon.strokeWidth = 1;
    }
    
    this.annotationShapeLayer.activate();
  }

  /**
   * Submit the annotations to the MTurk server
   */
  submitAnnotations() {
    const urlParams = this.props.urlParams;

    // collect polygon data
    var polygonData = [];
    for (const polygon of this.annotationShapeLayer.children) {
      const polygonPoints = [];
      for (const segment of polygon.segments) {
        polygonPoints.push({
          x: segment.getPoint().x,
          y: segment.getPoint().y
        })
      }
      polygonData.push(polygonPoints);
    }

    var form = document.createElement("form");
    form.method = 'POST';
    form.action = urlParams.turkSubmitTo + '/mturk/externalSubmit';
    const appendField = (key, value) => {
      var field = document.createElement("input");
      field.name = key;
      field.value = value;
      form.appendChild(field);
    }
    appendField('assignmentId', urlParams.assignmentId);
    appendField('answerData', JSON.stringify(polygonData));

    document.body.appendChild(form);
    form.submit();
  }

  toggleHints() {
    this.staticShapeLayer.visible = !this.staticShapeLayer.visible;
  }

  resetAnnotations() {
    this.annotationShapeLayer.removeChildren();
    this.zoomToFit();
  }

  zoomToFit() {
    if (this.raster === null || this.raster.loaded === false) {
      console.error('Cannot fit view: No image loaded.');
      return;
    }
    var view = window.paper.view;
    const imageWidth = this.raster.size.width;
    const imageHeight = this.raster.size.height;
    const widthRatio = view.viewSize.width / imageWidth;
    const heightRatio = view.viewSize.height / imageHeight;
    view.center = new window.paper.Size(0.5 * imageWidth, 0.5 * imageHeight);
    view.zoom = Math.min(widthRatio, heightRatio);
  }

  render() {
    return (
      <canvas className="annotationCanvas"
              ref="rawCanvas"
              width={this.props.width}
              height={this.props.height}>
      </canvas>
    );
  }
}
