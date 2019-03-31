import pkgImporter
import util.system as SYSTEM
import util.excel as EXCEL
import util.fileIO as FILE_IO
import util.log as LOGGER
import util.xml2Json as CONVERTOR

# ===================================================
import sys
import json
import codecs
# ===================================================


def init():
    catalog = readParam()
    if catalog['catalogId'] != None:
        generateReport(catalog)

# ===================================================


def readParam():
    SYSTEM.clear()
    LOGGER.show('info', ('#===============================================================================================#'))
    LOGGER.show('info', ('#\tStarting Reporting Process\t\t\t\t\t\t\t\t#'))
    LOGGER.show('info', ('#\t\tFor Processing System needs two files in data folder \t\t\t\t#'))
    LOGGER.show('info', ('#\t\t1. catelogId.xml\t\t [Eg. ./data/APL977-a80en.xml] \t\t\t#'))
    LOGGER.show('info', ('#\t\t2. catelogId-progress.json\t [Eg. ./data/APL977-a80en-progress.json] \t#'))
    LOGGER.show('info', ('#===============================================================================================#'))
    LOGGER.show('info', ('\n'))
    catalogId = 'APL977-a80en'
    catalogId = raw_input("Enter Course CatlogId without extension ")
    LOGGER.show('info', ('\n'))
    catalogId = catalogId.strip()
    courseXml = pkgImporter.getFileWithPath('data/'+catalogId+'.xml')
    courseData = pkgImporter.getFileWithPath('data/'+catalogId+'.json')
    courseProgress = pkgImporter.getFileWithPath('data/'+catalogId+'-progress.json')

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

    return {'catalogId': catalogId, 'courseData': courseData,  'courseProgress': courseProgress}

# ===================================================


def generateReport(catalog):
    lBreaker = ('======================================================================\n')
    qBreaker = ('-------------------------------------\n')
    strLine = ''

    assessedLesson = 0

    jsonCourseData = FILE_IO.readData(catalog['courseData'])['course']
    jsonProgressData = FILE_IO.readData(catalog['courseProgress'])
    courseData = getCourseData(jsonCourseData)
    passingPercent = jsonCourseData["assessment"]['@passingPercentage']

    for user in jsonProgressData:
        aCtr = 0
        score = 0
        tQctr = 0
        pQctr = 0
        plData = parseUserResult(user['coreLesson'])
        lessonStatus = plData['lessonStatus']

        strLine += (lBreaker)
        strLine += ('User Id\t\t\t : %s \t Name : %s\n' % (user['userId'], user['userName']))
        strLine += ('Course Name \t : %s \n' % (jsonCourseData['@catalogId']))
        strLine += ('Has Assessment \t : %s \n' % (str(jsonCourseData['assessment']['@lessonType'] == 'personalizedLearning')))
        strLine += ('Passing Percent\t : %s \n' % (passingPercent))
        strLine += ('Pooling \t\t : %s \n' % (jsonCourseData["assessment"]['@pooling']))
        strLine += ('Randomization \t : %s [question, option, all, none] \n' % (jsonCourseData["assessment"]['@randomize']))
        strLine += (lBreaker)

        testoutTaken = True if len(plData['testoutData']) > 0 else False

        if testoutTaken == True:
            for lesson in courseData:
                strLine += ('Lesson Id\t\t : %s \n' % (lesson['lessonId']))
                strLine += ('Lesson title\t : %s \n' % (lesson['title']))
                if lesson['assessment'] == None:
                    strLine += ('Assessment\t\t : Not Available - Mandatory Lesson \n')
                else:
                    questions = lesson['assessment']['question']
                    strLine += ('Assessment\t\t : Questions Available : [%d] \t Pooled : [%s] \n' % (len(questions), lesson['assessment']['@poolSize']))
                    assessmentData = normalizeData(plData['testoutData'][aCtr], len(questions))
                    qCtr = 0
                    assessedLesson += 1
                    for question in questions:
                        strLine += (qBreaker)
                        strLine += ('\t %d %s \n' % ((qCtr+1), question['questionText']['p']))
                        cCtr = 0
                        tQctr += 1
                        correctChoice = []
                        for choice in question['choice']:
                            isCorrect = choice['@isCorrect'] == 'true'
                            if isCorrect:
                                correctChoice.append(str(choice['@choiceId']))
                            strLine += ('\t\t %s\t%s \n' % (choice['@choiceId'], choice['#text']))
                            cCtr += 1
                        result = getResult(correctChoice, assessmentData[qCtr]['optionIdx'])
                        if result == 'Correct':
                            score += 1
                            pQctr += 1
                        elif result == 'Incorrect':
                            pQctr += 1

                        strLine += ('\t\t\tcorrect : %s \t selected : %s \t result : [%s]   \n' % (str(correctChoice), str(assessmentData[qCtr]['optionIdx']), result))
                        qCtr += 1

                    aCtr += 1

                strLine += (lBreaker)

        strLine += ('\n\n')
        strLine += ('\t\t*********************************************************\n')
        strLine += ('\t\t*                     SUMMARY                           *\n')
        strLine += ('\t\t*********************************************************\n')

        if testoutTaken == True:
            percObtained = score*100/pQctr

            status = 'NOT PASSED'
            if percObtained >= int(passingPercent):
                status = 'PASSED   '

            strLine += ('\t\t*\tTotal Question in the course\t : [%d] \t\t\t*\n' % (tQctr))
            strLine += ('\t\t*\t\t\t\tQuestions Offered\t : [%d] \t\t\t*\n' % (pQctr))
            strLine += ('\t\t*\t\t\t\tCorrect Answered\t : [%d]  \t\t\t*\n' % (score))
            strLine += ('\t\t*\t\t\t\tIncorrect Answered\t : [%d]  \t\t\t*\n' % (pQctr-score))
            strLine += ('\t\t*\tPassing Percent\t\t\t\t\t : [%s] \t\t\t*\n' % (passingPercent))
            strLine += ('\t\t*\tObtained Percent\t\t\t\t : [%d]  \t\t\t*\n' % (percObtained))
            strLine += ('\t\t*\tResult Status\t\t\t\t\t : [%s]\t\t*\n' % (status))
            strLine += ('\t\t*\tLast Question Attempted\t\t\t : [%s]\t\t\t\t*\n' % (plData['lastQuestion']))

        tstStatus = 'DONE' if plData['plStatus'].upper() == 'RESULT' else plData['plStatus'].upper()
        strLine += ('\t\t*\tTestout Status\t\t\t\t\t : [%s]   \t\t*\n' % (tstStatus))
        strLine += ('\t\t*\tLesson Status\t\t\t\t\t : [%s]  \t*\n' % (lessonStatus))
        strLine += ('\t\t*********************************************************\n')
        strLine += ('\n\n')

    reportFile = catalog['catalogId']
    reportFile = pkgImporter.getFileWithPath('data/'+reportFile+'-report.txt')

    FILE_IO.writeFile(reportFile, strLine)
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
        placeHolder = {'optionIdx': [], 'questionIdx': str(ctr+1)}
        mappedData.append(placeHolder)

    for data in testoutData:
        qIdx = data['questionIdx']
        for ctr in range(totalQuestion):
            cIdx = mappedData[ctr].get('questionIdx')
            if cIdx == qIdx:
                mappedData[ctr]['optionIdx'] = data['optionIdx']

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
