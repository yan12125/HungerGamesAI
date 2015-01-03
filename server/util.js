var map_dimension = 13;
var grid_count = map_dimension * map_dimension;

var gridToPos = function (gridX, gridY) {
    return gridX + gridY * map_dimension;
};

var coordToGrid = function (x, y) {
    return [ Math.floor(x/60), Math.floor(y/60) ];
};

var coordToPos = function (x, y) {
    return gridToPos.apply(undefined, coordToGrid(x, y));
};

var posToGrid = function (pos) {
    return [ pos % 13, Math.floor(pos/13) ];
};

var gridToStr = function (gridX, gridY) {
    return '('+gridX+', '+gridY+')';
};

var posToStr= function (pos) {
    return gridToStr.apply(undefined, posToGrid(pos));
};

module.exports = {
    map_dimension: map_dimension,
    grid_count: map_dimension * map_dimension,
    gridToPos: gridToPos,
    posToGrid: posToGrid,
    coordToGrid: coordToGrid,
    coordToPos: coordToPos,
    posToStr: posToStr,
    gridToStr: gridToStr
};
