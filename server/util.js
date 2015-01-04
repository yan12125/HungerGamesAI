"use strict";

var sntp = require('sntp');

var map_dimension = 13;
var grid_count = map_dimension * map_dimension;
var ntp_offset = NaN;

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

var isTimerObject = function (obj) {
    /*
     * check whether obj is a returned value of
     * setTimeout/setInterval or not
     * browsers return positive integers, while
     * node.js return objects
     */
    return (obj >= 1 || obj instanceof Object);
}

var ntpOffsetWorker = function() {
    var options = {
        timeout: 1000
    };

    sntp.time(options, function (err, time) {
        if (err) {
            console.log(('Warning: failed to fetch remote time: ' + err.message).red);
            ntp_offset = NaN;
        } else {
            console.log('SNTP: time difference='+time.t);
            ntp_offset = time.t / 1000;
        }
    });
};

ntpOffsetWorker();

setInterval(ntpOffsetWorker, 30000);

var getNtpOffset = function () {
    return ntp_offset;
};

module.exports = {
    map_dimension: map_dimension,
    grid_count: map_dimension * map_dimension,
    gridToPos: gridToPos,
    posToGrid: posToGrid,
    coordToGrid: coordToGrid,
    coordToPos: coordToPos,
    posToStr: posToStr,
    gridToStr: gridToStr,
    isTimerObject: isTimerObject,
    getNtpOffset: getNtpOffset
};
