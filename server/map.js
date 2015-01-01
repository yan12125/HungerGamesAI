var fs = require('fs');
var util = require('./util.js');

/*
 * TODO initial bomb support
 * */
var symbolToType = {
    'o': 'empty',
    'x': 'vwall',
    'X': 'nvwall'
};

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

function iniMap(map_name) {
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

module.exports = {
    'iniMap': iniMap, 
    'grids': grids
};
