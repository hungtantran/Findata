import React from 'react'

var Header = React.createClass({
  render: function() {
    return (
      <div className="row">
        <h1 className="col-sm-4">
          <a href="/">Findata</a>
        </h1>
        <nav className="col-sm-8">
          <p><a href="/about">About Us</a></p>
          <p><a href="/contact">Contact Us</a></p>
          <p><a href="/login">Login</a></p>
          <p><a href="/signup">Register</a></p>
        </nav>
      </div>
    );
  }
});

export default Header