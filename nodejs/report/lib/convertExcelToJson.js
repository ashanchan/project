var notifier = require('./notifier');
var xlsxToJson = require('xlsx-to-json');
//==================================================================
function init(fileName) {
    var filePath = './data/' + fileName;
    var options = {
        input: filePath + '.xlsx',
        output: null
    };
    var callback = function (err, result) {
        if (err) {
            sendData('onExcelDataError', undefined);
        } else {
            sendData('onExcelDataParsed', result);
        }
    };
    //===
    try {
        xlsxToJson(options, callback);
    } catch (e) {
        sendData('onExcelFileError', undefined);
    }
}
//==================================================================
function sendData(eventId, data) {
    notifier.emit(eventId, data);
}
//==================================================================
module.exports.init = init;
//==================================================================