import ReactDOM from 'react-dom'
import React, { Component } from 'react'
import { Router, Route } from 'react-router'
import Index from './index'
import About from './about'
import Contact from './contact'
import Login from './login'
import Signup from './signup'
import NotFound from './notfound'

ReactDOM.render((
  <Router>
    <Route path="/" component={Index} />
    <Route path="/about" component={About} />
    <Route path="/contact" component={Contact} />
    <Route path="/login" component={Login} />
    <Route path="/signup" component={Signup} />
    <Route path="/notfound" component={NotFound} />
  </Router>
), document.getElementById('root'));