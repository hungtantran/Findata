import React from 'react'; 
import Root from './redux/containers/root';
import Footer from './components/footer';
import Header from './components/header';

class Home extends React.Component {
  render() {
    return (
        <div>
          <Header />
          <Root />
          <Footer />
        </div>
    );
  }
}

export default Home;