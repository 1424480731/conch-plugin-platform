from database.mongo import MongoChengJiApi

class Generation(MongoChengJiApi):


    def __init__(self):

        super().__init__()
        self.task_dic = {}


    def generation_fc_all_task(self):


        area_list = []
        data_list = self.dbFind(self.dbname,self.setname,{'id':'市名'})
        category_list = ['fangwuchuzu']

        for data in data_list:
            road_sign_list = []
            area_sign = data.get('area_sign')
            district_box = data.get('district_box')
            if district_box:
                for district in district_box:
                    road_box = district.get('road_box')
                    if road_box:
                        for road in road_box:
                            road_sign=road.get('road_sign')
                        road_sign_list.append(road_sign)

            area_list.append({'area_sign':area_sign,'road_sign_list':road_sign_list})

        self.task_dic.update({'category_list':category_list,'area_list':area_list})

        return self.task_dic


    def generation_fc_task_by_category(self,categorys):

        category_list = self.task_dic.get('category_list')
        area_list = self.task_dic.get('area_list')

        task_list = []
        for category in category_list:
            if category in categorys:
                for area in area_list:
                    road_sign_list = area.get('road_sign_list')
                    if road_sign_list:
                        for road_sign in road_sign_list:
                            task_list.append({
                                'area_sign':area.get('area_sign'), \
                                 'road_sign':road_sign, \
                                 'category':category
                            })

        return task_list



# *******************************************生成链接*****************************************************
    def generation_page_url(self,task_list):

        url_list = []
        temp = [['http://www.go007.com/{0}/{1}/{2}/p1'\
                        .format(task.get('area_sign'), \
                                task.get('road_sign'),\
                                'fangwuchuzu'), \
                    'http://www.go007.com/{0}/{1}/{2}/p2' \
                        .format(task.get('area_sign'), \
                                task.get('road_sign'), \
                                'fangwuchuzu')]
                    for task in task_list]
        for url in temp:
            url_list.extend(url)


        return url_list


    def generation_detail_html_url(self,task_list):

        link = 'http://www.go007.com/{0}/{1}/{2}'
        url_list  = []
        for task in task_list:
            area_sign = task.get('area_sign')
            road_sign = task.get('road_sign')
            categroy_name = 'fangwuchuzu'
            html_box = self.get_detail_html_links(road_sign)
            url_list.extend([{'detail_url':link.format(area_sign,categroy_name,html_msg.get('id')+'.htm'),'road_sign':road_sign}\
                             for html_msg in html_box])
        return url_list

    def genneration_detail_page_picture_url(self,task_list):

        picture_list = []
        for task in task_list:
            road_sign = task.get('road_sign')
            html_box = self.get_detail_html_links(road_sign)
            for html_msg in html_box:
                data  =html_msg.get('data')
                if data:
                    image_url = data.get('img_url')
                    image_box = data.get('img_box')
                    if image_box or image_url:
                        picture_list.append({
                            'img_url':image_url,
                            'image_box':image_box,
                            'road_sign':road_sign,
                            'id': html_msg.get('id')
                        })
        return picture_list

if __name__ == '__main__':

    g = Generation()
    # print(g.generation_fc_all_task())

    g.generation_fc_all_task()
    list_g = g.generation_fc_task_by_category(['fangwuchuzu'])
    pu = g.genneration_detail_page_picture_url(list_g)
    print(pu)
    # print(list_g)
    # print(list_g)
    # url_list = g.generation_page_url(list_g)
    # url_list = g.generation_detail_html_url(list_g)
    # print(url_list)
    # for url in url_list:
    #     print(url)

    # print(g.generation_detail_html_url(list_g))
    # for url in g.generation_url(list_g):
    #     print(url)
    # a = [{'2125895a48276fba': ''}, {'998790293850a899': ''},]
    # for i in a:
    #     print(list(i.keys())[0])
    from database import mongo
    mb = mongo.MongoBase()
    a = 'c8eb0012ff9b4afc'

    # def get_detail_html_links():
    #
    #     g = Generation()
    #     g.generation_fc_all_task()
    #     list_g = g.generation_fc_task_by_category(['fangwuchuzu'])
    #     list_d = g.generation_detail_html_url(list_g)
    #     table_conn = mb.get_table('zf', 'cjzf')
    #     for  d in list_d:
    #         road_sign =d.get('road_sign')
    #         key = d.get('detail_url').split('/')[-1].split('.')[0]
    #         print(list_d.index(d),d.get('detail_url'),road_sign,key)
    #         table_conn.update_one(
    #             {'district_box.road_box.road_sign':road_sign },
    #             {'$unset': {"district_box.$[outter].road_box.$[inner].html_box.$[box]."+key: ''}},
    #             array_filters=[{"outter.road_box": {'$ne': []}}, {"inner.road_sign": road_sign},
    #                            {"box.id" : key}, ]
    #         )
    #
    # get_detail_html_links()