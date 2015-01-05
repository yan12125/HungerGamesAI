"use strict";

/**
* Module dependencies
*/
var path = require('path');
var uuid = require('node-uuid');
var express = require('express');
var commander = require('commander');
var WebSocketServer = require('websocket').server;
var colors = require('colors');

var map = require('./map.js');
var util = require('./util.js');

commander
.option('-p, --port <port>', 'A port for HTTP/WebSocket ', parseInt)
.option('-m, --map <map>', 'Map file to use')
.parse(process.argv);

/**
* Constants
*/
var WEB_SERVER_PORT = commander.port || 3000;
var MAP_FILE = commander.map || 'patrit14';
/**
* images URL
*/
var images = ['img/red.png', 'img/orange.png','img/yellow.png','img/green.png','img/blue.png','img/purple.png'];

/**
* game started?
*/
var gameStarted = false;
var __gameStarting = false; // 記錄是否已經輸入過 go 了

/**
* Express web server
*
*    - Serve the .html/.css/.js files to browser
*
*/
var app = express.createServer();
var wsConnections = [];


app.configure(function () {
  app.use(express.errorHandler({
    dumpExceptions: true,
    showStack: true
  }));
  app.use(app.router);

  // Client-side data are under ../client
  app.use(express.static(path.join(path.dirname(__dirname), 'client')));
});

// Express router:
app.get('/test', function(req, res) {
  // 回應訊息，表示這一個 ip:port 的伺服器還活著
  res.send('ok');
});

// for start game
app.get('/start_game', function (req, res) {
  if(!wsConnections.length) {
    res.send('No clients yet');
    return;
  } else if (__gameStarting) {
    res.send('game is starting');
    return;
  } else if (gameStarted) {
    res.send('game is already started');
    console.log('[Notice] Hunger Game has been started.');
    return;
  } else {
    __gameStarting = true; // 避免打太多次 go<Enter> 的問題
    console.log('[Notice] Hunger Game is starting in 3 seconds...');
    sendObjToAllClient({
      event: 'game_started',
      already_started: false
    });
    setTimeout(function() {
      gameStarted = true;
      __gameStarting = false;
      console.log('[Notice] Hunger Game has been successfully started.');
    }, 3000);
    res.send('Starting game ok');
  }
});

app.get('/report', function (req, res) {
    var infos = [];
    for(var i = 0; i < wsConnections.length; i++) {
        var playerInfo = wsConnections[i].playerInfo;
        infos.push(playerInfo);
    }
    res.send(JSON.stringify(infos));
});

/**
* My webscoket server
*
*    - Attached the the http web server (express app)
*    - Directly communicate with browsers
*
*/
var wsServer = new WebSocketServer({
  httpServer: app,
  autoAcceptConnections: false
});

wsServer.on("request",function(request){
  // console.log(request.requestedProtocols);
  var connection = request.accept('game-protocol', request.origin);

  newPlayer(connection);
});

function getConnectionById(uuid) {
  for (var i = 0, len = wsConnections.length; i < len; i += 1)
    if (wsConnections[i] && wsConnections[i].playerInfo.playerid === uuid) {
        return wsConnections[i];
    }
};

process.on('exit', function (code) {
  disconnectAll('server_down');
  console.log('Exitting...');
});
process.on('SIGINT', function() {
  process.exit();
});

/*
 * Main entry of the game
 * */
var main = function () {
    app.listen(WEB_SERVER_PORT, function () {
      console.log('Server listens at port %d', app.address().port);
    });

    map.iniMap(MAP_FILE);

    toolappear();
};

main();

function newPlayer(connection) {
  wsConnections.push(connection);
  console.log('A WebSocket connection is opened');
  // connection.playerInfo 內儲存使用者資訊（ uuid 、昵稱、隊伍編號... ）
  // 預設只有 uuid 用來分辨多個玩家彼此
  connection.playerInfo = {
    playerid: uuid.v4().substr(0, 8)
  };

  // 一開始當然是活的
  connection.playerInfo.dead = false;
  connection.playerInfo.disconnected = false;

  // 第N個玩家就放第N張圖
  //console.log(Math.floor(Math.random() * (images.length)));
  /** TODO image/player correspondence*/
  connection.playerInfo.image = images[wsConnections.indexOf(connection)%6];

  sendObjToClient({
    event: 'playerid',
    playerid: connection.playerInfo.playerid
  }, connection);

  sendObjToClient({
    event: 'map_initial',
    grids: map.grids,
    ntp_offset: util.getNtpOffset()
  }, connection);

  if ( gameStarted ) {
    sendObjToClient({
      event: 'game_started',
      already_started: true
    }, connection);
  }

  connection.on('close', function (reasonCode, description) {
    var idx = wsConnections.indexOf(connection);
    if (idx !== -1) {
      // Remove this connection object from the global array
      // wsConnections.splice(idx, 1);
      // NOT remove it because others will need dead player's informtion
      connection.playerInfo.disconnected = true;
      console.log('Some WebSocket connection is closed');
      // TODO 告訴所有人，此玩家已經離線
      if(!connection.playerInfo.dead) {
        sendObjToAllClient({
          event: 'player_offline',
          playerid: connection.playerInfo.playerid,
          reason: 'just_offline'
        });
      }
    }
    if(howManyPlayers() <= 0) {
      map.iniMap(MAP_FILE);
      // dicsonnect all clients with message 'game_end'
      //gameStarted = false;
      disconnectAll('game_end');
      if (gameStarted || __gameStarting) {
        console.log('[Notice] Hunger Game ends.');
      }
      wsConnections = [];
      gameStarted = false;
      __gameStarting = false;
    }
  });

  connection.on('message', function (event) {
    if (event.type !== 'utf8') return;

    // msg: 收到的字串
    // obj: 收到的物件 (由 JSON 轉成)
    var msg, obj;
    try {
      msg = event.utf8Data;
      obj = JSON.parse(msg);
    } catch (e) {}
    if (!obj) return;

    // TODO 告訴所有人，此 玩家 已經上線
    // 剛建立連線時，使用者還不在場上，直到將昵稱和隊伍給 server 確定以後，
    // server 隨機給予一個起始座標和 uuid ，該玩家才正式開始進入此遊戲場景，
    // 擁有 3 秒鐘的無敵準備時間

    /**********************************************
    * TODO
    * 來自使用者的資料 <--- From client
    **********************************************/
    if (obj.event === 'update_player_info') {
      // TODO 告訴這個使用者，現在哪些人在線上
      if (obj.name) connection.playerInfo.name = obj.name;
      var playerInfoList = [];
      for (var i = 0; i < wsConnections.length; i++) {
        if(!wsConnections[i].playerInfo.disconnected) {
          playerInfoList.push(wsConnections[i].playerInfo);
        }
      }

      connection.playerInfo.isObserver = obj.isObserver;

      var _pos = -1;

      if(obj.position_request) {
        _pos = obj.position_request;
        console.log("Player "+obj.name+" requests position ("+_pos%13+","+parseInt(_pos/13)+")");
      }

      if (_pos === -1) {
        _pos = randIniPos(true);
      }
      if (_pos === -1) {
        throw "Failed to find a position for a new player";
      }

      var iniPos = coordCalc(_pos);
      connection.playerInfo.x = iniPos.x;
      connection.playerInfo.y = iniPos.y;
      // console.log(playerInfoList);
      sendObjToAllClient({
        event: 'player_list',
        list: playerInfoList
      });

      // is user got the tool immediately?
      checkEatTools(connection.playerInfo);
    } else if (obj.event === 'player_position') {
      // 使用者請求更新座標至 (obj.x, obj.y)
      sendObjToAllClient({
        event: 'player_position',
        playerid: connection.playerInfo.playerid,
        x: obj.x,
        y: obj.y
      });
      connection.playerInfo.x = obj.x;
      connection.playerInfo.y = obj.y;
      checkEatTools(connection.playerInfo);
    }
    /** bomb starts here */
    else if (obj.event === 'put_bomb') {
      putBomb(obj.playerid, obj.x, obj.y, obj.bombingPower);
    }
    /** bomb ends here */
    /** tool starts here */
    else if (obj.event === 'ufo_removal'){
      sendObjToAllClient({
        event: 'ufo_removal',
        playerid: obj.playerid
      })
    }
    /** tool ends here */
  }); // end of connection.on('message')
}
// end of wsServer.on('request')


// 廣播資訊給所有人
function sendObjToAllClient(obj) {
  for (var idx = 0, len = wsConnections.length; idx < len; ++idx) {
    wsConnections[idx] && wsConnections[idx].sendUTF(JSON.stringify(obj));
  }
}

function disconnectAll(desc) {
  for(var i = 0;i<wsConnections.length;i++) {
    if(wsConnections[i] && wsConnections[i].connected) {
      wsConnections[i].close(1000, desc);
    }
  }
}

function randIniPos(allowOnTool) {
  var test = Math.floor(Math.random() * 169);
  var round = 0;
  var toolList = [];
  while (map.grids[test].type != 'empty') {
    test = Math.floor(Math.random() * 169);
    round++;
    if (round > 500) {
      test = Math.floor(Math.random() * 169);
      for(var i=0;i<169;i++) {
        var idx = (test+i)%169;
        var grid_type = map.grids[idx].type;
        if(grid_type === 'empty') {
          return idx;
        } else if (grid_type === 'tool') {
          toolList[idx] = true;
        }
      }
      var toolsPos = Object.keys(toolList);
      if(allowOnTool && toolsPos.length > 0) {
        return toolsPos[Math.floor(Math.random() * toolsPos.length)];
      }
      return -1; // map full, no empty grid found
    }
  }
  return test;
}

function gridCalc(x, y) {
    return 13 * Math.floor(y / 60) + Math.floor(x / 60);
}

function coordCalc(index) {
    return {
        x: index % 13 * 60 + 30,
        y: parseInt((index / 13), 10) * 60 + 30
    };
}

/** tool starts here */

function sendObjToClient(obj, playerConn) {
  playerConn && playerConn.sendUTF(JSON.stringify(obj));
}

function checkEatTools(playerInfo) {
  var pos = gridCalc(playerInfo.x, playerInfo.y);
  if (map.grids[pos].type !== 'tool') {
    return;
  }
  map.grids[pos].empty = true;
  map.grids[pos].type = 'empty';
  console.log('Tool '+map.grids[pos].tool+' at ('+pos%13+','+Math.floor(pos/13)+') eaten by '+playerInfo.playerid);
  sendObjToAllClient({
    event: 'tool_disappeared',
    glogrid: pos,
    tooltype: map.grids[pos].tool,
    eater: playerInfo.playerid
  });
}

function randTool() {
  var temp = Math.floor(Math.random() * 100);
  if(temp < 30)
    return 1;
  else if(temp >= 30 && temp < 41)
    return 2;
  else if(temp >= 41 && temp < 66)
    return 3;
  else if(temp >= 66 && temp < 96)
    return 4;
  else if(temp >= 96 && temp < 99)
    return 5;
  else if(temp >=99 && temp < 100)
    return 5; // removes 6, the god mode
}

function toolappear_impl(getgrid) {
  var toolty = randTool();
  if (map.grids[getgrid].empty) {
    map.grids[getgrid].empty = true;
    map.grids[getgrid].type = 'tool';
    map.grids[getgrid].tool = toolty;
    sendObjToAllClient({
      event: 'tool_appeared',
      grid: getgrid,
      tooltype: toolty
    });
    // Users may stand on the grid with new tool
    for(var i = 0; i < wsConnections.length; i++) {
      var playerInfo = wsConnections[i].playerInfo;
      if(!playerInfo.dead && !playerInfo.disconnected) {
        checkEatTools(playerInfo);
      }
    }
  }
  //console.log('tool');
  //console.log(getgrid);
}

function toolappear() {
  setTimeout(toolappear, Math.floor(Math.random() * 3000) + 5000);
  var getgrid = randIniPos(false);
  if(getgrid !== -1) {
    toolappear_impl(getgrid);
  }
}

/** tool ends here */

/** bomb starts here */

function player_bombed(playerid) {
  console.log('Player ' + playerid + ' was bombed');
  var conn = getConnectionById(playerid);
  var playerInfo = conn.playerInfo;

  if (playerInfo.dead || playerInfo.disconnected || playerInfo.isObserver) {
    return;
  }
  sendObjToAllClient({
    event: 'player_bombed',
    playerid: playerid
  });
  conn.playerInfo.dead = true;
  conn.close(1000, 'dead');
}

function putBomb(playerid, x, y, bombingPower) {
  var pos = x + y * 13;
  var grid = map.grids[pos];
  //console.log(pos);
  //console.log(map.grids[pos]);
  if (grid.type !== 'empty') {
    console.log(("[Warning] Bomb put on non-empty grid "+util.posToStr(pos)).green);
    return;
  }
  console.log('Player ' + playerid + ' put a bomb at (' + x + ', ' + y + ')');
  grid.empty = false; // 炸彈不能過
  grid.type = 'bomb';
  grid.bombingPower = bombingPower;
  grid.murderer = playerid;
  grid.bombPutTime = (new Date()).getTime(); // unix timestamp in milliseconds
  map.bombingTimers[pos] = setTimeout(function () {
    bombing(x, y);
  }, 3000);
  sendObjToAllClient({
    event: 'bomb_put',
    x: x,
    y: y,
    murdererid: playerid,
    power: bombingPower
  });
}

function bombing(bombX, bombY) {
    var result = map.bombing(bombX, bombY);
    sendObjToAllClient({
        'event': 'bombing',
        'bombing': result.bombing,
        'gridBombed': result.gridBombed,
        'wallBombed': result.wallBombed
    });
    for(var i = 0; i < result.bombing.length; i++) {
        var curPos = result.bombing[i].pos;
        var grid = map.grids[curPos];
        // console.log("Bombing timer = "+map.bombingTimers[i]);
        if(!util.isTimerObject(map.bombingTimers[curPos])) {
            console.log('[Warning] invalid bombing timer');
            console.log(map.bombingTimers[curPos]);
        }
        console.log("Clearing timer for bomb at "+util.posToStr(curPos));
        clearTimeout(map.bombingTimers[curPos]);
        map.bombingTimers[curPos] = null;
    }
    for(var i = 0; i < result.wallBombed.length; i++) {
        if(Math.random() < 0.3) {
            (function(pos) {
                setTimeout(function() { toolappearbybombed(pos) }, 750);
            })(result.wallBombed[i]);
        }
    }
    for(var i = 0; i < result.gridBombed.length; i++) {
        /* Additional work before really bombing the grid */
        var pos = result.gridBombed[i];
        var grid = map.grids[pos];
        if(grid.type === 'tool') {
            console.log('Tool '+grid.tool+' at ('+pos%13+','+Math.floor(pos/13)+') bombed');
            sendObjToAllClient({
                event: 'tool_disappeared',
                glogrid: pos,
                tooltype: grid.tool,
                eater: 'bomb'
            });
        }
        for (var j = 0; j < wsConnections.length; j++) {
            var info = wsConnections[j].playerInfo;
            if (util.coordToPos(info.x, info.y) == pos) {
                player_bombed(info.playerid);
            }
        }

        // Done the work
        grid.type = 'empty';
        grid.empty = true;
    }
}
/** bomb ends here */

/** calculate how many valid players are there */
// valid === neither disconnected nor dead
function howManyPlayers()
{
  if(!wsConnections) { // return -1 when no websockets yet
    return -1;
  }
  var count = 0;
  for(var i = 0;i<wsConnections.length;i++) {
    var playerInfo = wsConnections[i].playerInfo;
    if(playerInfo && !playerInfo.disconnected && !playerInfo.dead) {
        count++;
    }
  }
  return count;
}

function toolappearbybombed(grid) {
  toolappear_impl(grid);
}
