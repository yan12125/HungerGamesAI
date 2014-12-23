#!/usr/bin/env node

/**
* Module dependencies
*/
var uuid = require('node-uuid');
var express = require('express');
var commander = require('commander');
var WebSocketServer = require('websocket').server;

commander
.option('-p, --port <port>', 'A port for HTTP/WebSocket ', parseInt)
.parse(process.argv);


/**
* Constants
*/
var WEB_SERVER_PORT = commander.port || 3000;


/**
* Express web server
*
*    - Serve the .html/.css/.js files to browser
*
*/
var app = module.exports = express.createServer();

app.configure(function () {
  app.use(express.errorHandler({
    dumpExceptions: true,
    showStack: true
  }));
  app.use(app.router);

  // Client-side data are under ../client
  app.use(express.static(require('path').dirname(__dirname) + '/client'));
});

// Express router:
// for start game
app.get('/test', function(req, res) {
  // 回應訊息，表示這一個 ip:port 的伺服器還活著
  res.send('ok');
});

/**
* game started?
*/
var gameStarted = false;
var __gameStarting = false; // 記錄是否已經輸入過 go 了

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
      toolappear();
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

app.listen(WEB_SERVER_PORT, function () {
  console.log('Web server starts listening port %d for %s',
    app.address().port, 'HTTP requests and WebSockets');
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
/**
* images URL
*/
var images = ['img/red.png', 'img/orange.png','img/yellow.png','img/green.png','img/blue.png','img/purple.png'];

var grids = new Array();
iniMap();

var wsConnections = [];
getConnectionById = function (uuid) {
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
    grids: grids
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
      iniMap();
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
      var _pos = randIniPos(true);
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

function iniMap() {
  console.log('[Notice] Initializing the map...');
  var wall = require('./wall.js');
  for (var i = 0; i < 169; i++) {
    grids[i] = {};
    grids[i].empty = true;
    grids[i].type = 'empty'; //1.tool 2.bomb 3.vwall 4.nvwall 5.empty
  }
  for (var i = 0; i < 169; i++) {
    if (wall.raw[i] === 'empty') continue;
    grids[i].empty = false;
    grids[i].type = wall.raw[i];
  }
  return;
}

function randIniPos(allowOnTool) {
  var test = Math.floor(Math.random() * 169);
  var round = 0;
  var toolList = [];
  while (grids[test].type != 'empty') {
    test = Math.floor(Math.random() * 169);
    round++;
    if (round > 500) {
      test = Math.floor(Math.random() * 169);
      for(var i=0;i<169;i++) {
        var idx = (test+i)%169;
        var grid_type = grids[idx].type;
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
  if (grids[pos].type !== 'tool') {
    return;
  }
  grids[pos].empty = true;
  grids[pos].type = 'empty';
  console.log('Tool '+grids[pos].tool+' at ('+pos%13+','+Math.floor(pos/13)+') eaten by '+playerInfo.playerid);
  sendObjToAllClient({
    event: 'tool_disappeared',
    glogrid: pos,
    tooltype: grids[pos].tool,
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
    return 6;
}

function toolappear_impl(getgrid) {
  var toolty = randTool();
  if (grids[getgrid].empty) {
    grids[getgrid].empty = true;
    grids[getgrid].type = 'tool';
    grids[getgrid].tool = toolty;
  }
  sendObjToAllClient({
    event: 'tool_appeared',
    grid: getgrid,
    tooltype: toolty
  });
  //console.log('tool');
  //console.log(getgrid);
}

function toolappear() {
  /*
  if(!gameStarted) {
    return;
  }
  */
  setTimeout(toolappear,Math.floor(Math.random() * 5000)+30000);
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

  if (conn.playerInfo.dead || conn.playerInfo.disconnected) {
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
  //console.log(pos);
  //console.log(grids[pos]);
  if (grids[pos].type !== 'empty') {
    return;
  }
  console.log('Player ' + playerid + ' put a bomb at (' + x + ', ' + y + ')');
  grids[pos].empty = false; // 炸彈不能過
  grids[pos].type = 'bomb';
  grids[pos].bombingPower = bombingPower;
  grids[pos].murderer = playerid;
  sendObjToAllClient({
    event: 'bomb_put',
    x: x,
    y: y,
    murdererid: playerid, 
    power: bombingPower
  });
  setTimeout(function () {
    bombing(x, y);
  }, 3000);
}

/*
 * 對炸彈本身而言，range和dir都是undefined
 * "餘波" 會把range設成剩下的範圍，dir是餘波的方向
 * */
function bombing(bombX, bombY, range, dir) {
  //console.log("bombing("+bombX+","+bombY+","+range+","+dir+")");
  if(!(0 <= bombX && bombX <= 12 && 0 <= bombY && bombY <= 12)) {
    return;
  }
  var grid = grids[bombX + bombY * 13];
  var original = (typeof range === 'undefined');
  if (original && grid.type !== 'bomb') { // bombs may be bombed
    //console.log('('+bombX+','+bombY+') is not a bomb');
    return;
  } else if (!original && grid.type == 'bomb') {
    bombing(bombX, bombY); // 餘波可以穿越炸彈
  } else if (!original && dir && grid.type === 'nvwall') {
    //console.log('Bombing stopped at NVWall ('+bombX+','+bombY+')');
    return;
  } else if (!original && range < 0) {
    return;
  }
  if(original) {
    range = grid.bombingPower;
    var obj = {
        event: 'bombing', 
        murderer: grid.murderer, 
        x: bombX, 
        y: bombY
    };
    console.log(obj)
    sendObjToAllClient(obj);
  }
  var old_type = grid.type; // type is set to empty after bombing
  grid_bombed(bombX, bombY);

  // bomb bombed would explode
  if(original) {
    var dirs = [ [1,0], [-1,0], [0,1], [0,-1] ];
    dirs.forEach(function(item) {
      var newBombX = bombX + item[0];
      var newBombY = bombY + item[1];
      bombing(newBombX, newBombY, range-1, item);
    });
  } else {
    if (old_type === 'vwall') {
      return; // 餘波威力不穿透vwall
    }
    var newBombX = bombX + dir[0];
    var newBombY = bombY + dir[1];
    bombing(newBombX, newBombY, range-1, dir);
  }
}

function grid_bombed(x, y) {
  var pos = x + y * 13;
  var grid = grids[pos];
  //console.log("Grid ("+x+","+y+") bombed");
  //console.log(grids[pos].type);

  /* Additional work before really bombing the grid */
  if (grid.type === 'vwall') {
    //console.log("VWall at ("+x+","+y+") vanished");
    var posibility=Math.floor(Math.random()*100);
    if(posibility<30) {
      setTimeout(function(){ toolappearbybombed(pos); },750);
    }
    grid.type = 'empty';
    grid.empty = true;
    sendObjToAllClient({
      event: 'wall_vanish',
      x: x,
      y: y
    });
  } else if (grid.type === 'tool') {
    console.log('Tool '+grids[pos].tool+' at ('+pos%13+','+Math.floor(pos/13)+') bombed');
    sendObjToAllClient({
      event: 'tool_disappeared',
      glogrid: pos,
      tooltype: grids[pos].tool,
      eater: 'bomb'
    });
  }
  for (var i = 0; i < wsConnections.length; i++) {
    var info = wsConnections[i].playerInfo;
    if (x == Math.floor(info.x / 60) && y == Math.floor(info.y / 60)) {
      player_bombed(info.playerid);
    }
  }

  // Done the work
  sendObjToAllClient({
    event: 'grid_bombed',
    x: x,
    y: y
  });
  grid.type = 'empty';
  grid.empty = true;
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
