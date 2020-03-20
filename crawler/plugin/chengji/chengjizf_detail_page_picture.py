from crawler.search.chengji.search_chuzu import SearchChuzu
from database.mongo import MongoChengJiApi
from crawler.tools.chengji.generation import Generation
from crawler.tools.chengji.utils import div_array,ProxyTool,write_to_disk
from crawler.tools.chengji.threading_m import ThreadPool
from env.exception import ProxyFailureException,UnknowErrorException,TimeOutError,NotHaveThatPageException,ParseFailureException
from env.params import chengji_params
import time,random,threading
index = 0
lock = threading.RLock()

def run():
    cjz = ChengJianZuFangDetailPicture(chengji_params)
    crawl_all_link(cjz, chengji_params)

# -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-

class ChengJianZuFangDetailPicture:

    def __init__(self, params):

        self.search = SearchChuzu(params)
        self.mongo_client = MongoChengJiApi()
        self.result = {}
        self.generation = Generation()
        self.pool = ThreadPool()
        self.proxies_tools = ProxyTool()

    def generation_detail_pic_group(self):

        self.generation.generation_fc_all_task()
        list_g = self.generation.generation_fc_task_by_category(['fangwuchuzu'])
        list_page = self.generation.genneration_detail_page_picture_url(list_g)
        list_g_group = div_array(list_page, group_size=30000)
        return list_g_group

    def crawl_picture_group(self, picture_list):

        global index, index_2
        proxies = self.proxies_tools.get_proxies()
        path = 'E:\image\chengji\chnegji_fangwuchuzu'
        for detail_box in picture_list:
            pic_url_box = []
            pic_url_box.append(detail_box.get('img_url'))
            pic_url_box.extend(detail_box.get('image_box'))
            road_sign = detail_box.get('road_sign')
            id = detail_box.get('id')
            cond = {'road_sign': detail_box.get('road_sign'),'id':id}
            if not self.mongo_client.check_pic_crawl_status(cond):

                for pic_url in pic_url_box:

                    for tr in range(2):

                        try:
                            filename = road_sign+'_'+pic_url.split('/')[-1]
                            time.sleep(random.randint(1, 5))
                            data = self.search.crawl_detail_picture(pic_url, proxies=proxies)
                            write_to_disk(path,filename,data)
                            self.mongo_client.update_pic_status({'road_sign': cond.get('road_sign'),'id':id})
                            lock.acquire()
                            index += 1
                            lock.release()
                            print(threading.current_thread().name, '<--', index, ':', cond, pic_url, data[10])
                            if data:
                                break
                        except (ProxyFailureException, TimeOutError,) as e:
                            print(threading.current_thread().name, '<--', pic_url, e, proxies)
                            proxies = self.proxies_tools.get_proxies()
                        except (UnknowErrorException, NotHaveThatPageException) as e:
                            print(threading.current_thread().name, '<--', pic_url, e)
                        except ParseFailureException as e:
                            raise e
                        except BaseException as e:
                            print(threading.current_thread().name, '<--', pic_url, e)

def crawl_all_link(cjz_obj, cj_params):
    detail_pic_group = cjz_obj.generation_detail_pic_group()
    group_th = [threading.Thread(target=ChengJianZuFangDetailPicture(cj_params).crawl_picture_group, \
                                 name='crawler---' + str(detail_pic_group.index(group)), \
                                 args=(group,)) for group in detail_pic_group]
    cjz_obj.pool.add(group_th)
    cjz_obj.pool.start()
    cjz_obj.pool.join()


if __name__ == '__main__':
    pt = ProxyTool().add_to_white_list()
    cjz = ChengJianZuFangDetailPicture(chengji_params)
    print(crawl_all_link(cjz, chengji_params))
