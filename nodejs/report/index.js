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
        exit('Issue : Excel Data', false);
    });
    notifier.on('onExcelFileError', function (data) {
        exit('Issue : Excel File not found', false);
    });
    notifier.on('onExcelDataParsed', function (data) {
        dataHolder.excelData = data;
        convertXmlToJson.init(dataHolder.fileData.dataFile);
    });
    notifier.on('onXmlDataError', function (data) {
        exit('Issue : Xml Data', false);
    });
    notifier.on('onXmlFileError', function (data) {
        exit('Issue : Xml File not found', false);
    });
    notifier.on('onXmlDataParsed', function (data) {
        dataHolder.xmlData = data;
        report.init(dataHolder);
    });
    notifier.on('onReportDataError', function (data) {
        exit('Issue : unable to create report', false);
    });
    notifier.on('onReportCompleted', function (data) {
        exit('Success : Report generated', true);
    });
}
//==================================================================
function exit(msg, flag) {
    console.log(msg);
    if (!flag) {
        process.exit();
    }
}
//==================================================================
init();
//==================================================================