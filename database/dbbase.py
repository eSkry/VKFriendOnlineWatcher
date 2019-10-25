from abc import ABCMeta, abstractmethod, abstractproperty

class DbBase:    
    @abstractmethod
    def SetUserOnline(self, user_id, timestamp):
        pass
    
    @abstractmethod
    def SetUserOffline(self, user_id, timestamp):
        pass

    @abstractmethod
    def GetUserLastState(self, user_id):
        pass

    @abstractmethod
    def IsUSerExists(self, user_id):
        pass
    
    @abstractmethod
    def AddUser(self, user_id, full_name):
        pass
    
    @abstractmethod
    def GetConnection(self):
        pass