import ReactDOM from 'react-dom'
import React from 'react' 
import Footer from './components/footer'
import Header from './components/header'

var Signup = React.createClass({
  render: function() {
    return (
      <div className="signup">
        Signup
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
  <Signup />,
  document.getElementById('content'));