import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir) 

def getFileWithPath(fileName) :
    dirname = os.path.dirname(__file__)
    return os.path.join(dirname, fileName)

def getLenOfDir () :
    return len(os.path.dirname(__file__))
    