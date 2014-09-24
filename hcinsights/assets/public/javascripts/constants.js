'use strict';

var keyMirror = require('react/lib/keyMirror');

module.exports = {

  ActionTypes: keyMirror({
    AUTH_SET: null,
    CONFIG_SET: null
  }),

  PayloadSources: keyMirror({
    SERVER_ACTION: null,
    VIEW_ACTION: null
  })

};