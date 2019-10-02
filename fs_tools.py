import os

# Return true if file exists
def IsFileExists(file):
    return os.path.exists(file) and os.path.isfile(file)

# Return true if folder exists
def IsFolderExists(folder):
    return os.path.exists(folder) and os.path.isdir(folder)

# Reading file to string and return his
def ReadAllFile(file: str):
    if IsFileExists(file):
        f = open(file, 'r')
        data = f.read()
        f.close()
        return data
    else:
        return ''

def GetIdList(file: str):
    return ReadAllFile(file).split('\n')
