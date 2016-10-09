import React from 'react'
import GetCookie from './utilities';

class Header extends React.Component {
  constructor(props) {
      super(props);
    }

    render() {
      var navMenu = "";
      var username = GetCookie("Username");
      var fullname = GetCookie("Fullname");
      if (username !== "" && fullname !== "") {
        navMenu = (
          <nav className="col-sm-8">
              <p><a href="/about">About Us</a></p>
              <p><a href="/contact">Contact Us</a></p>
              <div className="dropdown">
                <a href="#">{fullname} ({username})</a>
                <ul className="dropdown_menu">
                  <li className="dropdown_item"><a href="#">Manager Account</a></li>
                  <li className="dropdown_item"><a href="/logout">Sign out</a></li>
                </ul>
              </div>
          </nav>
        );
      } else {
        navMenu = (
          <nav className="col-sm-8">
              <p><a href="/about">About Us</a></p>
              <p><a href="/contact">Contact Us</a></p>
              <p><a href="/login">Login</a></p>
              <p><a href="/signup">Register</a></p>
          </nav>
        );
      }

      var header = (
        <div id="header" className='container'>
          <div className="row">
            <h1 className="col-sm-4">
              <a href="/">Findata</a>
            </h1>
            {navMenu}
          </div>
        </div>
      );
      return header;
    }
}

export default Header