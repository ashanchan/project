var readlineSync = require('readline-sync');
var notifier = require('./notifier');
var report = {
    type: '',
    dataFile: '',
    userId: ''
};
//==================================================================
function init() {
    if (readlineSync.keyInYN('Do you want to run Full Report?')) {
        report.type = 'R';
        getDataName();
    } else {
        report.type = 'U';
        getUserId();
    }
}
//==================================================================
function getUserId() {
    report.userId = readlineSync.question('Enter user Id : ');
    getDataName();
}
//==================================================================
function getDataName() {
    report.dataFile = readlineSync.question('What is the data file Name? ');
    report.dataFile = 'APL986-a80en';
    sendData();
}
//==================================================================
function sendData() {
    notifier.emit('onParamReceived', report);
}
//==================================================================
module.exports.init = init;
//==================================================================