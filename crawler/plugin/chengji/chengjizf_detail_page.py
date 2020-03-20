from crawler.search.chengji.search_chuzu import SearchChuzu
from crawler.parse.chengji.parse_chengji_fc import ChengJiFangChan
from database.mongo import MongoChengJiApi
from crawler.tools.chengji.generation import Generation
from crawler.tools.chengji.utils import div_array,ProxyTool
from crawler.tools.chengji.threading_m import ThreadPool
from env.exception import ProxyFailureException,UnknowErrorException,TimeOutError,NotHaveThatPageException,ParseFailureException
from env.params import chengji_params
import time,random,threading
index = 0
lock = threading.RLock()

def run():
    cjz = ChengJianZuFangDetail(chengji_params)
    print(crawl_all_link(cjz, chengji_params))

# -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
class ChengJianZuFangDetail:

    def __init__(self, params):

        self.search = SearchChuzu(params)
        self.zf_parse = ChengJiFangChan()
        self.mongo_client = MongoChengJiApi()
        self.result = {}
        self.generation = Generation()
        self.pool = ThreadPool()
        self.proxies_tools = ProxyTool()

    def generation_detail_group(self):

        self.generation.generation_fc_all_task()
        list_g = self.generation.generation_fc_task_by_category(['fangwuchuzu'])
        list_page = self.generation.generation_detail_html_url(list_g)
        list_g_group = div_array(list_page, group_size=30000)
        return list_g_group

    def crawl_detail_group(self, list_detail):

        global index, index_2
        proxies = self.proxies_tools.get_proxies()

        for detail_box in list_detail:


            url = detail_box.get('detail_url')
            id = url.split('/')[-1].split('.')[0]
            cond = {'road_sign': detail_box.get('road_sign'),'id':id}
            if not self.mongo_client.check_detail_html_data_exist(cond):
                for tr in range(2):

                    try:
                        time.sleep(random.randint(1, 5))
                        res = self.search.crawl_detail_html(url, proxies=proxies)
                        data = self.zf_parse.parse_html(res)
                        self.mongo_client.update_detail_html({'road_sign': cond.get('road_sign'),'link':url,'data': data})
                        lock.acquire()
                        index += 1
                        lock.release()
                        print(threading.current_thread().name, '<--', index, ':', cond, url, res.find('我要留言'), data)
                        if data.get('status'):
                            break
                    except (ProxyFailureException, TimeOutError,) as e:
                        print(threading.current_thread().name, '<--', url, e, proxies)
                        proxies = self.proxies_tools.get_proxies()
                    except (UnknowErrorException, NotHaveThatPageException) as e:
                        print(threading.current_thread().name, '<--', url, e)
                    except ParseFailureException as e:
                        raise e
                    except BaseException as e:
                        print(threading.current_thread().name, '<--', url, e)

def crawl_all_link(cjz_obj, cj_params):
    detail_page_group = cjz_obj.generation_detail_group()
    group_th = [threading.Thread(target=ChengJianZuFangDetail(cj_params).crawl_detail_group, \
                                 name='crawler---' + str(detail_page_group.index(group)), \
                                 args=(group,)) for group in detail_page_group]
    cjz_obj.pool.add(group_th)
    cjz_obj.pool.start()
    cjz_obj.pool.join()





if __name__ == '__main__':
    pt = ProxyTool().add_to_white_list()
    cjz = ChengJianZuFangDetail(chengji_params)
    print(crawl_all_link(cjz, chengji_params))


