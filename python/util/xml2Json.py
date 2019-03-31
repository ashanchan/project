import json
import codecs
import xmltodict
# ===================================================


def convert(fileName):
    with open(fileName+'.xml') as fd:
        rawData = xmltodict.parse(fd.read())

    with codecs.open(fileName+'.json', 'w', encoding='utf-8') as fileStream:
        json.dump(rawData, fileStream, ensure_ascii=False, indent=4, sort_keys=True)
# ===================================================
