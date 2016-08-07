import ReactDOM from 'react-dom'
import React from 'react' 
import Footer from './components/footer'
import Header from './components/header'

var About = React.createClass({
  render: function() {
    return (
      <div className="about">
        About Us
      </div>
    );
  }
});

ReactDOM.render(
  <Footer />,
  document.getElementById('footer'));

ReactDOM.render(
  <Header />,
  document.getElementById('header'));

ReactDOM.render(
  <About />,
  document.getElementById('content'));