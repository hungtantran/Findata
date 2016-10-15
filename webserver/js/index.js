import ReactDOM from 'react-dom';
import React from 'react'; 
import Workspace from './components/workspace/workspace';
import Footer from './components/footer';
import Header from './components/header';

class Home extends React.Component {
  render() {
    return (
      <div>
        <Header />
        <Workspace />
        <Footer />
      </div>
    );
  }
}

export default Home;