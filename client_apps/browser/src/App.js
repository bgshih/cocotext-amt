import React, { Component } from 'react';
import './App.css';
import {Button, ButtonGroup} from 'react-bootstrap';

class ImgPart extends React.Component {
  constructor(props){
    super(props);
    this.updateCanvas = this.updateCanvas.bind(this);
  }
  componentDidMount() {
    this.updateCanvas(-1);
  }

  componentDidUpdate() {
    this.updateCanvas(-1);
  }

  updateCanvas(flag) {
    const ctx = this.refs.canvas.getContext('2d');
    const image = new Image();
    var imgId = this.props.imgId.toString();
    var canvasWidth = this.props.canvasWidth;
    var canvasHeight = this.props.canvasHeight;
    var imgWidth = this.props.imgWidth;
    var imgHeight = this.props.imgHeight;
    var horMargin = (canvasWidth-imgWidth)/2;
    var verMargin = (canvasHeight-imgHeight)/2;
    var currAnnotations = this.props.currAnnotations;
    var temp = "";
    var imgUrl;
    // TODO: need a scale
    for(var i=0;i<12-imgId.length;i++){
      temp+='0';
    }
    if(imgId!=='-1'){
      imgUrl = 'https://s3.amazonaws.com/cocotext-images/train2014/COCO_train2014_'
        +temp+imgId+'.jpg';
    } else {
      imgUrl = 'data:image/gif;base64,R0lGODlhAQABAAAAACwAAAAAAQABAAA=';
    }

    image.src = imgUrl;
    image.onload = () => {
      ctx.drawImage(image, horMargin, verMargin, canvasWidth, canvasHeight);
      var isInitial = flag===-1;
      var length = isInitial? currAnnotations.length : 1;
      for(var i=0; i<length; i++){
        var idx = isInitial? i : flag;
        var currPolygon = currAnnotations[idx].polygon;
        ctx.beginPath();
        for(var j=0; j<currPolygon.length; j++){
          var x = currPolygon[j].x+horMargin;
          var y = currPolygon[j].y+verMargin;
          if(j===0){
            ctx.moveTo(x,y);
          } else{
            ctx.lineTo(x,y);
          }
        }
        ctx.closePath();
        ctx.lineWidth = 1;
        ctx.strokeStyle = 'rgba(0, 255, 0, 0.9)';
        ctx.stroke();
        ctx.fillStyle = 'rgba(0, 255, 0, 0.2)';
        ctx.fill();  
      }
    }
  }

  render(){
    var obj = this;
    var currAnnotations = this.props.currAnnotations;
    const currAnnotIds = [];

    for(var i=0; i<currAnnotations.length; i++){
      currAnnotIds.push(currAnnotations[i].annot_id.toString());
    }

    return(
      <div className="imgPart">
          <canvas ref="canvas" 
            height = {this.props.canvasHeight} 
            width={this.props.canvasWidth}></canvas>

          <ButtonGroup vertical className="annots">
            {currAnnotIds.map(function(item, key){
              return <Button key={key} bsStyle="primary" 
              onClick={()=>{obj.updateCanvas(key)}}> {item} </Button>;
            })}
          </ButtonGroup>
      </div>
    )
  }
}

class App extends Component {
  constructor(props){
    super(props);
    this.state = {
      text: '',
      jsonValue: {},
      idx: 0,
      imgId: -1,
      currAnnotations: [] 
    }
    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleClick = this.handleClick.bind(this);
  }

  isJsonStr(str) {
    if(str===""){
      return false;
    } 
    try{
      var temp = JSON.parse(str);
      if(temp && typeof temp==="object"){
        return true;
      }
    } catch (e) {
      return false;
    }
    return false;
  }

  handleChange(event) {
    this.setState({text: event.target.value});
  }

  handleSubmit(event) {
    var isJson = this.isJsonStr(this.state.text);

    if(isJson){
      try{  
        var obj = JSON.parse(this.state.text);
        this.setState({
          jsonValue: obj,
          idx: 0,
          imgId: obj.data[0].image_id,
          currAnnotations: obj.data[0].annotations
        })
      } catch (e){
        alert ("Input should follow the Json data format listed here:" + 
          "https://vision.cornell.edu/se3/coco-text-2/")
      }
    } else {
      alert ("Input is not valid Json value. Check the accepted format here" + 
          "https://vision.cornell.edu/se3/coco-text-2/")
    }
    event.preventDefault();
  }

  handleClick(flag){
    var currIdx = this.state.idx;
    var isNext = flag===1;
    var idx;
    var temp = isNext? this.state.jsonValue.data.length-1:0;
    
    if(this.state.imgId===-1){
      alert ("Please input your json data and click update first!");
      return;
    }
    
    if(currIdx!==temp){
      idx = isNext? currIdx+1 : currIdx-1;
    } else {
      idx = isNext? 0: this.state.jsonValue.data.length-1;
    }
    this.setState({
      idx: idx,
      imgId: this.state.jsonValue.data[idx].image_id,
      currAnnotations: this.state.jsonValue.data[idx].annotations
    })
  }

  render() {
    return (
      <div className="App">
        <div className="App-header">
          <h2>Welcome to CoCo Browser</h2>
        </div>

        <div className="img">
          <ImgPart imgId={this.state.imgId} canvasWidth={350} 
            canvasHeight={350} imgWidth={300} imgHeight={300}
            currAnnotations={this.state.currAnnotations}/>  
        </div>

        <div className="textArea">
          <h4> Please input your json data below: </h4>
          <form onSubmit={this.handleSubmit}>
            <input type="text" value={this.state.value} onChange={this.handleChange} 
              style={{width: "50%", height: "135px", margin: "15px"}}/>
              <br/>
              <ButtonGroup style={{margin: "15px"}}>
                <Button type="submit" bsStyle="primary" >
                  Update
                </Button>
                <Button  bsStyle="primary" onClick={()=>this.handleClick(-1)}>
                  Previous
                </Button>
                <Button bsStyle="primary" onClick={()=> this.handleClick(1)}>
                  Next
                </Button>
              </ButtonGroup>
          </form>
        </div> 
      </div>
    );
  }
}

export default App;
