'use strict';

var Dispatcher = require('../dispatcher');


module.exports = {

  createConfig: function(db, username, password) {
    Dispatcher.handleViewAction({
      type: ActionTypes.CONFIG_SET,
      db: db,
      username: username,
      password: password
    });
  }

};