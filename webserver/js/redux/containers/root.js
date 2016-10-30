import 'babel-polyfill';

import React from 'react';
import { Provider } from 'react-redux';
import configureStore from '../common/configureStore';
import App from './app';

const store = configureStore();

export default class Root extends React.Component {
    render() {
        return (
            <Provider store={store}>
                <App />
            </Provider>
        );
    }
}