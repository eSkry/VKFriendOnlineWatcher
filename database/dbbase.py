import os


class DbBase:
    def __init__(self):
        pass

    def SetUserOnline(self, user_id, timestamp):
        pass
    
    def SetUserOffline(self, user_id, timestamp):
        pass

    def GetUserLastState(self, user_id):
        pass

    def IsUSerExists(self, user_id):
        pass

    def AddUser(self, user_id, full_name):
        pass

    def GetConnection(self):
        pass