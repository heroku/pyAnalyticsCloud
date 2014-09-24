'use strict';

var Dispatcher = require('../dispatcher');


module.exports = {

  createAuth: function(username, password) {
    Dispatcher.handleViewAction({
      type: ActionTypes.AUTH_SET,
      username: username,
      password: password
    });
  }

};