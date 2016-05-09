"use strict";

var gulp = require('gulp'),
	connect = require('gulp-connect'),
	less = require('gulp-less'),
	minifyCSS = require('gulp-minify-css'),
	rename = require('gulp-rename'),
	browserify = require('browserify'),
	babelify = require('babelify'),
	source = require('vinyl-source-stream'),
	ngmin = require('gulp-ngmin'),
	uglify = require('gulp-uglify');

gulp.task('connect', function(cb){
	connect.server({
		root: '.',
		livereload: true,
		port:8081
	});
	cb();
});

gulp.task('reload', ['less', 'browserify'], function(){
	return gulp.src(['./*.html', './assets/**/*', './src/**/*'])
		.pipe(connect.reload());
});

gulp.task('watch', ['watch-html', 'watch-less', 'watch-js']);

gulp.task('watch-html', function(){
	gulp.watch(['./*.html'], ['reload']);
});

gulp.task('watch-less', function(){
	gulp.watch(['./assets/less/*.less'], ['reload']);
});

gulp.task('watch-js', function(){
	gulp.watch(['./src/**/*.js'], ['reload']);
});

gulp.task('run', ['compile', 'connect', 'watch']);

gulp.task('compile', ['less', 'browserify']);

gulp.task('vendor', function(){
	return gulp.src('./vendor/**/*')
		.pipe(gulp.dest('./assets'));
});

gulp.task('browserify', function(){
	return browserify('./src/app.js', { debug: true })
		.transform(babelify)
		.bundle()
		.pipe(source('bundle.js'))
		.pipe(rename({ basename: 'app', extname: '.js'}))
		.pipe(gulp.dest('./assets/js/'))
});

gulp.task('uglify', function(){
	return gulp.src('./assets/js/**/*.js')
		.pipe(ngmin({dynamic: false}))
		.pipe(uglify({outSourceMap: false}))
		.pipe(rename({ basename: 'app', extname: '.min.js'}))
		.pipe(gulp.dest('./assets/js/'));
});

gulp.task('less', function(){
	return gulp.src('./assets/less/*.less')
		.pipe(less())
		.pipe(gulp.dest('./assets/css'))
		.pipe(minifyCSS())
		.pipe(rename({ extname: '.min.css' }))
		.pipe(gulp.dest('./assets/css'));
});
