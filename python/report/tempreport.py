import sys
import json
import codecs
# ===================================================


def init():
    lBreaker = ('======================================================================\n')
    qBreaker = ('-------------------------------------\n')
    strLine = ''
    aCtr = 0
    score = 0
    assessedLesson = 0
    jsonCourseData = readData('./APL977.json')['course']
    jsonProgressData = readData('./progress.json')
    courseData = getCourseData(jsonCourseData)

    for user in jsonProgressData:
        plData = parseUserResult(user['coreLesson'])
        strLine += (lBreaker)
        strLine += ('User Id\t\t\t : %s \t Name : %s\n' % (user['userId'], user['userName']))
        strLine += ('Course Name \t : %s \n' % (jsonCourseData['@catalogId']))
        strLine += ('Has Assessment \t : %s \n' % (str(jsonCourseData['assessment']['@lessonType'] == 'personalizedLearning')))
        strLine += ('Passing Percent\t : %s \n' % (jsonCourseData["assessment"]['@passingPercentage']))
        strLine += ('Pooling \t\t : %s \n' % (jsonCourseData["assessment"]['@pooling']))
        strLine += ('Randomization \t : %s [question, option, all, none] \n' % (jsonCourseData["assessment"]['@randomize']))
        strLine += (lBreaker)

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
                    correctChoice = []
                    for choice in question['choice']:
                        isCorrect = choice['@isCorrect'] == 'true'
                        if isCorrect:
                            correctChoice.append(str(choice['@choiceId']))
                        strLine += ('\t\t %s\t%s \n' % (choice['@choiceId'], choice['#text']))
                        cCtr += 1
                    result = getResult(correctChoice, assessmentData[qCtr]['optionIdx'])
                    if result == 'Correct' :
                        score +=1
                    strLine += ('\t\t\tcorrect : %s \t selected : %s \t result : [%s]   \n' % (str(correctChoice), str(assessmentData[qCtr]['optionIdx']), result))
                    qCtr += 1

                aCtr += 1

            strLine += (lBreaker)

    print ('what is the score %d %d'  %(score, assessedLesson ))
    writeFile('report.txt', strLine)


# ===================================================

def readData(fileName):
    with open(fileName, 'r') as fp:
        obj = json.load(fp)
    return obj

# ===================================================


def writeFile(fileName, data):
    file = codecs.open(fileName, 'w', 'utf-8')
    file.write(data)
    file.close()
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

    for x in mappedData:
        print('%s \t : %s' % (x['questionIdx'], x['optionIdx']))

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
        else :
            return 'Incorrect'
# ===================================================

init()
