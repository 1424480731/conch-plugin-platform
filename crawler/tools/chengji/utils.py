import requests,socket,time
import os

def div_array(array_list,group_size):
    len_array = len(array_list)
    mid_array = len_array//2
    if len_array<=group_size:
        return [array_list]
    left = div_array(array_list[:mid_array],group_size)
    right=div_array(array_list[mid_array:],group_size)
    return left+right

def write_to_disk(path, filename, data):
    path_c = os.path.join(path, filename)
    with open(path_c,'wb') as fp:
        fp.write(data)


class ProxyTool:

    def __init__(self):

        self.white_blank_url = 'http://webapi.jghttp.golangapi.com/index/index/save_white?neek=12182&appkey=5a24a50c10c30f388ab26a4d286cbbe7&white={0}'
        self.get_proxy_api = 'http://d.jghttp.golangapi.com/getip?num=1&type=2&pro=&city=0&yys=0&port=1&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
        self.get_proxy_apis = 'http://d.jghttp.golangapi.com/getip?num={0}&type=2&pro=&city=0&yys=0&port=11&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='


    def add_to_white_list(self):

        for i in range(3):
            try:
                ip = requests.get('http://httpbin.org/get').json().get("origin")
                ret = requests.get(self.white_blank_url.format(ip)).json()
                if ret.get('success') or ret.get('code') == 115:
                    print('added to white blank list:',True)
                else:
                    print('added to white blank list:',False)
                return None
            except:
                pass

    def get_proxies(self):

        for i in range(3):
            ret = requests.get(self.get_proxy_api.format(1)).json()
            if ret.get('success'):
                ip = ret.get('data')[0].get('ip')
                port = ret.get('data')[0].get('port')
                proxies = {
                    'http':'http://'+ip+':'+str(port),
                    'https':'https://'+ip+':'+str(port),
                }
                return proxies
            else:
                time.sleep(3)





if __name__ == '__main__':

    pt = ProxyTool()
    # pt.get_proxies()
    # pt.get_proxies()
    proxies = pt.get_proxies()
    print(proxies)
    # proxies = {'http': 'http://117.69.149.118:4527', 'https': 'https://117.69.149.118:4527'}
    # proxies = {'https': 'https://123.119.35.9:45811', 'http': 'http://123.119.35.9:45811'}
    # from crawler.parse.chengji.parse_chengji_fc import ChengJiFangChan
    # cjfc = ChengJiFangChan()
    headers = {
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16'
    }

    res = requests.get('http://www.go007.com/aletai/fangwuchuzu/2125895a48276fba.htm',proxies=proxies,headers=headers).text
    # res = requests.get('http://www.go007.com/gaotangxian/fangwuchuzu/7f91265718c8373d.htm',proxies=proxies,headers=headers)
    # print(requests.get('http://httpbin.org/get').text)
    #
    from lxml import etree
    e = etree.HTML(res)
    phone = e.xpath('.//input[@id="hfPhone"]/@value')[0]
    print(phone)
    # print(res.status_code,cjfc.parse_zf_link(res.text))
    # print(len(cjz.generation_group()))


