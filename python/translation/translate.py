#!/usr/bin/python3
import pkgImporter
import util.system as SYSTEM
import util.system as SYSTEM
import util.excel as EXCEL
import util.fileIO as FILE_IO
import util.log as LOGGER
lineBreak = SYSTEM.repeat2Length('=', 130) 
s3Bucket = 'aws-ashtra-translation'
# ===================================================


def init():
    SYSTEM.clear()
    createDataFolder()
    pointer = ['data/ResourceBundle.xlsx', 'data/fluidx_constant_key.xlsx']

    MODE = readParam()
    resourceDataObj = readExcelData(pointer[0])
    constantDataObj = readExcelData(pointer[1])

    LOGGER.show('info', (lineBreak))
    LOGGER.show('info', ('\tFile Name : %s      >> Total Rows read : %d ' % (pointer[0], len(resourceDataObj['data']))))
    LOGGER.show('info', ('\tFile Name : %s >> Total Rows read : %d ' % (pointer[1], len(constantDataObj['data']))))
    LOGGER.show('info', (lineBreak))    
    LOGGER.show('info', ('\tCreating References '))

    if len(resourceDataObj) != 0:
        mappedRef = createKeyReferences(resourceDataObj['data'], constantDataObj['data'])
        transRef = createLanguageMapping(mappedRef['mapReference'], resourceDataObj['data'], constantDataObj['data'])
        createFolders(transRef['language'])
        generateTranslation(transRef, mappedRef, MODE)
        copy2Bucket()
        LOGGER.show('info', ('\tExiting Translation Process'))
        LOGGER.show('info', (lineBreak))

    LOGGER.reset()

# ===================================================


def createDataFolder():
    rootDir = pkgImporter.getDirPath()
    tempFolder = ['/messages', '/data']

    for folder in tempFolder:
        try:
            SYSTEM.rmtree(rootDir+folder)
        except:
            LOGGER.show('warning', ('no dir found'))
        finally:
            SYSTEM.makedirs(rootDir+folder)


# ===================================================
def readParam():
    SYSTEM.clear()
    LOGGER.show('info', (lineBreak))
    LOGGER.show('info', ('\tStarting Translation Process'))
    LOGGER.show('info', ('\t\tFor Processing, System needs two files in aws s3 bucket'))
    LOGGER.show('info', ('\t\t1. s3/project-translation/data/ResourceBundle.xlsx\t\t [Eg. latest copied from the Perforce]'))
    LOGGER.show('info', ('\t\t2. s3/project-translation/data/fluidx_constant_key.xlsx\t\t [Eg. Mapped constants lists]'))
    LOGGER.show('info', (lineBreak))
    LOGGER.show('info', (''))
    mode = SYSTEM.acceptValidInput('For Fluidx : 2 or 3 [2/3] : ', [2, 3])
    LOGGER.show('info', (''))
    LOGGER.show('info', (lineBreak))
    LOGGER.show('info', ('\tConnecting aws server... Please wait...'))
    
    return mode
# ===================================================


def readExcelData(pointer):
    fileName = pkgImporter.getFileWithPath(pointer)
    FILE_IO.downloadFromS3Bucket(s3Bucket, pointer, fileName)
    return EXCEL.readData(fileName)
# ===================================================


def createKeyReferences(resourceData, constantData):
    rIdx = 0
    cIdx = 0
    mapReference = []
    notMappedFileName = pkgImporter.getFileWithPath('not_mapped.txt')
    notMapped = 0
    LOGGER.show('info', ('\t\tConstant Mappings    '))
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

    LOGGER.show('info', ('\t\tLanguage Mappings    '))
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
    LOGGER.show('info', (lineBreak))
    LOGGER.show('info', ('\tCreating Translation folder  '))
    rootDir = pkgImporter.getDirPath()

    try:
        SYSTEM.rmtree(rootDir+'/messages')
    except:
        LOGGER.show('warning', ('no dir found'))
    finally:
        for lang in language:
            folder = rootDir+'/messages/'+str(lang)
            SYSTEM.makedirs(folder)

# ===================================================


def generateTranslation(transRef, mappedRef, MODE):
    idx = 0
    for lang in transRef['language']:
        fileName = pkgImporter.getFileWithPath('messages/'+str(lang)+'/message.')
        fileName = fileName+'js' if MODE == 2 else fileName+'json'
        LOGGER.show('none', ('\t\tCreating file %d %s  ' % (idx, fileName)))
        idx += 1

    LOGGER.show('info', ('\tTranslation Generated for %d keys ' % (len(transRef['data']['en']))))
    LOGGER.show('info', ('\t\tMapped for %d keys ' % (len(transRef['data']['en']) - mappedRef['notMapped'])))
    LOGGER.show('info', ('\t\tNot Mapped for %d keys ' % mappedRef['notMapped']))
    LOGGER.show('info', ('\tTranslation successful for %d files ' % len(transRef['language'])))

    compressFolder = pkgImporter.getDirPath()+'/messages'

    LOGGER.show('info', (lineBreak))
    LOGGER.show('info', ('\tArchiving  %d files to %s.zip ' % (len(transRef['language']), compressFolder)))
    SYSTEM.compressFolder(compressFolder, compressFolder)

# ===================================================


def copy2Bucket():
    notMappedFileName = pkgImporter.getFileWithPath('not_mapped.txt')
    targetFileName = pkgImporter.getDirPath()+'/messages.zip'

    LOGGER.show('info', (lineBreak))
    LOGGER.show('info', ('\tCopying file to aws bucket  %s  ' % (notMappedFileName)))
    FILE_IO.upload2S3Bucket(s3Bucket, notMappedFileName, 'output/not_mapped.txt')
    LOGGER.show('info', ('\tCopying file to aws bucket  %s  ' % (targetFileName)))
    FILE_IO.upload2S3Bucket(s3Bucket, targetFileName, 'output/messages.zip')
    LOGGER.show('info', ('\tCleaning Repositories'))
    SYSTEM.rmtree(pkgImporter.getDirPath()+'/messages')
    SYSTEM.rmtree(pkgImporter.getDirPath()+'/data')


# ===================================================
init()
# ===================================================
