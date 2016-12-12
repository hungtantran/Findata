import React from 'react';
import GetCookie from '../common/utilities';

class GoogleSignin extends React.Component {
    constructor(props) {
        super(props);

        this.onGoogleSignIn = this.onGoogleSignIn.bind(this);
        this.parseLoginResult = this.parseLoginResult.bind(this);
    }

    parseLoginResult(json) {
        var result = 'false';
        if (json.result == true) {
            result = 'true';
            window.location = '/';
        }
        this.setState({
            success: result,
            message: json.message
        });
    }

    onGoogleSignIn(googleUser) {
        console.log('On signin');
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
                type: 'Google',
                fullname: profile.getName(),
                email: profile.getEmail(),
                username: profile.getEmail(),
                password: '',
                id_token: id_token,
            })
        }).then(function(response) {
            return response.json();
        }).catch(function(ex) {
            console.log('parsing failed', ex);
        }).then((json) => {
            console.log('Get result');
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
        console.log('Render Google');
        var username = GetCookie('Username');
        var fullname = GetCookie('Fullname');
        // Redirect if user is logined
        if (username !== '' && fullname !== '') {
            window.location = '/';
            return;
        }

        var signinButton = (
            <div className='g-signin2' id='g-signin2' data-onsuccess='onSignIn'>
            </div>
        );            
        return signinButton;
    }
}

export default GoogleSignin;