/** @jsx React.DOM */
'use strict';

var React = require('react/addons'),
    $ = require('jquery');

var ConfigActions = require('../actions/config');

var Signin = React.createClass({

  getInitialState: function() {
    return {
      submitting: false
    };
  },

  render: function() {
    return (
      <div className="in-signin">
        <form onSubmit={this.handleSubmit}>
          <input type="text" placeholder="User name" ref="username" />
          <input type="password" placeholder="Password" ref="password" />
          {this.state.submitting ? <button type="submit" className="btn btn-primary" disabled>Login</button> : <button type="submit" className="btn btn-primary">Login</button>}
        </form>
      </div>
    );
  },

  handleSubmit: function(event){
    event.preventDefault();

    if (this.state.submitting) return;

    this.setState({submitting: true});
    
    // Need validation
    var username = this.refs.username.getDOMNode().value.trim();
    var password = this.refs.password.getDOMNode().value.trim();

    // Action pings API for validation?
    ConfigActions.createAuth(username, password);
  }

});

module.exports = Signin;