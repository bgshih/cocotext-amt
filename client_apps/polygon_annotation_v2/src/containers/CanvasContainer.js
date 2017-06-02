import { connect } from 'react-redux'

const handleMouseMove = (e) => {
  e.preventDefault()
  dispatch()
}

let CanvasContainer = ({ dispatch }) => (
  <Canvas polygons={}
          viewParams={}
          activeTool={}
          onChangeView={}
          />
)
