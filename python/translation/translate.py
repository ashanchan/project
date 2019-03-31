import pkgImporter
import util.system as SYSTEM
import util.system as SYSTEM
import util.excel as EXCEL
import util.fileIO as FILE_IO
import util.log as LOGGER

# ===================================================


def init():
    SYSTEM.clear()
    LOGGER.show('info', ('#=======================================================================================#'))
    LOGGER.show('info', ('# Starting Translation Process\t\t\t\t\t\t\t\t#'))
    pointer = ['data/resourceBundle.xlsx', 'data/fluidx_constant_key.xlsx', 'data/sample_resource.xlsx', 'data/sample_constant_key.xlsx']

    resourceUrl = pkgImporter.getFileWithPath(pointer[0])
    constantUrl = pkgImporter.getFileWithPath(pointer[1])

    resourceDataObj = EXCEL.readData(resourceUrl)
    constantDataObj = EXCEL.readData(constantUrl)
    LOGGER.show('info', ('# \tFile Name : %s \t\t>> Total Rows read : %d \t#' % (resourceUrl, len(resourceDataObj['data']))))
    LOGGER.show('info', ('# \tFile Name : %s \t>> Total Rows read : %d \t#' % (constantUrl, len(constantDataObj['data']))))
    LOGGER.show('info', ('# \tCreating References \t\t\t\t\t\t\t\t#'))
    if len(resourceDataObj) != 0:
        mappedRef = createKeyReferences(resourceDataObj['data'], constantDataObj['data'])
        transRef = createLanguageMapping(mappedRef['mapReference'], resourceDataObj['data'], constantDataObj['data'])
        createFolders(transRef['language'])
        generateTranslation(transRef, mappedRef)
        LOGGER.show('info', ('# Exiting Translation Process\t\t\t\t\t\t\t\t#'))
        LOGGER.show('info', ('#=======================================================================================#'))

    LOGGER.reset()

# ===================================================


def createKeyReferences(resourceData, constantData):
    rIdx = 0
    cIdx = 0
    mapReference = []
    notMappedFileName = pkgImporter.getFileWithPath('not_mapped.txt')
    notMapped = 0
    LOGGER.show('info', ('# \t\tConstant Mappings    \t\t\t\t\t\t\t#'))
    SYSTEM.remove(notMappedFileName)

    for constant in constantData:
        row_data = {}
        rIdx = 0
        mapped = False
        for keys in resourceData:
            if constant['Mapped_Key'] == keys['key']:
                row_data = {'rIdx': rIdx, 'cIdx': cIdx}
                mapReference.append(row_data)
                mapped = True
                continue
            else:
                rIdx += 1

        if mapped == False:
            row_data = {'rIdx': -1, 'cIdx': cIdx}
            notMapped += 1
            with open(notMappedFileName, 'a') as the_file:
                the_file.write(str(constant['Mapped_Key'])+'\n')
            mapReference.append(row_data)

        cIdx += 1

    return {'mapReference': mapReference, 'notMapped': notMapped}

# ===================================================


def createLanguageMapping(mappedRef, resourceData, constantData):
    language = list(resourceData[0])
    language.sort()
    transReference = {}
    language.remove('usage')
    language.remove('key')

    LOGGER.show('info', ('# \t\tLanguage Mappings    \t\t\t\t\t\t\t#'))
    for lang in language:
        lang_data = {}
        for map in mappedRef:
            if map['rIdx'] == - 1:
                lang_data.update({str(constantData[map['cIdx']]['Constant_Key']): constantData[map['cIdx']]['Mapped_Key']})
            else:
                lang_data.update({str(constantData[map['cIdx']]['Constant_Key']): resourceData[map['rIdx']][lang]})
            transReference.update({lang: lang_data})

    return {'language': language, 'data': transReference}

# ===================================================


def createFolders(language):
    LOGGER.show('info', ('# \tCreating Translation folder  \t\t\t\t\t\t\t#'))

    try:
        SYSTEM.rmtree('./messages')
    except:
        LOGGER.show('warning', ('no dir found'))
    finally:
        for lang in language:
            folder = './messages/'+str(lang)
            SYSTEM.makedirs(folder)
# ===================================================


def generateTranslation(transRef, mappedRef):
    idx = 0
    for lang in transRef['language']:
        fileName = pkgImporter.getFileWithPath('./messages/'+str(lang)+'/message.json')
        LOGGER.show('info', ('# \t\tCreating file %d %s  \t\t\t\t#' % (idx, fileName)))
        idx += 1
        FILE_IO.writeJson(fileName, transRef['data'][lang])

    LOGGER.show('info', ('# \tTranslation Generated for %d keys \t\t\t\t\t\t#' % (len(transRef['data']['en']))))
    LOGGER.show('info', ('# \t\tMapped for %d keys \t\t\t\t\t\t\t#' % (len(transRef['data']['en']) - mappedRef['notMapped'])))
    LOGGER.show('info', ('# \t\tNot Mapped for %d keys \t\t\t\t\t\t\t#' % mappedRef['notMapped']))
    LOGGER.show('info', ('# \tTranslation successful for %d files \t\t\t\t\t\t#' % len(transRef['language'])))


# ===================================================
init()
# ===================================================