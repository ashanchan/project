var fs = require('fs');
var notifier = require('./notifier');
var xml2js = require('xml2js');
//==================================================================
function init(fileName) {
    var filePath = './data/' + fileName;
    var options = {
        input: filePath + '.xml',
        output: filePath + '-xml.json'
    };
    var rawXmlData, xmlData, parser = new xml2js.Parser();
    //===
    try {
        rawXmlData = fs.readFileSync(options.input);
        xmlData = rawXmlData.toString();
        //== need to find all <br> and replace it with<br/>
        parser = new xml2js.Parser();
        parser.parseString(xmlData.substring(0, xmlData.length), function (err, result) {
            if (err) {
                console.log(err);
                sendData('onXmlDataError', undefined);
            } else {
                sendData('onXmlDataParsed', result);
            }
            jsonData = result;
        });
    } catch (e) {
        sendData('onXmlFileError', undefined);
    }
}
//==================================================================
function sendData(eventId, data) {
    notifier.emit(eventId, data);
}
//==================================================================
module.exports.init = init;
//==================================================================