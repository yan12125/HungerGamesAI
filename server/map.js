"use strict";

var fs = require('fs');
var util = require('./util.js');
var _ = require('underscore');

/*
 * TODO initial bomb support
 * */
var symbolToType = {
    'o': 'empty',
    'x': 'vwall',
    'X': 'nvwall'
};

var directions = [ [0, 1], [0, -1], [1, 0], [-1, 0] ];

var grids = Array(util.grid_count);

function loadMapFromFile (map_name)
{
    var ret = Array(util.grid_count);

    var filename = './maps/' + map_name + '.txt';
    var content = fs.readFileSync(filename, { encoding: 'utf-8' });
    var rows = content.trim().split('\n');

    if(rows.length != util.map_dimension)
    {
        throw 'Unexpected number of rows: ' + rows.length;
    }

    for(var i = 0; i < util.map_dimension; i++)
    {
        var row = rows[i].trim().split(''); // is it portable?

        if(row.length != util.map_dimension)
        {
            throw 'Unexpected number of columns ' + row.length + ' in row ' + i;
        }

        for(var j = 0; j < util.map_dimension; j++)
        {
            var symbol = row[j];
            var type = symbolToType[symbol];

            if(typeof(type) == 'undefined')
            {
                throw 'Unexpected symbol ' + symbol + ' at ('+ i + ', ' + j + ')';
            }

            ret[i * util.map_dimension + j] = type;
        }
    }

    return ret;
}

function iniMap(map_name)
{
    console.log('[Notice] Initializing the map...');

    var wall = loadMapFromFile(map_name);

    for (var i = 0; i < util.grid_count; i++)
    {
        grids[i] = {
            empty: true,
            type: 'empty' //1.tool 2.bomb 3.vwall 4.nvwall 5.empty
        };

        if (wall[i] === 'empty')
        {
            continue;
        }

        grids[i].empty = false;
        grids[i].type = wall[i];
    }
}

function isValidGrid(gridX, gridY)
{
    var xValid = (0 <= gridX && gridX < util.map_dimension);
    var yValid = (0 <= gridY && gridY < util.map_dimension);
    return xValid && yValid;
}

function bombing(gridX, gridY)
{
    var dangerMap = Array(util.grid_count);

    for(var i = 0; i < util.grid_count; i++)
    {
        dangerMap[i] = false;
    }

    var bombingBombs = [util.gridToPos(gridX, gridY)];
    var bombIndex = 0;
    while(bombIndex < bombingBombs.length)
    {
        var curPos = bombingBombs[bombIndex];
        bombIndex++;

        var curGrids = util.posToGrid(curPos);
        console.log("Bomb at "+util.gridToStr.apply(undefined, curGrids)+" bombs");

        var grid = grids[curPos];
        if (grid.type !== 'bomb')
        {
            throw 'Unexpected: something not bomb bombs';
        }


        for(var i = 0; i < directions.length; i++)
        {
            var dir = directions[i];
            for(var j = 1; j <= grid.bombingPower; j++)
            {
                var newGridX = curGrids[0] + j * dir[0];
                var newGridY = curGrids[1] + j * dir[1];
                if(!isValidGrid(newGridX, newGridY))
                {
                    continue;
                }
                var newPos = util.gridToPos(newGridX, newGridY);
                console.log('Check grid '+util.posToStr(newPos));
                if(grids[newPos].type == 'bomb' && bombingBombs.indexOf(newPos) == -1)
                {
                    bombingBombs.push(newPos);
                }

                if(grids[newPos].type == 'nvwall')
                {
                    break;
                }

                dangerMap[newPos] = true;

                // vwalls is in danger, while nvwalls not
                if(grids[newPos].type == 'vwall')
                {
                    break;
                }
            }
        }
    }

    var gridBombed = [];
    var wallBombed = [];
    for(var i = 0; i < util.grid_count; i++)
    {
        if(dangerMap[i])
        {
            var grid = grids[i];
            gridBombed.push(i);
            if(grid.type == 'vwall')
            {
                wallBombed.push(i);
            }
        }
    }

    gridBombed = _.union(gridBombed, bombingBombs);

    var ret = {
        'bombing': bombingBombs,
        'gridBombed': gridBombed,
        'wallBombed': wallBombed
    };
    console.log('bombing results: ');
    console.log(ret);
    return ret;
}

module.exports = {
    'iniMap': iniMap,
    'grids': grids,
    'bombing': bombing
};
