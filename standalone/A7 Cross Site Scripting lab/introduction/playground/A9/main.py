import datetime


# f = open('test.log', 'a') --> use this file to log
class Log:
    def __init__(self,request):
        self.request = request
        
    def info(self,msg):
        pass
    
    def warning(self,msg):
        pass

    def error(self,msg):
        pass