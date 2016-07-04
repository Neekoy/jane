console.log("Greetings from the main controller.");
var socket = io();

var app = angular.module('janeApp', [], function($interpolateProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
});

app.controller('mainController', function($scope, $http) {

});

app.controller('janeController', function($scope, $http) {
	this.orderBy = '-unixTime';
	this.nagiosInfo = [];
	this.alertContentCSS = { "background-color": "#91E5FF" };
	this.paused = false;
	this.commenting = false;
	this.commentMessage = "";

	this.sortBy = function(data) {
		this.orderBy = data;
	};

	this.alertClicked = function (data) {
		socket.emit("alertClicked", data);
	};

	this.changeColour = function (data) {
		if ( data.person ) {
			return { "background-color": "#91FFBB" };
		} else {
			return { "background-color": "#91E5FF" };
		}
	};

	this.comment = function (data) {
		this.commenting = !this.commenting;
		if (!this.commenting) {
			this.paused = true;
			for ( var i in this.nagiosInfo ) {
				if ( data === this.nagiosInfo[i].server ) {
					this.nagiosInfo[i].commenting = 1;
				};
			}
		} else {
			this.paused = false;
			for ( var i in this.nagiosInfo ) {
				if ( data === this.nagiosInfo[i].server ) {
					this.nagiosInfo[i].commenting = 0;
				};
			}
		}
	}

	this.submitComment = function (data) {
		submitComment = {};
		submitComment['server'] = data; 
		submitComment['comment'] = this.commentMessage;
		socket.emit("newComment", submitComment);
		this.commentMessage = "";
		this.commenting = false;
		this.paused = false;
	}

	this.checkIfCommenting = function (data) {
		for ( var i in this.nagiosInfo ) {
			if ( data === this.nagiosInfo[i].server ) {
				if ( this.nagiosInfo[i].commenting === 1 ) {
					return true
				};
			};
		};
		return false;
	};

	socket.on('nagiosInfo', function(data) {
		if ( this.paused === false ) {
			this.nagiosInfo = data;
			$scope.$apply();
		};
	}.bind(this));
});