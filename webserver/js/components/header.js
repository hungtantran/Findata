import React from 'react';
import GetCookie from '../redux/common/utilities';

class Header extends React.Component {
    constructor(props) {
        super(props);
    }

    signout() {
        gapi.auth2.getAuthInstance().signOut();
    }

    render() {
        var navMenu = '';
        var username = GetCookie('Username');
        var fullname = GetCookie('Fullname');
        // If user is logined
        if (username !== '' && fullname !== '') {
            navMenu = (
              <ul className="nav navbar-nav navbar-right">
                  <li><a href='/about'>About Us</a></li>
                  <li><a href='/contact'>Contact Us</a></li>
                  <li className="dropdown">
                    <a
                      href="#"
                      className="dropdown-toggle"
                      data-toggle="dropdown"
                      role="button"
                      aria-haspopup="true"
                      aria-expanded="false"
                      style={{backgroundColor: 'black'}}
                    >
                        {fullname} ({username})
                        <span className="caret"></span>
                    </a>
                    <ul className="dropdown-menu" style={{width: '100%', backgroundColor: 'black'}}>
                      <li><a href='/logout'>Sign out</a></li>
                    </ul>
                  </li>
              </ul>
            );
        } else {
            // If user is not logined
            navMenu = (
              <ul className="nav navbar-nav navbar-right">
                  <li><a href='/about'>About Us</a></li>
                  <li><a href='/contact'>Contact Us</a></li>
                  <li><a href='/login'>Login</a></li>
                  <li><a href='/signup'>Register</a></li>
               </ul>
            );
        }

        var header = (
          <nav id='header' className="navbar navbar-default">
            <div className="container-fluid">
              <div className="navbar-header">
                <h1 className='col-sm-4'>
                  <a href='/'>Findata</a>
                </h1>
              </div>
              {navMenu}            
            </div>
          </nav>
        );
        return header;
    }
}

export default Header;