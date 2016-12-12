import ReactDOM from 'react-dom';
import React from 'react';
import Footer from './components/footer';
import Header from './components/header';

class About extends React.Component {
    render() {
        return (
          <div>
            <Header />
            <div className="about">
              About Us
            </div>
            <Footer />
          </div>
        );
    }
}

export default About;