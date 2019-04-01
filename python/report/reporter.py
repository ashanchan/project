#!/usr/bin/env python
import pkgImporter
import util.system as SYSTEM
import util.excel as EXCEL
import util.fileIO as FILE_IO
import util.log as LOGGER
import util.xml2Json as CONVERTOR
# ===================================================


class userData:

    def __init__(self, header, body, footer, mode):
        self.header = header
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
    summary = 'd'

    catalogId = SYSTEM.acceptValidInput('Enter Valid CatlogueId : ', [])
    summaryMode = SYSTEM.acceptValidInput('Report Mode : Detailed / Compact / Summary [D/C/S] : ', ['D', 'C', 'S', 'd', 'c', 's'])

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
    lBreaker = ('======================================================================')
    qBreaker = ('-------------------------------------')
    printLine = ''
    assessedLesson = 0

    jsonCourseData = FILE_IO.readData(catalog['courseData'])['course']
    jsonProgressData = EXCEL.readData(catalog['courseProgress'])
    courseData = getCourseData(jsonCourseData)
    passingPercent = jsonCourseData["assessment"]['@passingPercentage']

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

        reportHeader.append(lBreaker)
        reportHeader.append('User Id\t\t\t : %s \t Name : %s %s' % (user['USER_ID'], user['FIRSTNAME'], user['LASTNAME']))
        reportHeader.append('Course Name \t : %s ' % (jsonCourseData['@catalogId']))
        reportHeader.append('System Id \t\t : %s ' % (jsonCourseData['@systemId']))
        reportHeader.append('Has Assessment \t : %s ' % (str(jsonCourseData['assessment']['@lessonType'] == 'personalizedLearning')))
        reportHeader.append('Pooling \t\t : %s ' % (jsonCourseData["assessment"]['@pooling']))
        reportHeader.append('Randomized on \t : %s ' % (jsonCourseData["assessment"]['@randomize']))
        reportHeader.append(lBreaker)
        # =========
        testoutTaken = True if len(plData['testoutData']) > 0 else False

        if testoutTaken == True:
            for lesson in courseData:
                reportBody.append('Lesson Id\t\t : %s ' % (lesson['lessonId']))
                reportBody.append('Lesson title\t : %s ' % (lesson['title']))
                lCtr += 1
                if lesson['assessment'] == None:
                    reportBody.append('Assessment\t\t : Not Available - Mandatory Lesson ')
                else:
                    correctCtr = 0
                    questions = lesson['assessment']['question']
                    assessmentData = normalizeData(plData['testoutData'][aCtr], len(questions))
                    poolSize = int(lesson['assessment']['@poolSize'])
                    reportBody.append('Assessment\t\t : Questions Available : [%d] \t Pooled : [%s] ' % (len(questions), poolSize))

                    reportCompact.append('Lesson title\t : %s ' % (lesson['title']))
                    reportCompact.append('\tQuestions\t : Available\t : [%d] \t Pooled\t\t : [%s] ' % (len(questions), poolSize))

                    qCtr = 0
                    assessedLesson += 1
                    for question in questions:
                        reportBody.append(qBreaker)
                        reportBody.append('\t %d %s ' % ((qCtr+1), question['questionText']['p']))

                        cCtr = 0
                        tQctr += 1
                        correctChoice = []
                        for choice in question['choice']:
                            isCorrect = choice['@isCorrect'] == 'true'
                            if isCorrect:
                                correctChoice.append(str(choice['@choiceId']))

                            reportBody.append('\t\t %s\t%s ' % (choice['@choiceId'], choice['#text']))

                            cCtr += 1

                        result = getResult(correctChoice, assessmentData[qCtr]['optionIdx'])

                        if result == 'Correct':
                            score += 1
                            mCtr += 1
                            correctCtr += 1
                        elif result == 'Incorrect':
                            mCtr += 1

                        sOption = []
                        for s in assessmentData[qCtr]['optionIdx']:
                            sOption.append(str(s))

                        reportBody.append('\t\t\tcorrect : %s \t selected : %s \t result : [%s]   ' % (str(correctChoice), str(sOption), result))
                        qCtr += 1

                    aCtr += 1
                    reportCompact.append('\t\t\t\t : Correct\t\t : [%s] \t Incorrect\t : [%s]' % (correctCtr, (poolSize - correctCtr)))
                    reportCompact.append('')

                reportBody.append(lBreaker)
        reportCompact.append(lBreaker)
        reportFooter.append('')
        reportFooter.append('\t\t*********************************************************')
        reportFooter.append('\t\t\t                    SUMMARY ')
        reportFooter.append('\t\t*********************************************************')

        if testoutTaken == True:
            percObtained = score*100/mCtr

            status = 'NOT PASSED'
            if percObtained >= int(passingPercent):
                status = 'PASSED   '

            reportFooter.append('\t\t*\tTotal Lesson in the course\t\t : [%d] \t\t\t\t*' % (lCtr))
            reportFooter.append('\t\t*\t\tTestout Lesson   \t\t\t : [%d] \t\t\t\t*' % (aCtr))
            reportFooter.append('\t\t*\t\tMandatory Lesson \t\t\t : [%d] \t\t\t\t*' % (lCtr-aCtr))
            reportFooter.append('\t\t*\tTotal Question in the course\t : [%d] \t\t\t*' % (tQctr))
            reportFooter.append('\t\t*\t\t\t\tQuestions Offered\t : [%d] \t\t\t*' % (mCtr))
            reportFooter.append('\t\t*\t\t\t\tCorrect Answered\t : [%d]  \t\t\t*' % (score))
            reportFooter.append('\t\t*\t\t\t\tIncorrect Answered\t : [%d]  \t\t\t*' % (mCtr-score))
            reportFooter.append('\t\t*\tPassing Percent\t\t\t\t\t : [%s] \t\t\t*' % (passingPercent))
            reportFooter.append('\t\t*\tObtained Percent\t\t\t\t : [%d]  \t\t\t*' % (percObtained))
            reportFooter.append('\t\t*\tResult Status\t\t\t\t\t : [%s]\t\t*' % (status))
            reportFooter.append('\t\t*\tLast Question Attempted\t\t\t : [%s]\t\t\t\t*' % (plData['lastQuestion']))

        tstStatus = 'DONE' if plData['plStatus'].upper() == 'RESULT' else plData['plStatus'].upper()

        reportFooter.append('\t\t*\tTestout Status\t\t\t\t\t : [%s]    \t\t*' % (tstStatus))
        reportFooter.append('\t\t*\tLesson Status\t\t\t\t\t : [%s] \t\t*' % (lessonStatus))
        reportFooter.append('\t\t*********************************************************')
        reportFooter.append('')

        # ======
        if catalog['summaryMode'] == 'c':
            reportBody = reportCompact

        repo = userData(reportHeader, reportBody, reportFooter, catalog['summaryMode'])
        printLine += repo.getReport()

    reportFile = catalog['catalogId']
    reportFile = pkgImporter.getFileWithPath('data/'+reportFile+'-report.txt')

    FILE_IO.writeFile(reportFile, printLine)
    LOGGER.show('info', ('Report created  %s ' % (reportFile)))
    SYSTEM.remove(catalog['courseData'])

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
            return 'Correct'
        else:
            return 'Incorrect'

# ===================================================


init()
