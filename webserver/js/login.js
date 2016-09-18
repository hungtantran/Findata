import ReactDOM from 'react-dom'
import React from 'react' 
import Footer from './components/footer'
import Header from './components/header'

class Login extends React.Component {
    constructor(props) {
        super(props);

        this.handleMouseUp = this.handleMouseUp.bind(this);
    }

    handleMouseUp(event) {
        console.log(event);
    }

    render() {
        return (
            <div className="row">
                <div className="col-lg-4 col-md-3 hidden-sm hidden-xs"></div>
                <div className="formContainer col-lg-4 col-md-6">
                    <form>
                        <div className="form-group">
                            <label for="username">Username</label>
                            <input className="form-control" id="username"></input>
                        </div>
                        <div className="form-group">
                            <label for="password">Password</label>
                            <input type="password" className="form-control" id="password"></input>
                        </div>
                    </form>
                    <button className="btn btn-primary" onMouseUp={this.handleMouseUp}>Login</button>
                </div>
                <div className="col-lg-4 col-md-3 hidden-sm hidden-xs"></div>
            </div>
        )
    }
}

ReactDOM.render(
  <Footer />,
  document.getElementById('footer'));

ReactDOM.render(
  <Header />,
  document.getElementById('header'));

ReactDOM.render(
  <Login />,
  document.getElementById('content'));