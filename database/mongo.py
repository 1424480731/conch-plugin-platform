from pymongo import MongoClient
from env.exception import MongoDbDisconn,MongoTableDisconn
import urllib.parse as parse
import base64
import time
settings = {
    "ip":'127.0.0.1',
    "port":27017,
}

class MongoBase(object):

    def __init__(self):

        try:
            self.conn = MongoClient(settings["ip"], settings["port"])
        except Exception as e:
            raise e

    def get_table(self,dbname,setname):

        dbconn = None
        table_conn = None

        try:
            dbconn = self.conn[dbname]
            table_conn = dbconn[setname]
        except MongoDbDisconn:
            print('DB connect is not normal！！！')
        except MongoTableDisconn:
            print('Table connect is not normal！！！')
        return table_conn

    def insert(self,dbname,setname,dic):
        
        table_conn = self.get_table(dbname,setname)
        table_conn.insert(dic)

    def update(self, dbname,setname,dic, newdic):
        table_conn = self.get_table(dbname, setname)
        table_conn.update(dic, newdic)

    def delete(self, dbname,setname,dic):
        table_conn = self.get_table(dbname, setname)
        status = table_conn.remove(dic)
        return status
    def dbFind(self, dbname,setname,dic):
        table_conn = self.get_table(dbname, setname)
        data = table_conn.find(dic)
        data = list(data)
        return data

    def findAll(self,dbname,setname,):
        table_conn = self.get_table(dbname, setname)
        for i in table_conn.find():
            print(i)

class  MongoChengJiApi(MongoBase):

    def __init__(self):
        self.dbname = 'zf'
        self.setname = 'cjzf'
        super().__init__()

    def get_one_detail_html_links(self,cond):

        road_sign = cond.get('road_sign')
        id = cond.get('id')
        pipeline = [
            {'$match': {"district_box.road_box.road_sign": road_sign}},
            {'$unwind': "$district_box"},
            {'$unwind': "$district_box.road_box"},
            {'$unwind': "$district_box.road_box.html_box"},
            {'$match': {"district_box.road_box.html_box.id": id}},
            {'$project': {'district_box.road_box.html_box': 1, '_id': 0}}
        ]
        table_conn = self.get_table(self.dbname, self.setname)
        detail_link_box = table_conn.aggregate(pipeline)
        detail_link_box = list(detail_link_box)
        if detail_link_box:
            return detail_link_box[0].get('district_box').get('road_box').get('html_box')
        return {}

    def get_detail_html_links(self,road_sign):

        pipeline = [
            {'$match': {"district_box.road_box.road_sign": road_sign}},
            {'$unwind': "$district_box"},
            {'$unwind': "$district_box.road_box"},
            {'$match': {"district_box.road_box.road_sign": road_sign}},
            {'$project': {'district_box.road_box.html_box': 1, '_id': 0}}
        ]
        table_conn = self.get_table(self.dbname,self.setname)
        detail_link_box = table_conn.aggregate(pipeline)
        detail_link_box = list(detail_link_box)
        if detail_link_box:
            return detail_link_box[0].get('district_box').get('road_box').get('html_box')
        return {}

    def get_html_box(self,cond):
        road_sign = cond.get('road_sign')
        html_box = self.get_detail_html_links(road_sign)
        return html_box

    def get_html_box_size(self, cond):
        html_box = self.get_html_box(cond)
        size = len(html_box)
        return size

    def get_detail_html_link_keys(self,cond):
        key_list = []
        for html in self.get_html_box(cond):
            key_list.append(html.get('id'))
        return key_list


    def check_html_box_exist(self,cond):

        size = self.get_html_box_size(cond)
        if size > 0 :
            return True
        return False

    def trim_to_fix_size(self,cond):

        html_box=self.get_html_box(cond)
        box_size = len(html_box)
        if box_size < 60:
            return True

        if box_size >=60:
            box = html_box[0:40]
            road_sign = cond.get('road_sign')
            table_conn = self.get_table(self.dbname, self.setname)
            table_conn.update_one(
                {'district_box.road_box.road_sign': road_sign},
                {'$set': {"district_box.$[outter].road_box.$[inner].html_box":box}},
                array_filters=[{"outter.road_box": {'$ne': []}}, {"inner.road_sign": road_sign}]
            )
            return True
        return False

    def update_detail_link(self,data):

        l = data.get('url').split('/')
        dic_list  = data.get('data')
        area_sign,road_sign = l[-4],l[-3]
        table_conn = self.get_table(self.dbname, self.setname)
        link_keys = self.get_detail_html_link_keys({'road_sign':road_sign})
        for dic in dic_list:
            try:
                key = dic.get('key').split('/')
                key = key[-1].split('.')[0]
                res = dic.get('res')
                if key not in link_keys:
                    box = {
                        'id':key,
                        'data':res
                    }
                    table_conn.update_one(
                        {'district_box.road_box.road_sign': road_sign},
                        {'$addToSet': {"district_box.$[outter].road_box.$[inner].html_box": box}},
                        array_filters=[{"outter.road_box": {'$ne': []}}, {"inner.road_sign": road_sign}, ]
                    )
            except:
                pass

    def update_detail_html(self,data):

        road_sign = data.get('road_sign')
        html_link = data.get('link')
        key = html_link.split('/')[-1].split('.')[0]
        res = data.get('data')
        res.update({'header_link': html_link})
        table_conn = self.get_table(self.dbname, self.setname)
        try:
            table_conn.update_one(
                {'district_box.road_box.road_sign': road_sign},
                {'$set': {"district_box.$[outter].road_box.$[inner].html_box.$[box].data": res}},
                array_filters=[{"outter.road_box": {'$ne': []}}, {"inner.road_sign": road_sign},{"box.id":key},]
            )
        except:
            pass

    def update_pic_status(self,data):

        road_sign = data.get('road_sign')
        id = data.get('id')
        status = data.get('status')
        table_conn = self.get_table(self.dbname, self.setname)
        try:
            table_conn.update_one(
                {'district_box.road_box.road_sign': road_sign},
                {'$set': {"district_box.$[outter].road_box.$[inner].html_box.$[box].data.pic_crawl_stutas": status}},
                array_filters=[{"outter.road_box": {'$ne': []}}, {"inner.road_sign": road_sign},{"box.id":id},]
            )
        except:
            pass

#     **********************************详情页的操作*****************************

    def check_detail_html_data_exist(self,cond):


        html_box = self.get_one_detail_html_links(cond)
        data = html_box.get('data')
        if data:
            status = data.get('status')
            if status == 1:
                return True
        return False

    def check_pic_crawl_status(self,cond):
        html_box = self.get_one_detail_html_links(cond)
        status = html_box.get('data', {}).get('pic_crawl_stutas')
        if status == 1:
            return True
        return False




if __name__ == '__main__':

   ml = MongoBase()
   ml = MongoChengJiApi()
   dbname = 'zf'
   setname = 'cjzf'
   data = {
        'data':[{
            'key':'http://www.go007.com/aletai/fangwuchuzu/2125895a48276fba.htm',
            'res':'',
                }],
        'url': 'http://www.go007.com/aletai/aletaishi/fangwuchuzu/p1',
   }
   print(ml.get_detail_html_link_keys({'road_sign':'aletaishi','id':'c8eb0012ff9b4c'}))
   # ml.trim_to_fix_size({'road_sign':'nanfenqu'})
   # print(ml.get_html_box({'road_sign':'jimunaixian'}))
   # print({}.keys())
   # ml.update_detail_link(data)
   # print(ml.get_html_box_size({'road_sign':'zhangqianyiy'}))
   # print(ml.findAll(dbname,setname))
   # print(ml.insert(dbname,setname,{'1':'48fa4f54dasf'}))
   # print(ml.dbFind(dbname,setname,{'origin_net':'城际分类'}))
   # print(ml.delete(dbname,setname,{}))
   # for i in ml.dbFind(dbname, setname, {'origin_net': '城际分类'}):
   #     print(i.get('level_1_category_name'))
   #     for j in i.get('level_2_category_box'):
   #         print(j)
   # ml.get_table(dbname,setname).update_many({'district_box': {'$exists': False}, 'area':{'$exists': True}},{'$set':{'district_box':[]}})
