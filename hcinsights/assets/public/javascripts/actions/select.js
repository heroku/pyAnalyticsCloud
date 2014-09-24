'use strict';

var $ = require('jquery');

var Dispatcher = require('../dispatcher');


module.exports = {

  createUpload: function(table) {
    
    Dispatcher.handleViewAction({
      type: ActionTypes.CONFIG_SET,
      db: db,
      username: username,
      password: password
    });
  }

};