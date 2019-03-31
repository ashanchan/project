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
    except :
        print('')
# ===================================================

def talkBack(msg):
    os.system(msg)
    #os.system('say %s', %msg)

# ===================================================

def fileExist(fileName):
    return os.path.isfile(fileName)
    
    