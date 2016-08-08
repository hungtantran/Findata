import React from 'react'

var Header = React.createClass({
  render: function() {
    return (
      <div className="navbar navbar-inverse">
        <div className="navbar-header">
          <button type="button" className="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
            <span className="sr-only">Toggle navigation</span>
            <span className="icon-bar"></span>
            <span className="icon-bar"></span>
            <span className="icon-bar"></span>
          </button>
          <a className="navbar-brand" href="/">Findata</a>
        </div>
        <div id="navbar" className="collapse navbar-collapse navbar-right">
          <ul className="nav navbar-nav">
            <li><a href="/about">About</a></li>
            <li><a href="/contact">Contact</a></li>
          </ul>
        </div>
      </div>
    );
  }
});

export default Header