import ReactDOM from 'react-dom'
import React from 'react' 
import Footer from './components/footer'
import Header from './components/header'

class Contact extends React.Component {
  render() {
    return (
      <div>
        <Header />
        <div className="contact">
          Contact Us
        </div>
        <Footer />
      </div>
    );
  }
}

export default Contact;