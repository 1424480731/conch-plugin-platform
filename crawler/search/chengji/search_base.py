from env.exception import NetException,ProxyFailureException,NotHaveThatPageException,UnknowErrorException,TimeOutError
import requests
import random

class SearchBase:

    def __init__(self, headers_list=None, cookies_list=None, data=None):

        self.headers_list = headers_list
        self.cookies_list = cookies_list
        self.data = data

    def get(self, url, proxies=None):

        try:

            if self.headers_list:
                headers = self.headers_list[random.randint(0,len(self.headers_list)-1)]
            else:
                headers = None

            if not proxies:
                resp = requests.get(url=url, headers=headers,timeout=10)
            else:
                resp = requests.get(url=url, headers=headers,proxies=proxies,timeout=10)

        except BaseException as e:

            if str(e).find('Cannot connect to proxy') != -1:
                raise ProxyFailureException('Cannot connect to proxy')

            if str(e).find('connect: connection timed out') or str(e).find('Max retries exceeded with url'):
                raise TimeOutError('connect: connection timed out')

            raise e
        else:
            if resp.status_code == 403:
                raise ProxyFailureException('proxies failure ')

            if resp.status_code == 404:
                raise NotHaveThatPageException('not have this page')

            if resp.status_code == 502:
                raise TimeOutError('connection timed out')

        return resp



if __name__ == '__main__':

    url = "http://www.go007.com/aletai/habahexian/fangwuchuzu/p1/"
    for i in range(1):
        print(SearchBase().get(url).status_code)

