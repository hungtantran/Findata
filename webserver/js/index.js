import ReactDOM from 'react-dom';
import React from 'react'; 
import Workspace from './components/workspace';
import Footer from './components/footer';
import Header from './components/header';

ReactDOM.render(
  <Footer />,
  document.getElementById('footer'));

ReactDOM.render(
  <Header />,
  document.getElementById('header'));

ReactDOM.render(
  <Workspace />,
  document.getElementById('content'));