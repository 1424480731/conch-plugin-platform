
class NetException(BaseException):
    pass

class MongoDbDisconn(BaseException):
    pass

class MongoTableDisconn(BaseException):
    pass

class KeyAddedException(BaseException):
    pass

class ProxyFailureException(BaseException):
    pass

class NotHaveThatPageException(BaseException):
    pass

class UnknowErrorException(BaseException):

    def __init__(self,str):
        super().__init__(str)

class TimeOutError(BaseException):
    pass

class ParseFailureException(BaseException):
    pass



if __name__ == '__main__':

    raise UnknowErrorException()