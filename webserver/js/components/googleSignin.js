import ReactDOM from 'react-dom'
import React from 'react' 

class GoogleSignin extends React.Component {
    constructor(props) {
        super(props);

        this.onGoogleSignIn = this.onGoogleSignIn.bind(this);
        this.parseLoginResult = this.parseLoginResult.bind(this);
    }

    parseLoginResult(json) {
        console.log(json);
    }

    onGoogleSignIn(googleUser) {
        var profile = googleUser.getBasicProfile();
        var id_token = googleUser.getAuthResponse().id_token;
        fetch('/login', {
                credentials: 'same-origin',
                mode: 'no-cors',
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    type: "Google",
                    fullname: profile.getName(),
                    email: profile.getEmail(),
                    username: profile.getEmail(),
                    password: "",
                    id_token: id_token,
                })
            }).then(function(response) {
                return response.json();
            }).catch(function(ex) {
                console.log('parsing failed', ex);
            }).then((json) => {
                this.parseLoginResult(json);
            });
    }

    componentDidMount() {
        gapi.signin2.render('g-signin2', {
            'scope': 'https://www.googleapis.com/auth/plus.login',
            'width': 200,
            'height': 30,
            'longtitle': true,
            'theme': 'dark',
            'onsuccess': this.onGoogleSignIn
        });  
    }

    render() {
        var signinButton = <div className="g-signin2" id="g-signin2" data-onsuccess="onSignIn"></div>            
        return signinButton;
    }
}

export default GoogleSignin