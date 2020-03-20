from lxml import etree
from crawler.collection.key_map import go007_zf_map
import re
import urllib.parse as urllib_parse
from crawler.parse.parse_base import ParseBase
from env.exception import ParseFailureException


class ChengJiFangChan(ParseBase):

    def __init__(self):

        pass

    def parse_zf_link(self, resp):
        e = etree.HTML(resp)
        hrefs = e.xpath('.//ul[@class="box"]/li/a[contains(@href,"htm")]/@href | \
        .//ul[@class="box"]/li/h2/a[contains(@href,"htm")]/@href')
        return hrefs

    def parse_zf_detail_html_a(self, res):
        
        parse_result_a = {
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

        e = etree.HTML(res)
        parse_status = {'status':-1}
        try:
            detail_top = e.xpath('.//div[@class="content"]/div[@class="left"]/div[@class="details_top"]')
            if detail_top:
                detail_top = detail_top[0]
                viewad_header = detail_top.xpath('./div[@class="viewad-header"]')

                pic_box = detail_top.xpath('./div[@class="pic_box"]')

                viewad_box = detail_top.xpath('./div[@class="viewad_box"]')
                detail_view = detail_top.xpath('./dl[@class="detail_view"]')

                # print(viewad_header, pic_box, viewad_box, detail_view)

                if viewad_header:
                    viewad_header = viewad_header[0]
                    view_title = viewad_header.xpath('./div[@class="viewad-title "]/h1/text()')
                    view_actions = viewad_header.xpath('./div[@class="viewad-actions"]/span[1]/text()')

                    if view_title:
                        view_title = view_title[0].replace('\r\n', '').replace(' ', '')
                        parse_result_a['viewad_header']['view_title'] = view_title
                        # print(parse_result_a['viewad_header']['view_title'])
                    if view_actions:
                        parse_result_a['viewad_header']['view_actions'] = view_actions[0]
                    # print(view_title, view_actions[0])

                if pic_box:
                    pic_box = pic_box[0]
                    # print('''pic_box''')
                    img_url = pic_box.xpath('./img/@src')
                    if img_url:
                        parse_result_a['img_url'] = img_url[0]
                    # print(img_url[0])

                if viewad_box:
                    viewad_box = viewad_box[0]
                    viewad_meta = viewad_box.xpath('.//ul[@class="viewad-meta"]')
                    if len(viewad_meta) == 2:
                        viewad_meta_produce = viewad_meta[0]
                        viewad_meta_contact = viewad_meta[1]
                        viewad_meta_label_list = viewad_box.xpath('.//ul[@class="viewad-meta"]/li/label/text()')
                        label_list = [label.replace('\r\n', '').replace(' ', '').replace('：', '') for label in
                                      viewad_meta_label_list]
                        self.check_keys_exists(label_list, go007_zf_map)

                        viewad_meta_span_list = viewad_meta_produce.xpath('.//li/span/text()')
                        address = None
                        try:

                            meta_suf = ''
                            viewad_meta_contact = viewad_box.xpath('.//ul[@class="viewad-meta"]')[1]
                            meta_list_pre = viewad_meta_contact.xpath('.//li[3]/span/a/text()')[0]
                            meta_list_suf = viewad_meta_contact.xpath('.//li[3]/span/text()')
                            for _meta_suf in meta_list_suf:
                                meta_suf += _meta_suf.replace('\r\n', '').replace(' ', '')
                            address = meta_list_pre + meta_suf
                        except:
                            pass
                        viewad_meta_dic = {}
                        try:
                            name = re.search('unescape\("(.*?)\"\)', res).group(1).replace('%u', '\\u')
                            name = urllib_parse.unquote(name.encode().decode('unicode-escape'))
                            if not self.is_all_chinese(name):
                                name = None
                        except:
                            name = None
                        try:
                            phone = re.search('unescape\("(\d+)', res).group(1)
                        except:
                            phone = e.xpath('.//input[@id="hfPhone"]/@value')[0]
                        else:
                            phone =  None
                        viewad_meta_span_list.extend([name, phone, address])
                        # print(viewad_meta_span_list)
                        for label in label_list:
                            viewad_meta_dic.update({
                                go007_zf_map.get(label): viewad_meta_span_list[label_list.index(label)]
                            })
                        parse_result_a.update({
                            'viewad_box': viewad_meta_dic
                        })

                if detail_view:
                    detail_view = detail_view[0]
                    dtlist = detail_view.xpath('./dd/div[@class="dllist"]/dl/dt/text()')
                    dllist = detail_view.xpath('./dd/div[@class="dllist"]/dl/dd/text()')
                    view_box = detail_view.xpath('./dd/div[@class="view_box"]/text()')
                    container = detail_view.xpath('./dd/ul[@class="container"]/li/img/@src')
                    # print(dtlist, '\n', dllist)
                    d_dic = {}
                    for dt in dtlist:
                        if dt in go007_zf_map.keys():
                            d_dic.update({go007_zf_map.get(dt): dllist[dtlist.index(dt)]})

                    parse_result_a['detail_view']['detail_produce'] = d_dic
                    if view_box:
                        parse_result_a['detail_view']['view_box'] = view_box[0].replace('\r\n', '').replace(' ', '')
                    parse_result_a['detail_view']['img_box'] = container
                    # print('------\n', d_dic, '\n', view_box, '\n', container)
            # print(parse_result_a)
            parse_status = {'status': 1}
        except ParseFailureException as e:
            raise e('parse_html_a parse failure')
        parse_result_a.update(parse_status)
        return parse_result_a

    def parse_zf_detail_html_b(self, res):

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
        e = etree.HTML(res)
        parse_status = {'status': -1}
        try:
            detail_top = e.xpath('.//div[@class="content"]/div[@class="left"]/div[@class="details_top"]')
            if detail_top:
                detail_top = detail_top[0]
                viewad_header = detail_top.xpath('./div[@class="viewad-header"]')
                no_pic = detail_top.xpath('./div[@class="no_pic"]')

                if viewad_header:
                    viewad_header = viewad_header[0]
                    view_title = viewad_header.xpath('./div[@class="viewad-title "]/h1/text()')
                    view_actions = viewad_header.xpath('./div[@class="viewad-actions"]/span[1]/text()')

                    if view_title:
                        view_title = view_title[0].replace('\r\n', '').replace(' ', '')
                        parse_result_b['viewad_header']['view_title'] = view_title
                    if view_actions:
                        parse_result_b['viewad_header']['view_actions'] = view_actions[0]
                    # print(view_title, '\n', view_actions[0])

                if no_pic:
                    no_pic = no_pic[0]
                    nopic_dic = {}
                    dtlist_box = no_pic.xpath('./div[@class="dllist"]/dl/dt/text()')
                    dllist_box = no_pic.xpath('./div[@class="dllist"]/dl/dd/text()|\
                                                        ./div[@class="dllist"]/dl/dd/em/text()')
                    dllist = [dl.replace('\r\n', '').replace(' ', '') for dl in dllist_box if
                              dl.replace('\r\n', '').replace(' ', '') != '']
                    viewad = detail_top.xpath('./div[@class="no_pic"]/div[@class="viewad"]/ul[@class="viewad-meta"]')[0]
                    # print(dtlist_box, '\n', dllist, '\n', viewad)

                    address = ''
                    viewad_label_list = viewad.xpath('./li/label/text()')
                    label_list = [label.replace('\r\n', '').replace(' ', '') for label in viewad_label_list]
                    viewad_span_pre = viewad.xpath('./li[3]/span/a/text()')

                    for viewad_span in viewad_span_pre:
                        viewad_span = viewad_span + '-'
                        address += viewad_span

                    span_list = viewad.xpath('./li[3]/span/text()')
                    # print(span_list[-1])
                    viewad_span_suf = span_list[-1].replace('\r\n', '').replace(' ', '')
                    address += viewad_span_suf
                    try:
                        name = re.search('unescape\("(.*?)\"\)', res).group(1).replace('%u', '\\u')
                        name = urllib_parse.unquote(name.encode().decode('unicode-escape'))
                        if not self.is_all_chinese(name):
                            name = None
                        # print({'name': name})
                    except:
                        name = None
                    try:
                        phone = re.search('unescape\("(\d+)', res).group(1)
                    except:
                        phone = e.xpath('.//input[@id="hfPhone"]/@value')[0]
                    else:
                        phone = None
                    nopic_dic.update({'name': name, 'phone': phone, 'address': address})
                    if dtlist_box:

                        self.check_keys_exists(dtlist_box, go007_zf_map)
                        if dllist_box:
                            for dt in dtlist_box:
                                nopic_dic.update({go007_zf_map.get(dt): dllist[dtlist_box.index(dt)]})

                parse_result_b["nopic_box"] = nopic_dic
                parse_status = {'status': 1}
        except ParseFailureException as e:
            raise e('parse_html_a parse failure')
        parse_result_b.update(parse_status)
        return parse_result_b

    def parse_html(self, res):

        parse_result = {}
        result = {}
        if re.search('class="pic_box"', res):
            parse_result = self.parse_zf_detail_html_a(res)
            result.update({
                'header_link': None,
                'title': parse_result.get('viewad_header', {}).get('view_title'),
                'pubdate': parse_result.get('viewad_header', {}).get('view_actions', {}),
                'img_url': parse_result.get('img_url'),
                'msg_type': parse_result.get('viewad_box', {}).get('msg_type'),
                'source': parse_result.get('viewad_box', {}).get('source'),
                'area': parse_result.get('viewad_box', {}).get('area'),
                'price': parse_result.get('viewad_box', {}).get('price'),
                'name': parse_result.get('viewad_box', {}).get('name'),
                'phone': parse_result.get('viewad_box', {}).get('phone'),
                'address': parse_result.get('viewad_box', {}).get('address'),
                'decoration_situation': parse_result.get('detail_view', {}).get('detail_produce', {}).get(
                    'decoration_situation'),
                'storey': parse_result.get('detail_view').get('detail_produce', {}).get('storey'),
                'deposit': parse_result.get('detail_view').get('detail_produce', {}).get('deposit'),
                'layout': parse_result.get('detail_view').get('detail_produce', {}).get('layout'),
                'orientation': parse_result.get('detail_view').get('detail_produce', {}).get('orientation'),
                'housing_estate': parse_result.get('detail_view').get('detail_produce', {}).get('housing_estate'),
                'view_box': parse_result.get('detail_view').get('view_box'),
                'img_box': parse_result.get('detail_view').get('img_box'),
                'status' : parse_result.get('status')
            })
        if re.search('class="no_pic"', res):
            parse_result = self.parse_zf_detail_html_b(res)
            result.update({
                'header_link': None,
                'title': parse_result.get('viewad_header',{}).get('view_title'),
                'pubdate': parse_result.get('viewad_header',{}).get('view_actions',{}),
                'img_url': parse_result.get('img_url'),
                'msg_type': parse_result.get('nopic_box',{}).get('msg_type'),
                'source': parse_result.get('nopic_box',{}).get('source'),
                'area': parse_result.get('nopic_box',{}).get('area'),
                'price': parse_result.get('nopic_box',{}).get('price'),
                'name': parse_result.get('nopic_box',{}).get('name'),
                'phone': parse_result.get('nopic_box',{}).get('phone'),
                'address': parse_result.get('nopic_box',{}).get('address'),
                'decoration_situation': parse_result.get('nopic_box',{}).get('decoration_situation'),
                'storey': parse_result.get('nopic_box').get('storey'),
                'deposit': parse_result.get('nopic_box').get('deposit'),
                'layout': parse_result.get('nopic_box').get('layout'),
                'orientation': parse_result.get('nopic_box').get('orientation'),
                'housing_estate': parse_result.get('nopic_box').get('housing_estate'),
                'view_box': parse_result.get('nopic_box').get('view_box'),
                'img_box': parse_result.get('nopic_box').get('img_box'),
                'status':parse_result.get('status')
            })
        return result





if __name__ == '__main__':
    import requests

    res_a = requests.get('http://www.go007.com/haikou/fangwuchuzu/714411d2b15c5ea1.htm').text
    res_b = requests.get('http://www.go007.com/beijing/fangwuchuzu/e11fd68dd51dea68.htm').text

    cjfc = ChengJiFangChan()
    # cjfc.parse_zf_detail_html_a(res_a)
    # cjfc.parse_zf_detail_html_b(res_b)
    print(cjfc.parse_html(res_b))

    {'parse_type': 'A', 'img_url': 'http://img.go007.com/2020/02/11/714411d2b15c5ea1_0.jpg',
     'viewad_header': {'view_actions': '2020年02月11日 18:13', 'view_title': '在环境优美的村庄里'},
     'detail_view': {'view_box': '空气清新，环境优美，在老村文化室后面，平房，可养鸡?种菜，离镇上不远，靠近绿城满春风',
                     'detail_produce': {'orientation': '南', 'Rental_allocation': '床,热水器,独立卫生间,阳台,可做饭',
                                        'decoration_situation': '简单装修', 'housing_estate': '云龙镇老村'},
                     'img_box': ['http://img.go007.com/2020/02/11/714411d2b15c5ea1_1.jpg',
                                 'http://img.go007.com/2020/02/11/714411d2b15c5ea1_2.jpg',
                                 'http://img.go007.com/2020/02/11/714411d2b15c5ea1_3.jpg',
                                 'http://img.go007.com/2020/02/11/714411d2b15c5ea1_4.jpg']},
     'viewad_box': {'msg_type': '房产 房屋出租', 'source': '个人', 'phone': '13518066257', 'address': '海口-琼山_老村文化室',
                    'name': '匿名', 'price': ' 500元', 'area': '120㎡'}}

    {'viewad_header': {'view_actions': '2019年09月29日 16:40', 'view_title': '房东直租北三环国展左家庄一居室'}, 'parse_type': 'B',
     'nopic_box': {'price': '5700元', 'storey': '8层', 'Rental_allocation': '床,沙发,热水器,电脑桌椅,衣柜,电视,空调,冰箱,洗衣机,暖气',
                   'housing_estate': '左家庄北里', 'layout': '1室1厅1卫', 'phone': None, 'msg_type': '房产房屋出租', 'source': '个人',
                   'decoration_situation': '简单装修', 'deposit': '押一付三', 'address': '北京-朝阳区-三元桥-', 'name': None,
                   'area': '46㎡'}}

{'storey': None, 'view_title': '在环境优美的村庄里', 'Rental_allocation': '床,热水器,独立卫生间,阳台,可做饭', 'phone': '13518066257',
 'source': '个人', 'orientation': '南', 'title': None, 'deposit': None, 'view_actions': '2020年02月11日 18:13',
 'header_link': None, 'address': '海口-琼山_老村文化室', 'name': '匿名', 'price': ' 500元', 'decoration_situation': '简单装修',
 'housing_estate': '云龙镇老村', 'pubdate': None, 'area': '120㎡',
 'img_url': 'http://img.go007.com/2020/02/11/714411d2b15c5ea1_0.jpg', 'msg_type': '房产 房屋出租',
 'img_box': ['http://img.go007.com/2020/02/11/714411d2b15c5ea1_1.jpg',
             'http://img.go007.com/2020/02/11/714411d2b15c5ea1_2.jpg',
             'http://img.go007.com/2020/02/11/714411d2b15c5ea1_3.jpg',
             'http://img.go007.com/2020/02/11/714411d2b15c5ea1_4.jpg'],
 'view_box': '空气清新，环境优美，在老村文化室后面，平房，可养鸡?种菜，离镇上不远，靠近绿城满春风', 'layout': None}

{'storey': None, 'pubdate': '2020年02月11日 18:13', 'phone': '13518066257', 'name': '匿名', 'address': '海口-琼山_老村文化室',
 'orientation': '南', 'msg_type': '房产 房屋出租', 'img_url': 'http://img.go007.com/2020/02/11/714411d2b15c5ea1_0.jpg',
 'header_link': None, 'decoration_situation': '简单装修', 'housing_estate': '云龙镇老村', 'deposit': None, 'layout': None,
 'area': '120㎡', 'price': ' 500元', 'view_box': '空气清新，环境优美，在老村文化室后面，平房，可养鸡?种菜，离镇上不远，靠近绿城满春风',
 'img_box': ['http://img.go007.com/2020/02/11/714411d2b15c5ea1_1.jpg',
             'http://img.go007.com/2020/02/11/714411d2b15c5ea1_2.jpg',
             'http://img.go007.com/2020/02/11/714411d2b15c5ea1_3.jpg',
             'http://img.go007.com/2020/02/11/714411d2b15c5ea1_4.jpg'], 'source': '个人', 'title': '在环境优美的村庄里'}
