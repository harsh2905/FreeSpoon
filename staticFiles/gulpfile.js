"use strict";

var gulp = require('gulp'),
	connect = require('gulp-connect'),
	less = require('gulp-less'),
	minifyCSS = require('gulp-minify-css'),
	rename = require('gulp-rename');

gulp.task('connect', function(cb){
	connect.server({
		root: '.',
		livereload: true,
		port: 8888
	});
	cb();
});

gulp.task('reload', function(){
	gulp.src(['./*.html', './assets/**/*'])
		.pipe(connect.reload());
});

gulp.task('watch', ['watch-html', 'watch-less']);

gulp.task('watch-html', function(){
	gulp.watch(['./*.html'], ['reload']);
});

gulp.task('watch-less', function(){
	gulp.watch(['./assets/less/*.less'], ['less', 'reload']);
});

gulp.task('run', ['compile', 'connect', 'watch']);

gulp.task('compile', ['vendor', 'less']);

gulp.task('vendor', function(){
	return gulp.src('./vendor/**/*')
		.pipe(gulp.dest('./assets'));
});

gulp.task('less', function(){
	return gulp.src('./assets/less/*.less')
		.pipe(less())
		.pipe(gulp.dest('./assets/css'))
		.pipe(minifyCSS())
		.pipe(rename({ extname: '.min.css' }))
		.pipe(gulp.dest('./assets/css'));
});