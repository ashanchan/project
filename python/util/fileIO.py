#!/usr/bin/env python
import json
import codecs
#import util.log as LOGGER
# ===================================================


def writeJson(fileName, data):
    with codecs.open(fileName, 'w', encoding='utf-8') as fileStream:
        json.dump(data, fileStream, ensure_ascii=False, indent=4, sort_keys=True)

    validate(fileName)

# ===================================================


def validate(filename):
    with open(filename) as file:
        try:
            json.load(file)  # put JSON-data to a variable
        except json.JSONDecodeError:
            #LOGGER.show('error', ('# \t\t\tInvalid JSON \t\t\t\t\t\t#'))
            print('')
        else:
            #LOGGER.show('info', ('# \t\t\tValidiation Successful \t\t\t\t\t\t#'))
            print('')

# ===================================================


def readData(fileName):
    print(fileName)
    with open(fileName, 'r') as fp:
        obj = json.load(fp)
    return obj

# ===================================================
