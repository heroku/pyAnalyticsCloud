"use strict";

// core node reqs.
var path = require('path'),
    _ = require('lodash');

// gulp reqs.
var gulp = require('gulp');

// gulp plugins
var sass = require('gulp-sass'),
    plumber = require('gulp-plumber'),
    tap = require('gulp-tap'),
    rename = require('gulp-rename'),
    rev = require('gulp-rev'),
    reactify = require('reactify'),
    es6ify = require('es6ify');

// allow experimental es6 features -- namely block scope (let)
es6ify.traceurOverrides = { blockBinding: true };

// other plugins
var browserify = require('browserify');

// config
var sources = {
  js: ['public/javascripts/**/*.js', 'public/javascripts/**/*.jsx', '!public/javascripts/build/*.js', '!public/javascripts/vendor/**/*.js'],
  builtjs: 'public/javascripts/bundle/*.js',
  html: 'public/javascripts/**/*.html',
  scss: 'public/scss/**/*.scss',
  stylesheets: 'public/stylesheets/**/*'
};


var vendorLibs = ['jquery',
                  'lodash',
                  'backbone',
                  'react',
                  'url',
                  'util',
                  'es6-promise',
                  'async'];


// styles
gulp.task('sass', function () {
  return gulp.src('public/scss/style.scss')
    .pipe(sass({
      sourceComments: 'none',
      precision: 10,
      includePaths: ['bower_components']
    })
    .on('error', function (e) {
      console.log(String(e));
    }))
    .pipe(gulp.dest('public/stylesheets'));
});


// vendor.js
gulp.task('vendor.js', function() {

  var bundler = browserify({debug: false});
  bundler.add(es6ify.runtime);
  bundler.add('./public/javascripts/noop.js');

  _.each(vendorLibs, function (lib) { bundler.require(lib); });

  bundler.require('./node_modules/lodash/dist/lodash.underscore.js', {expose: 'underscore'});

  return gulp.src('./public/javascripts/noop.js', {read: false})
    .pipe(plumber())
    .pipe(tap(function (file) {
      file.contents = bundler.bundle();
    }))
    .pipe(rename('vendor.js'))
    .pipe(gulp.dest('./public/javascripts/bundle'));
});


// main.js
gulp.task('main.js', function() {

  var bundler = browserify({debug: false});

  bundler.transform(reactify);
  bundler.transform(es6ify.configure(/\.jsx?$/));

  bundler.add('./public/javascripts/main.jsx');
  _.each(vendorLibs, function (lib) { bundler.external(lib); });

  return gulp.src('./public/javascripts/main.jsx', {read: false})
    .pipe(plumber())
    .pipe(tap(function (file) {
      file.contents = bundler.bundle();
    }))
    .pipe(rename('main.js'))
    .pipe(gulp.dest('./public/javascripts/bundle'));
});


gulp.task('watch', function () {
  gulp.watch(sources.js, ['main.js']);
  gulp.watch(sources.html, ['main.js']);
  gulp.watch(sources.scss, ['sass']);
});


gulp.task('build', ['vendor.js', 'main.js']);
gulp.task('default', ['sass', 'vendor.js', 'main.js', 'watch']);
