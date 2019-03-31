import json
import codecs
import xmltodict
# ===================================================


def convert(source, target):
    with open(source) as fd:
        rawData = xmltodict.parse(fd.read())

    with codecs.open(target, 'w', encoding='utf-8') as fileStream:
        json.dump(rawData, fileStream, ensure_ascii=False, indent=4, sort_keys=True)
# ===================================================
