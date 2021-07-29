var notifier = require('./notifier');
var fs = require('fs');
var dataHolder;
var htmlStr = '';
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
    var jsFile = './' + dataHolder.fileData.dataFile + '-report.js';
    htmlStr = '';
    htmlStr += '<!DOCTYPE html>\n';
    htmlStr += '<html lang="en">\n\n';
    htmlStr += '<head>\n';
    htmlStr += '\t<meta charset="UTF-8">\n';
    htmlStr += '\t<meta http-equiv="X-UA-Compatible" content="IE=edge">\n';
    htmlStr += '\t<meta name="viewport" content="width=device-width, initial-scale=1.0">\n';
    htmlStr += '\t<title>' + report.header.title + '</title>\n';
    htmlStr += '\t<link rel="stylesheet" href="./../lib/style.css">\n';
    htmlStr += '\t<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>\n';
    htmlStr += '\t<script type="text/javascript" src="' + jsFile + '"></script>\n';
    htmlStr += '\t<script type="text/javascript" src="./../lib/script.js"></script>\n';
    htmlStr += '</head>\n\n';
    htmlStr += '<body onload="init()">\n';
    addTrackedData('header', null, null);
}
//==================================================================
function createBody(data, idx) {
    var qCtr = data.question.length,
        o = 0,
        oCtr = 0,
        strClass = '',
        isCorrect = true,
        isRadio = true;

    htmlStr += '\t<table id="LESSON_' + idx + '" class="detail">\n';
    htmlStr += '\t\t<tr>\n';
    addTrackedData('lesson', idx, data);
    htmlStr += '\t\t</tr>\n';
    for (var q = 0; q < qCtr; q++) {
        htmlStr += '\t\t<tr>\n';
        htmlStr += '\t\t\t<td>\n';
        addTrackedData('question', q, data);
        htmlStr += '\t\t\t\t\t<div class="js-data-holder">\n';
        htmlStr += '\t\t\t\t\t\t<ul>\n';
        oCtr = data.question[q].choice.length;
        isRadio = data.question[q].type === 'radio';
        for (o = 0; o < oCtr; o++) {
            isCorrect = data.question[q].choice[o].$.isCorrect === 'true';
            strClass = isRadio ? 'radio ' : 'checkbox ';
            strClass += isCorrect ? 'correct ' : 'incorrect';
            htmlStr += '\t\t\t\t\t\t\t<li class="' + strClass + '">' + '[' + data.question[q].choice[o].$.choiceId + '] ' + data.question[q].choice[o]._ + '</li>\n';
        }
        htmlStr += '\t\t\t\t\t\t</ul>\n';
        addTrackedData('choice', q, data);
        htmlStr += '\t\t\t</td>\n';
        htmlStr += '\t\t</tr>\n';
    }
    htmlStr += '\t</table>\n\n';
    htmlStr += '\t<hr>\n\n';
}
//==================================================================
function createFooter() {
    addTrackedData('analytics', null, null);
    htmlStr += '\t<div class="footer">&copy; LRN Corporation. Generated on : ' + new Date() + '</div>\n\n';
    htmlStr += '</body>\n\n';
    htmlStr += '</html>\n';
}
//==================================================================
function createReport() {
    var targetFile = './output/' + dataHolder.fileData.dataFile + '-report.html';
    var targetFile1 = './output/' + dataHolder.fileData.dataFile + '-report.js';
    fs.writeFile(targetFile, htmlStr, 'utf-8', function (err) {
        if (err) {
            sendData('onReportDataError', err.message);
        } else {
            sendData('onReportCompleted', null);
        }
    });
    //===
    report.body.course = {
        completed: userCount.completed,
        skipped: userCount.skipped
    };

    var reportData = 'var reportData = ' + JSON.stringify(report.body) + ';\n';
    //==
    fs.writeFile(targetFile1, reportData, 'utf-8', function (err) {
        if (err) {
            console.log(err.message);
            sendData('onReportDataErrorx', err.message);
        } else {
            sendData('onReportCompletedx', null);
        }
    });
}
//==================================================================
function sendData(eventId, data) {
    notifier.emit(eventId, data);
}
//==================================================================
function addTrackedData(type, idx, data) {
    switch (type) {
        case 'header':
            createToggle();
            htmlStr += '\t<table id="COURSE" class="header">\n';
            htmlStr += '\t\t<th id="DETAILS">\n';
            htmlStr += '\t\t\t<tr>\n';
            htmlStr += '\t\t\t\t<h1>' + report.header.title + '</h1>\n';
            htmlStr += '\t\t\t\t<div id="COURSE">\n';
            htmlStr += '\t\t\t\t\t<div class="extra">\n';
            htmlStr += '\t\t\t\t\t\t<p>';
            htmlStr += report.header.description + '<br>';
            htmlStr += '<strong>modified on</strong> : [' + report.header.modified + '] <strong>System Id</strong> : [' + report.header.systemId + '] <strong>Catalog Id</strong> :[' + report.header.catalogId + ']</p>\n';
            htmlStr += '\t\t\t\t\t\t<hr>\n';
            htmlStr += '\t\t\t\t\t\t<p>';
            htmlStr += '<strong>Testout Mode</strong> : [' + report.header.assessment[0].$.testOutMode + '] <strong>Testout Level</strong> :[' + report.header.assessment[0].$.testOutMode + '] <strong>Randomize</strong> : [' + report.header.assessment[0].$.randomize + '] <strong>Pooling</strong> : [' + report.header.assessment[0].$.pooling + ']<br>';
            htmlStr += '<strong>Total User</strong> : [' + userCount.total + '] <strong>Total Attempted</strong> : [' + userCount.completed + '] <strong>Total Skipped</strong> : [' + userCount.skipped + ']<br>';
            htmlStr += '</p>\n';
            htmlStr += '\t\t\t\t\t</div>\n';
            htmlStr += '\t\t\t\t</div>\n';
            htmlStr += '\t\t\t</tr>\n';
            htmlStr += '\t\t</th>\n';
            htmlStr += '\t</table>\n\n';
            break;

        case 'lesson':
            htmlStr += '\t\t\t<th id="' + idx + '">\n';
            htmlStr += '\t\t\t\t<h2>' + data.title + '</h2>\n';
            htmlStr += '\t\t\t\t<div class="extra">\n';
            htmlStr += '\t\t\t\t\t<span><strong>Attempted By</strong> : [' + Number(data.passedId.length + data.failedId.length) + '] <strong>Total Passed</strong> : [' + Number(data.passedId.length) + '] <strong>Total Not Passed</strong> : [' + Number(data.failedId.length) + ']</span><br>\n';
            htmlStr += '\t\t\t\t\t<span><strong>Passed</strong> : [' + data.passedName + ']</span><br>\n';
            htmlStr += '\t\t\t\t\t<span><strong>Not Passed</strong> : [' + data.failedName + ']</span><br>\n';
            htmlStr += '\t\t\t\t</div>\n';
            htmlStr += '\t\t\t</th>\n';
            break;

        case 'question':
            htmlStr += '\t\t\t\t<div class="js-data-holder">\n';
            htmlStr += '\t\t\t\t\t<h3 class="question">[' + data.question[idx].id + '] ' + data.question[idx].questionText[0].p + '</h3>\n';
            break;

        case 'choice':
            htmlStr += '\t\t\t\t\t\t<div id="QUESTION_' + idx + '">\n';
            htmlStr += '\t\t\t\t\t\t\t<div class="extra"><strong>Attempted By</strong> : [' + Number(data.question[idx].passedId.length + data.question[idx].failedId.length) + '] <strong>Total Passed</strong> : [' + Number(data.question[idx].passedId.length) + '] <strong>Total Not Passed</strong> : [' + Number(data.question[idx].failedId.length) + ']</div>\n';
            htmlStr += '\t\t\t\t\t\t\t<div class="extra"><strong>Passed</strong> : [' + data.question[idx].passedId + '] <strong>Not Passed</strong> : [' + data.question[idx].failedId + ']</div>\n';
            htmlStr += '\t\t\t\t\t\t</div>\n';
            htmlStr += '\t\t\t\t\t\t<div id="CHOICE_' + idx + '" class="js-data-holder">\n';
            htmlStr += '\t\t\t\t\t\t\t';
            var oCtr = data.question[idx].choice.length;
            for (var o = 0; o < oCtr; o++) {
                htmlStr += 'Number of Learner selected choice ' + o + ': [' + Number(data.question[idx].choice[o].userId.length) + ']<br>';
            }
            htmlStr += '\n\t\t\t\t\t\t</div>\n';
            htmlStr += '\t\t\t\t\t</div>\n';
            htmlStr += '\t\t\t\t</div>\n';
            break;

        case 'analytics':
            htmlStr += '\t<table id="ANALYTICS" class="header">\n';
            htmlStr += '\t\t<th id="GRAPH_DATA">\n';
            htmlStr += '\t\t\t<tr>\n';
            htmlStr += '\t\t\t\t<h2>Anaylitcs</h2>\n';
            htmlStr += '\t\t\t</tr>\n';
            htmlStr += '\t\t</th>\n';

            htmlStr += '\t\t\t<tr>\n';
            htmlStr += '\t\t<td>\n';
            htmlStr += '\t\t\t<div id="COURSE_CHART_DIV"></div>\n';
            htmlStr += '\t\t</td>\n';
            htmlStr += '\t\t\t</tr>\n';

            htmlStr += '\t\t\t<tr>\n';
            htmlStr += '\t\t<td>\n';
            htmlStr += '\t\t\t<div id="LESSON_CHART_DIV"></div>\n';
            htmlStr += '\t\t</td>\n';
            htmlStr += '\t\t\t</tr>\n';

            htmlStr += '\t\t\t<tr>\n';
            htmlStr += '\t\t<td>\n';
            htmlStr += '\t\t\t<div id="QUESTION_CHART_DIV"></div>\n';
            htmlStr += '\t\t</td>\n';
            htmlStr += '\t\t\t</tr>\n';

            htmlStr += '\t</table>\n\n';
            break;
    }
}
//==================================================================
function getTextNode(textNode) {
    // for (var i in textNode) {
    //     //console.log(i, textNode[i]);
    // }
}
//==================================================================
function createToggle() {
    htmlStr += '\t<div id="TOGGLER">';
    htmlStr += '<label class="switch"><input type="checkbox" id="I_BOX" onclick="toggleData(event)"><span class="slider"> </span></label >';
    htmlStr += '</div>\n\n';
}
//==================================================================
module.exports.init = init;
//==================================================================