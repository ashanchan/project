import sys
import os
import shutil
# ===================================================


def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

# ===================================================


def exit():
    sys.exit(0)
# ===================================================


def makedirs(folder):
    os.makedirs(folder)
# ===================================================


def rmtree(folder):
    shutil.rmtree(folder)
# ===================================================


def remove(fileName):
    try:
        os.remove(fileName)
    except:
        print('')
# ===================================================


def talkBack(msg):
    os.system(msg)
    # os.system('say %s', %msg)

# ===================================================


def fileExist(fileName):
    return os.path.isfile(fileName)


# ===================================================
def acceptValidInput(prompt, inputRange):
    if len(inputRange) > 1:
        while True:
            val = raw_input(prompt)
            isInt = isInteger(val)
            if isInt :
                if int(val) not in inputRange:
                    sys.stdout.flush()
                else:
                    break
            else :    
                if val.lower() not in inputRange:
                    sys.stdout.flush()
                else:
                    break
    else:
        val = raw_input(prompt)


    if isInt:
        return int(val)
    else :    
        return val.lower()

# ===================================================

def isInteger(val) :
    try:
        val = int(val)
        return True
    except ValueError:
        return False

# ===================================================    
def getUniqueKeyFromList(list, key):
    unique_list = []
    for x in list:
        if x[key] not in unique_list:
            unique_list.append(x)

    return unique_list

# ===================================================


def isUnique(list, key, value):
    if len(list[key]) == 0:
        return True

    for x in list[key]:
        if x == value:
            #print('exist '+value)
            return False

    #print('not found '+value)
    return True

# ===================================================


def multikeysort(items, columns):
    from operator import itemgetter
    comparers = [((itemgetter(col[1:].strip()), -1) if col.startswith('-') else
                  (itemgetter(col.strip()), 1)) for col in columns]

    def comparer(left, right):
        for fn, mult in comparers:
            result = cmp(fn(left), fn(right))
            if result:
                return mult * result
        else:
            return 0
    return sorted(items, cmp=comparer)

# ===================================================


def compressFolder(sourceDir, targetFileName):
    shutil.make_archive(targetFileName, 'zip', sourceDir)
