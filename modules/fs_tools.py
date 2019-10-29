from sys import platform
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
        return None

def GetIdList(file: str):
    result = ReadAllFile(file)
    return '' if result == None else result.split('\n')

def GetConfigPath():
    path1 = './config/config.conf'
    if IsFileExists(path1):
        return path1

    if platform == "linux" or platform == "linux2":
        path2 = '~/.local/VKFriendOnlineWatcher/config.conf'
        path3 = '/etc/depish/VKFriendOnlineWatcher/config.conf'
        if IsFileExists(path2):
            return path2
        if IsFileExists(path3):
            return path3

    return None

    