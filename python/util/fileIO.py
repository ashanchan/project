import json
import codecs
import boto3
import util.log as LOGGER
# ===================================================


def writeJson(fileName, data):
    with codecs.open(fileName, 'w', encoding='utf-8') as fileStream:
        json.dump(data, fileStream, ensure_ascii=False,
                  indent=4, sort_keys=True)

    validate(fileName)

# ===================================================


def writeJs(fileName, data):
    strLine = ''
    strLine += '(function(ns, window) {\n'
    strLine += '\tvar messages = new Object();\n'

    sortedData = sorted(data)

    for line in sortedData:
        strLine += ('\tmessages["%s"] = "%s";\n' % (line, data[line]))

    strLine += '\tns.data.commonMessages = messages;\n'
    strLine += '\ttry{\n'
    strLine += '\t\tif(module && module.exports)module.exports = messages;\n'
    strLine += '\t}catch(e){}\n'
    strLine += '})(window.com.lrn.courseware, window)'

    print(fileName)
    with codecs.open(fileName, "w", encoding="utf-8") as my_file:
        my_file.write(strLine)


# ===================================================


def validate(filename):
    with open(filename) as file:
        try:
            json.load(file)  # put JSON-data to a variable
        except json.JSONDecodeError:
            LOGGER.show('error', ('\t\t\tInvalid JSON '))
        else:
            LOGGER.show('none', ('\t\t\tValidiation Successful '))


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


def downloadFromS3Bucket(bucketName, fileName, targetName):
    s3 = boto3.client('s3', aws_access_key_id='AKIAIBF2BWIKB6UA2TQA', aws_secret_access_key='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')
    s3.download_file(bucketName, fileName, targetName)

# ===================================================


def upload2S3Bucket(bucketName, fileName, targetName):
    s3 = boto3.resource('s3')
    data = open(fileName, 'rb')
    s3.Bucket(bucketName).put_object(Key=targetName, Body=data)

# ===================================================
