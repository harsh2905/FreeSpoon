//Index

import React from 'react'
import ReactDOM from 'react-dom'

import Framework from '../components/Framework.jsx'
import Face from '../components/Face.jsx'
import Footer from '../components/Footer.jsx'

window.onload = function(){

//ReactDOM.render(<Framework headerComponent={Face} footerComponent={Footer} />, 
ReactDOM.render(<Framework footerComponent={Footer} />, 
	document.getElementById('content'));

}
