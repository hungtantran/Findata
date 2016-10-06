import ReactDOM from 'react-dom'
import React from 'react' 
import Footer from './components/footer'
import Header from './components/header'
import GoogleSignin from './components/googleSignin'

class Login extends React.Component {
    constructor(props) {
        super(props);

        this.handleMouseUp = this.handleMouseUp.bind(this);
        this.parseLoginResult = this.parseLoginResult.bind(this);

        this.state = {
            success: "None",
            message: ""
        };
    }

    handleMouseUp(event) {
        var username = document.getElementById('username').value;
        var password = document.getElementById('password').value;

        // TODO change this to GET request and use /user handle instead
        fetch('/login', {
            credentials: 'same-origin',
            mode: 'no-cors',
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                type: "Findata",
                username: username,
                password: password,
            })
        }).then(function(response) {
            return response.json();
        }).catch(function(ex) {
            console.log('parsing failed', ex);
        }).then((json) => {
            this.parseLoginResult(json);
        });
    }

    parseLoginResult(json) {
        var result = "false";
        if (json.result == true) {
            result = "true";
        }
        this.setState({
            success: result,
            message: json.message
        });
    }

    render() {
        // TODO add form validator
        if (this.state.success === "true") {
            return (
                <div className="row">
                    <div className="col-lg-4 col-md-3 hidden-sm hidden-xs"></div>
                    <div className="formContainer col-lg-4 col-md-6">
                        Successful login to Findata.
                    </div>
                </div>
            )
        }

        var loginForm = (
        <div>
            <Header />
            <div className="row">
                <div className="col-lg-4 col-md-3 hidden-sm hidden-xs"></div>
                <div className="formContainer col-lg-4 col-md-6">
                    <div className="g-signin2" id="g-signin2" data-onsuccess="onSignIn"></div>            
                    <GoogleSignin />
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
            <Footer />
        </div>
        )

        return loginForm;
    }
}

export default Login;