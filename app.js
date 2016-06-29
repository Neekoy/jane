var express = require('express');
var path = require('path');
var cookieParser = require('cookie-parser');
var bodyParser = require('body-parser');
var exphbs = require('express-handlebars');
var expressValidator = require('express-validator');
var flash = require('connect-flash');
var session = require('express-session');
var passport = require('passport');
var LocalStrategy = require('passport-local').Strategy;
var mongo = require('mongodb');
var mongoose = require('mongoose');
var MemcachedStore = require('connect-memcached')(session);
var uuid = require('node-uuid');
var Schema = mongoose.Schema;
var async = require("async");
var request = require("request");
var moment = require("moment");

mongoose.connect('mongodb://localhost/jane');
global.db = mongoose.connection;

var routes = require('./routes/index');
var users = require('./routes/users');

// Init App
var app = express();
var serv = require('http').Server(app);
var io = require('socket.io').listen(serv);

// Declare the Express session
var sessionMiddleware = session({
    secret: 'the most secretive secret possible',
    saveUninitialized: true,
    resave: true,
    store: new MemcachedStore({
        hosts: ['127.0.0.1:11211'],
    })
});

// Express session middleware for Socket.io
io.use(function(socket, next) {
    sessionMiddleware(socket.request, socket.request.res, next);
});

// Initialise the Express Session
app.use(sessionMiddleware);

// View Engine
app.set('views', path.join(__dirname, 'views'));
app.engine('handlebars', exphbs({defaultLayout:'layout'}));
app.set('view engine', 'handlebars');

// BodyParser Middleware
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(cookieParser());

// Set Static Folder
app.use(express.static(path.join(__dirname, 'public')));

// Passport init
app.use(passport.initialize());
app.use(passport.session());

// Express Validator
app.use(expressValidator({
  errorFormatter: function(param, msg, value) {
      var namespace = param.split('.')
      , root    = namespace.shift()
      , formParam = root;

    while(namespace.length) {
      formParam += '[' + namespace.shift() + ']';
    }
    return {
      param : formParam,
      msg   : msg,
      value : value
    };
  }
}));

// Connect Flash
app.use(flash());

// Global Vars
app.use(function (req, res, next) {
  res.locals.success_msg = req.flash('success_msg');
  res.locals.error_msg = req.flash('error_msg');
  res.locals.error = req.flash('error');
  res.locals.user = req.user || null;
  if (res.locals.user) {
    for (var i in res.locals.user) {
      if (i === 'username') {
        req.session.username = res.locals.user[i];
      }
    }
  }
  next();
});

app.use('/', routes);
app.use('/users', users);

// Set Port
app.set('port', (process.env.PORT || 3000));

// Start the Server
serv.listen(app.get('port'), function(){
  console.log('Server started on port '+app.get('port'));
});

ACTIVE_USERS = {};
WORKING_ON = {};
COMMENTS = {};

io.sockets.on('connection', function(socket) {

    username = socket.request.session.username;
    sessionid = socket.request.sessionID;

    ACTIVE_USERS[username] = socket.id;

    console.log("New socket connection " + username);

    socket.on('alertClicked', function(server) {
      found = false;
      async.forEach(Object.keys(WORKING_ON), function(item, callback) {
        if ( server === item ) {
          delete WORKING_ON[item];
          found = true;
        }
        callback();
      }, function(err) {
        if ( found === false ) {
          WORKING_ON[server] = username;
        };
      }
      );
    });

    socket.on('newComment', function(data) {
      COMMENTS[data.server] = { user: username, comment: data.comment };
      for ( var i in COMMENTS ) {
        console.log(COMMENTS[i]);
      }
    });

    socket.on('disconnect', function() {
        delete ACTIVE_USERS[socket.id];
    });

});

setInterval(function() {
  request('http://nagios-001.sl5.misp.co.uk/apiv2/services/critical', function(error, response, body) {
    if (!error && response.statusCode == 200) {
      toSubmit = [];
      var info = JSON.parse(body);
      async.forEach (info, function (i, callback) {
        existingInList = false;
        data = {};
        alertTime = i[5];
        alertName = i[1];
        reason = i[2];
        timeDiff = moment.unix(alertTime).fromNow();
        i[6] = timeDiff;
        i[7] = "";

        async.forEach(toSubmit, function(item, callback) {
          if ( item.server === i[0] ) {
            for ( var s in toSubmit ) {
              if ( toSubmit[s].server === item.server ) {
                newAlert = { alertName: alertName, alertReason: reason };
                toSubmit[s].alerts.push(newAlert);
                existingInList = true;
//                console.log(toSubmit[s]);
              };
            }
          }
          callback();
        }, function(err) {
            if ( existingInList === false) {
            async.forEach(Object.keys(WORKING_ON), function(server, callback) {
              if ( server === i[0] ) {
                i[7] = WORKING_ON[server];
              };
              callback();
            });
            async.forEach(Object.keys(COMMENTS), function(server, callback) {
              if ( server === i[0] ) {
                i[8] = COMMENTS[server];
              };
              callback();
            });
            data['server'] = i[0];
            data['alerts'] = [ { alertName: alertName, alertReason: reason } ];
            data['unixTime'] = i[5];
            data['timeElapsed'] = i[6];
            data['person'] = i[7];
            data['comments'] = i[8];
            if (data) {
              toSubmit.push(data);
            };
          };
        });
      callback();
      }, function(err) {
        io.sockets.emit('nagiosInfo', toSubmit);
      }
      );

    }
  });
}, 1000/4);