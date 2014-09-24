'use strict';

var _ = require('lodash');

var Dispatcher = require('flux').Dispatcher,
    Constants = require('./constants');

var AppDispatcher = _.extend(new Dispatcher(), {
  handleViewAction: function(action) {
    this.dispatch({
      source: Constants.PayloadSources.VIEW_ACTION,
      action: action
    });
  },

  handleServerAction: function(action) {
    this.dispatch({
      source: Constants.PayloadSources.SERVER_ACTION,
      action: action
    });
  }
});

module.exports = AppDispatcher;
