var notifier = require('./lib/notifier');
var checkParam = require('./lib/checkParam');
var convertExcelToJson = require('./lib/convertExcelToJson');
var convertXmlToJson = require('./lib/convertXmlToJson.js');
var report = require('./lib/report');
var dataHolder = {
    fileData: '',
    excelData: '',
    xmlData: '',
    htmlData: ''
};
//==================================================================
function init() {
    console.clear();
    addListener();
    checkParam.init();
}
//==================================================================
function addListener() {
    notifier.on('onParamReceived', function (data) {
        dataHolder.fileData = data;
        convertExcelToJson.init(dataHolder.fileData.dataFile);
    });
    notifier.on('onExcelDataError', function (data) {
        exit(false, 'Issue : Excel Data', data);
    });
    notifier.on('onExcelFileError', function (data) {
        exit(false, 'Issue : Excel File not found', data);
    });
    notifier.on('onExcelDataParsed', function (data) {
        dataHolder.excelData = data;
        convertXmlToJson.init(dataHolder.fileData.dataFile);
    });
    notifier.on('onXmlDataError', function (data) {
        exit(false, 'Issue : Xml Data', data);
    });
    notifier.on('onXmlFileError', function (data) {
        exit(false, 'Issue : Xml File not found', data);
    });
    notifier.on('onXmlDataParsed', function (data) {
        dataHolder.xmlData = data;
        report.init(dataHolder);
    });
    notifier.on('onReportDataError', function (data) {
        exit(false, 'Issue : unable to create report', data);
    });
    notifier.on('onReportDataProcessError', function (data) {
        exit(false, 'Issue : unable to process report data', data);
    });
    notifier.on('onReportCompleted', function (data) {
        exit(true, 'Success : Report generated', data);
    });
}
//==================================================================
function exit(flag, msg, data) {
    if (flag) {
        console.log(msg);
    } else {
        console.log(msg, ' :: ', data);
        process.exit();
    }
}
//==================================================================
init();
//==================================================================