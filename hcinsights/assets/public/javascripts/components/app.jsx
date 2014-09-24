/** @jsx React.DOM */
'use strict';

var _ = require('lodash'),
    $ = require('jquery'),
    React = require('react/addons'),
    Backbone = require('backbone');

Backbone.$ = $;

var Dispatcher = require('../dispatcher');

var Home = require('./Home.jsx'),
    Signin = require('./Signin.jsx');
//     AuthConfig = require('./components/AuthConfig.jsx'),
//     AuthSelect = require('./components/AuthSelect.jsx');


var Router = Backbone.Router.extend({

  routes: {
    '': 'home',
    'signin': 'signin',
    'auth/config': 'authConfig',
    'auth/select': 'authSelect'
  },

  initialize: function (app) {
    this.app = app;
  },

  home: function () {
    this.app.setState({
      page: React.addons.update(this.app.state.page, {
        path: {$set: ''},
        params: {$set: null}
      })
    });
  },

  signin: function () {
    this.app.setState({
      page: React.addons.update(this.app.state.page, {
        path: {$set: 'signin'},
        params: {$set: null}
      })
    });
  },

  authConfig: function () {
    this.app.setState({
      page: React.addons.update(this.app.state.page, {
        path: {$set: 'authConfig'},
        params: {$set: null}
      })
    });
  },

  authSelect: function () {
    this.app.setState({
      page: React.addons.update(this.app.state.page, {
        path: {$set: 'authSelect'},
        params: {$set: null}
      })
    });
  }

});

var App = React.createClass({

  router: null,

  mixins: [],

  getInitialState: function () {
    return {
      page: {
        path: '',
        params: ''
      }
    };
  },

  componentDidMount: function () {
    this.router = new Router(this);
    if (!Backbone.history.start({pushState: true})) {
      this.router.navigate('', {trigger: true, replace: true});
    }
  },

  render: function() {
    var component;
    switch(this.state.page.path) {
      case '':
        component = <Home app={this} />;
        break;
      case 'signin':
        component = <Signin app={this} />;
        break;
      // case 'authConfig':
      //   component = <AuthConfig app={this} />;
      //   break;
      // case 'authSelect':
      //   component = <AuthSelect app={this} />;
      //   break;
    }

    return (
      <div>
        <div className="container-fluid">
          {component}
        </div>
      </div>
    );
  }
});

module.exports = App;
