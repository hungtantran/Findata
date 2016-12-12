import ReactDOM from 'react-dom';
import React from 'react';
import Footer from './components/footer';
import Header from './components/header';

var NotFound = React.createClass({
    render: function() {
        return (
            <div>
              <Header />
              <div className="notfound">
                404 Not Found
              </div>
              <Footer />
            </div>
        );
    }
});

export default NotFound;