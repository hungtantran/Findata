import ReactDOM from 'react-dom'
import React from 'react' 
import Footer from './components/footer'
import Header from './components/header'

var NotFound = React.createClass({
  render: function() {
    return (
      <div className="notfound">
        404 Not Found
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
  <NotFound />,
  document.getElementById('content'));