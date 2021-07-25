var notifier = require('./notifier');
var fs = require('fs');
var dataHolder;
var htmlStr = '';
var verbose = true;
var refPointer = [];

var report = {
    header: {},
    body: {},
    footer: {}
};
//==================================================================
function init(dHolder) {
    dataHolder = dHolder;
    createLessonNode(dataHolder.xmlData.course);
    mapResults(dataHolder.excelData, report.body);
    generateReport();
    createReport();
}
//==================================================================
function createLessonNode(data) {
    var lCtr = data.topic.length,
        qCtr, qNode, lPtr = 0,
        hasAssessment, isMandatory, lessonNode;
    report.header.systemId = data.$.systemId;
    report.header.baseCatalogId = data.$.baseCatalogId;
    report.header.catalogId = data.$.catalogId;
    report.header.modified = data.modified;
    report.header.title = data.title[0];
    report.header.description = data.description[0].p.toString();
    report.header.assessment = data.assessment;
    report.body.lesson = [];
    //===
    for (var l = 0; l < lCtr; l++) {
        hasAssessment = data.topic[l].assessment && data.topic[l].assessment[0].question && data.topic[l].assessment[0].question.length > 0;
        isMandatory = data.topic[l].$.lessonMode === 'mandatory';
        if (hasAssessment && !isMandatory) {
            lessonNode = {};
            lessonNode.lessonId = data.topic[l].$.lessonId;
            lessonNode.title = data.topic[l].title[0];
            lessonNode.passed = [];
            lessonNode.failed = [];
            lessonNode.userId = '';
            lessonNode.userName = '';
            lessonNode.question = [];
            qCtr = data.topic[l].assessment[0].question.length;
            for (var q = 0; q < qCtr; q++) {
                qNode = {};
                qNode.id = data.topic[l].assessment[0].question[q].$.pageid;
                refPointer[qNode.id] = {
                    lessonIdx: lPtr,
                    questionIdx: q
                };
                qNode.type = data.topic[l].assessment[0].question[q].$.type === 'checkAll' ? 'checkbox' : 'radio';
                qNode.questionText = data.topic[l].assessment[0].question[q].questionText;
                qNode.passed = [];
                qNode.failed = [];
                qNode.userId = '';
                qNode.userName = '';
                qNode.choice = data.topic[l].assessment[0].question[q].choice;
                lessonNode.question[q] = qNode;
            }
            report.body.lesson.push(lessonNode);
            lPtr++;
        }
    }
}
//==================================================================
function mapResults(data, report) {
    var uCtr = data.length,
        uData, ctoData, resultData, qCtr, cCtr, rCtr, ref, uid, uName;
    uCtr = 1;
    try {
        for (var u = 0; u < uCtr; u++) {
            uData = data[u].CORE_LESSON.split('$')[1];
            uid = data[u].USER_ID;
            uName = data[u].LASTNAME + ' ' + data[u].FIRSTNAME;
            ctoData = uData.split('|');
            qData = ctoData[8].split(',');
            resultData = ctoData[11].split(',');
            qCtr = qData.length;
            for (var q = 0; q < qCtr; q++) {
                ref = refPointer[qData[q]];
                if (resultData[q]) {
                    report.lesson[ref.lessonIdx].question[ref.questionIdx].passed.push(uid);
                } else {
                    report.lesson[ref.lessonIdx].question[ref.questionIdx].failed.push(uid);
                }
            }
        }
    } catch (err) {
        sendData('onReportDataProcessError', err.message);
    }
}
//==================================================================
function generateReport() {
    var lCtr = report.body.lesson.length;
    createHeader();
    for (var l = 0; l < lCtr; l++) {
        createBody(report.body.lesson[l], l);
    }
    createFooter();
}
//==================================================================
function createHeader() {
    htmlStr = '';
    htmlStr += '<!DOCTYPE html>\n';
    htmlStr += '<html lang="en">\n';
    htmlStr += '<head>\n';
    htmlStr += '\t<meta charset="UTF-8">\n';
    htmlStr += '\t<meta http-equiv="X-UA-Compatible" content="IE=edge">\n';
    htmlStr += '\t<meta name="viewport" content="width=device-width, initial-scale=1.0">\n';
    htmlStr += '\t<title>' + report.header.title + '</title>\n';
    htmlStr += '\t<link rel="stylesheet" href="style.css">\n';
    htmlStr += '</head>\n';
    htmlStr += '<body>\n';
    htmlStr += '\t<table id="main">';
    htmlStr += '\t\t<tr>';
    htmlStr += '\t\t\t<td>';
    htmlStr += '<h1>' + report.header.title + '</h1>';
    if (verbose) {
        htmlStr += '<p>' + report.header.description + '</p>';
        htmlStr += '<p> <b>modified on</b> : [' + report.header.modified + '] <b>System Id</b> : [' + report.header.systemId + '] <b>Catalog Id</b> :[' + report.header.catalogId + ']</p>';
    }
    htmlStr += '</td>';
    htmlStr += '\t\t</tr>';
    htmlStr += '\t</table>';
    console.log(refPointer['101'], ' >>> ', refPointer['110']);
    //console.log(report.header.assessment);
}
//==================================================================
function createBody(data, idx) {
    var hStr = '',
        qCtr = data.question.length,
        oCtr = 0,
        strClass = '',
        extra = '',
        isCorrect = true,
        isRadio = true;
    if (verbose) {
        extra = '<span class="lessonId"> [' + data.lessonId + ']</span> ';
    }
    hStr += '<h2>' + data.title + extra + '</h2>';
    htmlStr += '\t<table>\n';
    htmlStr += '\t\t<tr>\n';
    htmlStr += '\t\t\t<th id="' + idx + '">' + hStr + '</th>\n';
    htmlStr += '\t\t</tr>\n';
    for (var q = 0; q < qCtr; q++) {
        htmlStr += '\t\t<tr>\n';
        htmlStr += '\t\t\t<td>';
        if (verbose) {
            extra = '[' + data.question[q].id + '] ';
        }
        htmlStr += '<h3 class="question">' + extra + data.question[q].questionText[0].p + '</h3>';
        htmlStr += '<div><ul>';
        oCtr = data.question[q].choice.length;
        isRadio = data.question[q].type === 'radio';
        for (var o = 0; o < oCtr; o++) {
            isCorrect = data.question[q].choice[o].$.isCorrect === 'true';
            strClass = isRadio ? 'radio ' : 'checkbox ';
            strClass += isCorrect ? 'correct ' : 'incorrect';
            if (verbose) {
                extra = '[' + data.question[q].choice[o].$.choiceId + '] ';
            }
            htmlStr += '<li class="' + strClass + '">' + extra + data.question[q].choice[o]._ + '</li>';
        }
        htmlStr += '</ul></div>';
        htmlStr += '</td>\n';
        htmlStr += '\t\t</tr>\n';
    }
    htmlStr += '\t</table>\n\n';
    htmlStr += '\t<hr>\n';
}
//==================================================================
function createFooter() {
    htmlStr += '<div class="footer">&copy; LRN. Generated on : ' + new Date() + '</div>\n';
    htmlStr += '</body>\n';
    htmlStr += '</html>\n';
}
//==================================================================
function createReport() {
    var targetFile = './data/' + dataHolder.fileData.dataFile + '-report.html';
    fs.writeFile(targetFile, htmlStr, 'utf-8', function (err) {
        if (err) {
            sendData('onReportDataError', err.message);
        } else {
            sendData('onReportCompleted', null);
        }
    });
}
//==================================================================
function sendData(eventId, data) {
    notifier.emit(eventId, data);
}
//==================================================================
function stripHTMLTags(str) {
    var strTagStrippedText = str.toString().replace(/<\/?[^>]+(>|$)/g, '');
    return strTagStrippedText;
}
//==================================================================
module.exports.init = init;
//==================================================================