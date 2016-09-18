import ReactDOM from 'react-dom'
import React from 'react' 
import Footer from './components/footer'
import Header from './components/header'

var Login = React.createClass({
  render: function() {
    return (
      <div className="login">
        Login
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
  <Login />,
  document.getElementById('content'));