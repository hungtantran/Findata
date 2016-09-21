import ReactDOM from 'react-dom'
import React from 'react' 
import Footer from './components/footer'
import Header from './components/header'
import GoogleSignin from './components/googleSignin'

class Signup extends React.Component {
    constructor(props) {
        super(props);

        this.handleMouseUp = this.handleMouseUp.bind(this);
        this.parseRegisterResult = this.parseRegisterResult.bind(this);

        this.state = {
            success: "None",
            message: ""
        };
    }

    handleMouseUp(event) {
        var fullname = document.getElementById('fullname').value;
        var email = document.getElementById('email').value;
        var username = document.getElementById('username').value;
        var password = document.getElementById('password').value;

        fetch('/signup', {
                mode: 'no-cors',
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    type: "Findata",
                    fullname: fullname,
                    email: email,
                    username: username,
                    password: password,
                })
            }).then(function(response) {
                return response.json();
            }).catch(function(ex) {
                console.log('parsing failed', ex);
            }).then((json) => {
                this.parseRegisterResult(json);
            });
    }

    parseRegisterResult(json) {
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
                        Congratulation! You have successfully register for Findata.
                    </div>
                </div>
            )
        }

        var signUpForm = (
        <div>
            <Header />
            <div className="row">
                <div className="col-lg-4 col-md-3 hidden-sm hidden-xs"></div>
                <div className="formContainer col-lg-4 col-md-6">
                    <GoogleSignin />
                    {this.state.message}
                    <form data-toggle="validator" role="form">
                        <div className="form-group">
                            <label for="fullname">Full Name</label>
                            <input className="form-control" id="fullname" placeholder="Jones Smith"></input>
                        </div>
                        <div className="form-group">
                            <label for="email">Email address</label>
                            <input type="email" className="form-control" id="email" aria-describedby="emailHelp" placeholder="abc@example.com"></input>
                        </div>
                        <div className="form-group">
                            <label for="username">Username</label>
                            <input className="form-control" id="username"></input>
                        </div>
                        <div className="form-group">
                            <label for="password">Password</label>
                            <input type="password" className="form-control" id="password" data-minlength="6" required></input>
                        </div>
                        <div className="form-group">
                            <label for="confirmedpassword">Confirm Password</label>
                            <input type="password" className="form-control" id="confirmedpassword" data-match="#password" data-match-error="Don't match. Please try again" required></input>
                        </div>
                        <div className="form-check">
                            <label className="form-check-label">
                                <input type="checkbox" className="form-check-input"></input>
                                By checking this box you are indicating that you have read and accept the <a href="">terms of use.</a>
                            </label>
                        </div>
                    </form>
                    <button className="btn btn-primary" onMouseUp={this.handleMouseUp}>Register</button>
                </div>
                <div className="col-lg-4 col-md-3 hidden-sm hidden-xs"></div>
            </div>
            <Footer />
        </div>
        )

        return signUpForm;
    }
}

export default Signup;