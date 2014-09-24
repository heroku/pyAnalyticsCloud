/** @jsx React.DOM */
'use strict';

var React = require('react/addons'),
    $ = require('jquery');

var Home = React.createClass({

  getInitialState: function() {
    return {};
  },

  componentDidMount: function () {
    // check auth status.. look at browser cookie, ask api?
    var that = this;
    setTimeout(function(){
      that.props.app.router.navigate('signin', {trigger: true});
    }, 2000);
  },

  render: function() {
    return (
      <div className="in-home">
        <div className="throbber throbber-lg"></div>
      </div>
    );
  }

});

module.exports = Home;