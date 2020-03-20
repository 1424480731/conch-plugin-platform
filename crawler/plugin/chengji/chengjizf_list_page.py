from crawler.search.chengji.search_chuzu import SearchChuzu
from crawler.parse.chengji.parse_chengji_fc import ChengJiFangChan
from database.mongo import MongoChengJiApi
from crawler.tools.chengji.generation import Generation
from crawler.tools.chengji.utils import div_array,ProxyTool
from crawler.tools.chengji.threading_m import ThreadPool
from env.exception import ProxyFailureException,UnknowErrorException,TimeOutError,NotHaveThatPageException
from env.params import chengji_params
import time,random,threading
index = 0
lock = threading.RLock()


def run():
    cjz = ChengJianZuFangList(chengji_params)
    crawl_all_link(cjz, chengji_params)

# -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
class ChengJianZuFangList:

    def __init__(self,params):

        self.search = SearchChuzu(params)
        self.zf_parse = ChengJiFangChan()
        self.mongo_client = MongoChengJiApi()
        self.result = {}
        self.generation = Generation()
        self.pool = ThreadPool()
        self.proxies_tools = ProxyTool()

    def generation_page_group(self):

        self.generation.generation_fc_all_task()
        list_g = self.generation.generation_fc_task_by_category(['fangwuchuzu'])
        list_page = self.generation.generation_page_url(list_g)
        list_g_group =  div_array(list_page,group_size = 1000)
        return list_g_group

    def crawl_page_group(self,list_page):

        global index,index_2
        proxies = self.proxies_tools.get_proxies()

        for url in list_page:

            cond = {'road_sign': url.split('/')[-3]}
            if self.mongo_client.trim_to_fix_size(cond):
                for tr in range(2):

                    try:
                        time.sleep(random.randint(1,5))
                        res = self.search.crawl_detail_html_urls(url,proxies=proxies)
                        link_list = self.zf_parse.parse_zf_link(res)
                        data = []
                        for link in link_list:
                            data.append({'key': link, 'res': ''})
                        self.mongo_client.update_detail_link({'url': url, 'data': data})
                        lock.acquire()
                        index += 1
                        lock.release()
                        print(threading.current_thread().name,'<--',index ,':',cond,url,res.find('免费发布信息'),data)
                        if not data:
                            break

                    except (ProxyFailureException,TimeOutError) as e:
                        print(threading.current_thread().name,'<--',url,e,proxies)
                        proxies = self.proxies_tools.get_proxies()
                    except (UnknowErrorException,NotHaveThatPageException) as e:
                        print(threading.current_thread().name,'<--',url,e)
                    except BaseException as e:
                        print(threading.current_thread().name,'<--',url,e)



def crawl_all_link(cjz_obj,cj_params):

    list_page_group = cjz_obj.generation_page_group()
    group_th = [threading.Thread(target=ChengJianZuFangList(cj_params).crawl_page_group,\
                                 name = 'crawler---'+str(list_page_group.index(group))\
                                 ,args=(group,))for group in list_page_group]
    cjz_obj.pool.add(group_th)
    cjz_obj.pool.start()
    cjz_obj.pool.join()


if __name__ == '__main__':
    pt = ProxyTool().add_to_white_list()
    cjz = ChengJianZuFangList(chengji_params)
    print(crawl_all_link(cjz,chengji_params))



