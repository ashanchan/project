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
    catalogId = readParam()
    #catalogId = 'APL977-a80en'
    if catalogId != None:
        generateReport(catalogId)

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
    catalogId = raw_input("Enter Course CatlogId without extension ")
    LOGGER.show('info', ('\n'))
    catalogId = catalogId.strip()

    isExist1 = SYSTEM.fileExist('./data/'+catalogId+'.xml')
    if isExist1 == False:
        LOGGER.show('error', ('File %s does not exists' % ('./data/'+catalogId+'.xml')))

    isExist2 = SYSTEM.fileExist('./data/'+catalogId+'-progress.json')
    if isExist2 == False:
        LOGGER.show('error', ('File %s does not exists' % ('./data/'+catalogId+'-progress.json')))

    if isExist1 == True and isExist2 == True:
        CONVERTOR.convert('./data/'+catalogId)
    else:
        catalogId = None

    return catalogId

# ===================================================


def generateReport(catalogId):
    lBreaker = ('======================================================================\n')
    qBreaker = ('-------------------------------------\n')
    strLine = ''
    aCtr = 0
    score = 0
    tQctr = 0
    pQctr = 0
    assessedLesson = 0

    jsonCourseData = FILE_IO.readData('./data/'+catalogId+'.json')['course']
    jsonProgressData = FILE_IO.readData('./data/'+catalogId+'-progress.json')
    courseData = getCourseData(jsonCourseData)
    passingPercent = jsonCourseData["assessment"]['@passingPercentage']
    testoutTaken = False
    lessonStatus = 'COMPLETED'
    for user in jsonProgressData:
        plData = parseUserResult(user['coreLesson'])
        strLine += (lBreaker)
        strLine += ('User Id\t\t\t : %s \t Name : %s\n' % (user['userId'], user['userName']))
        strLine += ('Course Name \t : %s \n' % (jsonCourseData['@catalogId']))
        strLine += ('Has Assessment \t : %s \n' % (str(jsonCourseData['assessment']['@lessonType'] == 'personalizedLearning')))
        strLine += ('Passing Percent\t : %s \n' % (passingPercent))
        strLine += ('Pooling \t\t : %s \n' % (jsonCourseData["assessment"]['@pooling']))
        strLine += ('Randomization \t : %s [question, option, all, none] \n' % (jsonCourseData["assessment"]['@randomize']))
        strLine += (lBreaker)

        if plData['plStatus'] == 'done':
            testoutTaken = True

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
        if percObtained >= passingPercent:
            status = 'PASSED'

        strLine += ('\t\t*\tTotal Question in the course\t : [%d] \t\t\t*\n' % (tQctr))
        strLine += ('\t\t*\t\t\t\tQuestions Offered\t : [%d] \t\t\t*\n' % (pQctr))
        strLine += ('\t\t*\t\t\t\tCorrect Answered\t : [%d]  \t\t\t*\n' % (score))
        strLine += ('\t\t*\t\t\t\tIncorrect Answered\t : [%d]  \t\t\t*\n' % (pQctr-score))
        strLine += ('\t\t*\tPassing Percent\t\t\t\t\t : [%s] \t\t\t*\n' % (passingPercent))
        strLine += ('\t\t*\tObtained Percent\t\t\t\t : [%d]  \t\t\t*\n' % (percObtained))
        strLine += ('\t\t*\tResult Status\t\t\t\t\t : [%s]  \t*\n' % (status))
    else:
        strLine += ('\t\t*\tTestout Status\t\t\t\t\t : [%s]   \t\t*\n' % (plData['plStatus'].upper()))

    strLine += ('\t\t*\tLesson Status\t\t\t\t\t : [%s]  \t*\n' % (lessonStatus))
    strLine += ('\t\t*********************************************************\n')
    strLine += ('\n\n')

    FILE_IO.writeFile('./data/'+catalogId+'-report.txt', strLine)

    LOGGER.show('info', ('Report created  %s ' % ('./data/'+catalogId+'-report.txt')))


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
    tempPlData = coreLesson.split('PL.')[1]
    rawPlData = tempPlData.split('|')
    plStatus = rawPlData[0]
    rawPlQuestion = rawPlData[1]
    mappedQuestion = rawPlQuestion.split(',')
    optionIterator = 2
    testoutData = []

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
    return {'plStatus': plStatus, 'testoutData': testoutData}


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