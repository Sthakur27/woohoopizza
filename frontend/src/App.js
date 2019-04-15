import React, { Component } from 'react';
import {
  Container, Col, Form,
  FormGroup, Label, Input,
  Button,
} from 'reactstrap';
import './App.css';
import Login from './Components/login.js';
import Signup from './Components/signup.js';

class App extends Component {
  render() {
    return (
      <Signup/>
    );
  }
}

export default App;
