import os
import sys
import inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# ===================================================


def getDirPath():
    return os.path.dirname(__file__)
# ===================================================


def getFileWithPath(fileName):
    return os.path.join(getDirPath(), fileName)

# ===================================================


def getLenOfDir():
    return len(os.path.dirname(__file__))
