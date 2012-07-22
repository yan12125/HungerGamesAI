#!/usr/bin/env node

/**
* Module dependencies
*/
var dgram = require('dgram');
var uuid = require('node-uuid');
var express = require('express');
var commander = require('commander');
var WebSocketServer = require('websocket').server;

commander
.option('-p, --port <port>', 'A port for HTTP/WebSocket ', parseInt)
.option('-n, --number <player Number>', 'numver od players', parseInt)
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
  app.set('views', __dirname + '/views');
  app.set('view engine', 'ejs');
  app.use(express.errorHandler({
    dumpExceptions: true,
    showStack: true
  }));
  app.use(express.bodyParser());
  app.use(express.methodOverride());
  app.use(express.cookieParser());
  app.use(express.session({
    secret: 'your secret here'
  }));
  app.use(app.router);

  // Client-side data are under ../client
  app.use(express.static(require('path').dirname(__dirname) + '/client'));
});

// Express router:
// for start game
app.get('/test', function(req, res) {
  // TODO 回應訊息，表示這一個 ip:port 的伺服器還活著
});

  /**
  * game started?
  */
  var gameStarted = false;
// 使用 stdin 取代 HTTP GET 方法
// 如果使用者在 standard input 輸入 go<Enter> 則遊戲會開始
var stdin = process.openStdin();
var sendObjToAll;
var __gameStarting = false; // 記錄是否已經輸入過 go 了
stdin.on('data', function(chunk) {
  if (chunk.toString().search('go') === 0) {
    // if (!gameStarted && !__gameStarting) {
      __gameStarting = true; // 避免打太多次 go<Enter> 的問題
      console.log('[Notice] Hunger Game is starting in 3 seconds...');
      sendObjToAll({ event: 'game_started' });
      setCount(0);
      setTimeout(function() {
        gameStarted = true;
        //toolappear();
        console.log('[Notice] Hunger Game has been successfully started.');
      }, 3000);
      //  } else {
        //    console.log('[Notice] Hunger Game has been started.');
        //  }
  }
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
var rooms=[];
var count=0;
function setCount(n){ count = n };
wsServer.on("request",function(request){
  // console.log(request.requestedProtocols);
  if(request.requestedProtocols[0]=="test"){
    var cc_ = request.accept('test', request.origin);
    cc_.on('close', function(){ /* console.log('QQ') */ });
    cc_.on('open' , function(){  });

    return;
  }

  var connection = request.accept('game-protocol', request.origin);

  if(count==0){
    count=commander.number || 3;
    var x=newRoom();
    rooms.push(x);
    x(connection);
  }
  else{
    var x=rooms[rooms.length-1];
    x(connection);
  }
  count--;
});
function newRoom(){
  sendObjToAll=sendObjToAllClient;
  //sendObjToAllClient();
  /**
  * images URL
  */
  var images = ['red.png', 'orange.png','yellow.png','green.png','blue.png','purple.png'];
  var picCount = [0,2,4,1,3,5];




  var wsConnections = [];
  wsConnections.getConnectionById = function (uuid) {
    for (var i = 0, len = this.length; i < len; i += 1)
      if (this[i] && this[i].playerInfo.playerid === uuid) return this[i];
  };


  //  wsServer.on('request', 
    var newPlayer = function (connection) {

      // Accept the request and then establish a connection
      // Push this connection into a global array
      //var connection = request.accept('game-protocol', request.origin);
      //if(gameStarted) {
        //  connection.drop(1000, 'error_game_started');
        //  connection.close();
        //  return;
        //}
        /** ping's addition 
        if (howManyPlayers() < 1) {
        iniMap();
        gameStarted = false;
        }
        end of addition */
        //!
        //!
        wsConnections.push(connection);
        console.log('A WebSocket connection is opened');
        if(count==1){
          sendObjToAll({ event: 'game_started' });
          toolappear();
        }
        // connection.playerInfo 內儲存使用者資訊（ uuid 、昵稱、隊伍編號... ）
        // 預設只有 uuid 用來分辨多個玩家彼此
        connection.playerInfo = {
          playerid: uuid.v4()
        };

        // 一開始當然是活的
        connection.playerInfo.dead = false;
        connection.playerInfo.disconnected = false;

        // 第N個玩家就放第N張圖
        //console.log(Math.floor(Math.random() * (images.length)));
        /** TODO image/player correspondence*/
        connection.playerInfo.image = images[picCount[wsConnections.indexOf(connection)%6]];

        connection.sendUTF(JSON.stringify({
          event: 'playerid',
          playerid: connection.playerInfo.playerid,
          image: connection.playerInfo.image
        }));
        connection.sendUTF(JSON.stringify({
          event: 'map_initial',
          grids: grids
        }));
        connection.sendUTF(JSON.stringify({
          event: 'pos_initial',
          pos: randIniPos()
        }));

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
          /** edition by ping 
          if (wsConnections.length < 1) {
          iniMap();
          }
          /** end of edition*/
          if(howManyPlayers()<=0) {
            iniMap();
            gameStarted = false;
            __gameStarting = false;
            console.log('[Notice] Hunger Game ends.');
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
          if (obj.event === 'ask_variables') {
            var playerInfos = [];
            for(var i=0;i<wsConnections.length;i++) {
              if(wsConnections[i].playerInfo) {
                playerInfos.push(wsConnections[i].playerInfo);
              }
            }
            sendObjToClient({
              event: 'resp_variables', 
              variables: {
                grids: grids, 
                playerInfos: playerInfos
              }
            }, connection);
          } else if (obj.event === 'update_player_info') {
            // TODO 告訴這個使用者，現在哪些人在線上
            if (obj.name) connection.playerInfo.name = obj.name;
            if (obj.team) connection.playerInfo.team = obj.team;
            var playerInfoList = [];
            for (var i = 0; i < wsConnections.length; i++) {
              if(!wsConnections[i].playerInfo.disconnected) {
                playerInfoList.push(wsConnections[i].playerInfo);
              }
            }
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
          } else if (obj.event === 'ask_player_info') {
            var _cn = wsConnections.getConnectionById(obj.playerid)
            if (!_cn) return;
            _cn = _cn.playerInfo;
            sendObjToAllClient({
              event: 'resp_player_info',
              playerid: obj.playerid,
              name: _cn.name,
              team: _cn.team,
              image: _cn.image
            });
          }
          /** bomb starts here */
          else if (obj.event === 'put_bomb') {
            putBomb(obj.playerid, obj.x, obj.y, obj.bombingPower);
          } else if (obj.event === 'player_bombed') {
            if (obj.playerid) {
              player_bombed(obj.playerid);
            }
          }
          /** bomb ends here */
          /** tool starts here */
          else if (obj.event === 'tool_disappeared') {
            grids[obj.gridc].empty = true;
            grids[obj.gridc].type = 'empty';
            sendObjToAllClient({
              event: 'global_tool_disappeared',
              glogrid: obj.gridc
            });
            sendObjToClient({
              event: 'tool_disappeared_by_bombed',
              bombedgrid:obj.gridc
            }, connection)
            //console.log(grids[obj.gridc]); 
          } else if (obj.event === 'tool_disappeared_by_eaten') {
            grids[obj.gridc].empty = true;
            grids[obj.gridc].type = 'empty';
            sendObjToAllClient({
              event: 'global_tool_disappeared',
              glogrid: obj.gridc,
              tooltype: obj.tooltype,
              eater:obj.eater
            });
            /*if(obj.tooltype === 5 || obj.tooltype === 6) {
              sendObjToClient({
              event: 'tool_eaten_type',
              tooltype: obj.tooltype,
              playerid: connection.playerInfo.playerid
              }, connection);*/
              //} else {
                sendObjToAllClient({
                  event: 'tool_eaten_type', 
                  tooltype: obj.tooltype, 
                  playerid: connection.playerInfo.playerid
                });
                //}
          } else if (obj.event === 'ufo_removal'){
            sendObjToAllClient({
              event: 'ufo_removal',
              playerid: obj.playerid
            })
          }
          /** tool ends here*/
        }); // end of connection.on('message')

    }
  //); // end of wsServer.on('request')


  // 廣播資訊給所有人
  function sendObjToAllClient(obj) {
    for (var idx = 0, len = wsConnections.length; idx < len; ++idx) {
      wsConnections[idx] && wsConnections[idx].sendUTF(JSON.stringify(obj));
    }
  }

  var grids = new Array();

  function iniMap() {
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
  iniMap();

  function randIniPos() {
    var test = Math.floor(Math.random() * 169);
    var round = 0;
    while (grids[test].type != 'empty') {
      test = Math.floor(Math.random() * 169);
      round++;
      if (round > 500) {
        test = Math.floor(Math.random() * 169);
        for(var i=0;i<169;i++)
          if(grids[(test+i)%169].type==='empty')
            return test+i;
          return -1;
          // map full, no empty grid found
      }
    }
    return test;
  }


  /** tool starts here */

  function sendObjToClient(obj, playerConn) {
    playerConn && playerConn.sendUTF(JSON.stringify(obj));
  }

  function toolappear() {
    //if(!gameStarted)
      //  return;
    setTimeout(toolappear,Math.floor(Math.random() * 5000)+30000);
    var getgrid = randIniPos();
    if (getgrid !== -1) {
      var toolty = (function(){
        var temp = Math.floor(Math.random() * 100) ;
        /*if (tmp<10)
          return 2;
          return 1;*/
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
      }());
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

  }
  // toolappear();

  /** tool ends here */

  /** bomb starts here */

  function putBomb(playerid, x, y, bombingPower) {
    if (grids.length === 169) {
      var pos = x + y * 13;
      //console.log(pos);
      //console.log(grids[pos]);
      if (grids[pos].type === 'empty') {
        //console.log('Player ' + wsConnections.getConnectionById(playerid).playerInfo.name + ' put a bomb at (' + x + ', ' + y + ')\n');
        grids[pos].empty = false; // 炸彈不能過
        /*setTimeout(function () {
          grids[pos].empty = false;
          }, 1500); // but 850 milliseconds 內要能出去*/
          grids[pos].type = 'bomb';
          grids[pos].bombingPower = bombingPower;
          sendObjToAllClient({
            event: 'bomb_put',
            x: x,
            y: y,
            murdererid: playerid
          });
          setTimeout(function () {
            bombing(x, y);
          }, 3000);
      }
    }
  }

  function bombing(bombX, bombY) {
    var pos = bombX + bombY * 13;
    if (grids[pos].type === 'bomb') {
      grids[pos].type = 'empty';
      grids[pos].empty = true;
      var range = grids[pos].bombingPower;
      grid_bombed(bombX, bombY, bombX, bombY);
      for (var j = range; j > 0; j--) {
        grid_bombed(bombX, bombY, bombX + j, bombY);
        grid_bombed(bombX, bombY, bombX - j, bombY);
        grid_bombed(bombX, bombY, bombX, bombY + j);
        grid_bombed(bombX, bombY, bombX, bombY - j);

        // bomb bombed would explode
        if (0 <= bombX + j && bombX + j <= 12 && grids[(bombX + j) + bombY * 13].type === 'bomb' && vwall_checkBombed(bombX, bombY, bombX + j, bombY)) {
          bombing(bombX + j, bombY);
        }
        if (0 <= bombX - j && bombX - j <= 12 && grids[(bombX - j) + bombY * 13].type === 'bomb' && vwall_checkBombed(bombX, bombY, bombX - j, bombY)) {
          bombing(bombX - j, bombY);
        }
        if (0 <= bombY + j && bombY + j <= 12 && grids[bombX + (bombY + j) * 13].type === 'bomb' && vwall_checkBombed(bombX, bombY, bombX, bombY + j)) {
          bombing(bombX, bombY + j);
        }
        if (0 <= bombY - j && bombY - j <= 12 && grids[bombX + (bombY - j) * 13].type === 'bomb' && vwall_checkBombed(bombX, bombY, bombX, bombY - j)) {
          bombing(bombX, bombY - j);
        }
      }

      sendObjToAllClient({
        event: 'bomb_explode',
        bombPower: range,
        x: bombX,
        y: bombY
      });
    }
  }

  function player_bombed(playerid) {
    sendObjToAllClient({
      event: 'player_bombed',
      playerid: playerid
    });
    //console.log('Player ' + wsConnections.getConnectionById(playerid).playerInfo.name + ' was bombed');
    wsConnections.getConnectionById(playerid).playerInfo.dead = true;
    if(howManyPlayers() <= 1) {
      //iniMap();
      // dicsonnect all clients with message 'game_end'
      sendObjToAllClient({
        event: 'player_offline',
        playerid: playerid, 
        reason: 'dead'
      });
      //gameStarted = false;
      for(var i = 0;i<wsConnections.length;i++) {
        if(wsConnections[i]) {
          wsConnections[i].drop(1000, 'game_end');
          wsConnections[i].close();
        }
      }
    }
  }

  // 爆炸威力不能穿過牆，所以check vwall和bomb "中間" 有沒有nvwall or vwall
  function vwall_checkBombed(bombX, bombY, wallX, wallY) {
    //console.log('bombX='+bombX+' bombY='+bombY+' wallX='+wallX+' wallY='+wallY);
    if (grids[wallX+wallY*13].type==='nvwall')
      return false;
    if (bombX === wallX) { // 牆和炸彈在同一水平線
      if( Math.abs(bombY-wallY)===1 && grids[wallX+wallY*13].type==='nvwall' ) {
        return false;
      }
      var flag = bombY > wallY;
      var i_initial = bombY + (flag ? (-1) : (1));
      for (var i = i_initial; flag ? (i > wallY) : (i < wallY); flag ? (i--) : (i++)) {
        //console.log(bombX+', '+i);
        if (grids[bombX + i * 13].type === 'nvwall' || grids[bombX + i * 13].type === 'vwall') {
          //console.log('false=>'+bombX+','+i);
          return false;
        }
      }
    } else if (bombY === wallY) { // 牆和炸彈在同一垂直線
      if( Math.abs(bombX-wallX)===1 && grids[wallX+wallY*13].type==='nvwall' ) {
        return false;
      }
      var flag = bombX > wallX;
      var i_initial = bombX + (flag ? (-1) : (1));
      for (var i = i_initial; flag ? (i > wallX) : (i < wallX); flag ? (i--) : (i++)) {
        if (grids[i + bombY * 13].type === 'nvwall' || grids[i + bombY * 13].type === 'vwall') {
          //console.log('false=>'+i+','+bombY);
          return false;
        }
      }
    }
    //console.log('true');
    return true;
  }

  function grid_bombed(bombX, bombY, x, y) {
    if ((0 <= x && x <= 12) && (0 <= y && y <= 12) && vwall_checkBombed(bombX, bombY, x, y)) {
      sendObjToAllClient({
        event: 'grid_bombed',
        x: x,
        y: y
      });
      if (grids[x + y * 13].type === 'vwall') {
        var posibility=Math.floor(Math.random()*100);
        if(posibility<30)
          setTimeout(function(){toolappearbybombed(x + y * 13);},750);
        grids[x + y * 13].type = 'empty';
        grids[x + y * 13].empty = true;
        sendObjToAllClient({
          event: 'wall_vanish',
          x: x,
          y: y
        });
      }
    }
  }
  /** bomb ends here */

  /** calculate how many valid players are there */
  // valid === neither disconnected nor dead
  function howManyPlayers()
  {
    var count = 0;
    if(wsConnections) {
      for(var i = 0;i<wsConnections.length;i++) {
        if(wsConnections[i].playerInfo && 
          ( !wsConnections[i].playerInfo.disconnected && 
          !wsConnections[i].playerInfo.dead)) {
            count++;
          }
      }
      return count;
    }
    return -1; // return -1 when no websockets yet
  }

  function toolappearbybombed(grid) {
    var getgrid = grid;
    if (getgrid !== -1) {
      var toolty = (function(){
        var temp = Math.floor(Math.random() * 100) ;
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
        else if(temp >= 99 && temp < 100)
          return 6;
      }());
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

  }
  return newPlayer;
}
