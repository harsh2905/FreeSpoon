"use strict";

var gulp = require('gulp'),
	connect = require('gulp-connect');

gulp.task('connect', function(cb){
	connect.server({
		root: '.',
		livereload: true,
		port: 7777
	});
	cb();
});
