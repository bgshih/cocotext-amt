import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';

class ImgPart extends React.Component {
  render(){
    var temp = "";
    var imgId = this.props.imgId.toString();
    var imgUrl;

    for(var i=0;i<12-imgId.length;i++){
      temp+='0';
    }
    if(imgId!=='-1'){
      imgUrl = 'https://s3.amazonaws.com/cocotext-images/train2014/COCO_train2014_'
        +temp+imgId+'.jpg';
    } else {
      imgUrl = 'data:image/gif;base64,R0lGODlhAQABAAAAACwAAAAAAQABAAA=';
    }

    return(
        <img src={imgUrl} alt="img not found" 
          style={{margin: "25px"}}/>
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
    this.handleClickPrev = this.handleClickPrev.bind(this);
    this.handleClickNext = this.handleClickNext.bind(this);
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

  handleClickPrev(){
    var currIdx = this.state.idx;
    var idx;
    if(currIdx!==0){
      idx = currIdx-1;
    } else {
      idx = this.state.jsonValue.data.length-1;
    }
    this.setState({
      idx: idx,
      imgId: this.state.jsonValue.data[idx].image_id,
      currAnnotations: this.state.jsonValue.data[idx].annotations
    })
  }

  handleClickNext(){
    var currIdx = this.state.idx;
    var idx;
    if(currIdx!==this.state.jsonValue.data.length-1){
      idx = currIdx+1;
    } else {
      idx = 0;
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
          <img src={logo} className="App-logo" alt="logo" />
          <h2>Welcome to CoCo Browser</h2>
        </div>

        <div className="img">
        <ImgPart imgId={this.state.imgId}/>  
        </div>

        <div className="textArea">
          <form onSubmit={this.handleSubmit}>
            <input type="text" value={this.state.value} onChange={this.handleChange} 
              style={{width: "50%", height: "200px", margin: "5px"}}/>
              <br/>
            <input type="submit" value="Update" />
          </form>

          <button onClick = {this.handleClickPrev}>
            Previous
          </button>

          <button onClick = {this.handleClickNext}>
            next
          </button>
        </div>
      </div>
    );
  }
  
}

export default App;
