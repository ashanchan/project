var notifier = require('./notifier');
var fs = require('fs');
var dataHolder;
var htmlStr = '';
var verbose = true;
var refPointer = [];
var userCount = {
    total: 0,
    completed: 0,
    skipped: 0
};

var report = {
    header: {},
    body: {},
    footer: {}
};
//==================================================================
function init(dHolder) {
    dataHolder = dHolder;
    createLessonNode(dataHolder.xmlData.course);
    mapResults(dataHolder.excelData);
    generateReport();
    createReport();
}
//==================================================================
function createLessonNode(data) {
    var lCtr = data.topic.length,
        qCtr, qNode, lPtr = 0,
        cCtr,
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
            lessonNode.passedId = [];
            lessonNode.failedId = [];
            lessonNode.passedName = [];
            lessonNode.failedName = [];
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
                getTextNode(qNode.questionText);
                qNode.passedId = [];
                qNode.failedId = [];
                qNode.passedName = [];
                qNode.failedName = [];
                qNode.choice = data.topic[l].assessment[0].question[q].choice;
                cCtr = qNode.choice.length;
                for (var c = 0; c < cCtr; c++) {
                    qNode.choice[c].userId = [];
                    qNode.choice[c].userName = [];
                    qNode.choice[c].ctr = 0;
                }
                lessonNode.question[q] = qNode;
            }
            report.body.lesson.push(lessonNode);
            lPtr++;
        }
    }
}
//==================================================================
function mapResults(data) {
    var uCtr = data.length,
        uData, ctoData, resultData, qCtr, completedData, ref, uId, uName, qData, choiceData, selectedData, cCtr;
    try {
        userCount.total = uCtr;
        for (var u = 0; u < uCtr; u++) {
            uData = data[u].CORE_LESSON.split('$')[1];
            uId = data[u].USER_ID;
            uName = data[u].LASTNAME + ' ' + data[u].FIRSTNAME;
            ctoData = uData.split('|');
            if (ctoData[13] === 'S') {
                userCount.skipped++;
                continue;
            }
            userCount.completed++;
            qData = ctoData[8].split(',');
            choiceData = ctoData[10].split(',');
            resultData = ctoData[11].split(',');
            completedData = ctoData[12].split(',');
            qCtr = qData.length;
            for (var q = 0; q < qCtr; q++) {
                ref = refPointer[qData[q]];
                selectedData = choiceData[q].split('-');
                cCtr = selectedData.length;
                for (var c = 0; c < cCtr; c++) {
                    if (selectedData[c] === '1') {
                        report.body.lesson[ref.lessonIdx].question[ref.questionIdx].choice[c].userId.push(uId);
                        report.body.lesson[ref.lessonIdx].question[ref.questionIdx].choice[c].userName.push(uName);
                        report.body.lesson[ref.lessonIdx].question[ref.questionIdx].choice[c].ctr++;
                    }
                }
                if (resultData[q] === 'P') {
                    report.body.lesson[ref.lessonIdx].question[ref.questionIdx].passedId.push(uId);
                    report.body.lesson[ref.lessonIdx].question[ref.questionIdx].passedName.push(uName);
                } else {
                    report.body.lesson[ref.lessonIdx].question[ref.questionIdx].failedId.push(uId);
                    report.body.lesson[ref.lessonIdx].question[ref.questionIdx].failedName.push(uName);
                }
            }
            checkLessonCompletion(completedData, uId, uName);
        }
    } catch (err) {
        sendData('onReportDataProcessError', err.message);
    }
}
//==================================================================
function checkLessonCompletion(completedData, uId, uName) {
    var lCtr = report.body.lesson.length,
        lessonCompleted, cCtr, lId;
    for (var l = 0; l < lCtr; l++) {
        lId = report.body.lesson[l].lessonId.split('_')[1];
        cCtr = completedData.length;
        for (var c = 0; c < cCtr; c++) {
            lessonCompleted = completedData[c].split('_');
            if (lId === lessonCompleted[0]) {
                if (lessonCompleted[1] === 'P') {
                    report.body.lesson[l].passedId.push(uId);
                    report.body.lesson[l].passedName.push(uName);
                } else {
                    report.body.lesson[l].failedId.push(uId);
                    report.body.lesson[l].failedName.push(uName);
                }
                completedData.splice(c, 1);
                break;
            }
        }
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
    htmlStr += '<div class="extra"><p><b>Testout Mode</b> : [' + report.header.assessment[0].$.testOutMode + '] <b>Testout Level</b> :[' + report.header.assessment[0].$.testOutMode + '] <b>Randomize</b> : [' + report.header.assessment[0].$.randomize + '] <b>Pooling</b> : [' + report.header.assessment[0].$.pooling + ']</p></div>';
    htmlStr += '<div class="extra"><p><b>Total User</b> : [' + userCount.total + '] <b>Total Attempted</b> : [' + userCount.completed + '] <b>Total Skipped</b> : [' + userCount.skipped + '] </p></div > ';
    htmlStr += '</td>';
    htmlStr += '\t\t</tr>';
    htmlStr += '\t</table>';
}
//==================================================================
function createBody(data, idx) {
    var qCtr = data.question.length,
        o = 0,
        oCtr = 0,
        strClass = '',
        extra = '',
        isCorrect = true,
        isRadio = true;
    htmlStr += '\t<table>\n';
    htmlStr += '\t\t<tr>\n';
    addExtraData('lesson', idx, data);
    htmlStr += '\t\t</tr>\n';
    for (var q = 0; q < qCtr; q++) {
        htmlStr += '\t\t<tr>\n';
        htmlStr += '\t\t\t<td>';
        htmlStr += '<h3 class="question">[' + data.question[q].id + '] ' + data.question[q].questionText[0].p + '</h3>';
        if (verbose) {
            htmlStr += '<div class="extra"><b>Attempted By</b> : [' + Number(data.question[q].passedId.length + data.question[q].failedId.length) + '] <b>Total Passed</b> : [' + Number(data.question[q].passedId.length) + '] <b>Total Not Passed</b> : [' + Number(data.question[q].failedId.length) + ']</div>';
            htmlStr += '<div class="extra"><b>Passed</b> : [' + data.question[q].passedId + '] <b>Not Passed</b> : [' + data.question[q].failedId + ']</div>';
        }
        htmlStr += '<div><ul>';
        oCtr = data.question[q].choice.length;
        isRadio = data.question[q].type === 'radio';
        for (o = 0; o < oCtr; o++) {
            isCorrect = data.question[q].choice[o].$.isCorrect === 'true';
            strClass = isRadio ? 'radio ' : 'checkbox ';
            strClass += isCorrect ? 'correct ' : 'incorrect';
            if (verbose) {
                extra = '[' + data.question[q].choice[o].$.choiceId + '] ';
            }
            htmlStr += '<li class="' + strClass + '">' + extra + data.question[q].choice[o]._ + '</li>';
        }
        htmlStr += '</ul></div>';
        if (verbose) {
            extra = '';
            for (o = 0; o < oCtr; o++) {
                extra += '<b>Choice ' + o + '<b> : [' + data.question[q].choice[o].userId + ']<br>';
            }
            htmlStr += '<div class="extra">' + extra + '</div>';
        }
        htmlStr += '</td>\n';
        htmlStr += '\t\t</tr>\n';
    }
    htmlStr += '\t</table>\n\n';
    htmlStr += '\t<hr>\n';
}
//==================================================================
function addExtraData(type, idx, data) {
    switch (type) {
        case 'lesson':
            htmlStr += '\t\t\t<th id="' + idx + '">';
            htmlStr += '<h2>' + data.title + '</h2>';
            htmlStr += '<div id="LESSON_"' + idx + ' class="not_expanded">';
            htmlStr += '<div class="extra"><b>Attempted By</b> : [' + Number(data.passedId.length + data.failedId.length) + '] <b>Total Passed</b> : [' + Number(data.passedId.length) + '] <b>Total Not Passed</b> : [' + Number(data.failedId.length) + ']</div>';
            htmlStr += '<div class="extra"><b>Passed</b> : [' + data.passedId + '] <b>Not Passed</b> : [' + data.failedId + ']</div>';
            htmlStr += '</div>';
            htmlStr += '</th>\n';
            break;

        case 'question':
            break;
        case 'choice':
            break;
        default:
            break;
    }
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
function getTextNode(textNode) {
    for (var i in textNode) {
        console.log(i, textNode[i]);
    }
}
//==================================================================
module.exports.init = init;
//==================================================================