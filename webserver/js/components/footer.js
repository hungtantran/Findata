import React from 'react'

var Footer = React.createClass({
  render: function() {
    return (
      <div id="footer" className='container'>
        <footer className="container">
          <div className="row">
            <p className="col-sm-4">&copy; 2016 Findata</p>
            <ul className="col-sm-8">
              <li className="col-sm-1">
                <img src="https://s3.amazonaws.com/codecademy-content/projects/make-a-website/lesson-4/twitter.svg"/>
              </li>
              <li className="col-sm-1">
                <img src="https://s3.amazonaws.com/codecademy-content/projects/make-a-website/lesson-4/facebook.svg"/>
              </li>
              <li className="col-sm-1">
                <img src="https://s3.amazonaws.com/codecademy-content/projects/make-a-website/lesson-4/instagram.svg"/>
              </li>
              <li className="col-sm-1">
                <img src="https://s3.amazonaws.com/codecademy-content/projects/make-a-website/lesson-4/medium.svg"/>
              </li>
            </ul>
          </div>
        </footer>
      </div>
    );
  }
});

export default Footer