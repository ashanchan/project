#!/usr/bin/env python
import pkgImporter
import util.system as SYSTEM
import util.excel as EXCEL
import util.fileIO as FILE_IO
import util.log as LOGGER
import util.xml2Json as CONVERTOR
import datetime
# ===================================================


class userData:

    def __init__(self, header, body, footer, analytics, courseData, mode):
        self.header = header
        self.body = body
        self.footer = footer
        self.analytics = analytics
        self.courseData = courseData
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

    def getAnalytics(self):
        printLine = ''
        uniqueLesson = SYSTEM.getUniqueKeyFromList(self.analytics, 'lessonId')
        ctr = 0
        for lesson in uniqueLesson:
            uniqueQuestion = SYSTEM.getUniqueKeyFromList(self.analytics[lesson], 'questionId')
            for question in uniqueQuestion:
                print('abc')

            ctr += 1

        reportFile = pkgImporter.getFileWithPath('data/analytics.txt')
        FILE_IO.writeFile(reportFile, printLine)

        # for lesson in self.courseData:
        #     print(lesson['lessonId'])
        #     cCtr = 0
        #     iCtr = 0

        #     for data in report:
        #         if lesson['lessonId'] == data['lessonId']:
        #             if data['result'] != 'NA':
        #                 if data['result'] == 'Passed':
        #                     cCtr += 1
        #                 else:
        #                     iCtr += 1

        #                 print('\t %s  \t%s' % (data['userName'], data['result']))

        #     print ('total [%s], passed [%s], failed [%s]' % (cCtr+iCtr, cCtr, iCtr))
        #     aCtr +=1
        #     if aCtr == 3 :
        #         break

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
    summaryMode = 'c'

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
    reportAnalytics = createAnayticsNode(courseData)

    for user in jsonProgressData['data']:
        reportHeader = []
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
        reportHeader.append('<h4>User Name : %s %s [%s]</h4>' % (user['FIRSTNAME'], user['LASTNAME'], user['USER_ID']))
        reportAnalytics['userId'].append(user['USER_ID'])
        reportAnalytics['userName'].append(user['FIRSTNAME'] + ' ' + user['LASTNAME'])

        # =========

        testoutTaken = True if len(plData['testoutData']) > 0 else False

        if testoutTaken == True:
            reportBody.append('<table>')
            reportCompact.append('<table>')
            for lesson in courseData:
                reportBody.append('<tr class="lessonNode"> <td>Lesson Id</td> <td> %s </td>  <td>Lesson Title</td> <td> %s </td>  </tr>' % (lesson['lessonId'], lesson['title']))
                lCtr += 1
                if lesson['assessment'] == None:
                    reportBody.append('<tr> <td colspan="2">Assessment</td> <td colspan="2"> Not Available - Mandatory Lesson  </td>  </tr>')
                else:
                    correctCtr = 0
                    questions = lesson['assessment']['question']
                    assessmentData = normalizeData(plData['testoutData'][aCtr], len(questions))
                    poolSize = int(lesson['assessment']['@poolSize'])
                    reportBody.append('<tr> <td>Questions Available</td> <td> [%d] </td> <td> Pooled </td> <td> [%s]  </td>  </tr>' % (len(questions), poolSize))
                    reportCompact.append('<tr class="lessonNode"> <td>Lesson Id</td> <td> %s </td>  <td>Lesson Title</td> <td> %s </td>  </tr>' % (lesson['lessonId'], lesson['title']))
                    reportCompact.append('<tr> <td>Questions Available : [%d] </td> <td> Pooled : [%d] </td>' % (len(questions), poolSize))

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

                        # isUniqueLesson = SYSTEM.isUnique(reportAnalytics, 'lessonId', lesson['lessonId'])
                        # if isUniqueLesson:
                        #         reportAnalytics['lessonId'].append(lesson['lessonId'])

                        # isUniqueQuestion = SYSTEM.isUnique(reportAnalytics['quesitonId'], '@questionId', question['@questionId'])
                        # if isUniqueLesson:
                        #         reportAnalytics['questionId'].append(questions['@questionId'])

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
                    reportCompact.append('<td>Correct : [%s]</td> <td>Incorrect : [%s]  </td></tr>' % (correctCtr, (poolSize - correctCtr)))
            reportBody.append('</table>')
            reportCompact.append('</table>')

        reportFooter.append('<br><br><table class="summary"><thead><th colspan="2">Summary</th></thead>')

        if testoutTaken == True:
            percObtained = score*100/mCtr

            status = 'NOT PASSED'
            if percObtained >= int(passingPercent):
                status = 'PASSED   '

            reportFooter.append('<tr> <td>Total Lesson in the course</td> <td> %d </td> </tr>' % (lCtr))
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

        repo = userData(reportHeader, reportBody, reportFooter, reportAnalytics, courseData, catalog['summaryMode'])
        printLine += repo.getReport()

    for z in reportAnalytics['lessonId']:
        print(z)

    reportFile = catalog['catalogId']+'-detail'
    if catalog['summaryMode'] == 'c':
        reportFile = catalog['catalogId']+'-compact'
    elif catalog['summaryMode'] == 's':
        reportFile = catalog['catalogId']+'-summary'

    reportFile = pkgImporter.getFileWithPath('data/'+reportFile+'-report')

    htmlText = '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><meta http-equiv="X-UA-Compatible" content="ie=edge"><title>Document</title> <style>body {font-family: Verdana, Geneva, Tahoma, sans-serif;}table {width: 100%; height: 100%;border-spacing: 0.5rem;border-collapse: collapse;}thead {background: blue;}tfoot {background: yellow;} td,th {border: 1px solid #999;padding: 0.5rem;vertical-align: top;width: 25%;} .userNode {background:red;} .lessonNode {background:orange;} .summary{ width:50%; text-align: center; margin:auto;} .align-right{text-align:right;} .not-pooled{background: gray;opacity: 0.5;}</style></head>\n'
    htmlText += '<body>\n'
    htmlText += ('<h2>%s</h2>' % jsonCourseData['title'])
    htmlText += ('<p>Course Name : %s  <br>System Id : %s </br> Assessment Mode : %s  <br>Pooling : %s  <br>Randomized on : %s</p>' % (jsonCourseData['@catalogId'], jsonCourseData['@systemId'], hasTestOut, jsonCourseData["assessment"]['@pooling'], jsonCourseData["assessment"]['@randomize']))

    htmlText += printLine
    htmlText += ('<p class="align-right">Generated on %s</p>' % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
    htmlText += '\n</body>'

    FILE_IO.writeFile(reportFile+'.html', htmlText)

    convertHtmlToPdf(reportFile)

    LOGGER.show('info', ('Report created  %s ' % (reportFile)))
    SYSTEM.remove(catalog['courseData'])
    #repo.getAnalytics()

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


def convertHtmlToPdf(fileName):
    print ('test1')


# ===================================================

def createAnayticsNode(courseData) :
    reportAnalytics = {'lessonId': [], 'title': [], 'quesitonId': [], 'question': [], 'userId' : [], 'userName' : [], 'result': []}
    for lesson in courseData:
        reportAnalytics['lessonId'].append(lesson['lessonId'])
        reportAnalytics['title'].append(lesson['title'])
        if lesson['assessment'] :
            questions = lesson['assessment']['question']
            for question in questions :
                reportAnalytics['quesitonId'].append(str(question['@questionId']))
                reportAnalytics['question'].append(question['questionText']['p'])

    return reportAnalytics

# ===================================================    
init()
