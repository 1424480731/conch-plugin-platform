import requests
from lxml import etree
from database.mongo import MongoBase
import re
import urllib.parse as urllib_parse

# bad_r = requests.get('http://www.go007.com/aletai/fangwuchuzu/').text
# r = etree.HTML(bad_r)
# elist = r.xpath('.//ul[@class="box"]/li/a[contains(@href,"htm")]/@href')
# for e in elist:
#     print(e)
#
url = 'http://www.go007.com/changecity.aspx'
mon = MongoBase()
dbname = 'zf'
setname = 'cjzf'
go007_zf_map = {

    '信息类别': 'msg_type',
    '来源': 'source',
    '面积': 'area',
    '价格': 'price',
    '联系人': 'name',
    '手机': 'phone',
    '地址': 'address',
    '装修情况': 'decoration_situation',
    '出租配置': 'Rental_allocation',
    '楼层': 'storey',
    '押金': 'deposit',
    '户型': 'layout',
    '朝向': 'orientation',
    '小区': 'housing_estate'

}
parse_result = {

    'parse_type': 'A',
    'viewad_header': {
        'view_title': None,
        'view_actions': None,
    },
    'img_url': None,
    'viewad_box': {
        'msg_type': None,
        'source': None,
        'area': None,
        'price': None,
        'name': None,
        'phone': None,
        'address': None
    },
    'detail_view': {
        'detail_produce': {
            'decoration_situation': None,
            'storey': None,
            'deposit': None,
            'layout': None,
            'orientation': None,
            'housing_estate': None,
        },
        'view_box': None,
        'img_box': []
    }
}

def chengji(url):
    res = requests.get(url).text
    r = etree.HTML(res)
    ar = r.xpath('.//ul[@class="cities"]/li/a')
    for e in ar:
        a = e.xpath('./@href')[0].split('/')[-2]
        try:
            za = e.xpath('./text()')[0]
        except:
            za = e.xpath('./span/text()')[0]
        print(a, za)
        mon.insert(dbname, setname, {'area_sign': a, 'area': za, 'id': "市名"})


def get_catagory():
    pass


def erj():
    url = 'http://www.go007.com/{}/'
    p = mon.dbFind(dbname, setname, {})
    res = requests.get(url.format('beijing')).text
    r = etree.HTML(res)
    dl = r.xpath('.//dl')
    for d in dl:
        one = d.xpath('.//dt/a/text()')[0]
        two = d.xpath('.//dd/div[@class="lista"]/a | .//dd/div[@class="listbox"]/a')
        for t in two:
            level_2_catagory_name = t.xpath('./text()')[0]
            level_2_catagory_name_sign = t.xpath('./@href')[0].split('/')[-2:]
            if level_2_catagory_name_sign[-1] == '':
                level_2_catagory_name_sign = level_2_catagory_name_sign[0]
                print(one, level_2_catagory_name, level_2_catagory_name_sign)
            else:
                level_2_catagory_name_sign = level_2_catagory_name_sign[0] + ',' + level_2_catagory_name_sign[1]
                print(one, level_2_catagory_name, level_2_catagory_name_sign)
            if mon.dbFind(dbname, setname, {'origin_net': '城际分类', 'level_1_category_name': one}) == []:
                mon.insert(dbname, setname, {'origin_net': '城际分类', 'level_1_category_name': one,
                                             'level_2_category_box': [{'level_2_catagory_name': level_2_catagory_name,
                                                                       'level_2_catagory_name_sign': level_2_catagory_name_sign}]})
            else:

                mon.update(dbname, setname, {'origin_net': '城际分类', 'level_1_category_name': one}, {'$push': {
                    'level_2_category_box': {'level_2_catagory_name': level_2_catagory_name,
                                             'level_2_catagory_name_sign': level_2_catagory_name_sign}}})


def get_district():
    url = 'http://www.go007.com/{0}/{1}'
    md = mon.dbFind(dbname, setname, {'id': '市名', 'district_box': []})
    import time, random
    for i in md:
        time.sleep(random.randint(10, 20))
        area_sign = i.get('area_sign')
        print(area_sign)
        res = requests.get(url.format(area_sign, 'fangwuchuzu')).text
        r = etree.HTML(res)
        dl = r.xpath('.//div[@class="box sH"]/a')[2:]
        for d in dl:
            district_sign = d.xpath('./@href')[0].split('/')[-3]
            district = d.xpath('./text()')[0]
            print(district_sign, district)
            mon.update(dbname, setname, {'area_sign': area_sign},
                       {'$push': {'district_box': {'district': district, 'district_sign': district_sign}}})


def parse_a():

    pic_url_list = []
    res = requests.get('http://www.go007.com/haikou/fangwuchuzu/714411d2b15c5ea1.htm').text
    e = etree.HTML(res)

    detail_top = e.xpath('.//div[@class="content"]/div[@class="left"]/div[@class="details_top"]')

    if detail_top:
        detail_top = detail_top[0]
        viewad_header = detail_top.xpath('./div[@class="viewad-header"]')

        pic_box = detail_top.xpath('./div[@class="pic_box"]')

        viewad_box = detail_top.xpath('./div[@class="viewad_box"]')
        detail_view = detail_top.xpath('./dl[@class="detail_view"]')

        print(viewad_header, pic_box, viewad_box, detail_view)

        if viewad_header:
            viewad_header = viewad_header[0]
            view_title = viewad_header.xpath('./div[@class="viewad-title "]/h1/text()')
            view_actions = viewad_header.xpath('./div[@class="viewad-actions"]/span[1]/text()')

            if view_title:
                view_title = view_title[0].replace('\r\n', '').replace(' ', '')
                parse_result['viewad_header']['view_title'] = view_title
                print(parse_result['viewad_header']['view_title'])
            if view_actions:
                parse_result['viewad_header']['view_actions'] = view_actions[0]
            print(view_title, view_actions[0])
        if pic_box:
            pic_box = pic_box[0]
            print('''pic_box''')
            img_url = pic_box.xpath('./img/@src')
            if img_url:
                parse_result['img_url'] = img_url[0]
            print(img_url[0])
        if viewad_box:
            viewad_box = viewad_box[0]
            viewad_meta = viewad_box.xpath('.//ul[@class="viewad-meta"]')
            if len(viewad_meta) == 2:
                viewad_meta_produce = viewad_meta[0]
                viewad_meta_contact = viewad_meta[1]
                viewad_meta_label_list = viewad_box.xpath('.//ul[@class="viewad-meta"]/li/label/text()')
                label_list =[label.replace('\r\n', '').replace(' ', '').replace('：', '') for label in viewad_meta_label_list]
                check_keys_exists(label_list)

                viewad_meta_span_list = viewad_meta_produce.xpath('.//li/span/text()')
                address = None
                try:

                    meta_suf = ''
                    viewad_meta_contact =  viewad_box.xpath('.//ul[@class="viewad-meta"]')[1]
                    meta_list_pre = viewad_meta_contact.xpath('.//li[3]/span/a/text()')[0]
                    meta_list_suf = viewad_meta_contact.xpath('.//li[3]/span/text()')
                    for _meta_suf in meta_list_suf:
                        meta_suf += _meta_suf.replace('\r\n','').replace(' ','')
                    address = meta_list_pre + meta_suf
                except:
                    pass
                viewad_meta_dic = {}
                name = re.search('unescape\("(.*?)\"\)', res).group(1).replace('%u', '\\u')
                name = urllib_parse.unquote(name.encode().decode('unicode-escape'))
                phone = re.search('unescape\("(\d+)', res).group(1)
                viewad_meta_span_list.extend([name,phone,address])
                print(viewad_meta_span_list)
                for label in label_list:
                    viewad_meta_dic.update({
                                                go007_zf_map.get(label):viewad_meta_span_list[label_list.index(label)]
                                        })
                parse_result.update({
                                        'viewad_box':viewad_meta_dic
                                     })

        #     if len(viewad_meta_list) == 2:
        #         viewad_meta_produce = viewad_meta_list[0]
        #         viewad_meta_contact = viewad_meta_list[1]
        #         meta_list_label = view
        #         meta_list_span = viewad_meta_produce.xpath('.//li/span/text()')
        #
        #         print(meta_list)
        #         parse_result['viewad_box']['viewad_meta_produce']['msg_type'] = meta_list[0]
        #         parse_result['viewad_box']['viewad_meta_produce']['source'] = meta_list[1]
        #         parse_result['viewad_box']['viewad_meta_produce']['area'] = meta_list[2]
        #         parse_result['viewad_box']['viewad_meta_produce']['price'] = meta_list[3]
        #
        #         meta_list_pre = viewad_meta_contact.xpath('.//li[3]/span/a/text()')
        #         meta_list_suf = viewad_meta_contact.xpath('.//li[3]/span/text()')
        #         meta_suf = ''
        #         for _meta_suf in meta_list_suf:
        #             meta_suf += _meta_suf.replace('\r\n','').replace(' ','')
        #
        #         print(meta_suf)
        #         name = re.search('unescape\("(.*?)\"\)', res).group(1).replace('%u', '\\u')
        #         name = urllib_parse.unquote(name.encode().decode('unicode-escape'))
        #         phone = re.search('unescape\("(\d+)', res).group(1)
        #         print(name, phone)
        #         parse_result['viewad_box']['viewad_meta_contact']['name'] = name
        #         parse_result['viewad_box']['viewad_meta_contact']['phone'] = phone
        #         parse_result['viewad_box']['viewad_meta_contact']['address'] \
        #             = meta_list_pre[0] + meta_suf
        #         print(parse_result['viewad_box']['viewad_meta_contact']['address'])
        if detail_view:
            detail_view = detail_view[0]
            dtlist = detail_view.xpath('./dd/div[@class="dllist"]/dl/dt/text()')
            dllist = detail_view.xpath('./dd/div[@class="dllist"]/dl/dd/text()')
            view_box = detail_view.xpath('./dd/div[@class="view_box"]/text()')
            container = detail_view.xpath('./dd/ul[@class="container"]/li/img/@src')
            print(dtlist, dllist)
            d_dic = {}
            for dt in dtlist:
                if dt in go007_zf_map.keys():
                    d_dic.update({go007_zf_map.get(dt): dllist[dtlist.index(dt)]})

            parse_result['detail_view']['detail_produce'] = d_dic
            if view_box:
                parse_result['detail_view']['view_box'] = view_box[0].replace('\r\n','').replace(' ','')
            parse_result['detail_view']['img_box'] = container
            print('------\n', d_dic, '\n', view_box, '\n', container)

    print(parse_result)

    return parse_result


def check_keys_exists(key_list):

    added_key =set(key_list) - set(go007_zf_map.keys())
    if added_key == set():
        return True
    else:
        raise BaseException('新增Key{0}'.format(added_key))

parse_result_b = {

    'parse_type': 'B',
    'viewad_header': {
        'view_title': None,
        'view_actions': None,
    },
    'nopic_box': {
        'msg_type': None,
        'source': None,
        'area': None,
        'price': None,
        'name': None,
        'phone': None,
        'address': None,
        'decoration_situation': None,
        'storey': None,
        'deposit': None,
        'layout': None,
        'orientation': None,
        'housing_estate': None,
        'view_box': None,
    },
}


def parse_b():

    res = requests.get('http://www.go007.com/beijing/fangwuchuzu/e11fd68dd51dea68.htm').text
    e = etree.HTML(res)
    detail_top = e.xpath('.//div[@class="content"]/div[@class="left"]/div[@class="details_top"]')
    print(res)
    if detail_top:
        detail_top = detail_top[0]
        viewad_header = detail_top.xpath('./div[@class="viewad-header"]')

         


        if viewad_header:
            viewad_header = viewad_header[0]
            view_title = viewad_header.xpath('./div[@class="viewad-title "]/h1/text()')
            view_actions = viewad_header.xpath('./div[@class="viewad-actions"]/span[1]/text()')

            if view_title:
                view_title = view_title[0].replace('\r\n', '').replace(' ', '')
                parse_result_b['viewad_header']['view_title'] = view_title
                print(parse_result['viewad_header']['view_title'])
            if view_actions:
                parse_result_b['viewad_header']['view_actions'] = view_actions[0]
            print(view_title, view_actions[0])

        nopic_dic = {}
        dtlist_box = detail_top.xpath('./div[@class="no_pic"]/div[@class="dllist"]/dl/dt/text()')
        dllist_box = detail_top.xpath('./div[@class="no_pic"]/div[@class="dllist"]/dl/dd/text()|\
                                        ./div[@class="no_pic"]/div[@class="dllist"]/dl/dd/em/text()')
        dllist = [ dl.replace('\r\n', '').replace(' ', '') for dl in dllist_box if dl.replace('\r\n', '').replace(' ', '') != '']
        viewad  = detail_top.xpath('./div[@class="no_pic"]/div[@class="viewad"]/ul[@class="viewad-meta"]')[0]
        print(dtlist_box,dllist,viewad)

        address = ''
        viewad_label_list  = viewad.xpath('./li/label/text()')
        label_list = [ label.replace('\r\n','').replace(' ','') for label in viewad_label_list]
        viewad_span_pre = viewad.xpath('./li[3]/span/a/text()')

        for viewad_span in viewad_span_pre:
            viewad_span = viewad_span+'-'
            address += viewad_span
        viewad_span_suf = viewad.xpath('./li[3]/span/text()')[0].replace('\r\n','').replace(' ','')
        address += viewad_span_suf
        try:
            name = re.search('unescape\("(.*?)\"\)', res).group(1).replace('%u', '\\u')
            name = urllib_parse.unquote(name.encode().decode('unicode-escape'))
            if not is_all_chinese(name):
                name =  None
            print(name)
        except:
            name =  None
        try:
            phone = re.search('unescape\("(\d+)', res).group(1)
        except:
            phone = None

        nopic_dic.update({'name':name,'phone':phone,'address':address})


        if dtlist_box:

            check_keys_exists(dtlist_box)
            
            if dllist_box:
                for dt in dtlist_box:
                    nopic_dic.update({go007_zf_map.get(dt):dllist[dtlist_box.index(dt)]})



        parse_result_b["nopic_box"] = nopic_dic
    print(parse_result_b)


            


def is_all_chinese(strs):
    for _char in strs:
        if not '\u4e00' <= _char <= '\u9fa5':
            return False
    return True






from database.mongo import MongoChengJiApi
from crawler.tools.chengji.generation import Generation
import uuid,time,random,traceback

def get_level3_area():

   _url = "http://www.go007.com/{0}/{1}/fangwuchuzu/"
   g =  Generation()
   c = g.generation_fc_all_task()
   category = c.get('category_list')[0]
   area_list = c.get('area_list')
   list_g=[]
   for area in area_list:
        for district_sign in area.get('district_sign_list'):
            list_g.append({
               'category':category,
               'area_sign':area.get('area_sign'),
                'district_sign': district_sign})
   for lg in list_g:
       district_sign = lg.get('district_sign')
       area_sign = lg.get('area_sign')
       url = _url.format(area_sign,district_sign)
       print(url)
       a = g.dbFind('zf','cjzf',{'district_box.road_box.road_sign':district_sign})
       if not a:
           try:
               time.sleep(random.randint(10,30))
               res = requests.get(url).text
               e = etree.HTML(res)
               a = e.xpath('.//div[@class="box sH"]')[1]
               road_sign_list = a.xpath('./a/@href')[1:]
               road_list = a.xpath('./a/text()')[1:]
               print(road_list,'\n',road_sign_list)
               for index in range(len(road_list)):
                   box = {'district_box.$.road_box': {'road': road_list[index], 'road_sign': road_sign_list[index].split('/')[-3],'html_box': {}}}
                   g.update('zf','cjzf',{'district_box.district_sign':district_sign},{'$addToSet':box})
           except:
                traceback.print_stack()

import threading

def c():
    while True:
        print(threading.current_thread().name)

def a(p):
    for i in range(10):
        threading.Thread(target=c,name=p+str(i)).start()


if __name__ == '__main__':
    # chengji(url)
    # erj()
    # mon.update(dbname, setname, {'district_box': {'$exists': False}, 'area':{'$exists': True}},{'district_box':[]},multi=True)
    # get_district()
    # id = uuid.uuid4()
    # print(id)
    # get_level3_area()

    # url = 'http://'
    # proxies = {
    #     'http': 'http://121.232.195.179:4507',
    #     # 'https': 'http://10.10.1.10:1080',
    # }
    # print(requests.get('http://httpbin.org/get',proxies = proxies).text)

    # print(requests.get(url))
    # import datetime
    # print(type(time.time()))
    # print(a)
    import multiprocessing
    C = multiprocessing.Process(target=a,args=('C',))
    D = multiprocessing.Process(target=a,args=('D',))
    C.start()
    D.start()
    time.sleep(20)
    C.terminate()
    D.terminate()






















{'parse_type': 'A', 'detail_view': {'detail_produce': {'decoration_situation': '简单装修', 'housing_estate': '云龙镇老村',
                                                       'Rental_allocation': '床,热水器,独立卫生间,阳台,可做饭', 'orientation': '南'},
                                    'view_box': [
                                        '\r\n                    空气清新，环境优美，在老村文化室后面，平房，可养鸡?种菜，离镇上不远，靠近绿城满春风  \r\n                '],
                                    'img_box': ['http://img.go007.com/2020/02/11/714411d2b15c5ea1_1.jpg',
                                                'http://img.go007.com/2020/02/11/714411d2b15c5ea1_2.jpg',
                                                'http://img.go007.com/2020/02/11/714411d2b15c5ea1_3.jpg',
                                                'http://img.go007.com/2020/02/11/714411d2b15c5ea1_4.jpg']},
 'viewad_header': {'view_title': '在环境优美的村庄里', 'view_actions': '2020年02月11日 18:13'},
 'viewad_box': {'viewad_meta_contact': {'phone': None, 'address': None, 'name': None},
                'viewad_meta_produce': {'phone': '13518066257', 'source': '个人', 'msg_type': '房产 房屋出租', 'price': ' 500元',
                                        'address': ' -\r\n            琼山_老村文化室\r\n        ', 'name': '匿名',
                                        'area': '120㎡'}},
 'img_url': 'http://img.go007.com/2020/02/11/714411d2b15c5ea1_0.jpg'}
{
    'img_url': 'http://img.go007.com/2020/02/11/714411d2b15c5ea1_0.jpg', 'detail_view': {
    'detail_produce': {'Rental_allocation': '床,热水器,独立卫生间,阳台,可做饭', 'decoration_situation': '简单装修', 'orientation': '南',
                       'housing_estate': '云龙镇老村'},
    'view_box': '空气清新，环境优美，在老村文化室后面，平房，可养鸡?种菜，离镇上不远，靠近绿城满春风',
    'img_box': ['http://img.go007.com/2020/02/11/714411d2b15c5ea1_1.jpg',
                'http://img.go007.com/2020/02/11/714411d2b15c5ea1_2.jpg',
                'http://img.go007.com/2020/02/11/714411d2b15c5ea1_3.jpg',
                'http://img.go007.com/2020/02/11/714411d2b15c5ea1_4.jpg']},
    'viewad_header': {'view_actions': '2020年02月11日 18:13', 'view_title': '在环境优美的村庄里'},
    'viewad_box': {'viewad_meta_contact': {'address': None, 'name': None, 'phone': None},
    'viewad_meta_produce': {'area': '120㎡', 'address': ' -\r\n            琼山_老村文化室\r\n        ',
                                        'source': '个人', 'msg_type': '房产 房屋出租', 'price': ' 500元', 'name': '匿名',
                                        'phone': '13518066257'}}, 'parse_type': 'A'}
{   'viewad_box': {'viewad_meta_produce': {'price': ' 500元', 'name': '匿名', 'phone': '13518066257', 'address': '-琼山_老村文化室',
                                        'source': '个人', 'area': '120㎡', 'msg_type': '房产 房屋出租'},
                'viewad_meta_contact': {'phone': None, 'name': None, 'address': None}},
 'viewad_header': {'view_actions': '2020年02月11日 18:13', 'view_title': '在环境优美的村庄里'}, 'parse_type': 'A', 'detail_view': {
    'img_box': ['http://img.go007.com/2020/02/11/714411d2b15c5ea1_1.jpg',
                'http://img.go007.com/2020/02/11/714411d2b15c5ea1_2.jpg',
                'http://img.go007.com/2020/02/11/714411d2b15c5ea1_3.jpg',
                'http://img.go007.com/2020/02/11/714411d2b15c5ea1_4.jpg'],
    'view_box': '空气清新，环境优美，在老村文化室后面，平房，可养鸡?种菜，离镇上不远，靠近绿城满春风',
    'detail_produce': {'orientation': '南', 'Rental_allocation': '床,热水器,独立卫生间,阳台,可做饭', 'decoration_situation': '简单装修',
                       'housing_estate': '云龙镇老村'}}, 'img_url': 'http://img.go007.com/2020/02/11/714411d2b15c5ea1_0.jpg'}
{'img_url': 'http://img.go007.com/2020/02/11/714411d2b15c5ea1_0.jpg',
 'viewad_header': {'view_title': '在环境优美的村庄里', 'view_actions': '2020年02月11日 18:13'}, 'detail_view': {
    'img_box': ['http://img.go007.com/2020/02/11/714411d2b15c5ea1_1.jpg',
                'http://img.go007.com/2020/02/11/714411d2b15c5ea1_2.jpg',
                'http://img.go007.com/2020/02/11/714411d2b15c5ea1_3.jpg',
                'http://img.go007.com/2020/02/11/714411d2b15c5ea1_4.jpg'],
    'view_box': '空气清新，环境优美，在老村文化室后面，平房，可养鸡?种菜，离镇上不远，靠近绿城满春风',
    'detail_produce': {'Rental_allocation': '床,热水器,独立卫生间,阳台,可做饭', 'housing_estate': '云龙镇老村',
                       'decoration_situation': '简单装修', 'orientation': '南'}},
 'viewad_box': {'viewad_meta_produce': {'price': ' 500元', 'area': '120㎡', 'msg_type': '房产 房屋出租', 'source': '个人'},
                'viewad_meta_contact': {'name': '匿名', 'address': '海口-琼山_老村文化室', 'phone': '13518066257'}},
 'parse_type': 'A'}

{'parse_type': 'A', 'viewad_box': {'msg_type': '房产 房屋出租', 'area': '120㎡', 'price': ' 500元', 'phone': '13518066257',
                                   'address': '海口-琼山_老村文化室', 'source': '个人', 'name': '匿名'},
 'viewad_header': {'view_title': '在环境优美的村庄里', 'view_actions': '2020年02月11日 18:13'}, 'detail_view': {
    'detail_produce': {'housing_estate': '云龙镇老村', 'decoration_situation': '简单装修',
                       'Rental_allocation': '床,热水器,独立卫生间,阳台,可做饭', 'orientation': '南'},
    'view_box': '空气清新，环境优美，在老村文化室后面，平房，可养鸡?种菜，离镇上不远，靠近绿城满春风',
    'img_box': ['http://img.go007.com/2020/02/11/714411d2b15c5ea1_1.jpg',
                'http://img.go007.com/2020/02/11/714411d2b15c5ea1_2.jpg',
                'http://img.go007.com/2020/02/11/714411d2b15c5ea1_3.jpg',
                'http://img.go007.com/2020/02/11/714411d2b15c5ea1_4.jpg']},
 'img_url': 'http://img.go007.com/2020/02/11/714411d2b15c5ea1_0.jpg'}
{'parse_type': 'B',
 'nopic_box': {'area': '', 'layout': '押一付三', 'address': '北京-朝阳区-三元桥-', 'decoration_situation': '', 'phone': None,
               'Rental_allocation': '简单装修', 'storey': '床,沙发,热水器,电脑桌椅,衣柜,电视,空调,冰箱,洗衣机,暖气', 'price': '46㎡',
               'msg_type': '房产房屋出租', 'deposit': '8层', 'housing_estate': '1室1厅1卫', 'source': '个人',
               'name': '<script src=\'" + _bdhmProtocol + "hm.baidu.com/h.js?0eeb55807a58e8c459df75ad35dbea95\' type=\'text/javascript\'></script>'},
 'viewad_header': {'view_actions': None, 'view_title': None}}

{'nopic_box': {'storey': '8层', 'price': '5700元', 'phone': None, 'layout': '1室1厅1卫', 'deposit': '押一付三',
               'name': '<script src=\'" + _bdhmProtocol + "hm.baidu.com/h.js?0eeb55807a58e8c459df75ad35dbea95\' type=\'text/javascript\'></script>',
               'address': '北京-朝阳区-三元桥-', 'area': '46㎡', 'msg_type': '房产房屋出租', 'housing_estate': '左家庄北里',
               'decoration_situation': '简单装修', 'Rental_allocation': '床,沙发,热水器,电脑桌椅,衣柜,电视,空调,冰箱,洗衣机,暖气', 'source': '个人'},
 'viewad_header': {'view_title': '房东直租北三环国展左家庄一居室', 'view_actions': '2019年09月29日 16:40'}, 'parse_type': 'B'}

{'nopic_box': {
                'decoration_situation': '简单装修', 'Rental_allocation': '床,沙发,热水器,电脑桌椅,衣柜,电视,空调,冰箱,洗衣机,暖气', 'area': '46㎡',
               'phone': None, 'layout': '1室1厅1卫', 'price': '5700元', 'storey': '8层', 'msg_type': '房产房屋出租',
               'source': '个人', 'housing_estate': '左家庄北里', 'deposit': '押一付三', 'name': None, 'address': '北京-朝阳区-三元桥-'},
                'parse_type': 'B',
                    'viewad_header': {'view_title': '房东直租北三环国展左家庄一居室', 'view_actions': '2019年09月29日 16:40'}}
