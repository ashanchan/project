#!/usr/bin/env python
import pkgImporter
import util.system as SYSTEM
import util.excel as EXCEL
import util.fileIO as FILE_IO
import util.log as LOGGER
import util.xml2Json as CONVERTOR
# ===================================================


class userData:

    def __init__(self, header, title, body, footer, mode):
        self.header = header
        self.title = title
        self.body = body
        self.footer = footer
        self.mode = mode

    def getReport(self):
        strLine = ''
        for x in self.header:
            strLine += x + '\n'

        if self.mode != 's':
            for y in self.body:
                strLine += y + '\n'

        for z in self.footer:
            strLine += z+'\n'

        return strLine
# ===================================================


def init():
    catalog = None
    catalog = readParam()
    if catalog and catalog['catalogId'] != None:
        generateReport(catalog)

# ===================================================


def readParam():
    SYSTEM.clear()
    LOGGER.show('info', ('#===============================================================================================#'))
    LOGGER.show('info', ('#\tStarting Reporting Process\t\t\t\t\t\t\t\t#'))
    LOGGER.show('info', ('#\t\tFor Processing System needs two files in data folder \t\t\t\t#'))
    LOGGER.show('info', ('#\t\t1. catelogId.xml\t\t [Eg. ./data/APL977-a80en.xml] \t\t\t#'))
    LOGGER.show('info', ('#\t\t2. catelogId-progress.xlsx\t [Eg. ./data/APL977-a80en-progress.xlsx] \t#'))
    LOGGER.show('info', ('#===============================================================================================#'))
    LOGGER.show('info', (''))
    catalogId = 'APL977-a80en'
    summaryMode = 'd'

    #catalogId = SYSTEM.acceptValidInput('Enter Valid CatlogueId : ', [])
    #summaryMode = SYSTEM.acceptValidInput('Report Mode : Detailed / Compact / Summary [D/C/S] : ', ['D', 'C', 'S', 'd', 'c', 's'])

    LOGGER.show('info', (''))
    catalogId = catalogId.strip()
    courseXml = pkgImporter.getFileWithPath('data/'+catalogId+'.xml')
    courseData = pkgImporter.getFileWithPath('data/'+catalogId+'.json')
    courseProgress = pkgImporter.getFileWithPath('data/'+catalogId+'-progress.xlsx')

    isExist1 = SYSTEM.fileExist(courseXml)
    if isExist1 == False:
        LOGGER.show('error', ('File %s does not exists' % (courseXml)))

    isExist2 = SYSTEM.fileExist(courseProgress)
    if isExist2 == False:
        LOGGER.show('error', ('File %s does not exists' % (courseProgress)))

    if isExist1 == True and isExist2 == True:
        CONVERTOR.convert(courseXml, courseData)
    else:
        catalogId = None

    return {'catalogId': catalogId, 'courseData': courseData,  'courseProgress': courseProgress, 'summaryMode': summaryMode}

# ===================================================


def generateReport(catalog):
    printLine = ''
    assessedLesson = 0
    jsonCourseData = FILE_IO.readData(catalog['courseData'])['course']
    jsonProgressData = EXCEL.readData(catalog['courseProgress'])
    courseData = getCourseData(jsonCourseData)
    passingPercent = jsonCourseData["assessment"]['@passingPercentage']

    for user in jsonProgressData['data']:
        reportHeader = []
        reportTitle = []
        reportBody = []
        reportCompact = []
        reportFooter = []
        score = 0
        aCtr = 0
        lCtr = 0
        tQctr = 0
        mCtr = 0
        plData = parseUserResult(user['CORE_LESSON'])
        lessonStatus = plData['lessonStatus']
        hasTestOut = str(jsonCourseData['assessment']['@lessonType'] == 'personalizedLearning')
        #reportHeader.append('<table> <thead> <th>Course Name : [%s] <br> System Id : [%s] </th> <th> Has Assessment : [%s] </th> <th> Pooling : [%s] </th> <th> Randomized On : [%s] </th> </thead>' % (jsonCourseData['@catalogId'], jsonCourseData['@systemId'], hasTestOut, jsonCourseData["assessment"]['@pooling'], jsonCourseData["assessment"]['@randomize'] ))
        reportHeader.append('<h4>User Name : %s %s [%s]</h4>' %(user['FIRSTNAME'], user['LASTNAME'], user['USER_ID']))
        # =========

        testoutTaken = True if len(plData['testoutData']) > 0 else False

        if testoutTaken == True:
            reportBody.append('<table>')
            for lesson in courseData:
                reportBody.append('<tr class="lessonNode"> <td>Lesson Id</td> <td> %s </td>  <td>Lesson Title</td> <td> %s </td>  </tr>' % (lesson['lessonId'], lesson['title']))
                lCtr += 1
                if lesson['assessment'] == None:
                    reportBody.append('<tr> <td colspan="2">Assessment</td> <td colspan="2"> Not Available - Mandatory Lesson  </td>  </tr>' )
                else:
                    correctCtr = 0
                    questions = lesson['assessment']['question']
                    assessmentData = normalizeData(plData['testoutData'][aCtr], len(questions))
                    poolSize = int(lesson['assessment']['@poolSize'])
                    reportBody.append('<tr> <td>Questions Available</td> <td> [%d] </td> <td> Pooled </td> <td> [%s]  </td>  </tr>' % (len(questions), poolSize))

                    qCtr = 0
                    assessedLesson += 1
                    for question in questions:
                        pooledClass = 'pooled' if len(assessmentData[qCtr]['optionIdx']) > 0 else 'not-pooled'
                        reportBody.append('<tr class="%s"><td colspan="2">%d %s </td> <td colspan="2">' % (pooledClass, (qCtr+1), question['questionText']['p']))

                        cCtr = 0
                        tQctr += 1
                        correctChoice = []
                        for choice in question['choice']:
                            isCorrect = choice['@isCorrect'] == 'true'
                            if isCorrect:
                                correctChoice.append(str(choice['@choiceId']))

                            reportBody.append('%s %s <br>' % (choice['@choiceId'], choice['#text']))
                            cCtr += 1

                        result = getResult(correctChoice, assessmentData[qCtr]['optionIdx'])

                        if result == 'Passed':
                            score += 1
                            mCtr += 1
                            correctCtr += 1
                        elif result == 'NotPassed':
                            mCtr += 1

                        sOption = []
                        for s in assessmentData[qCtr]['optionIdx']:
                            sOption.append(str(s))

                        reportBody.append('<br>Correct : %s Selected : %s Result : %s </td></tr>' % (str(correctChoice), str(sOption), result))
                        qCtr += 1

                    aCtr += 1
                    #reportCompact.append('\t\t\t\t : Correct\t\t : [%s] \t Incorrect\t : [%s]' % (correctCtr, (poolSize - correctCtr)))
            reportBody.append('</table>')

        reportFooter.append('<br><br><table class="summary"><thead><th colspan="2">Summary</th></thead>')

        if testoutTaken == True:
            percObtained = score*100/mCtr

            status = 'NOT PASSED'
            if percObtained >= int(passingPercent):
                status = 'PASSED   '

            reportFooter.append('<tr> <td>Total Lesson in the course</td> <td> %d </td> </tr>' % (lCtr))
            reportFooter.append('<tr> <td class="align-right">Testout Lesson</td> <td> %d </td> </tr>' % (aCtr))
            reportFooter.append('<tr> <td class="align-right">Testout Lesson</td> <td> %d </td> </tr>' % (aCtr))
            reportFooter.append('<tr> <td class="align-right">Mandatory Lesson</td> <td> %d </td> </tr>' % (lCtr-aCtr))
            reportFooter.append('<tr> <td>Total Question in the course</td> <td>%d </td> </tr>' % (tQctr))
            reportFooter.append('<tr> <td class="align-right">Questions Offered</td> <td> %d </td> </tr>' % (mCtr))
            reportFooter.append('<tr> <td class="align-right">Correct Answered</td> <td> %d </td> </tr>' % (score))
            reportFooter.append('<tr> <td class="align-right">Incorrect Answered</td> <td> %d </td> </tr>' % (mCtr-score))
            reportFooter.append('<tr> <td>Last Question Attempted</td> <td> %s </td> </tr>' % (plData['lastQuestion']))
            reportFooter.append('<tr> <td>Passing Percent</td> <td> %s </td> </tr>' % (passingPercent))
            reportFooter.append('<tr> <td>Obtained Percent</td> <td> %d </td> </tr>' % (percObtained))
            reportFooter.append('<tr> <td>Result Status</td> <td> %s </td> </tr>' % (status))

        tstStatus = 'DONE' if plData['plStatus'].upper() == 'RESULT' else plData['plStatus'].upper()

        reportFooter.append('<tr> <td>Testout Status</td> <td> %s </td> </tr>' % (tstStatus))
        reportFooter.append('<tr> <td>Lesson Status</td> <td> %s </td> </tr>' % (lessonStatus))
        reportFooter.append('</table><hr>')

        # ======
        if catalog['summaryMode'] == 'c':
            reportBody = reportCompact

        repo = userData(reportHeader, reportHeader, reportBody, reportFooter, catalog['summaryMode'])
        printLine += repo.getReport()

    reportFile = catalog['catalogId']
    reportFile = pkgImporter.getFileWithPath('data/'+reportFile+'-report.txt')

    htmlText = '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><meta http-equiv="X-UA-Compatible" content="ie=edge"><title>Document</title> <style>body {font-family: Verdana, Geneva, Tahoma, sans-serif;}table {width: 100%; height: 100%;border-spacing: 0.5rem;border-collapse: collapse;}thead {background: blue;}tfoot {background: yellow;} td,th {border: 1px solid #999;padding: 0.5rem;vertical-align: top;width: 25%;} .userNode {background:red;} .lessonNode {background:orange;} .summary{ width:50%; text-align: center; margin:auto;} .align-right{text-align:right;} .not-pooled{background: gray;opacity: 0.5;}</style></head>\n'
    htmlText += '<body>\n'
    htmlText += ('<h2>%s</h2>' %jsonCourseData['title'])    
    htmlText += ('<p>Course Name : %s  <br>System Id : %s </br> Assessment Mode : %s  <br>Pooling : %s  <br>Randomized on : %s</p>' %(jsonCourseData['@catalogId'], jsonCourseData['@systemId'], hasTestOut, jsonCourseData["assessment"]['@pooling'], jsonCourseData["assessment"]['@randomize']))
    
    htmlText += printLine
    htmlText += '<p class="align-right">Generated on 10th Aug 2020.</p>'
    htmlText += '\n</body>'

    FILE_IO.writeFile(reportFile, htmlText)
    LOGGER.show('info', ('Report created  %s ' % (reportFile)))
    #SYSTEM.remove(catalog['courseData'])

# ===================================================


def getCourseData(data):
    courseData = []
    for lesson in data['topic']:
        lessonData = {'lessonId': str(lesson['@lessonId']), 'title': str(lesson['title']), 'assessment': None}
        aNode = lesson.get('assessment')
        if aNode != None:
            lessonData['assessment'] = aNode
        courseData.append(lessonData)
    return courseData
# ===================================================


def parseUserResult(coreLesson):
    coreData = coreLesson.split('PL.')
    tempPlData = coreData[1]
    rawPlData = tempPlData.split('|')
    plStatus = rawPlData[0]
    rawPlQuestion = rawPlData[1]
    mappedQuestion = rawPlQuestion.split(',')
    optionIterator = 2
    testoutData = []
    testoutTaken = True

    lessonStatus = 'COMPLETED' if 'lessonsdone' in coreData[0] else 'INCOMPLETE'

    if plStatus == 'skip':
        testoutTaken = False
    if plStatus == 'intro':
        testoutTaken = False

    if testoutTaken == True:
        for assessmentQuestion in mappedQuestion:
            ctr = 0
            mappedQuestionInLesson = assessmentQuestion.split('.')
            assessmentData = []
            for question in mappedQuestionInLesson:
                option = list(rawPlData[optionIterator].split(','))
                assessmentObj = {'questionIdx': question, 'optionIdx': option}
                assessmentData.append(assessmentObj)
                optionIterator += 1
                ctr += 1
            testoutData.append(assessmentData)
        return {'plStatus': plStatus, 'testoutData': testoutData, 'lessonStatus': lessonStatus, 'lastQuestion': rawPlData[optionIterator]}
    else:
        return {'plStatus': plStatus, 'testoutData': [], 'lessonStatus': lessonStatus, 'lastQuestion': 0}
# ===================================================


def normalizeData(testoutData, totalQuestion):
    mappedData = []
    for ctr in range(totalQuestion):
        placeHolder = {'optionIdx': [], 'questionIdx': str(ctr+1), "pooled": False}
        mappedData.append(placeHolder)

    for data in testoutData:
        qIdx = data['questionIdx']
        for ctr in range(totalQuestion):
            cIdx = mappedData[ctr].get('questionIdx')
            if cIdx == qIdx:
                mappedData[ctr]['optionIdx'] = data['optionIdx']
                mappedData[ctr]['pooled'] = True

    # for x in mappedData:
    #     print('%s \t : %s' % (x['questionIdx'], x['optionIdx']))

    return mappedData


# ===================================================

def getResult(correct, selection):
    correct.sort()
    selection.sort()

    if len(selection) == 0:
        return 'NA'
    else:
        if correct == selection:
            return 'Passed'
        else:
            return 'NotPassed'

# ===================================================


init()
