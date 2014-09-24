'use strict';

var $ = require('jquery'),
    React = require('react/addons');

var App = require('./components/app.jsx');

$(function () {
  React.renderComponent(<App />, $('#app').get(0));
});